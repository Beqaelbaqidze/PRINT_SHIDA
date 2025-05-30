from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

# -------------------- COMPANIES --------------------

class CompanyCreate(BaseModel):
    company_name: str = Field(..., example="GeoTech Ltd")
    company_number: str = Field(..., example="123456789")
    company_director: Optional[str] = Field(None, example="Nika Beridze")
    company_phone_number: Optional[str] = Field(None, example="+995 599 123 456")
    company_email: Optional[str] = Field(None, example="info@geotech.ge")
    company_address: Optional[str] = Field(None, example="Tbilisi, Georgia")

class CompanyRead(CompanyCreate):
    company_id: int = Field(..., example=1)

# -------------------- OPERATORS --------------------

class OperatorCreate(BaseModel):
    operator_name: str = Field(..., example="Giorgi Ivanidze")
    identify_id: str = Field(..., example="OP12345")

class OperatorRead(OperatorCreate):
    operator_id: int = Field(..., example=1)

# -------------------- COMPUTERS --------------------

class ComputerCreate(BaseModel):
    computer_guid: str = Field(..., example="6a90b8e4-a87a-4bc3-b110-1ff4e8c7a8e1")
    computer_mac_address: str = Field(..., example="00:1A:2B:3C:4D:5E")

class ComputerRead(ComputerCreate):
    computer_id: int = Field(..., example=1)

# -------------------- SOFTWARES --------------------

class SoftwareCreate(BaseModel):
    software_name: str = Field(..., example="AutoCAD 2025")
    price: float = Field(..., example=999.99)

class SoftwareRead(SoftwareCreate):
    software_id: int = Field(..., example=1)

# -------------------- LICENSES --------------------

class LicenseCreate(BaseModel):
    company_id: int = Field(..., example=1)
    operator_id: int = Field(..., example=1)
    computer_id: int = Field(..., example=1)
    software_id: int = Field(..., example=1)
    expire_date: date = Field(..., example="2025-12-31")
    paid: float = Field(default=0, example=100.00)
    stayed: float = Field(default=0, example=0.00)
    status: str = Field(default="active", example="active")
    license_status: str = Field(default="valid", example="valid")

class LicenseRead(LicenseCreate):
    license_id: int = Field(..., example=1)
