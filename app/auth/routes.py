from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session

from app.auth.schemas import RegisterSchema,LoginSchema
from app.core.dependencies import get_db,get_current_user
from app.models.user import User
from app.core.security import hash_password,verify_password
from app.auth.service import create_access_token


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)
#what ever the routes will bewill start with /auth

@router.post("/register")
def register_user(
    user: RegisterSchema,
    db: Session = Depends(get_db)
):

    hashed_password = hash_password(
        user.password
    )

    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully"
    }

@router.post("/login")
def login_user(
    user: LoginSchema,
    db: Session = Depends(get_db)
):

    db_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    is_password_correct = verify_password(
        user.password,
        db_user.password
    )

    if not is_password_correct:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        data={
            "sub": str(db_user.id)
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
    
