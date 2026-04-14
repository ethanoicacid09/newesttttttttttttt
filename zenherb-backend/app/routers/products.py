from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from ..database import get_db
from ..models import Product, Category
from ..schemas import ProductResponse, ProductListResponse, CategoryResponse
from ..auth.auth import get_current_active_user

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/", response_model=ProductListResponse)
async def get_products(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=100),
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = Query(None, enum=["price", "name", "created_at", "rating"]),
    sort_order: Optional[str] = Query("asc", enum=["asc", "desc"]),
    featured: Optional[bool] = None
):
    """Get all products with pagination and filters"""
    query = db.query(Product)
    
    # Apply filters
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if search:
        query = query.filter(
            Product.name.ilike(f"%{search}%") | 
            Product.description.ilike(f"%{search}%")
        )
    
    if featured is not None:
        query = query.filter(Product.is_featured == featured)
    
    # Apply sorting
    if sort_by:
        sort_column = getattr(Product, sort_by, Product.created_at)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(Product.created_at.desc())
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    products = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        "products": products,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }

@router.get("/featured", response_model=List[ProductResponse])
async def get_featured_products(
    db: Session = Depends(get_db),
    limit: int = Query(6, ge=1, le=20)
):
    """Get featured products"""
    products = db.query(Product).filter(
        Product.is_featured == True,
        Product.in_stock == True
    ).limit(limit).all()
    
    return products

@router.get("/bestsellers", response_model=List[ProductResponse])
async def get_bestseller_products(
    db: Session = Depends(get_db),
    limit: int = Query(6, ge=1, le=20)
):
    """Get bestseller products"""
    products = db.query(Product).filter(
        Product.is_bestseller == True,
        Product.in_stock == True
    ).limit(limit).all()
    
    return products

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get single product by ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product

@router.get("/slug/{slug}", response_model=ProductResponse)
async def get_product_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """Get single product by slug"""
    product = db.query(Product).filter(Product.slug == slug).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product

# Categories
@router.get("/categories/list", response_model=List[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    """Get all categories"""
    categories = db.query(Category).all()
    return categories

@router.get("/category/{category_id}", response_model=ProductListResponse)
async def get_products_by_category(
    category_id: int,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=100)
):
    """Get products by category"""
    query = db.query(Product).filter(Product.category_id == category_id)
    
    total = query.count()
    products = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        "products": products,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }