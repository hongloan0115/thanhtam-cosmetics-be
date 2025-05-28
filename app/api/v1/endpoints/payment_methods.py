from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.crud.payment_method import create_payment_method, get_payment_method, get_payment_methods, update_payment_method, delete_payment_method
from app.schemas.payment_method import PaymentMethod, PaymentMethodCreate, PaymentMethodUpdate

router = APIRouter()

@router.get("/", response_model=list[PaymentMethod])
def read_payment_methods(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_payment_methods(db, skip=skip, limit=limit)

@router.get("/{maPhuongThuc}", response_model=PaymentMethod)
def read_payment_method(maPhuongThuc: int, db: Session = Depends(get_db)):
    payment_method = get_payment_method(db, maPhuongThuc)
    if not payment_method:
        raise HTTPException(status_code=404, detail="Payment method not found")
    return payment_method

@router.post("/", response_model=PaymentMethod, status_code=status.HTTP_201_CREATED)
def create_payment_method(payment_method_in: PaymentMethodCreate, db: Session = Depends(get_db)):
    return create_payment_method(db, payment_method_in)

@router.put("/{maPhuongThuc}", response_model=PaymentMethod)
def update_payment_method(maPhuongThuc: int, payment_method_in: PaymentMethodUpdate, db: Session = Depends(get_db)):
    payment_method = update_payment_method(db, maPhuongThuc, payment_method_in)
    if not payment_method:
        raise HTTPException(status_code=404, detail="Payment method not found")
    return payment_method

@router.delete("/{maPhuongThuc}", response_model=PaymentMethod)
def delete_payment_method(maPhuongThuc: int, db: Session = Depends(get_db)):
    payment_method = delete_payment_method(db, maPhuongThuc)
    if not payment_method:
        raise HTTPException(status_code=404, detail="Payment method not found")
    return payment_method
