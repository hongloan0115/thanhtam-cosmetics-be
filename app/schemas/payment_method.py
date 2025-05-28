from pydantic import BaseModel
from typing import Optional

class PaymentMethodBase(BaseModel):
    tenPhuongThuc: str
    moTa: Optional[str] = None
    daKichHoat: Optional[bool] = True

class PaymentMethodCreate(PaymentMethodBase):
    pass

class PaymentMethodUpdate(PaymentMethodBase):
    pass

class PaymentMethod(PaymentMethodBase):
    maPhuongThuc: int

    model_config = {
        "from_attributes": True
    }
