from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.models.audit import AuditLog
from app.models.enums import AuditAction
from app.models.user import User
from app.schemas.auth import LoginRequest, ProfileUpdateRequest, PasswordChangeRequest, RequestAccessRequest, TokenResponse, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="This account has been disabled")

    token = create_access_token(user.id, {"role": user.role.value})
    db.add(AuditLog(user_id=user.id, action=AuditAction.LOGIN, status="SUCCESS", detail={"email": user.email}))
    db.commit()
    return TokenResponse(access_token=token)


@router.post("/logout")
def logout(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    db.add(AuditLog(user_id=user.id, action=AuditAction.LOGOUT, status="SUCCESS", detail={}))
    db.commit()
    return {"ok": True}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> User:
    return user


@router.patch("/me", response_model=UserOut)
def update_profile(payload: ProfileUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
    if payload.full_name is not None:
        user.full_name = payload.full_name
    db.commit()
    db.refresh(user)
    return user


@router.post("/me/password")
def change_password(payload: PasswordChangeRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    if not verify_password(payload.current_password, user.hashed_password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    user.hashed_password = hash_password(payload.new_password)
    db.commit()
    return {"ok": True}


@router.post("/request-access", status_code=status.HTTP_202_ACCEPTED)
def request_access(payload: RequestAccessRequest) -> dict:
    # Demo-mode stub: in production this would notify an administrator.
    # Intentionally does not create an account -- access is admin-granted.
    return {"ok": True, "message": "Your request has been received. An administrator will follow up."}
