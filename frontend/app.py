import streamlit as st
import requests


# ==========================================
# CONFIG
# ==========================================

API_URL = "http://127.0.0.1:8000"


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="QueryPilot",
    page_icon="⌘",
    layout="centered"
)


# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

    .block-container {
        max-width: 900px;
        padding-top: 3rem;
        padding-bottom: 4rem;
    }

    .title {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        text-align: center;
        color: #777;
        margin-bottom: 2.5rem;
    }

    .section-title {
        font-size: 1.05rem;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 0.6rem;
    }

    .file-box {
        padding: 1rem;
        border: 1px solid #ddd;
        border-radius: 10px;
        background: #fafafa;
        margin-bottom: 1rem;
    }

    .sql-title {
        font-size: 1.05rem;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 0.5rem;
    }

    footer {
        visibility: hidden;
    }

</style>
""", unsafe_allow_html=True)


# ==========================================
# HEADER
# ==========================================

st.markdown(
    '<div class="title">QueryPilot</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Ask your database questions in plain English.</div>',
    unsafe_allow_html=True
)


# ==========================================
# CSV UPLOAD
# ==========================================

st.markdown(
    '<div class="section-title">Upload your database</div>',
    unsafe_allow_html=True
)

uploaded_files = st.file_uploader(
    "Upload up to 5 CSV files",
    type=["csv"],
    accept_multiple_files=True
)

if uploaded_files:

    if len(uploaded_files) > 5:
        st.error("You can upload a maximum of 5 CSV files.")
        uploaded_files = uploaded_files[:5]

    st.markdown(
        '<div class="file-box">',
        unsafe_allow_html=True
    )

    for file in uploaded_files:
        st.write(f"✓ {file.name}")

    st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# UPLOAD BUTTON
# ==========================================

if uploaded_files:

    if st.button(
        "Upload & Prepare Data",
        use_container_width=True
    ):

        files = []

        for file in uploaded_files:
            files.append(
                (
                    "files",
                    (
                        file.name,
                        file.getvalue(),
                        "text/csv"
                    )
                )
            )

        try:

            with st.spinner(
                "Uploading and preparing your data..."
            ):

                response = requests.post(
                    f"{API_URL}/upload-csv",
                    files=files,
                    timeout=600
                )

            if response.status_code == 200:

                result = response.json()

                if result.get("success"):

                    st.session_state["session_id"] = result[
                        "session_id"
                    ]

                    st.session_state["uploaded"] = True

                    st.success(
                        "Your data is ready."
                    )

                else:

                    st.error(
                        result.get(
                            "message",
                            "Upload failed."
                        )
                    )

            else:

                st.error(
                    f"Upload failed: {response.text}"
                )

        except requests.exceptions.RequestException as e:

            st.error(
                f"Could not connect to QueryPilot API: {e}"
            )


# ==========================================
# QUERY INPUT
# ==========================================

if st.session_state.get("uploaded"):

    st.markdown(
        '<div class="section-title">Ask your database</div>',
        unsafe_allow_html=True
    )

    question = st.text_area(
        "Enter your question",
        placeholder="e.g. Which customers placed orders last month?",
        height=120,
        label_visibility="collapsed"
    )

    if st.button(
        "Generate SQL",
        type="primary",
        use_container_width=True
    ):

        if not question.strip():

            st.warning(
                "Please enter a question."
            )

        else:

            try:

                with st.spinner(
                    "Generating SQL..."
                ):

                    response = requests.post(
                        f"{API_URL}/generate-sql",
                        json={
    "question": question,
    "session_id": st.session_state["session_id"]
},
                        timeout=120
                    )

                if response.status_code == 200:

                    result = response.json()

                    st.markdown(
                        '<div class="sql-title">Generated SQL</div>',
                        unsafe_allow_html=True
                    )

                    st.code(
                        result["sql"],
                        language="sql"
                    )

                else:

                    try:
                        error = response.json().get(
                            "detail",
                            "SQL generation failed."
                        )
                    except Exception:
                        error = "SQL generation failed."

                    st.error(error)

            except requests.exceptions.RequestException as e:

                st.error(
                    f"Could not connect to QueryPilot API: {e}"
                )