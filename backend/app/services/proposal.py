from datetime import datetime
from typing import Dict, List
from app.core.config import settings

def compose_digital_quote(
    company: dict, 
    project: dict, 
    sections: Dict[str, str], 
    include_takeoff: bool = False, 
    takeoff_text: str = ""
) -> str:
    """
    Compose a digital-only quote/bid body matching desktop format
    """
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Header (letterhead-like, simple text)
    header = []
    header.append(company.get('company_name', ''))
    header.append(company.get('address', ''))
    
    # Contact line
    line3 = []
    if company.get('website'): 
        line3.append(company['website'])
    if company.get('email'):   
        line3.append(company['email'])
    if line3: 
        header.append(" • ".join(line3))
    
    header.append("")
    header.append("Proposal / Bid")
    header.append(f"Quote: {project.get('quote_number', '')}    Date: {today}")
    header.append(f"Project: {project.get('name', '')}    Customer: {project.get('customer', '')}")
    header.append("")

    # Sections order mirrors Capitol Engineering house style
    order = [
        ("Executive Summary", 'exec_summary'),
        ("General Notes", 'general_notes'),
        ("Materials", 'materials'),
        ("Welding", 'welding'),
        ("Scope of Work", 'scope'),
        ("Leadtime", 'leadtime'),
        ("Price & Terms", 'price_terms'),
        ("Delivery/Shipping", 'delivery'),
        ("Proposal Clarifications & Exclusions", 'clarifications'),
    ]

    body = []
    for title, key in order:
        body.append(title.upper())
        body.append("-" * len(title))
        body.append(sections.get(key, "").strip())
        body.append("")

    # Optional takeoff (off by default for digital quote)
    if include_takeoff:
        body.append("TAKEOFF SUMMARY")
        body.append("----------------")
        body.append(takeoff_text)

    # Signature footer (keeps 25-2126 vibe)
    sig = []
    sig.append("Thank you,")
    sig.append("")
    sig.append(company.get('contact', ''))
    sig.append("Project Manager")
    if company.get('phone'):  
        sig.append(f"Direct- {company['phone']}")
    if company.get('mobile'): 
        sig.append(f"Mobile- {company['mobile']}")
    if company.get('email'):  
        sig.append(company['email'])
    if company.get('website'):
        sig.append(company['website'])

    # Assemble final document
    parts = []
    parts.append("\n".join(header))
    parts.append("\n".join(body))
    parts.append("\n".join(sig))
    
    return "\n".join(parts).strip() + "\n"

def get_company_profile() -> dict:
    """
    Get company profile from settings
    """
    return {
        'company_name': settings.company_name,
        'address': settings.company_address,
        'phone': settings.company_phone,
        'mobile': settings.company_mobile,
        'contact': settings.company_contact,
        'email': settings.company_email,
        'website': settings.company_website,
        'logo_path': ''  # Optional PNG path
    }

def generate_proposal_sections(
    project_data: dict, 
    takeoff_items: List[dict],
    use_ai: bool = False
) -> Dict[str, str]:
    """
    Generate proposal sections (Phase 5 will add OpenAI enhancement)
    """
    # Default sections for now - Phase 5 will enhance with AI
    sections = {
        'exec_summary': f"""
Capitol Engineering Company is pleased to provide this proposal for {project_data.get('name', 'your project')}.

We specialize in structural steel fabrication and have been serving the Phoenix metropolitan area with quality craftsmanship and competitive pricing.

This proposal includes all materials, labor, and shop fabrication required for the scope outlined below.
        """.strip(),
        
        'general_notes': """
All work to be performed in accordance with applicable building codes and industry standards.
Material will be furnished per plans and specifications.
All structural steel to be AISC certified.
        """.strip(),
        
        'materials': """
All structural steel materials included in takeoff.
Materials sourced from certified suppliers.
Pricing based on current market rates.
        """.strip(),
        
        'welding': """
All welding to be performed per AWS D1.1 Structural Welding Code.
Certified welders on staff.
Visual and non-destructive testing as required.
        """.strip(),
        
        'scope': """
Furnish and fabricate structural steel members per drawings and specifications.
Shop fabrication includes cutting, drilling, welding, and finishing.
Material delivery to jobsite included.
        """.strip(),
        
        'leadtime': """
Standard lead time: 3-4 weeks from approved drawings and PO.
Rush orders available with premium pricing.
Lead times subject to current shop schedule.
        """.strip(),
        
        'price_terms': f"""
Total Project Price: [SEE CALCULATIONS PANEL]

Terms: Net 30 days
Payment required upon delivery
Material price valid for 30 days
        """.strip(),
        
        'delivery': """
Delivery included within 50 miles of shop.
Special delivery requirements quoted separately.
Customer responsible for unloading and storage.
        """.strip(),
        
        'clarifications': """
Pricing is based on information provided.
Field measurements and site conditions assumed normal.
Permits and engineering not included unless specified.
Change orders subject to additional charges.
        """.strip()
    }
    
    # Phase 5 TODO: Add OpenAI enhancement here
    if use_ai and settings.openai_api_key:
        # This will be implemented in Phase 5 with gpt-4o-mini
        pass
    
    return sections

def render_takeoff_table_text(takeoff_items: List[dict]) -> str:
    """
    Render takeoff items as text table for proposals
    """
    if not takeoff_items:
        return "No takeoff items available."
    
    lines = []
    lines.append("TAKEOFF SUMMARY")
    lines.append("=" * 50)
    lines.append(f"{'Material':<15} {'Qty':<8} {'Length':<10} {'Weight':<10} {'Cost':<12}")
    lines.append("-" * 55)
    
    total_weight = 0
    total_cost = 0
    
    for item in takeoff_items:
        material = item.get('material_shape_key', '')[:14]
        qty = item.get('qty', 0)
        length = item.get('length_ft', 0)
        weight = item.get('total_weight', 0)
        cost = item.get('total_cost', 0)
        
        total_weight += weight
        total_cost += cost
        
        lines.append(f"{material:<15} {qty:<8.0f} {length:<10.1f} {weight:<10.0f} ${cost:<11.2f}")
    
    lines.append("-" * 55)
    lines.append(f"{'TOTALS':<15} {'':<8} {'':<10} {total_weight:<10.0f} ${total_cost:<11.2f}")
    
    return "\n".join(lines)