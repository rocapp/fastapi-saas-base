from typing import List

from fastapi import Depends, FastAPI, Header, HTTPException
import uvicorn
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.dependencies.auth import get_current_account
from app.database import engine, Base
from app.routers import auth, accounts, email_addresses, random

# Create tables in database.
Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(
    title="FastAPI Base",
    description="This is a base app to be used in the future for real SAAS apps and hackathons.",
    version="0.0.1",
    docs_url="/docs", 
    redoc_url=None
)

# Startup Actions
@app.on_event("startup")
async def create_admin():
    db = get_db()
    """If admin account doesn't exist, create it."""
    from app.database import SessionLocal
    from app.controllers.account import create_account
    from app.controllers.account import get_account_by_email
    from app.schemas.account import AccountCreate

    db = SessionLocal()
    account_data = {
        "email": "admin@example.com",
        "password": "password123",
        "first_name": "Admin",
        "last_name": "Istrator",
        "is_system_admin": True
    }
    account_obj = get_account_by_email(db, email=account_data['email'])
    if account_obj:
        return
    
    create_account(
        db,
        AccountCreate(**account_data)
    )
    db.close()


# Add routers
app.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)
app.include_router(
    accounts.router,
    prefix="/accounts",
    tags=["accounts"],
    dependencies=[Depends(get_current_account)],
    responses={404: {"description": "Not found"}},
)
app.include_router(
    email_addresses.router,
    prefix="/email_addresses",
    tags=["email_addresses"],
    dependencies=[Depends(get_current_account)],
    responses={404: {"description": "Not found"}},
)

app.include_router(random.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)