from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import Course, CourseEnrollment
from ..schemas import CourseResponse, CourseListResponse, CourseEnrollmentResponse
from ..auth.auth import get_current_active_user

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get("/", response_model=CourseListResponse)
async def get_courses(
    db: Session = Depends(get_db),
    level: Optional[str] = None,
    featured: Optional[bool] = None,
    search: Optional[str] = None
):
    """Get all courses"""
    query = db.query(Course)
    
    if level:
        query = query.filter(Course.level == level)
    
    if featured is not None:
        query = query.filter(Course.is_featured == featured)
    
    if search:
        query = query.filter(
            Course.title.ilike(f"%{search}%") |
            Course.description.ilike(f"%{search}%")
        )
    
    courses = query.order_by(Course.created_at.desc()).all()
    
    return {"courses": courses, "total": len(courses)}

@router.get("/featured", response_model=List[CourseResponse])
async def get_featured_courses(
    db: Session = Depends(get_db),
    limit: int = Query(6, ge=1, le=20)
):
    """Get featured courses"""
    courses = db.query(Course).filter(Course.is_featured == True).limit(limit).all()
    return courses

@router.get("/levels")
async def get_course_levels(db: Session = Depends(get_db)):
    """Get all course levels"""
    levels = db.query(Course.level).distinct().all()
    return [level[0] for level in levels]

@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: int,
    db: Session = Depends(get_db)
):
    """Get single course by ID"""
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return course

@router.get("/slug/{slug}", response_model=CourseResponse)
async def get_course_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """Get single course by slug"""
    course = db.query(Course).filter(Course.slug == slug).first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return course

@router.post("/{course_id}/enroll", response_model=CourseEnrollmentResponse)
async def enroll_in_course(
    course_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Enroll in a course"""
    # Check if course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check if already enrolled
    existing = db.query(CourseEnrollment).filter(
        CourseEnrollment.user_id == current_user.id,
        CourseEnrollment.course_id == course_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already enrolled in this course")
    
    # Create enrollment
    enrollment = CourseEnrollment(
        user_id=current_user.id,
        course_id=course_id
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    
    return enrollment

@router.get("/user/enrollments", response_model=List[CourseEnrollmentResponse])
async def get_user_enrollments(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's course enrollments"""
    enrollments = db.query(CourseEnrollment).filter(
        CourseEnrollment.user_id == current_user.id
    ).all()
    
    return enrollments