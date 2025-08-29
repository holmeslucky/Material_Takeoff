"""
Capitol Engineering Company - PDF Generation Service
Professional proposal PDF generation using ReportLab
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import io
from typing import Dict, Any, List

class PDFService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles for Capitol Engineering branding"""
        
        # Company Header Style
        self.styles.add(ParagraphStyle(
            name='CompanyHeader',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f2937'),  # Dark gray
            alignment=TA_CENTER,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        # Company Info Style
        self.styles.add(ParagraphStyle(
            name='CompanyInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#6b7280'),  # Medium gray
            alignment=TA_CENTER,
            spaceAfter=20
        ))
        
        # Section Header Style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1f2937'),
            spaceBefore=16,
            spaceAfter=8,
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#e5e7eb'),
            borderPadding=8,
            backColor=colors.HexColor('#f9fafb')
        ))
        
        # Project Info Style
        self.styles.add(ParagraphStyle(
            name='ProjectInfo',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceBefore=4,
            spaceAfter=4
        ))
        
        # Cost Summary Style
        self.styles.add(ParagraphStyle(
            name='CostSummary',
            parent=self.styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            alignment=TA_RIGHT,
            spaceBefore=8
        ))

    def generate_proposal_pdf(self, proposal_data: Dict[str, Any]) -> bytes:
        """Generate a professional proposal PDF"""
        
        # Create PDF buffer
        buffer = io.BytesIO()
        
        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build content
        story = []
        
        # Header
        self._add_header(story)
        
        # Project Information
        self._add_project_info(story, proposal_data.get('project_info', {}))
        
        # Executive Summary  
        self._add_executive_summary(story, proposal_data.get('totals', {}))
        
        # Detailed Cost Breakdown
        self._add_proposal_details(story, proposal_data.get('totals', {}))
        
        # Project Scope & Inclusions
        self._add_project_scope(story)
        
        # Exclusions
        self._add_exclusions(story)
        
        # Terms and Conditions
        self._add_terms_and_conditions(story)
        
        # Footer
        self._add_footer(story)
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        buffer.seek(0)
        return buffer.getvalue()

    def _add_header(self, story: List):
        """Add company header matching Capitol Engineering format"""
        # Header with CE logo area and quote info (simulated)
        header_data = [
            ['CE\nCAPITOL ENGINEERING CO.', 'Quote Number: XXXX\nProject Name\nProject Details']
        ]
        
        header_table = Table(header_data, colWidths=[2*inch, 4*inch])
        header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 16),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica'),
            ('FONTSIZE', (1, 0), (1, 0), 10),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 20))
        
        # Main title
        story.append(Paragraph("STEEL FABRICATION DETAILED PROPOSAL", self.styles['CompanyHeader']))
        story.append(Spacer(1, 12))
        
        # Company contact info
        company_info = """
        <b>Capitol Engineering Company</b><br/>
        724 E Southern Pacific Dr, Phoenix AZ 85034<br/>
        <br/>
        Thank you,<br/>
        <b>Blake Holmes</b><br/>
        Project Manager<br/>
        Direct- 602-281-6517<br/>
        Mobile- 951-732-1514<br/>
        Blake@capitolAZ.com<br/>
        www.capitolaz.com
        """
        story.append(Paragraph(company_info, self.styles['CompanyInfo']))
        story.append(Spacer(1, 30))

    def _add_project_info(self, story: List, project_info: Dict[str, Any]):
        """Add project information section"""
        story.append(Paragraph("PROJECT INFORMATION", self.styles['SectionHeader']))
        
        date_str = datetime.now().strftime("%B %d, %Y")
        project_name = project_info.get('name', 'Untitled Project')
        client_name = project_info.get('client_name', 'Valued Client')
        project_location = project_info.get('project_location', 'TBD')
        project_id = project_info.get('id', 'N/A')
        
        project_data = [
            ['Date:', date_str],
            ['Project:', project_name],
            ['Client:', client_name],
            ['Location:', project_location],
            ['Project ID:', project_id]
        ]
        
        project_table = Table(project_data, colWidths=[1.5*inch, 4*inch])
        project_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        story.append(project_table)
        story.append(Spacer(1, 20))

    def _add_executive_summary(self, story: List, totals: Dict[str, Any]):
        """Add executive summary section"""
        story.append(Paragraph("EXECUTIVE SUMMARY", self.styles['SectionHeader']))
        
        total_cost = totals.get('total_cost', 0)
        total_weight = totals.get('total_weight_tons', 0)
        
        summary_text = f"""
        <b>Project Overview:</b><br/>
        Capitol Engineering Company is pleased to present this detailed proposal for steel fabrication services. 
        Our comprehensive approach includes material optimization, professional fabrication, and quality coatings to 
        ensure your project meets the highest industry standards.<br/><br/>
        
        <b>Total Investment:</b> ${total_cost:,.2f}<br/>
        <b>Total Steel Weight:</b> {total_weight:.1f} tons<br/><br/>
        
        This proposal represents our commitment to delivering exceptional value through optimized material utilization, 
        skilled craftsmanship, and adherence to all applicable codes and standards.
        """
        
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 20))

    def _add_project_scope(self, story: List):
        """Add project scope and inclusions section"""
        story.append(Paragraph("PROJECT SCOPE & INCLUSIONS", self.styles['SectionHeader']))
        
        scope_text = """
        <b>Fabrication Services Include:</b><br/>
        • Material procurement per engineering drawings and specifications<br/>
        • Professional cutting, drilling, and machining to AISC standards<br/>
        • MIG and stick welding by certified welders per AWS D1.1<br/>
        • Quality control inspection and documentation<br/>
        • Surface preparation and coating application as specified<br/>
        • Delivery coordination and material handling<br/><br/>
        
        <b>Engineering & Design:</b><br/>
        • Shop drawing review and approval process<br/>
        • Material optimization and nesting for cost efficiency<br/>
        • Compliance with all applicable building codes<br/>
        • Structural steel detailing coordination<br/><br/>
        
        <b>Quality Assurance:</b><br/>
        • AWS certified welding procedures<br/>
        • Material traceability and mill test reports<br/>
        • Dimensional inspection and fit-up verification<br/>
        • Final quality inspection before shipment
        """
        
        story.append(Paragraph(scope_text, self.styles['Normal']))
        story.append(Spacer(1, 20))

    def _add_exclusions(self, story: List):
        """Add exclusions section"""
        story.append(Paragraph("EXCLUSIONS", self.styles['SectionHeader']))
        
        exclusions_text = """
        <b>The following items are specifically excluded from this proposal:</b><br/><br/>
        
        • Site work, excavation, and concrete foundations<br/>
        • Structural engineering design and stamped drawings<br/>
        • Building permits and regulatory approvals<br/>
        • Site erection and installation services<br/>
        • Crane rental and rigging equipment<br/>
        • Electrical work and connections<br/>
        • Insulation, fireproofing, and non-structural elements<br/>
        • Temporary supports and construction aids<br/>
        • Sales tax (if applicable to your organization)<br/>
        • Any work not specifically detailed in the project scope<br/><br/>
        
        <b>Additional Services Available Upon Request:</b><br/>
        • Field erection and installation supervision<br/>
        • Structural engineering consultation<br/>
        • Expedited delivery scheduling<br/>
        • Additional coating systems and surface treatments<br/>
        • Custom packaging and shipping arrangements
        """
        
        story.append(Paragraph(exclusions_text, self.styles['Normal']))
        story.append(Spacer(1, 20))

    def _add_proposal_details(self, story: List, totals: Dict[str, Any]):
        """Add proposal cost breakdown"""
        story.append(Paragraph("COST BREAKDOWN", self.styles['SectionHeader']))
        
        material_cost = totals.get('material_with_markup', 0)
        labor_cost = totals.get('labor_cost', 0)
        coating_cost = totals.get('coating_cost', 0)
        total_cost = totals.get('total_cost', 0)
        total_weight = totals.get('total_weight_tons', 0)
        markup_percent = totals.get('markup_percentage', 35)
        
        # Cost breakdown table
        cost_data = [
            ['ITEM', 'AMOUNT'],
            ['Materials (with markup)', f'${material_cost:,.2f}'],
            ['Labor', f'${labor_cost:,.2f}'],
            ['Coatings', f'${coating_cost:,.2f}'],
            ['', ''],  # Spacer row
            ['TOTAL PROJECT COST', f'${total_cost:,.2f}']
        ]
        
        cost_table = Table(cost_data, colWidths=[4*inch, 2*inch])
        cost_table.setStyle(TableStyle([
            # Header row
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 11),
            ('ALIGN', (0, 1), (0, -2), 'LEFT'),
            ('ALIGN', (1, 1), (1, -2), 'RIGHT'),
            
            # Total row
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#dbeafe')),
            ('ALIGN', (0, -1), (0, -1), 'LEFT'),
            ('ALIGN', (1, -1), (1, -1), 'RIGHT'),
            
            # Borders
            ('GRID', (0, 0), (-1, -2), 1, colors.HexColor('#e5e7eb')),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#3b82f6')),
            ('LINEBELOW', (0, -1), (-1, -1), 2, colors.HexColor('#3b82f6')),
            
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(cost_table)
        story.append(Spacer(1, 20))
        
        # Project summary
        if total_weight > 0:
            summary_text = f"""
            <b>Project Summary:</b><br/>
            Total Steel Weight: {total_weight:.1f} tons<br/>
            Markup Applied: {markup_percent}%<br/>
            """
            story.append(Paragraph(summary_text, self.styles['Normal']))
            story.append(Spacer(1, 20))

    def _add_terms_and_conditions(self, story: List):
        """Add terms and conditions"""
        story.append(Paragraph("TERMS AND CONDITIONS", self.styles['SectionHeader']))
        
        terms = """
        • Pricing valid for 30 days from proposal date<br/>
        • Steel prices subject to mill price fluctuations<br/>
        • Fabrication timeline: 2-3 weeks after material delivery<br/>
        • Payment terms: Net 30 days<br/>
        • Capitol Engineering Company warranty applies<br/>
        • All work performed to AISC Code of Standard Practice
        """
        
        story.append(Paragraph(terms, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Company certifications
        story.append(Paragraph("COMPANY CERTIFICATIONS", self.styles['SectionHeader']))
        
        certifications = """
        • AISC Certified Fabricator<br/>
        • AWS Certified Welding Facility<br/>
        • Quality Management System ISO 9001<br/>
        • All work performed to industry standards
        """
        
        story.append(Paragraph(certifications, self.styles['Normal']))
        story.append(Spacer(1, 20))

    def _add_footer(self, story: List):
        """Add footer"""
        footer_text = """
        We appreciate the opportunity to provide this proposal. Please contact us with 
        any questions or to discuss project requirements.<br/><br/>
        
        <b>Sincerely,</b><br/><br/>
        
        <b>Capitol Engineering Company</b><br/>
        Phone: 602-281-6517<br/>
        Mobile: 951-732-1514
        """
        
        story.append(Paragraph(footer_text, self.styles['Normal']))

# Create service instance
pdf_service = PDFService()