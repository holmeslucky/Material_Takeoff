"""
Capitol Engineering Company - Proposal Generation Service
Professional proposal generation with company branding and templates
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from app.core.config import settings

class ProposalService:
    """Service for generating professional takeoff proposals"""
    
    def __init__(self):
        self.company_profile = {
            'company_name': settings.company_name,
            'address': settings.company_address,
            'phone': settings.company_phone,
            'mobile': settings.company_mobile,
            'website': settings.company_website,
        }
    
    def generate_proposal(
        self,
        project_data: Dict[str, Any],
        entries: List[Dict[str, Any]],
        template_type: str = "standard",
        markup_percentage: float = 15.0,
        include_labor: bool = True,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a professional proposal from takeoff data
        
        Args:
            project_data: Project information
            entries: List of takeoff entries
            template_type: Type of proposal template
            markup_percentage: Markup percentage for pricing
            include_labor: Whether to include labor costs
            notes: Additional project notes
        """
        
        # Calculate totals
        totals = self._calculate_proposal_totals(entries, include_labor)
        
        # Apply markup
        material_with_markup = totals['material_cost'] * (1 + markup_percentage / 100)
        labor_with_markup = totals['labor_cost'] * (1 + markup_percentage / 100) if include_labor else 0
        total_with_markup = material_with_markup + labor_with_markup
        
        # Generate proposal content based on template
        if template_type == "detailed":
            content = self._generate_detailed_proposal(
                project_data, entries, totals, markup_percentage, include_labor, notes
            )
        elif template_type == "summary":
            content = self._generate_summary_proposal(
                project_data, totals, markup_percentage, include_labor, notes
            )
        else:  # standard
            content = self._generate_standard_proposal(
                project_data, entries, totals, markup_percentage, include_labor, notes
            )
        
        return {
            'proposal_content': content,
            'project_info': project_data,
            'totals': {
                'material_cost': totals['material_cost'],
                'labor_cost': totals['labor_cost'],
                'markup_percentage': markup_percentage,
                'material_with_markup': material_with_markup,
                'labor_with_markup': labor_with_markup,
                'total_cost': total_with_markup,
                'total_weight_tons': totals['total_weight_tons'],
                'total_entries': totals['total_entries']
            },
            'generated_at': datetime.now().isoformat(),
            'template_type': template_type,
            'company_info': self.company_profile
        }
    
    def _calculate_proposal_totals(self, entries: List[Dict[str, Any]], include_labor: bool) -> Dict[str, float]:
        """Calculate totals for proposal"""
        
        material_cost = sum(entry.get('total_price', 0) for entry in entries)
        labor_cost = sum(entry.get('labor_cost', 0) for entry in entries) if include_labor else 0
        total_weight_tons = sum(entry.get('total_weight_tons', 0) for entry in entries)
        total_entries = len(entries)
        
        # Category breakdown
        category_breakdown = {}
        for entry in entries:
            category = entry.get('category', 'Other')
            if category not in category_breakdown:
                category_breakdown[category] = {
                    'count': 0,
                    'weight_tons': 0,
                    'cost': 0
                }
            category_breakdown[category]['count'] += 1
            category_breakdown[category]['weight_tons'] += entry.get('total_weight_tons', 0)
            category_breakdown[category]['cost'] += entry.get('total_price', 0)
        
        return {
            'material_cost': material_cost,
            'labor_cost': labor_cost,
            'total_weight_tons': total_weight_tons,
            'total_entries': total_entries,
            'category_breakdown': category_breakdown
        }
    
    def _generate_standard_proposal(
        self,
        project_data: Dict[str, Any],
        entries: List[Dict[str, Any]],
        totals: Dict[str, Any],
        markup_percentage: float,
        include_labor: bool,
        notes: Optional[str]
    ) -> str:
        """Generate standard proposal template"""
        
        proposal_date = datetime.now().strftime("%B %d, %Y")
        
        content = f"""
STEEL FABRICATION PROPOSAL

{self.company_profile['company_name']}
{self.company_profile['address']}
Phone: {self.company_profile['phone']} • Mobile: {self.company_profile['mobile']}
Website: {self.company_profile['website']}

═══════════════════════════════════════════════════════════════

DATE: {proposal_date}
PROJECT: {project_data.get('name', 'Steel Fabrication Project')}
CLIENT: {project_data.get('client', 'Valued Client')}
LOCATION: {project_data.get('location', 'TBD')}
PROJECT ID: {project_data.get('id', 'TBD')}

═══════════════════════════════════════════════════════════════

PROJECT OVERVIEW

We are pleased to provide this proposal for steel fabrication services for the 
{project_data.get('name', 'above-referenced project')}. This proposal includes 
all materials, fabrication, and {('labor costs' if include_labor else 'material costs only')} 
based on the specifications provided.

═══════════════════════════════════════════════════════════════

SCOPE OF WORK

Total Steel Weight: {totals['total_weight_tons']:.2f} tons
Number of Components: {totals['total_entries']} items

Material Categories:
"""
        
        # Add category breakdown
        for category, data in totals['category_breakdown'].items():
            content += f"• {category}: {data['count']} items, {data['weight_tons']:.2f} tons\n"
        
        content += f"""
═══════════════════════════════════════════════════════════════

PRICING SUMMARY

Material Cost:           ${totals['material_cost']:,.2f}"""
        
        if include_labor:
            content += f"""
Labor Cost:              ${totals['labor_cost']:,.2f}
Subtotal:                ${totals['material_cost'] + totals['labor_cost']:,.2f}"""
        else:
            content += f"""
Subtotal:                ${totals['material_cost']:,.2f}"""
        
        markup_amount = totals['material_cost'] * (markup_percentage / 100)
        if include_labor:
            markup_amount += totals['labor_cost'] * (markup_percentage / 100)
        
        total_amount = totals['material_cost'] + totals['labor_cost'] + markup_amount
        
        content += f"""
Markup ({markup_percentage}%):          ${markup_amount:,.2f}

TOTAL PROJECT COST:      ${total_amount:,.2f}

═══════════════════════════════════════════════════════════════

TERMS AND CONDITIONS

• Pricing valid for 30 days from proposal date
• Steel prices subject to mill price fluctuations
• Fabrication timeline: 2-3 weeks after material delivery
• Payment terms: Net 30 days
• Capitol Engineering Company warranty applies

═══════════════════════════════════════════════════════════════

COMPANY CERTIFICATIONS

• AISC Certified Fabricator
• AWS Certified Welding Facility
• Quality Management System ISO 9001
• All work performed to AISC Code of Standard Practice

"""
        
        if notes:
            content += f"""
═══════════════════════════════════════════════════════════════

ADDITIONAL NOTES

{notes}

"""
        
        content += f"""
═══════════════════════════════════════════════════════════════

We appreciate the opportunity to provide this proposal. Please contact us with 
any questions or to discuss project requirements.

Sincerely,

{self.company_profile['company_name']}
Phone: {self.company_profile['phone']}
Mobile: {self.company_profile['mobile']}

This proposal generated on {proposal_date}
"""
        
        return content.strip()
    
    def _generate_detailed_proposal(
        self,
        project_data: Dict[str, Any],
        entries: List[Dict[str, Any]],
        totals: Dict[str, Any],
        markup_percentage: float,
        include_labor: bool,
        notes: Optional[str]
    ) -> str:
        """Generate detailed proposal with item breakdown"""
        
        # Start with standard proposal
        content = self._generate_standard_proposal(
            project_data, entries, totals, markup_percentage, include_labor, notes
        )
        
        # Add detailed breakdown section
        breakdown = f"""

═══════════════════════════════════════════════════════════════

DETAILED MATERIAL BREAKDOWN

{'Qty':<6} {'Shape':<12} {'Description':<25} {'Length':<8} {'Weight':<10} {'Price':<12}
{'─'*6} {'─'*12} {'─'*25} {'─'*8} {'─'*10} {'─'*12}
"""
        
        for entry in entries[:20]:  # Limit to first 20 entries for readability
            breakdown += f"{entry.get('qty', 0):<6} "
            breakdown += f"{entry.get('shape_key', ''):<12} "
            breakdown += f"{entry.get('description', '')[:25]:<25} "
            breakdown += f"{entry.get('length_ft', 0):>7.1f} "
            breakdown += f"{entry.get('total_weight_tons', 0):>9.2f} "
            breakdown += f"${entry.get('total_price', 0):>10.2f}\n"
        
        if len(entries) > 20:
            breakdown += f"\n... and {len(entries) - 20} additional items\n"
        
        # Insert breakdown before terms and conditions
        terms_index = content.find("TERMS AND CONDITIONS")
        if terms_index != -1:
            content = content[:terms_index] + breakdown + "\n" + content[terms_index:]
        
        return content
    
    def _generate_summary_proposal(
        self,
        project_data: Dict[str, Any],
        totals: Dict[str, Any],
        markup_percentage: float,
        include_labor: bool,
        notes: Optional[str]
    ) -> str:
        """Generate summary proposal (brief version)"""
        
        proposal_date = datetime.now().strftime("%B %d, %Y")
        
        markup_amount = totals['material_cost'] * (markup_percentage / 100)
        if include_labor:
            markup_amount += totals['labor_cost'] * (markup_percentage / 100)
        
        total_amount = totals['material_cost'] + totals['labor_cost'] + markup_amount
        
        content = f"""
STEEL FABRICATION PROPOSAL - SUMMARY

{self.company_profile['company_name']}
{self.company_profile['address']}
Phone: {self.company_profile['phone']} • Mobile: {self.company_profile['mobile']}

═══════════════════════════════════════════════════════════════

DATE: {proposal_date}
PROJECT: {project_data.get('name', 'Steel Fabrication Project')}
CLIENT: {project_data.get('client', 'Valued Client')}
PROJECT ID: {project_data.get('id', 'TBD')}

═══════════════════════════════════════════════════════════════

PROJECT SUMMARY

Steel Weight: {totals['total_weight_tons']:.2f} tons
Components: {totals['total_entries']} items

TOTAL PROJECT COST: ${total_amount:,.2f}

(Includes materials{', labor,' if include_labor else ','} and {markup_percentage}% markup)

═══════════════════════════════════════════════════════════════

Terms: Net 30 days • Valid 30 days • AISC Certified Fabricator

Contact: {self.company_profile['phone']} for questions

Generated: {proposal_date}
"""
        
        return content.strip()
    
    def export_proposal_pdf(self, proposal_data: Dict[str, Any]) -> bytes:
        """
        Export proposal to PDF format
        (Placeholder for Phase 4 - would use reportlab or similar)
        """
        # This would be implemented in Phase 4 with proper PDF generation
        return proposal_data['proposal_content'].encode('utf-8')
    
    def get_proposal_templates(self) -> List[Dict[str, str]]:
        """Get available proposal templates"""
        return [
            {
                'id': 'standard',
                'name': 'Standard Proposal',
                'description': 'Complete proposal with company branding and terms'
            },
            {
                'id': 'detailed',
                'name': 'Detailed Breakdown',
                'description': 'Standard proposal with itemized material breakdown'
            },
            {
                'id': 'summary',
                'name': 'Summary Quote',
                'description': 'Brief proposal with totals only'
            }
        ]