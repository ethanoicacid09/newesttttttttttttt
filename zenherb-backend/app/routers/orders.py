from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
import random
import string
from ..database import get_db
from ..models import User, Product, Order, OrderItem, CartItem
from ..schemas import OrderResponse, OrderListResponse, OrderCreate
from ..auth.auth import get_current_active_user

router = APIRouter(prefix="/orders", tags=["Orders"])

def generate_order_number():
    """Generate unique order number"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"ZH{timestamp}{random_part}"

@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new order"""
    if not order_data.items:
        raise HTTPException(status_code=400, detail="Order must have at least one item")
    
    # Calculate totals
    subtotal = 0
    order_items = []
    
    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        
        if not product.in_stock:
            raise HTTPException(status_code=400, detail=f"{product.name} is out of stock")
        
        item_total = product.price * item.quantity
        subtotal += item_total
        
        order_items.append({
            "product_id": item.product_id,
            "quantity": item.quantity,
            "price": product.price
        })
    
    # Calculate shipping and tax
    shipping = 0 if subtotal >= 500 else 50
    tax = round(subtotal * 0.05, 2)  # 5% tax
    total = subtotal + shipping + tax
    
    # Create order
    order = Order(
        order_number=generate_order_number(),
        user_id=current_user.id,
        subtotal=subtotal,
        shipping_cost=shipping,
        tax=tax,
        total=total,
        shipping_name=order_data.shipping_name,
        shipping_address=order_data.shipping_address,
        shipping_city=order_data.shipping_city,
        shipping_state=order_data.shipping_state,
        shipping_pincode=order_data.shipping_pincode,
        shipping_phone=order_data.shipping_phone,
        notes=order_data.notes,
        payment_method=order_data.payment_method
    )
    db.add(order)
    db.flush()
    
    # Create order items
    for item_data in order_items:
        order_item = OrderItem(
            order_id=order.id,
            **item_data
        )
        db.add(order_item)
        
        # Update stock
        product = db.query(Product).filter(Product.id == item_data["product_id"]).first()
        product.stock_quantity -= item_data["quantity"]
    
    # Clear user's cart
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    
    db.commit()
    db.refresh(order)
    
    return order

@router.get("/", response_model=OrderListResponse)
async def get_user_orders(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 10
):
    """Get current user's orders"""
    query = db.query(Order).filter(Order.user_id == current_user.id)
    
    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()
    
    return {
        "orders": orders,
        "total": total
    }

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get single order by ID"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order

@router.get("/number/{order_number}", response_model=OrderResponse)
async def get_order_by_number(
    order_number: str,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get order by order number"""
    order = db.query(Order).filter(
        Order.order_number == order_number,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order

@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cancel an order"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status not in ["pending", "confirmed"]:
        raise HTTPException(status_code=400, detail="Order cannot be cancelled at this stage")
    
    # Restore stock
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        product.stock_quantity += item.quantity
    
    order.status = "cancelled"
    db.commit()
    
    return {"message": "Order cancelled successfully", "order": order}

@router.get("/stats/summary")
async def get_order_stats(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get order statistics for current user"""
    total_orders = db.query(func.count(Order.id)).filter(
        Order.user_id == current_user.id
    ).scalar() or 0
    
    total_spent = db.query(func.sum(Order.total)).filter(
        Order.user_id == current_user.id,
        Order.status != "cancelled"
    ).scalar() or 0
    
    pending_orders = db.query(func.count(Order.id)).filter(
        Order.user_id == current_user.id,
        Order.status.in_(["pending", "confirmed", "processing"])
    ).scalar() or 0
    
    delivered_orders = db.query(func.count(Order.id)).filter(
        Order.user_id == current_user.id,
        Order.status == "delivered"
    ).scalar() or 0
    
    return {
        "total_orders": total_orders,
        "total_spent": round(total_spent, 2),
        "pending_orders": pending_orders,
        "delivered_orders": delivered_orders
    }