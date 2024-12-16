from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    username: str
    email: str
    cuit: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password_hash: str

# UserUpdate Schema
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    cuit: Optional[str] = None
    full_name: Optional[str] = None
    password_hash: Optional[str] = None

class User(UserBase):
    user_id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Client Schemas
class ClientBase(BaseModel):
    name: str
    cuit: Optional[str] = None
    tax_condition: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: bool = True

class ClientCreate(ClientBase):
    pass

# ClientUpdate Schema
class ClientUpdate(BaseModel):
    name: Optional[str] = None
    cuit: Optional[str] = None
    tax_condition: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None

class Client(ClientBase):
    client_id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Invoice Schemas
class InvoiceBase(BaseModel):
    invoice_number: Optional[str] = None
    invoice_type: str
    point_of_sale: int
    date: datetime
    total_amount: float
    net_amount: Optional[float] = None
    tax_amount: Optional[float] = None
    cae: Optional[str] = None
    cae_expiration_date: Optional[datetime] = None
    status: str = "draft"

class InvoiceCreate(InvoiceBase):
    client_id: int

# InvoiceUpdate Schema
class InvoiceUpdate(BaseModel):
    invoice_number: Optional[str] = None
    invoice_type: Optional[str] = None
    point_of_sale: Optional[int] = None
    date: Optional[datetime] = None
    total_amount: Optional[float] = None
    net_amount: Optional[float] = None
    tax_amount: Optional[float] = None
    cae: Optional[str] = None
    cae_expiration_date: Optional[datetime] = None
    status: Optional[str] = None
    client_id: Optional[int] = None

class Invoice(InvoiceBase):
    invoice_id: int
    user_id: int
    client_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# InvoiceItem Schemas
class InvoiceItemBase(BaseModel):
    description: str
    quantity: float
    unit_price: float
    total_price: float
    tax_rate: Optional[float] = None
    tax_amount: Optional[float] = None

class InvoiceItemCreate(InvoiceItemBase):
    invoice_id: int

# InvoiceItemUpdate Schema
class InvoiceItemUpdate(BaseModel):
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total_price: Optional[float] = None
    tax_rate: Optional[float] = None
    tax_amount: Optional[float] = None

class InvoiceItem(InvoiceItemBase):
    item_id: int
    invoice_id: int

    model_config = ConfigDict(from_attributes=True)

# Certificate Schemas
class CertificateBase(BaseModel):
    cert_alias: str

class CertificateCreate(CertificateBase):
    certificate: str
    private_key: str

# CertificateUpdate Schema
class CertificateUpdate(BaseModel):
    cert_alias: Optional[str] = None
    certificate: Optional[str] = None
    private_key: Optional[str] = None

class Certificate(CertificateBase):
    certificate_id: int
    user_id: int
    created_at: datetime
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AuthorizationBase(BaseModel):
    service: str
    status: str

class AuthorizationCreate(AuthorizationBase):
    certificate_id: int

class Authorization(AuthorizationBase):
    authorization_id: int
    certificate_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)