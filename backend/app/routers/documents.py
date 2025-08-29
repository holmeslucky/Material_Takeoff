"""
Document Management API Routes
For Senior Project Engineer document control system
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import shutil
from pathlib import Path

from app.core.database import get_db
from app.models.document import (
    Document, DocumentRevision, DocumentComment, 
    DocumentApproval, DocumentDistribution,
    DrawingSet, DrawingSetItem, TransmittalRecord
)
from app.schemas.document import (
    DocumentCreate, DocumentUpdate, DocumentResponse,
    RevisionCreate, RevisionResponse,
    CommentCreate, CommentUpdate, CommentResponse,
    ApprovalCreate, ApprovalDecision, ApprovalResponse,
    DistributionCreate, DistributionAcknowledge, DistributionResponse,
    DrawingSetCreate, DrawingSetItemCreate, DrawingSetResponse,
    TransmittalCreate, TransmittalResponse,
    DocumentSearch, BulkDocumentUpdate, BulkApproval
)

router = APIRouter()

# Configure upload directory
UPLOAD_DIR = Path("uploads/documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# Document endpoints
@router.post("/documents", response_model=DocumentResponse)
async def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db)
):
    """Create a new document"""
    # Check if document number already exists
    existing = db.query(Document).filter(
        Document.document_number == document.document_number
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Document number already exists")
    
    db_document = Document(**document.dict())
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


@router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    project_id: str,
    document_number: str,
    title: str,
    document_type: str,
    uploaded_by: str,
    file: UploadFile = File(...),
    description: Optional[str] = None,
    discipline: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Upload a document file"""
    # Create project directory if it doesn't exist
    project_dir = UPLOAD_DIR / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = Path(file.filename).suffix
    safe_filename = f"{document_number}_{timestamp}{file_extension}"
    file_path = project_dir / safe_filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Get file size in MB
    file_size = os.path.getsize(file_path) / (1024 * 1024)
    
    # Create document record
    db_document = Document(
        project_id=project_id,
        document_number=document_number,
        title=title,
        description=description,
        document_type=document_type,
        discipline=discipline,
        category=category,
        file_name=file.filename,
        file_path=str(file_path),
        file_size=file_size,
        file_format=file_extension[1:] if file_extension else None,
        uploaded_by=uploaded_by
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get a specific document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.get("/documents", response_model=List[DocumentResponse])
def list_documents(
    project_id: Optional[str] = Query(None),
    document_type: Optional[str] = Query(None),
    discipline: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    is_latest: bool = Query(True),
    skip: int = Query(0),
    limit: int = Query(100),
    db: Session = Depends(get_db)
):
    """List documents with optional filters"""
    query = db.query(Document)
    
    if project_id:
        query = query.filter(Document.project_id == project_id)
    if document_type:
        query = query.filter(Document.document_type == document_type)
    if discipline:
        query = query.filter(Document.discipline == discipline)
    if status:
        query = query.filter(Document.status == status)
    if is_latest:
        query = query.filter(Document.is_latest == True)
    
    documents = query.offset(skip).limit(limit).all()
    return documents


@router.put("/documents/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    db: Session = Depends(get_db)
):
    """Update document metadata"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    update_data = document_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(document, field, value)
    
    db.commit()
    db.refresh(document)
    return document


@router.delete("/documents/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file from disk
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    db.delete(document)
    db.commit()
    return {"message": "Document deleted successfully"}


# Revision endpoints
@router.post("/documents/{document_id}/revisions", response_model=RevisionResponse)
async def create_revision(
    document_id: int,
    file: UploadFile = File(...),
    revision: str = Body(...),
    change_description: str = Body(...),
    reason_for_change: Optional[str] = Body(None),
    created_by: str = Body(...),
    db: Session = Depends(get_db)
):
    """Create a new document revision"""
    # Get original document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Save new revision file
    project_dir = UPLOAD_DIR / document.project_id / "revisions"
    project_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = Path(file.filename).suffix
    safe_filename = f"{document.document_number}_rev{revision}_{timestamp}{file_extension}"
    file_path = project_dir / safe_filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    file_size = os.path.getsize(file_path) / (1024 * 1024)
    
    # Create revision record
    new_revision_number = document.revision_number + 1
    db_revision = DocumentRevision(
        document_id=document_id,
        revision=revision,
        revision_number=new_revision_number,
        file_name=file.filename,
        file_path=str(file_path),
        file_size=file_size,
        change_description=change_description,
        reason_for_change=reason_for_change,
        created_by=created_by
    )
    
    # Update document with new revision info
    document.version = revision
    document.revision_number = new_revision_number
    document.file_name = file.filename
    document.file_path = str(file_path)
    document.file_size = file_size
    
    db.add(db_revision)
    db.commit()
    db.refresh(db_revision)
    return db_revision


@router.get("/documents/{document_id}/revisions", response_model=List[RevisionResponse])
def get_document_revisions(document_id: int, db: Session = Depends(get_db)):
    """Get all revisions for a document"""
    revisions = db.query(DocumentRevision).filter(
        DocumentRevision.document_id == document_id
    ).order_by(DocumentRevision.revision_number.desc()).all()
    return revisions


# Comment endpoints
@router.post("/documents/{document_id}/comments", response_model=CommentResponse)
def create_comment(
    document_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db)
):
    """Add a comment to a document"""
    # Verify document exists
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db_comment = DocumentComment(**comment.dict())
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


@router.get("/documents/{document_id}/comments", response_model=List[CommentResponse])
def get_document_comments(
    document_id: int,
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get comments for a document"""
    query = db.query(DocumentComment).filter(
        DocumentComment.document_id == document_id
    )
    
    if status:
        query = query.filter(DocumentComment.status == status)
    
    comments = query.order_by(DocumentComment.created_at.desc()).all()
    return comments


@router.put("/comments/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    db: Session = Depends(get_db)
):
    """Update a comment"""
    comment = db.query(DocumentComment).filter(DocumentComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    update_data = comment_update.dict(exclude_unset=True)
    
    # If resolving, set resolved timestamp
    if update_data.get("status") == "resolved" and not comment.resolved_at:
        comment.resolved_at = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(comment, field, value)
    
    db.commit()
    db.refresh(comment)
    return comment


# Approval endpoints
@router.post("/documents/{document_id}/approvals", response_model=ApprovalResponse)
def create_approval_request(
    document_id: int,
    approval: ApprovalCreate,
    db: Session = Depends(get_db)
):
    """Create an approval request for a document"""
    # Verify document exists
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db_approval = DocumentApproval(**approval.dict())
    db.add(db_approval)
    db.commit()
    db.refresh(db_approval)
    return db_approval


@router.get("/documents/{document_id}/approvals", response_model=List[ApprovalResponse])
def get_document_approvals(
    document_id: int,
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get approval requests for a document"""
    query = db.query(DocumentApproval).filter(
        DocumentApproval.document_id == document_id
    )
    
    if status:
        query = query.filter(DocumentApproval.status == status)
    
    approvals = query.order_by(DocumentApproval.approval_level).all()
    return approvals


@router.put("/approvals/{approval_id}/decision", response_model=ApprovalResponse)
def make_approval_decision(
    approval_id: int,
    decision: ApprovalDecision,
    db: Session = Depends(get_db)
):
    """Make an approval decision"""
    approval = db.query(DocumentApproval).filter(
        DocumentApproval.id == approval_id
    ).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")
    
    # Update approval
    approval.decision = decision.decision
    approval.comments = decision.comments
    approval.conditions = decision.conditions
    approval.signature_hash = decision.signature_hash
    approval.reviewed_at = datetime.utcnow()
    
    if decision.signature_hash:
        approval.signature_timestamp = datetime.utcnow()
    
    # Update status based on decision
    if decision.decision == "approved":
        approval.status = "approved"
        
        # If this is the final approval, update document status
        document = db.query(Document).filter(
            Document.id == approval.document_id
        ).first()
        
        # Check if all required approvals are complete
        pending_approvals = db.query(DocumentApproval).filter(
            DocumentApproval.document_id == approval.document_id,
            DocumentApproval.status == "pending",
            DocumentApproval.id != approval_id
        ).count()
        
        if pending_approvals == 0:
            document.status = "approved"
            document.approval_date = datetime.utcnow()
            document.approved_by = approval.approver_name
    
    elif decision.decision == "rejected":
        approval.status = "rejected"
        
        # Update document status
        document = db.query(Document).filter(
            Document.id == approval.document_id
        ).first()
        document.review_status = "rejected"
    
    db.commit()
    db.refresh(approval)
    return approval


# Distribution endpoints
@router.post("/documents/{document_id}/distribute", response_model=DistributionResponse)
def distribute_document(
    document_id: int,
    distribution: DistributionCreate,
    db: Session = Depends(get_db)
):
    """Create a distribution record for a document"""
    # Verify document exists
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db_distribution = DocumentDistribution(**distribution.dict())
    db.add(db_distribution)
    db.commit()
    db.refresh(db_distribution)
    
    # TODO: Send email notification to recipient
    
    return db_distribution


@router.get("/documents/{document_id}/distributions", response_model=List[DistributionResponse])
def get_document_distributions(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get distribution records for a document"""
    distributions = db.query(DocumentDistribution).filter(
        DocumentDistribution.document_id == document_id
    ).order_by(DocumentDistribution.sent_at.desc()).all()
    return distributions


@router.put("/distributions/{distribution_id}/acknowledge", response_model=DistributionResponse)
def acknowledge_distribution(
    distribution_id: int,
    acknowledgment: DistributionAcknowledge,
    db: Session = Depends(get_db)
):
    """Acknowledge receipt of a distributed document"""
    distribution = db.query(DocumentDistribution).filter(
        DocumentDistribution.id == distribution_id
    ).first()
    if not distribution:
        raise HTTPException(status_code=404, detail="Distribution record not found")
    
    distribution.acknowledged = True
    distribution.acknowledged_at = datetime.utcnow()
    distribution.acknowledgment_method = acknowledgment.acknowledgment_method
    
    db.commit()
    db.refresh(distribution)
    return distribution


# Drawing Set endpoints
@router.post("/drawing-sets", response_model=DrawingSetResponse)
def create_drawing_set(
    drawing_set: DrawingSetCreate,
    db: Session = Depends(get_db)
):
    """Create a new drawing set"""
    # Check if set number already exists
    existing = db.query(DrawingSet).filter(
        DrawingSet.set_number == drawing_set.set_number
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Drawing set number already exists")
    
    db_drawing_set = DrawingSet(**drawing_set.dict())
    db.add(db_drawing_set)
    db.commit()
    db.refresh(db_drawing_set)
    return db_drawing_set


@router.post("/drawing-sets/{set_id}/drawings")
def add_drawing_to_set(
    set_id: int,
    drawing_item: DrawingSetItemCreate,
    db: Session = Depends(get_db)
):
    """Add a drawing to a drawing set"""
    # Verify drawing set exists
    drawing_set = db.query(DrawingSet).filter(DrawingSet.id == set_id).first()
    if not drawing_set:
        raise HTTPException(status_code=404, detail="Drawing set not found")
    
    # Verify document exists
    document = db.query(Document).filter(
        Document.id == drawing_item.document_id
    ).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db_item = DrawingSetItem(
        drawing_set_id=set_id,
        **drawing_item.dict()
    )
    db.add(db_item)
    db.commit()
    
    return {"message": "Drawing added to set successfully"}


@router.get("/drawing-sets/{set_id}", response_model=DrawingSetResponse)
def get_drawing_set(set_id: int, db: Session = Depends(get_db)):
    """Get a drawing set with its drawings"""
    drawing_set = db.query(DrawingSet).filter(DrawingSet.id == set_id).first()
    if not drawing_set:
        raise HTTPException(status_code=404, detail="Drawing set not found")
    
    # Get drawings in the set
    items = db.query(DrawingSetItem).filter(
        DrawingSetItem.drawing_set_id == set_id
    ).order_by(DrawingSetItem.sequence_number).all()
    
    # Format drawings data
    drawings = []
    for item in items:
        document = db.query(Document).filter(Document.id == item.document_id).first()
        if document:
            drawings.append({
                "document_id": document.id,
                "document_number": document.document_number,
                "title": document.title,
                "revision": document.version,
                "sequence_number": item.sequence_number,
                "sheet_number": item.sheet_number,
                "notes": item.notes
            })
    
    drawing_set_dict = drawing_set.__dict__
    drawing_set_dict["drawings"] = drawings
    
    return drawing_set_dict


# Transmittal endpoints
@router.post("/transmittals", response_model=TransmittalResponse)
def create_transmittal(
    transmittal: TransmittalCreate,
    db: Session = Depends(get_db)
):
    """Create a transmittal record"""
    # Check if transmittal number already exists
    existing = db.query(TransmittalRecord).filter(
        TransmittalRecord.transmittal_number == transmittal.transmittal_number
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Transmittal number already exists")
    
    db_transmittal = TransmittalRecord(**transmittal.dict())
    db.add(db_transmittal)
    db.commit()
    db.refresh(db_transmittal)
    
    # TODO: Send transmittal email
    
    return db_transmittal


@router.get("/transmittals/{transmittal_id}", response_model=TransmittalResponse)
def get_transmittal(transmittal_id: int, db: Session = Depends(get_db)):
    """Get a transmittal record"""
    transmittal = db.query(TransmittalRecord).filter(
        TransmittalRecord.id == transmittal_id
    ).first()
    if not transmittal:
        raise HTTPException(status_code=404, detail="Transmittal not found")
    return transmittal


# Search endpoint
@router.post("/documents/search", response_model=List[DocumentResponse])
def search_documents(
    search: DocumentSearch,
    db: Session = Depends(get_db)
):
    """Advanced document search"""
    query = db.query(Document)
    
    if search.project_id:
        query = query.filter(Document.project_id == search.project_id)
    if search.document_type:
        query = query.filter(Document.document_type == search.document_type)
    if search.discipline:
        query = query.filter(Document.discipline == search.discipline)
    if search.category:
        query = query.filter(Document.category == search.category)
    if search.status:
        query = query.filter(Document.status == search.status)
    if search.uploaded_by:
        query = query.filter(Document.uploaded_by == search.uploaded_by)
    
    if search.search_text:
        query = query.filter(
            (Document.title.contains(search.search_text)) |
            (Document.description.contains(search.search_text)) |
            (Document.document_number.contains(search.search_text))
        )
    
    if search.date_from:
        query = query.filter(Document.created_at >= search.date_from)
    if search.date_to:
        query = query.filter(Document.created_at <= search.date_to)
    
    if not search.include_superseded:
        query = query.filter(Document.status != "superseded")
    
    # Pagination
    offset = (search.page - 1) * search.page_size
    documents = query.offset(offset).limit(search.page_size).all()
    
    return documents


# Bulk operations
@router.put("/documents/bulk-update")
def bulk_update_documents(
    bulk_update: BulkDocumentUpdate,
    db: Session = Depends(get_db)
):
    """Update multiple documents at once"""
    documents = db.query(Document).filter(
        Document.id.in_(bulk_update.document_ids)
    ).all()
    
    if len(documents) != len(bulk_update.document_ids):
        raise HTTPException(status_code=404, detail="Some documents not found")
    
    update_data = bulk_update.update_data.dict(exclude_unset=True)
    
    for document in documents:
        for field, value in update_data.items():
            setattr(document, field, value)
    
    db.commit()
    
    return {"message": f"Updated {len(documents)} documents successfully"}


@router.put("/approvals/bulk-approve")
def bulk_approve(
    bulk_approval: BulkApproval,
    db: Session = Depends(get_db)
):
    """Approve multiple documents at once"""
    approvals = db.query(DocumentApproval).filter(
        DocumentApproval.id.in_(bulk_approval.approval_ids)
    ).all()
    
    if len(approvals) != len(bulk_approval.approval_ids):
        raise HTTPException(status_code=404, detail="Some approval requests not found")
    
    decision_data = bulk_approval.decision.dict()
    
    for approval in approvals:
        approval.decision = decision_data["decision"]
        approval.comments = decision_data.get("comments")
        approval.conditions = decision_data.get("conditions")
        approval.signature_hash = decision_data.get("signature_hash")
        approval.reviewed_at = datetime.utcnow()
        
        if decision_data.get("signature_hash"):
            approval.signature_timestamp = datetime.utcnow()
        
        # Update status
        if decision_data["decision"] == "approved":
            approval.status = "approved"
        elif decision_data["decision"] == "rejected":
            approval.status = "rejected"
    
    db.commit()
    
    return {"message": f"Processed {len(approvals)} approval requests successfully"}