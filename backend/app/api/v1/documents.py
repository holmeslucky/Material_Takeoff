"""
Document Management API Endpoints
For Senior Project Engineer document control and archival system
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.models.document import Document, DocumentRevision, DocumentComment, DocumentApproval

router = APIRouter()

# Archive schemas
class ArchiveDocumentRequest(BaseModel):
    document_id: int
    reason: str
    archived_by: str
    archive_location: Optional[str] = None

class BulkArchiveRequest(BaseModel):
    document_ids: List[int]
    reason: str
    archived_by: str
    archive_location: Optional[str] = None

@router.get("/")
async def list_documents(
    project_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    document_type: Optional[str] = Query(None),
    include_archived: bool = Query(False),
    limit: int = Query(100),
    skip: int = Query(0),
    db: Session = Depends(get_db)
):
    """List documents with filtering options"""
    
    query = db.query(Document)
    
    # Filter by project
    if project_id:
        query = query.filter(Document.project_id == project_id)
    
    # Filter by status
    if status:
        query = query.filter(Document.status == status)
    
    # Filter by document type
    if document_type:
        query = query.filter(Document.document_type == document_type)
    
    # Archive filter
    if not include_archived:
        query = query.filter(Document.is_archived == False)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    documents = query.offset(skip).limit(limit).all()
    
    return {
        "documents": [
            {
                "id": doc.id,
                "document_number": doc.document_number,
                "title": doc.title,
                "description": doc.description,
                "document_type": doc.document_type,
                "discipline": doc.discipline,
                "category": doc.category,
                "version": doc.version,
                "status": doc.status,
                "is_archived": doc.is_archived,
                "archived_date": doc.archived_date,
                "archived_by": doc.archived_by,
                "created_at": doc.created_at,
                "updated_at": doc.updated_at
            }
            for doc in documents
        ],
        "total": total,
        "limit": limit,
        "skip": skip
    }

@router.post("/archive")
async def archive_document(request: ArchiveDocumentRequest, db: Session = Depends(get_db)):
    """Archive a single document"""
    
    document = db.query(Document).filter(Document.id == request.document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.is_archived:
        raise HTTPException(status_code=400, detail="Document is already archived")
    
    # Update archive fields
    document.is_archived = True
    document.archived_date = func.now()
    document.archived_by = request.archived_by
    document.archive_reason = request.reason
    document.status = "archived"
    
    if request.archive_location:
        document.archive_location = request.archive_location
    
    db.commit()
    db.refresh(document)
    
    return {
        "message": f"Document {document.document_number} archived successfully",
        "document_id": document.id,
        "archived_date": document.archived_date,
        "archived_by": document.archived_by
    }

@router.post("/archive/bulk")
async def bulk_archive_documents(request: BulkArchiveRequest, db: Session = Depends(get_db)):
    """Archive multiple documents at once"""
    
    documents = db.query(Document).filter(
        Document.id.in_(request.document_ids),
        Document.is_archived == False
    ).all()
    
    if not documents:
        raise HTTPException(status_code=404, detail="No unarchived documents found with provided IDs")
    
    archived_count = 0
    archived_docs = []
    
    for document in documents:
        document.is_archived = True
        document.archived_date = func.now()
        document.archived_by = request.archived_by
        document.archive_reason = request.reason
        document.status = "archived"
        
        if request.archive_location:
            document.archive_location = request.archive_location
        
        archived_docs.append({
            "id": document.id,
            "document_number": document.document_number,
            "title": document.title
        })
        archived_count += 1
    
    db.commit()
    
    return {
        "message": f"Successfully archived {archived_count} documents",
        "archived_count": archived_count,
        "archived_documents": archived_docs
    }

@router.post("/unarchive/{document_id}")
async def unarchive_document(
    document_id: int, 
    unarchived_by: str = Query(..., description="User who is unarchiving"),
    db: Session = Depends(get_db)
):
    """Restore a document from archive"""
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not document.is_archived:
        raise HTTPException(status_code=400, detail="Document is not archived")
    
    # Restore from archive
    document.is_archived = False
    document.archived_date = None
    document.archived_by = None
    document.archive_reason = None
    document.archive_location = None
    document.status = "approved"  # Restore to approved status
    document.updated_at = func.now()
    
    db.commit()
    db.refresh(document)
    
    return {
        "message": f"Document {document.document_number} restored from archive",
        "document_id": document.id,
        "unarchived_by": unarchived_by,
        "restored_date": document.updated_at
    }

@router.get("/archive")
async def list_archived_documents(
    project_id: Optional[str] = Query(None),
    archived_by: Optional[str] = Query(None),
    archive_date_start: Optional[str] = Query(None),
    archive_date_end: Optional[str] = Query(None),
    limit: int = Query(100),
    skip: int = Query(0),
    db: Session = Depends(get_db)
):
    """List archived documents with filtering"""
    
    query = db.query(Document).filter(Document.is_archived == True)
    
    # Filter by project
    if project_id:
        query = query.filter(Document.project_id == project_id)
    
    # Filter by who archived
    if archived_by:
        query = query.filter(Document.archived_by == archived_by)
    
    # Filter by archive date range
    if archive_date_start:
        start_date = datetime.fromisoformat(archive_date_start)
        query = query.filter(Document.archived_date >= start_date)
    
    if archive_date_end:
        end_date = datetime.fromisoformat(archive_date_end)
        query = query.filter(Document.archived_date <= end_date)
    
    # Order by archive date (newest first)
    query = query.order_by(Document.archived_date.desc())
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    documents = query.offset(skip).limit(limit).all()
    
    return {
        "archived_documents": [
            {
                "id": doc.id,
                "document_number": doc.document_number,
                "title": doc.title,
                "description": doc.description,
                "document_type": doc.document_type,
                "discipline": doc.discipline,
                "version": doc.version,
                "archived_date": doc.archived_date,
                "archived_by": doc.archived_by,
                "archive_reason": doc.archive_reason,
                "archive_location": doc.archive_location,
                "original_created_date": doc.created_at
            }
            for doc in documents
        ],
        "total": total,
        "limit": limit,
        "skip": skip
    }

@router.get("/archive/stats")
async def get_archive_statistics(
    project_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get archive statistics and summary"""
    
    base_query = db.query(Document)
    if project_id:
        base_query = base_query.filter(Document.project_id == project_id)
    
    # Total documents
    total_documents = base_query.count()
    
    # Archived documents
    archived_documents = base_query.filter(Document.is_archived == True).count()
    
    # Active documents
    active_documents = base_query.filter(Document.is_archived == False).count()
    
    # Documents by type (archived)
    archived_by_type = db.query(
        Document.document_type, 
        func.count(Document.id).label('count')
    ).filter(
        Document.is_archived == True
    ).group_by(Document.document_type).all()
    
    # Recently archived (last 30 days)
    thirty_days_ago = func.date('now', '-30 days')
    recently_archived = base_query.filter(
        Document.is_archived == True,
        Document.archived_date >= thirty_days_ago
    ).count()
    
    # Archive by user
    archived_by_user = db.query(
        Document.archived_by,
        func.count(Document.id).label('count')
    ).filter(
        Document.is_archived == True,
        Document.archived_by.isnot(None)
    ).group_by(Document.archived_by).all()
    
    return {
        "summary": {
            "total_documents": total_documents,
            "archived_documents": archived_documents,
            "active_documents": active_documents,
            "archive_percentage": (archived_documents / total_documents * 100) if total_documents > 0 else 0,
            "recently_archived": recently_archived
        },
        "breakdown": {
            "by_type": [{"type": item[0], "count": item[1]} for item in archived_by_type],
            "by_user": [{"user": item[0], "count": item[1]} for item in archived_by_user]
        }
    }

@router.get("/{document_id}")
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get specific document details including archive status"""
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "id": document.id,
        "project_id": document.project_id,
        "document_number": document.document_number,
        "title": document.title,
        "description": document.description,
        "document_type": document.document_type,
        "discipline": document.discipline,
        "category": document.category,
        "file_name": document.file_name,
        "file_path": document.file_path,
        "file_size": document.file_size,
        "file_format": document.file_format,
        "version": document.version,
        "revision_number": document.revision_number,
        "status": document.status,
        "review_status": document.review_status,
        "is_archived": document.is_archived,
        "archived_date": document.archived_date,
        "archived_by": document.archived_by,
        "archive_reason": document.archive_reason,
        "archive_location": document.archive_location,
        "uploaded_by": document.uploaded_by,
        "reviewed_by": document.reviewed_by,
        "approved_by": document.approved_by,
        "created_at": document.created_at,
        "updated_at": document.updated_at,
        "issued_date": document.issued_date,
        "effective_date": document.effective_date,
        "expiry_date": document.expiry_date
    }