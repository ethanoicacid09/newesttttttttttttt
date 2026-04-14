from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import User, Product, CartItem
from ..schemas import CartItemResponse, CartItemCreate, CartItemUpdate
from ..auth.auth import get_current_active_user

router = APIRouter(prefix="/cart", tags=["Shopping Cart"])

@router.get("/", response_model=List[CartItemResponse])
async def get_cart(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's cart items"""
    cart_items = db.query(CartItem).filter(
        CartItem.user_id == current_user.id
    ).all()
    
    return cart_items

@router.post("/add", response_model=CartItemResponse)
async def add_to_cart(
    item: CartItemCreate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add item to cart"""
    # Check if product exists and is in stock
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if not product.in_stock:
        raise HTTPException(status_code=400, detail="Product is out of stock")
    
    # Check if item already in cart
    existing_item = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.product_id == item.product_id
    ).first()
    
    if existing_item:
        # Update quantity
        existing_item.quantity += item.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
    
    # Create new cart item
    cart_item = CartItem(
        user_id=current_user.id,
        product_id=item.product_id,
        quantity=item.quantity
    )
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    
    return cart_item

@router.put("/{item_id}", response_model=CartItemResponse)
async def update_cart_item(
    item_id: int,
    update_data: CartItemUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update cart item quantity"""
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    if update_data.quantity <= 0:
        db.delete(cart_item)
        db.commit()
        return cart_item
    
    cart_item.quantity = update_data.quantity
    db.commit()
    db.refresh(cart_item)
    
    return cart_item

@router.delete("/{item_id}")
async def remove_from_cart(
    item_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove item from cart"""
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    db.delete(cart_item)
    db.commit()
    
    return {"message": "Item removed from cart"}

@router.delete("/")
async def clear_cart(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Clear all cart items"""
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    db.commit()
    
    return {"message": "Cart cleared"}

@router.get("/count")
async def get_cart_count(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get total number of items in cart"""
    from sqlalchemy import func
    count = db.query(func.sum(CartItem.quantity)).filter(
        CartItem.user_id == current_user.id
    ).scalar() or 0
    
    return {"count": count}

@router.get("/total")
async def get_cart_total(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get cart total price"""
    cart_items = db.query(CartItem).filter(
        CartItem.user_id == current_user.id
    ).all()
    
    total = sum(item.product.price * item.quantity for item in cart_items)
    item_count = sum(item.quantity for item in cart_items)
    
    return {
        "subtotal": round(total, 2),
        "item_count": item_count,
        "shipping": 0 if total >= 500 else 50,  # Free shipping over Rs. 500
        "total": round(total + (0 if total >= 500 else 50), 2)
    }