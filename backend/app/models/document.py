"""
Document and Drawing Management Models
For Senior Project Engineer document control system
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Document(Base):
    """Main document/drawing table"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(20), ForeignKey("takeoff_projects.id"), nullable=False, index=True)
    document_number = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Document classification
    document_type = Column(String(50), nullable=False)  # drawing, specification, report, procedure, etc.
    discipline = Column(String(50))  # mechanical, electrical, civil, structural, etc.
    category = Column(String(50))  # P&ID, isometric, GA, detail, etc.
    
    # File information
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Float)  # in MB
    file_format = Column(String(20))  # pdf, dwg, dxf, docx, etc.
    
    # Version control
    version = Column(String(20), default="A")
    revision_number = Column(Integer, default=0)
    is_latest = Column(Boolean, default=True)
    superseded_by = Column(Integer, ForeignKey("documents.id"), nullable=True)
    
    # Status and workflow
    status = Column(String(50), default="draft")  # draft, for_review, approved, superseded, obsolete, archived
    review_status = Column(String(50))  # pending, in_review, approved, rejected
    approval_date = Column(DateTime)
    
    # Archive functionality
    is_archived = Column(Boolean, default=False)
    archived_date = Column(DateTime)
    archived_by = Column(String(100))
    archive_reason = Column(String(255))
    archive_location = Column(String(500))  # physical or digital archive location
    
    # People involved
    uploaded_by = Column(String(100), nullable=False)
    reviewed_by = Column(String(100))
    approved_by = Column(String(100))
    engineer_of_record = Column(String(100))
    
    # Dates
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    issued_date = Column(DateTime)
    effective_date = Column(DateTime)
    expiry_date = Column(DateTime)
    
    # Additional metadata
    tags = Column(JSON)  # searchable tags
    document_metadata = Column(JSON)  # flexible storage for custom fields
    
    # Security and access
    access_level = Column(String(50), default="internal")  # public, internal, confidential, restricted
    is_controlled = Column(Boolean, default=False)  # controlled document requiring special handling
    
    # Relationships - using back_populates to avoid circular import issues
    # project = relationship("Project", back_populates="documents")
    revisions = relationship("DocumentRevision", back_populates="document", cascade="all, delete-orphan")
    comments = relationship("DocumentComment", back_populates="document", cascade="all, delete-orphan")
    approvals = relationship("DocumentApproval", back_populates="document", cascade="all, delete-orphan")
    distributions = relationship("DocumentDistribution", back_populates="document", cascade="all, delete-orphan")


class DocumentRevision(Base):
    """Track all document revisions"""
    __tablename__ = "document_revisions"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    revision = Column(String(20), nullable=False)
    revision_number = Column(Integer, nullable=False)
    
    # File information for this revision
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Float)
    
    # Revision details
    change_description = Column(Text, nullable=False)
    reason_for_change = Column(String(255))
    
    # Status
    status = Column(String(50), default="active")
    
    # People and dates
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="revisions")


class DocumentComment(Base):
    """Comments and markups on documents"""
    __tablename__ = "document_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    revision_id = Column(Integer, ForeignKey("document_revisions.id"))
    
    # Comment details
    comment_type = Column(String(50))  # general, technical, markup, redline
    comment_text = Column(Text, nullable=False)
    page_number = Column(Integer)
    coordinates = Column(JSON)  # for markup positioning
    
    # Status
    status = Column(String(50), default="open")  # open, resolved, closed
    priority = Column(String(20), default="normal")  # low, normal, high, critical
    
    # Resolution
    resolution = Column(Text)
    resolved_by = Column(String(100))
    resolved_at = Column(DateTime)
    
    # People and dates
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="comments")
    attachments = relationship("CommentAttachment", back_populates="comment", cascade="all, delete-orphan")


class CommentAttachment(Base):
    """Attachments for document comments"""
    __tablename__ = "comment_attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("document_comments.id"), nullable=False)
    
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))
    file_size = Column(Float)
    
    uploaded_by = Column(String(100), nullable=False)
    uploaded_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    comment = relationship("DocumentComment", back_populates="attachments")


class DocumentApproval(Base):
    """Approval workflow for documents"""
    __tablename__ = "document_approvals"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    revision_id = Column(Integer, ForeignKey("document_revisions.id"))
    
    # Approval details
    approval_level = Column(Integer, nullable=False)  # 1, 2, 3 for multi-level approval
    approval_type = Column(String(50))  # technical, quality, management, client
    
    # Approver information
    approver_name = Column(String(100), nullable=False)
    approver_role = Column(String(100))
    approver_email = Column(String(255))
    
    # Status
    status = Column(String(50), default="pending")  # pending, approved, rejected, on_hold
    
    # Decision details
    decision = Column(String(50))  # approved, rejected, conditional
    comments = Column(Text)
    conditions = Column(Text)  # for conditional approval
    
    # Dates
    requested_at = Column(DateTime, server_default=func.now())
    reviewed_at = Column(DateTime)
    due_date = Column(DateTime)
    
    # Digital signature
    signature_hash = Column(String(255))
    signature_timestamp = Column(DateTime)
    
    # Relationships
    document = relationship("Document", back_populates="approvals")


class DocumentDistribution(Base):
    """Track document distribution"""
    __tablename__ = "document_distributions"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    revision_id = Column(Integer, ForeignKey("document_revisions.id"))
    
    # Distribution details
    distribution_type = Column(String(50))  # email, hardcopy, system, external
    recipient_name = Column(String(100), nullable=False)
    recipient_email = Column(String(255))
    recipient_company = Column(String(255))
    recipient_role = Column(String(100))
    
    # Tracking
    sent_at = Column(DateTime, server_default=func.now())
    sent_by = Column(String(100), nullable=False)
    delivery_method = Column(String(50))
    
    # Acknowledgment
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime)
    acknowledgment_method = Column(String(50))
    
    # Copy control
    copy_number = Column(String(50))  # for controlled copies
    is_controlled_copy = Column(Boolean, default=False)
    
    # Notes
    notes = Column(Text)
    
    # Relationships
    document = relationship("Document", back_populates="distributions")


class DrawingSet(Base):
    """Group related drawings into sets"""
    __tablename__ = "drawing_sets"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(20), ForeignKey("takeoff_projects.id"), nullable=False, index=True)
    
    set_name = Column(String(255), nullable=False)
    set_number = Column(String(100), unique=True, index=True)
    description = Column(Text)
    
    # Set type
    set_type = Column(String(50))  # construction, as-built, tender, approval
    discipline = Column(String(50))
    
    # Status
    status = Column(String(50), default="active")
    issue_date = Column(DateTime)
    
    # Metadata
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    drawings = relationship("DrawingSetItem", back_populates="drawing_set", cascade="all, delete-orphan")


class DrawingSetItem(Base):
    """Link documents to drawing sets"""
    __tablename__ = "drawing_set_items"
    
    id = Column(Integer, primary_key=True, index=True)
    drawing_set_id = Column(Integer, ForeignKey("drawing_sets.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    
    # Order in set
    sequence_number = Column(Integer)
    sheet_number = Column(String(50))
    
    # Include specific revision
    revision_id = Column(Integer, ForeignKey("document_revisions.id"))
    
    # Notes
    notes = Column(Text)
    
    # Relationships
    drawing_set = relationship("DrawingSet", back_populates="drawings")


class TransmittalRecord(Base):
    """Track formal document transmittals"""
    __tablename__ = "transmittal_records"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(20), ForeignKey("takeoff_projects.id"), nullable=False, index=True)
    
    transmittal_number = Column(String(100), unique=True, index=True, nullable=False)
    subject = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Recipients
    to_company = Column(String(255), nullable=False)
    to_attention = Column(String(100))
    to_email = Column(String(255))
    
    cc_list = Column(JSON)  # list of CC recipients
    
    # Sender
    from_company = Column(String(255), nullable=False)
    from_name = Column(String(100), nullable=False)
    from_email = Column(String(255))
    
    # Purpose
    purpose = Column(String(100))  # for_information, for_review, for_approval, for_construction
    response_required = Column(Boolean, default=False)
    response_due_date = Column(DateTime)
    
    # Status
    status = Column(String(50), default="sent")
    sent_date = Column(DateTime, server_default=func.now())
    
    # Metadata
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Documents included
    documents = Column(JSON)  # list of document IDs and revisions