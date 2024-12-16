from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy.sql import func
from datetime import datetime, timedelta, timezone


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    cuit = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    clients = relationship("Client", backref="user")
    invoices = relationship("Invoice", backref="user")
    certificates = relationship("Certificate", back_populates="user")


class Client(Base):
    __tablename__ = "client"

    client_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    name = Column(String(255), nullable=False)
    cuit = Column(String(20))
    tax_condition = Column(String(100))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Invoice(Base):
    __tablename__ = "invoice"

    invoice_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    client_id = Column(Integer, ForeignKey("client.client_id"))
    invoice_number = Column(String(50))
    invoice_type = Column(String(10))
    point_of_sale = Column(Integer)
    date = Column(DateTime, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    net_amount = Column(Numeric(10, 2))
    tax_amount = Column(Numeric(10, 2))
    cae = Column(String(50))
    cae_expiration_date = Column(DateTime)
    status = Column(String(50), default="draft")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class InvoiceItem(Base):
    __tablename__ = "invoice_item"

    item_id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoice.invoice_id"))
    description = Column(String, nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    tax_rate = Column(Numeric(5, 2))
    tax_amount = Column(Numeric(10, 2))

class Certificate(Base):
    __tablename__ = "certificate"

    certificate_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    cert_alias = Column(String, nullable=False)
    certificate = Column(String, nullable=False)
    private_key = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime, default=lambda: datetime.now() + timedelta(days=365))

    user = relationship("User", back_populates="certificates")
    authorizations = relationship("Authorization", back_populates="certificate", cascade="all, delete-orphan")


class Authorization(Base):
    __tablename__ = "authorizations"

    authorization_id = Column(Integer, primary_key=True, index=True)
    certificate_id = Column(Integer, ForeignKey("certificate.certificate_id"), nullable=False)
    service = Column(String, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    certificate = relationship("Certificate", back_populates="authorizations")