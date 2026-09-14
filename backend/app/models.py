from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    ForeignKey,
    Text,
    Index,
)

from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    gender = Column(String(50))
    signup_date = Column(Date)
    country = Column(String(100))


class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True)
    product_name = Column(String(255), nullable=False)
    category = Column(String(100))
    price = Column(Float)
    stock_quantity = Column(Integer)
    brand = Column(String(100))


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True)

    customer_id = Column(
        Integer,
        ForeignKey("customers.customer_id"),
        nullable=False
    )

    order_date = Column(Date)
    total_amount = Column(Float)
    payment_method = Column(String(100))
    shipping_country = Column(String(100))

    __table_args__ = (
        Index("idx_orders_customer_id", "customer_id"),
        Index("idx_orders_order_date", "order_date"),
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    order_item_id = Column(Integer, primary_key=True)

    order_id = Column(
        Integer,
        ForeignKey("orders.order_id"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.product_id"),
        nullable=False
    )

    quantity = Column(Integer)
    unit_price = Column(Float)

    __table_args__ = (
        Index("idx_order_items_order_id", "order_id"),
        Index("idx_order_items_product_id", "product_id"),
    )


class ProductReview(Base):
    __tablename__ = "product_reviews"

    review_id = Column(Integer, primary_key=True)

    product_id = Column(
        Integer,
        ForeignKey("products.product_id"),
        nullable=False
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.customer_id"),
        nullable=False
    )

    rating = Column(Integer)
    review_text = Column(Text)
    review_date = Column(Date)

    __table_args__ = (
        Index("idx_reviews_product_id", "product_id"),
        Index("idx_reviews_customer_id", "customer_id"),
    )