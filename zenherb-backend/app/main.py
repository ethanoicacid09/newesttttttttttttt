from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, products, courses, cart, orders, users, contact
from fastapi.staticfiles import StaticFiles
# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ZenHerb API",
    description="Natural Wellness & Yoga E-commerce Platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(courses.router, prefix="/courses", tags=["Courses"])
app.include_router(cart.router, prefix="/cart", tags=["Shopping Cart"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(contact.router, prefix="/contact", tags=["Contact"])

@app.get("/")
async def root():
    return {"message": "Welcome to ZenHerb API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
