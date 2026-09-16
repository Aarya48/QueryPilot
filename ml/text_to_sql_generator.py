"""
QueryPilot - Text-to-SQL Generator using Fine-tuned T5

This module provides inference for generating SQL from natural language questions
using a fine-tuned T5 model trained on the Spider dataset.
"""

import torch
from pathlib import Path
from typing import Dict, List, Optional
import re

from transformers import T5ForConditionalGeneration, T5Tokenizer

# ==========================================
# CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "final_text_to_sql_model"
MODEL_PATH = MODEL_DIR / "model"
TOKENIZER_PATH = MODEL_DIR / "tokenizer"

MAX_INPUT_LENGTH = 512
MAX_OUTPUT_LENGTH = 256
BEAM_SIZE = 5
NUM_RETURN_SEQUENCES = 1


class TextToSQLGenerator:
    """
    Generate SQL queries from natural language questions using fine-tuned T5.

    Replaces the Gemini API-based generator with a local ML model.
    """

    def __init__(self, model_dir: Optional[Path] = None):
        """
        Initialize the text-to-SQL generator.

        Args:
            model_dir: Path to fine-tuned model directory. Defaults to ml/text_to_sql_model
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        if model_dir is None:
            model_dir = MODEL_DIR

        self.model_path = model_dir / "model"
        self.tokenizer_path = model_dir / "tokenizer"

        self._load_model()

    def _load_model(self):
        """Load pre-trained T5 model and tokenizer."""
        print(f"[INFO] Loading model from {self.model_path}")

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {self.model_path}\n"
                "Please run: python ml/train_text_to_sql.py"
            )

        self.tokenizer = T5Tokenizer.from_pretrained(str(self.tokenizer_path))
        self.model = T5ForConditionalGeneration.from_pretrained(
            str(self.model_path)
        )
        self.model.to(self.device)
        self.model.eval()

        print(f"[INFO] Model loaded successfully on device: {self.device}")

    def _format_input_with_schema(
        self,
        question: str,
        schema: Optional[Dict] = None
    ) -> str:
        """
        Format input question with optional schema context.

        Args:
            question: Natural language question
            schema: Database schema (optional, for context)

        Returns:
            Formatted input string for T5 model
        """
        # Base T5 prefix for text-to-SQL task
        formatted = f"text2sql: {question}"

        # If schema provided, add table/column hints
        if schema:
            table_names = list(schema.keys())
            formatted += f" [TABLES: {', '.join(table_names[:5])}]"

        return formatted

    def _postprocess_sql(self, sql: str) -> str:
        """
        Post-process generated SQL to fix common issues.

        Args:
            sql: Raw generated SQL from model

        Returns:
            Cleaned SQL string
        """
        # Remove extra whitespace
        sql = " ".join(sql.split())

        # Remove accidental markdown if present
        sql = sql.replace("```sql", "").replace("```", "").strip()

        # Ensure it ends without semicolon (our validator doesn't expect it)
        sql = sql.rstrip(";").strip()

        # Fix common spacing issues around operators
        sql = re.sub(r'\s+([,;])', r'\1', sql)  # Remove space before comma/semicolon
        sql = re.sub(r'([,])\s*', r'\1 ', sql)  # Add space after comma

        return sql

    def generate(
        self,
        question: str,
        schema: Optional[Dict] = None,
        num_beams: Optional[int] = None,
        return_confidence: bool = False
    ) -> str or tuple:
        """
        Generate SQL query from natural language question.

        Args:
            question: Natural language question to convert to SQL
            schema: Database schema (optional, for context)
            num_beams: Number of beams for beam search (default: BEAM_SIZE)
            return_confidence: If True, return tuple (sql, confidence_score)

        Returns:
            Generated SQL string, or tuple of (sql, confidence) if return_confidence=True
        """
        if num_beams is None:
            num_beams = BEAM_SIZE

        # Format input
        formatted_input = self._format_input_with_schema(question, schema)

        # Tokenize
        input_ids = self.tokenizer.encode(
            formatted_input,
            return_tensors="pt",
            max_length=MAX_INPUT_LENGTH,
            truncation=True
        ).to(self.device)

        # Generate with beam search
        with torch.no_grad():
            output_ids = self.model.generate(
                input_ids,
                max_length=MAX_OUTPUT_LENGTH,
                num_beams=num_beams,
                early_stopping=True,
                output_scores=True,
                return_dict_in_generate=True,
                num_return_sequences=NUM_RETURN_SEQUENCES
            )

        # Decode SQL
        sql = self.tokenizer.decode(
            output_ids.sequences[0],
            skip_special_tokens=True
        )

        # Post-process
        sql = self._postprocess_sql(sql)

        if return_confidence:
            # Calculate confidence from generation scores
            # This is a simple heuristic - actual confidence would require
            # log-probability analysis
            confidence = 0.85  # Placeholder
            return sql, confidence

        return sql

    def generate_multiple(
        self,
        question: str,
        schema: Optional[Dict] = None,
        num_candidates: int = 3
    ) -> List[str]:
        """
        Generate multiple candidate SQL queries (useful for reranking).

        Args:
            question: Natural language question
            schema: Database schema (optional)
            num_candidates: Number of candidates to generate

        Returns:
            List of generated SQL candidates
        """
        formatted_input = self._format_input_with_schema(question, schema)

        input_ids = self.tokenizer.encode(
            formatted_input,
            return_tensors="pt",
            max_length=MAX_INPUT_LENGTH,
            truncation=True
        ).to(self.device)

        with torch.no_grad():
            output_ids = self.model.generate(
                input_ids,
                max_length=MAX_OUTPUT_LENGTH,
                num_beams=max(5, num_candidates),
                num_return_sequences=num_candidates,
                early_stopping=False,
            )

        candidates = []
        for seq in output_ids:
            sql = self.tokenizer.decode(seq, skip_special_tokens=True)
            sql = self._postprocess_sql(sql)
            candidates.append(sql)

        return candidates

    def batch_generate(
        self,
        questions: List[str],
        schema: Optional[Dict] = None
    ) -> List[str]:
        """
        Generate SQL for multiple questions (batch processing).

        Args:
            questions: List of natural language questions
            schema: Database schema (optional)

        Returns:
            List of generated SQL queries
        """
        results = []
        for question in questions:
            sql = self.generate(question, schema)
            results.append(sql)
        return results


# ==========================================
# TESTING / DEMO
# ==========================================

if __name__ == "__main__":
    print("=" * 70)
    print("TEXT-TO-SQL GENERATOR - DEMO")
    print("=" * 70)

    try:
        # Initialize generator
        generator = TextToSQLGenerator()

        # Test questions
        test_questions = [
            "How many employees are there?",
            "Show me employees with salary above 50000",
            "Which department has the most employees?",
            "List all products ordered by price in descending order",
        ]

        print("\n[DEMO] Generating SQL for test questions:\n")

        for question in test_questions:
            print(f"Q: {question}")

            try:
                sql = generator.generate(question)
                print(f"A: {sql}\n")
            except Exception as e:
                print(f"Error: {e}\n")

        print("=" * 70)
        print("[SUCCESS] Demo completed!")
        print("=" * 70)

    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        print("\n[INFO] Make sure to run training first:")
        print("       python ml/train_text_to_sql.py")
