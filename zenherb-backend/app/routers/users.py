from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import User, Product, WishlistItem, Order
from ..schemas import UserResponse, UserUpdate, WishlistItemResponse, OrderListResponse
from ..auth.auth import get_current_active_user

router = APIRouter(prefix="/users", tags=["User Management"])

@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user = Depends(get_current_active_user)
):
    """Get current user's profile"""
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    update_data: UserUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    if update_data.full_name is not None:
        current_user.full_name = update_data.full_name
    if update_data.phone is not None:
        current_user.phone = update_data.phone
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

# Wishlist
@router.get("/wishlist", response_model=List[WishlistItemResponse])
async def get_wishlist(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's wishlist"""
    wishlist_items = db.query(WishlistItem).filter(
        WishlistItem.user_id == current_user.id
    ).all()
    
    return wishlist_items

@router.post("/wishlist/{product_id}")
async def add_to_wishlist(
    product_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add product to wishlist"""
    # Check if product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if already in wishlist
    existing = db.query(WishlistItem).filter(
        WishlistItem.user_id == current_user.id,
        WishlistItem.product_id == product_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Product already in wishlist")
    
    wishlist_item = WishlistItem(
        user_id=current_user.id,
        product_id=product_id
    )
    db.add(wishlist_item)
    db.commit()
    
    return {"message": "Added to wishlist"}

@router.delete("/wishlist/{product_id}")
async def remove_from_wishlist(
    product_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove product from wishlist"""
    wishlist_item = db.query(WishlistItem).filter(
        WishlistItem.user_id == current_user.id,
        WishlistItem.product_id == product_id
    ).first()
    
    if not wishlist_item:
        raise HTTPException(status_code=404, detail="Item not found in wishlist")
    
    db.delete(wishlist_item)
    db.commit()
    
    return {"message": "Removed from wishlist"}

@router.get("/wishlist/check/{product_id}")
async def check_in_wishlist(
    product_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Check if product is in wishlist"""
    item = db.query(WishlistItem).filter(
        WishlistItem.user_id == current_user.id,
        WishlistItem.product_id == product_id
    ).first()
    
    return {"in_wishlist": item is not None}

# Order History
@router.get("/orders", response_model=OrderListResponse)
async def get_user_orders(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 10
):
    """Get user's order history"""
    from app.routers.orders import router as orders_router
    # Reuse the logic from orders router
    query = db.query(Order).filter(Order.user_id == current_user.id)
    
    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()
    
    return {
        "orders": orders,
        "total": total
    }

# Dashboard Stats
@router.get("/dashboard")
async def get_dashboard_stats(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user dashboard statistics"""
    from sqlalchemy import func
    
    # Order stats
    total_orders = db.query(func.count(Order.id)).filter(
        Order.user_id == current_user.id
    ).scalar() or 0
    
    total_spent = db.query(func.sum(Order.total)).filter(
        Order.user_id == current_user.id,
        Order.status != "cancelled"
    ).scalar() or 0
    
    # Wishlist count
    wishlist_count = db.query(func.count(WishlistItem.id)).filter(
        WishlistItem.user_id == current_user.id
    ).scalar() or 0
    
    # Cart count
    from ..models import CartItem
    cart_count = db.query(func.sum(CartItem.quantity)).filter(
        CartItem.user_id == current_user.id
    ).scalar() or 0
    
    return {
        "total_orders": total_orders,
        "total_spent": round(total_spent, 2),
        "wishlist_count": wishlist_count,
        "cart_count": cart_count,
        "user": {
            "name": current_user.full_name or current_user.username,
            "email": current_user.email
        }
    }