"""
Pydantic schemas for Document Management System
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    DRAWING = "drawing"
    SPECIFICATION = "specification"
    REPORT = "report"
    PROCEDURE = "procedure"
    DATASHEET = "datasheet"
    MANUAL = "manual"
    STANDARD = "standard"
    OTHER = "other"


class DocumentStatus(str, Enum):
    DRAFT = "draft"
    FOR_REVIEW = "for_review"
    APPROVED = "approved"
    SUPERSEDED = "superseded"
    OBSOLETE = "obsolete"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ON_HOLD = "on_hold"


class CommentStatus(str, Enum):
    OPEN = "open"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Priority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


# Base schemas
class DocumentBase(BaseModel):
    project_id: str
    document_number: str
    title: str
    description: Optional[str] = None
    document_type: DocumentType
    discipline: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = []
    document_metadata: Optional[Dict[str, Any]] = {}
    access_level: str = "internal"
    is_controlled: bool = False


class DocumentCreate(DocumentBase):
    file_name: str
    file_path: str
    file_size: Optional[float] = None
    file_format: Optional[str] = None
    uploaded_by: str
    engineer_of_record: Optional[str] = None


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    discipline: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    document_metadata: Optional[Dict[str, Any]] = None
    access_level: Optional[str] = None
    is_controlled: Optional[bool] = None
    engineer_of_record: Optional[str] = None


class DocumentResponse(DocumentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    version: str
    revision_number: int
    is_latest: bool
    status: DocumentStatus
    review_status: Optional[str] = None
    file_name: str
    file_path: str
    file_size: Optional[float] = None
    file_format: Optional[str] = None
    uploaded_by: str
    reviewed_by: Optional[str] = None
    approved_by: Optional[str] = None
    engineer_of_record: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    issued_date: Optional[datetime] = None
    approval_date: Optional[datetime] = None


# Revision schemas
class RevisionCreate(BaseModel):
    document_id: int
    revision: str
    change_description: str
    reason_for_change: Optional[str] = None
    file_name: str
    file_path: str
    file_size: Optional[float] = None
    created_by: str


class RevisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    document_id: int
    revision: str
    revision_number: int
    file_name: str
    file_path: str
    file_size: Optional[float] = None
    change_description: str
    reason_for_change: Optional[str] = None
    status: str
    created_by: str
    created_at: datetime


# Comment schemas
class CommentCreate(BaseModel):
    document_id: int
    revision_id: Optional[int] = None
    comment_type: Optional[str] = None
    comment_text: str
    page_number: Optional[int] = None
    coordinates: Optional[Dict[str, Any]] = None
    priority: Priority = Priority.NORMAL
    created_by: str


class CommentUpdate(BaseModel):
    comment_text: Optional[str] = None
    status: Optional[CommentStatus] = None
    priority: Optional[Priority] = None
    resolution: Optional[str] = None
    resolved_by: Optional[str] = None


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    document_id: int
    revision_id: Optional[int] = None
    comment_type: Optional[str] = None
    comment_text: str
    page_number: Optional[int] = None
    coordinates: Optional[Dict[str, Any]] = None
    status: CommentStatus
    priority: Priority
    resolution: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None


# Approval schemas
class ApprovalCreate(BaseModel):
    document_id: int
    revision_id: Optional[int] = None
    approval_level: int
    approval_type: Optional[str] = None
    approver_name: str
    approver_role: Optional[str] = None
    approver_email: Optional[str] = None
    due_date: Optional[datetime] = None


class ApprovalDecision(BaseModel):
    decision: str  # approved, rejected, conditional
    comments: Optional[str] = None
    conditions: Optional[str] = None
    signature_hash: Optional[str] = None


class ApprovalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    document_id: int
    revision_id: Optional[int] = None
    approval_level: int
    approval_type: Optional[str] = None
    approver_name: str
    approver_role: Optional[str] = None
    approver_email: Optional[str] = None
    status: ApprovalStatus
    decision: Optional[str] = None
    comments: Optional[str] = None
    conditions: Optional[str] = None
    requested_at: datetime
    reviewed_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    signature_hash: Optional[str] = None
    signature_timestamp: Optional[datetime] = None


# Distribution schemas
class DistributionCreate(BaseModel):
    document_id: int
    revision_id: Optional[int] = None
    distribution_type: Optional[str] = None
    recipient_name: str
    recipient_email: Optional[str] = None
    recipient_company: Optional[str] = None
    recipient_role: Optional[str] = None
    delivery_method: Optional[str] = None
    copy_number: Optional[str] = None
    is_controlled_copy: bool = False
    notes: Optional[str] = None
    sent_by: str


class DistributionAcknowledge(BaseModel):
    acknowledgment_method: Optional[str] = None


class DistributionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    document_id: int
    revision_id: Optional[int] = None
    distribution_type: Optional[str] = None
    recipient_name: str
    recipient_email: Optional[str] = None
    recipient_company: Optional[str] = None
    recipient_role: Optional[str] = None
    sent_at: datetime
    sent_by: str
    delivery_method: Optional[str] = None
    acknowledged: bool
    acknowledged_at: Optional[datetime] = None
    acknowledgment_method: Optional[str] = None
    copy_number: Optional[str] = None
    is_controlled_copy: bool
    notes: Optional[str] = None


# Drawing Set schemas
class DrawingSetCreate(BaseModel):
    project_id: str
    set_name: str
    set_number: str
    description: Optional[str] = None
    set_type: Optional[str] = None
    discipline: Optional[str] = None
    created_by: str


class DrawingSetItemCreate(BaseModel):
    document_id: int
    revision_id: Optional[int] = None
    sequence_number: Optional[int] = None
    sheet_number: Optional[str] = None
    notes: Optional[str] = None


class DrawingSetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    project_id: str
    set_name: str
    set_number: str
    description: Optional[str] = None
    set_type: Optional[str] = None
    discipline: Optional[str] = None
    status: str
    issue_date: Optional[datetime] = None
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    drawings: List[Dict[str, Any]] = []


# Transmittal schemas
class TransmittalCreate(BaseModel):
    project_id: str
    transmittal_number: str
    subject: str
    description: Optional[str] = None
    to_company: str
    to_attention: Optional[str] = None
    to_email: Optional[str] = None
    cc_list: Optional[List[Dict[str, str]]] = []
    from_company: str
    from_name: str
    from_email: Optional[str] = None
    purpose: Optional[str] = None
    response_required: bool = False
    response_due_date: Optional[datetime] = None
    documents: List[Dict[str, Any]] = []
    created_by: str


class TransmittalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    project_id: str
    transmittal_number: str
    subject: str
    description: Optional[str] = None
    to_company: str
    to_attention: Optional[str] = None
    to_email: Optional[str] = None
    cc_list: Optional[List[Dict[str, str]]] = []
    from_company: str
    from_name: str
    from_email: Optional[str] = None
    purpose: Optional[str] = None
    response_required: bool
    response_due_date: Optional[datetime] = None
    status: str
    sent_date: datetime
    created_by: str
    created_at: datetime
    documents: List[Dict[str, Any]] = []


# Search and filter schemas
class DocumentSearch(BaseModel):
    project_id: Optional[str] = None
    document_type: Optional[DocumentType] = None
    discipline: Optional[str] = None
    category: Optional[str] = None
    status: Optional[DocumentStatus] = None
    search_text: Optional[str] = None
    tags: Optional[List[str]] = None
    uploaded_by: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    include_superseded: bool = False
    page: int = 1
    page_size: int = 20


# Bulk operations
class BulkDocumentUpdate(BaseModel):
    document_ids: List[int]
    update_data: DocumentUpdate


class BulkApproval(BaseModel):
    approval_ids: List[int]
    decision: ApprovalDecision