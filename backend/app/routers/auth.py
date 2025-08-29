from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    """Register new user"""
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(400, "Email already registered")
    
    user = User(
        email=email, 
        password_hash=get_password_hash(password),
        role="admin"  # Default role for Capitol Engineering
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    token = create_access_token(str(user.id))
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    """Login user"""
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    
    token = create_access_token(str(user.id))
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
def get_current_user():
    """Get current user info (placeholder for JWT validation)"""
    # TODO: Add JWT validation middleware in main app
    return {"id": 1, "email": "admin@capitolaz.com", "role": "admin"}