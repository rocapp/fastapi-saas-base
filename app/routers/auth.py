from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED

from app.dependencies import get_db
from app.controllers.auth import ACCESS_TOKEN_EXPIRE_MINUTES, Token, authenticate_user, create_access_token
from app.dependencies.auth import get_current_account
from app.schemas.account import Account
router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db_session: Session = Depends(get_db)):
    account = authenticate_user(db_session, form_data.username, form_data.password)
    if not account:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": account.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
    