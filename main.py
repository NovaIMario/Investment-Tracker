from fastapi import FastAPI, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from db.database import SessionLocal, Base, engine
from db.models import User, MoneyEntry
from datetime import date as dateType
from sqlalchemy.orm import Session

app = FastAPI()

# Access static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create database tables if not exist 
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# Add session
app.add_middleware(SessionMiddleware, secret_key="secret_key")

# Set up templates eg HTML
templates = Jinja2Templates(directory="templates")

@app.get("/")
def home(request: Request):
    # If user not logged in, redirect to login
    if "user" not in request.session:
        return RedirectResponse(url="/login", status_code=303)
    #return home page
    return templates.TemplateResponse("index.html", {"request": request, "user": request.session["user"]})

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register(request: Request, username: str=Form(...), password: str=Form(...), db: Session=Depends(get_db)):
    # Check if user already exists
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username already exists"})
    user = User(username=username, password=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    # Redirect to login page
    return RedirectResponse(url="/login", status_code=303)

@app.post("/login")
def login(request: Request, username: str=Form(...), password: str=Form(...), db: Session=Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    # Validate user username and password
    if not user or user.password != password:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"})
    # Set session
    request.session["user"] = username
    # Redirect to home page
    return RedirectResponse(url="/", status_code=303)

@app.get("/logout")
def logout(request: Request):
    # Clear session
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

@app.post("/add_entry")
def add_entry(request: Request, amount: int=Form(...), date: dateType=Form(...), db: Session=Depends(get_db)):
    if "user" not in request.session:
        return RedirectResponse(url="/login", status_code=303)
    user = db.query(User).filter(User.username == request.session["user"]).first()
    already_exists = db.query(MoneyEntry).filter(MoneyEntry.user_id == user.id, MoneyEntry.date == date).first()
    if(already_exists):
        return templates.TemplateResponse("index.html", {"request": request, "user": request.session["user"], "error": "Entry for this date already exists"})
    entry = MoneyEntry(user_id=user.id, amount=amount, date=date)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return RedirectResponse(url="/", status_code=303)

@app.post("/delete_entry")
def delete_entry(request: Request, date: dateType=Form(...), db: Session=Depends(get_db)):
    if "user" not in request.session:
        return RedirectResponse(url="/login", status_code=303)
    user = db.query(User).filter(User.username == request.session["user"]).first()
    entry = db.query(MoneyEntry).filter(MoneyEntry.user_id == user.id, MoneyEntry.date == date).first()
    if not entry:
        return templates.TemplateResponse("index.html", {"request": request, "user": request.session["user"], "error": "There isn't an entry for this date"})
    db.delete(entry)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/data")
def get_data(request: Request, db: Session=Depends(get_db)):
    if "user" not in request.session:
        return RedirectResponse(url="/login", status_code=303)
    user = db.query(User).filter(User.username == request.session["user"]).first()
    entries = db.query(MoneyEntry).filter(MoneyEntry.user_id == user.id).order_by(MoneyEntry.date).all()
    return {"dates": [entry.date.isoformat() for entry in entries], "amounts": [entry.amount for entry in entries]}