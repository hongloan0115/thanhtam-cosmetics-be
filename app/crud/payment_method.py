from sqlalchemy.orm import Session
from app.models.payment_method import PaymentMethod
from app.schemas.payment_method import PaymentMethodCreate, PaymentMethodUpdate

def get_payment_method(db: Session, maPhuongThuc: int):
    return db.query(PaymentMethod).filter(PaymentMethod.maPhuongThuc == maPhuongThuc).first()

def get_payment_methods(db: Session, skip: int = 0, limit: int = 100):
    return db.query(PaymentMethod).offset(skip).limit(limit).all()

def create_payment_method(db: Session, payment_method: PaymentMethodCreate):
    db_payment_method = PaymentMethod(
        tenPhuongThuc=payment_method.tenPhuongThuc,
        moTa=payment_method.moTa,
        daKichHoat=payment_method.daKichHoat
    )
    db.add(db_payment_method)
    db.commit()
    db.refresh(db_payment_method)
    return db_payment_method

def update_payment_method(db: Session, maPhuongThuc: int, payment_method: PaymentMethodUpdate):
    db_payment_method = db.query(PaymentMethod).filter(PaymentMethod.maPhuongThuc == maPhuongThuc).first()
    if not db_payment_method:
        return None
    for var, value in vars(payment_method).items():
        if value is not None:
            setattr(db_payment_method, var, value)
    db.commit()
    db.refresh(db_payment_method)
    return db_payment_method

def delete_payment_method(db: Session, maPhuongThuc: int):
    db_payment_method = db.query(PaymentMethod).filter(PaymentMethod.maPhuongThuc == maPhuongThuc).first()
    if not db_payment_method:
        return None
    db_payment_method.daKichHoat = False
    db.commit()
    db.refresh(db_payment_method)
    return db_payment_method
