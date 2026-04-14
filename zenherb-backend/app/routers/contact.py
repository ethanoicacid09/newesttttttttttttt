from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import ContactMessage
from ..schemas import ContactMessageCreate, ContactMessageResponse
from ..auth.auth import get_current_active_user

router = APIRouter(prefix="/contact", tags=["Contact"])

@router.post("/", response_model=ContactMessageResponse)
async def submit_contact_message(
    message_data: ContactMessageCreate,
    db: Session = Depends(get_db)
):
    """Submit a contact message"""
    message = ContactMessage(
        name=message_data.name,
        email=message_data.email,
        subject=message_data.subject,
        message=message_data.message
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    
    return message

@router.get("/", response_model=List[ContactMessageResponse])
async def get_messages(
    db: Session = Depends(get_db)
):
    """Get all contact messages (admin only)"""
    messages = db.query(ContactMessage).order_by(
        ContactMessage.created_at.desc()
    ).all()
    
    return messages

@router.get("/unread/count")
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Get count of unread messages"""
    count = db.query(ContactMessage).filter(
        ContactMessage.is_read == False
    ).count()
    
    return {"unread_count": count}

@router.put("/{message_id}/read")
async def mark_message_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Mark a message as read"""
    message = db.query(ContactMessage).filter(
        ContactMessage.id == message_id
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    message.is_read = True
    db.commit()
    
    return {"message": "Message marked as read"}

@router.delete("/{message_id}")
async def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Delete a contact message"""
    message = db.query(ContactMessage).filter(
        ContactMessage.id == message_id
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    db.delete(message)
    db.commit()
    
    return {"message": "Message deleted"}