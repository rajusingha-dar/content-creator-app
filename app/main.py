from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api import auth
from app.database import get_db, engine, Base
from app.utils.security import get_current_user

# Create tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Content Creator App")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])

# Templates
templates = Jinja2Templates(directory="templates")

# Root route - redirect to login if not authenticated
@app.get("/")
async def root(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("index.html", {"request": request})

# Dashboard route - requires authentication
@app.get("/dashboard")
async def dashboard(request: Request, db: Session = Depends(get_db)):
    try:
        current_user = await get_current_user(request, db)
        return templates.TemplateResponse("dashboard.html", {"request": request, "user": current_user})
    except HTTPException:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)

# Error handler for 401 Unauthorized
@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
async def unauthorized_exception_handler(request, exc):
    return RedirectResponse(url="/auth/login")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)