"""
Capitol Engineering Company - AI-Enhanced Features API
OpenAI GPT-4o-mini integration for proposals and smart suggestions
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.takeoff import TakeoffProject, TakeoffEntry
from app.models.nesting import NestingOptimization, MaterialPurchaseRecommendation
from app.services.openai_service import OpenAIService
from app.services.nesting_service import nesting_service
from app.schemas.takeoff import ProposalGenerationRequest, ProposalGenerationResponse
from pydantic import BaseModel

router = APIRouter()
openai_service = OpenAIService()

class MaterialSuggestionRequest(BaseModel):
    project_description: str
    limit: int = 5

class MaterialSuggestionResponse(BaseModel):
    suggestions: List[str]
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None

class TakeoffOptimizationRequest(BaseModel):
    project_id: str

class TakeoffOptimizationResponse(BaseModel):
    suggestions: str
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None

@router.post("/proposals/generate", response_model=ProposalGenerationResponse)
async def generate_ai_proposal(
    request: ProposalGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate AI-enhanced proposal using GPT-4o-mini
    Optimized for cost efficiency while maintaining professional quality
    """
    
    # Get project data
    project = db.query(TakeoffProject).filter(
        TakeoffProject.id == request.project_id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get takeoff entries
    entries = db.query(TakeoffEntry).filter(
        TakeoffEntry.project_id == request.project_id
    ).all()
    
    if not entries:
        raise HTTPException(status_code=400, detail="Project has no takeoff entries")
    
    # Convert to dict format for AI service
    project_data = {
        'id': project.id,
        'name': project.name,
        'client': project.client,
        'location': project.location,
        'description': project.description,
        'status': project.status
    }
    
    entry_dicts = []
    for entry in entries:
        entry_dict = {
            'qty': entry.qty,
            'shape_key': entry.shape_key,
            'description': entry.description,
            'length_ft': entry.length_ft,
            'total_weight_tons': entry.total_weight_tons,
            'total_price': entry.total_price,
            'category': entry.material.category if entry.material else 'Other'
        }
        entry_dicts.append(entry_dict)
    
    # ALWAYS run material optimization during proposal generation - this is the "2nd heart"!
    optimization_data = None
    optimized_material_cost = None
    waste_percentage = None
    cost_savings = 0.0
    
    try:
        print(f"🔧 Running AI material optimization for {len(entry_dicts)} entries...")
        
        # Run complete material optimization using your actual stock lengths from nest.pdf
        optimization_result = nesting_service.optimize_project_materials(
            takeoff_entries=entry_dicts,
            project_id=request.project_id
        )
        
        # Calculate cost comparison
        original_cost = sum(float(entry.get('total_price', 0)) for entry in entry_dicts)
        optimized_material_cost = float(optimization_result.total_cost)
        cost_savings = max(0, original_cost - optimized_material_cost)
        waste_percentage = optimization_result.total_waste_percentage
        
        optimization_data = {
            'original_cost': original_cost,
            'total_cost': optimized_material_cost,
            'cost_savings': cost_savings,
            'savings_percentage': (cost_savings / original_cost * 100) if original_cost > 0 else 0,
            'waste_percentage': waste_percentage,
            'efficiency_grade': 'A' if waste_percentage <= 10 else
                              'B' if waste_percentage <= 20 else
                              'C' if waste_percentage <= 35 else 'D',
            'summary': optimization_result.optimization_summary,
            'total_purchases': len(optimization_result.material_purchases),
            'material_purchases': [
                {
                    'shape_key': p.shape_key,
                    'size_description': p.size_description,
                    'pieces_needed': p.pieces_needed,
                    'total_cost': float(p.total_cost),
                    'waste_percentage': p.waste_percentage,
                    'waste_cost': float(p.waste_cost),
                    'cuts_count': len(p.cuts_from_this_size)
                }
                for p in optimization_result.material_purchases
            ]
        }
        
        print(f"✅ Material optimization complete:")
        print(f"   - Waste: {waste_percentage:.1f}% (Grade {optimization_data['efficiency_grade']})")
        print(f"   - Savings: ${cost_savings:,.2f} ({optimization_data['savings_percentage']:.1f}%)")
        print(f"   - Purchases: {len(optimization_result.material_purchases)} different sizes")
        
    except Exception as e:
        print(f"❌ Material optimization failed: {e}")
        # Continue with original costs if optimization fails
        original_cost = sum(float(entry.get('total_price', 0)) for entry in entry_dicts)
        optimized_material_cost = original_cost
        optimization_data = None
    
    # Generate AI-enhanced proposal
    try:
        result = await openai_service.generate_enhanced_proposal(
            project_data=project_data,
            takeoff_entries=entry_dicts,
            template_type=request.template_type,
            special_requirements=request.notes,
            optimization_data=optimization_data
        )
        
        # Calculate total amount with markup using optimized costs
        if optimized_material_cost:
            material_cost = optimized_material_cost
        else:
            material_cost = sum(entry['total_price'] for entry in entry_dicts)
            
        if request.include_labor:
            labor_cost = sum(entry.labor_cost or 0 for entry in entries)
            subtotal = material_cost + labor_cost
        else:
            subtotal = material_cost
        
        total_amount = subtotal * (1 + request.markup_percentage / 100)
        
        return ProposalGenerationResponse(
            proposal_id=f"PROP-{project.id}-{int(datetime.now().timestamp())}",
            project_id=request.project_id,
            generated_content=result['enhanced_proposal'],
            total_amount=total_amount,
            created_at=datetime.now(),
            optimization_included=optimization_data is not None,
            optimized_material_cost=optimized_material_cost,
            material_waste_percentage=waste_percentage,
            cost_savings=cost_savings,
            tokens_used=result.get('ai_metadata', {}).get('tokens_used'),
            model_used=result.get('ai_metadata', {}).get('model_used')
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Proposal generation failed: {str(e)}"
        )

@router.post("/materials/suggest", response_model=MaterialSuggestionResponse)
async def suggest_materials(request: MaterialSuggestionRequest):
    """
    Get AI-powered material suggestions based on project description
    Uses GPT-4o-mini for cost-effective suggestions
    """
    
    try:
        suggestions = await openai_service.suggest_materials(
            project_description=request.project_description,
            limit=request.limit
        )
        
        return MaterialSuggestionResponse(
            suggestions=suggestions
        )
        
    except Exception as e:
        # Provide fallback suggestions if AI fails
        fallback_suggestions = [
            'W12X26', 'W14X30', 'PL1/2X12', 'L4X4X1/2', 
            'HSS6X6X1/4', 'C12X20.7', 'PL3/4X8'
        ]
        
        return MaterialSuggestionResponse(
            suggestions=fallback_suggestions[:request.limit]
        )

@router.post("/takeoff/optimize", response_model=TakeoffOptimizationResponse)
async def optimize_takeoff(
    request: TakeoffOptimizationRequest,
    db: Session = Depends(get_db)
):
    """
    Get AI-powered takeoff optimization suggestions
    Analyzes entries for consolidation and efficiency opportunities
    """
    
    # Get takeoff entries
    entries = db.query(TakeoffEntry).filter(
        TakeoffEntry.project_id == request.project_id
    ).all()
    
    if not entries:
        raise HTTPException(status_code=404, detail="No takeoff entries found")
    
    # Convert to dict format
    entry_dicts = []
    for entry in entries:
        entry_dict = {
            'qty': entry.qty,
            'shape_key': entry.shape_key,
            'length_ft': entry.length_ft,
            'total_weight_tons': entry.total_weight_tons,
            'total_price': entry.total_price
        }
        entry_dicts.append(entry_dict)
    
    try:
        result = await openai_service.optimize_takeoff(entry_dicts)
        
        return TakeoffOptimizationResponse(
            suggestions=result['suggestions'],
            tokens_used=result.get('tokens_used'),
            cost_estimate=result.get('cost_estimate')
        )
        
    except Exception as e:
        # Provide basic optimization suggestions if AI fails
        fallback_suggestions = """
        Takeoff Optimization Suggestions:
        
        1. Material Consolidation: Review similar shapes and lengths for potential consolidation opportunities.
        
        2. Length Optimization: Consider standard mill lengths (20', 25', 30', 40') to minimize waste.
        
        3. Fabrication Efficiency: Group similar operations and materials for batch processing.
        """
        
        return TakeoffOptimizationResponse(
            suggestions=fallback_suggestions
        )

@router.get("/status")
async def get_ai_service_status():
    """Get AI service status and capabilities"""
    
    return openai_service.get_usage_stats()

@router.get("/templates")
async def get_proposal_templates():
    """Get available AI proposal templates"""
    
    return [
        {
            'id': 'professional',
            'name': 'Professional Proposal',
            'description': 'Comprehensive business proposal with technical details',
            'ai_enhanced': True
        },
        {
            'id': 'executive',
            'name': 'Executive Summary',
            'description': 'High-level proposal focused on key benefits and investment',
            'ai_enhanced': True
        },
        {
            'id': 'technical',
            'name': 'Technical Proposal',
            'description': 'Detailed technical specifications and procedures',
            'ai_enhanced': True
        }
    ]

@router.post("/chat/takeoff")
async def takeoff_assistant_chat(
    message: str,
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    AI takeoff assistant chat interface
    Provides context-aware help for takeoff tasks
    """
    
    # Get project context
    project = db.query(TakeoffProject).filter(
        TakeoffProject.id == project_id
    ).first()
    
    context_prompt = f"""
You are a helpful takeoff assistant for Capitol Engineering Company, a steel fabrication shop in Phoenix, AZ.

Current Project: {project.name if project else 'Unknown'}
Client: {project.client if project else 'Unknown'}

User Question: {message}

Provide a helpful, concise response focusing on:
- Steel fabrication best practices
- Takeoff accuracy tips
- Material selection guidance
- Capitol Engineering capabilities

Keep responses under 200 words and professional.
"""
    
    try:
        response = await openai_service._call_openai_api(
            context_prompt,
            max_tokens=300,
            temperature=0.4
        )
        
        return {
            'response': response.get('content', 'I apologize, but I cannot process your request at the moment.'),
            'tokens_used': response.get('usage', {}).get('total_tokens', 0)
        }
        
    except Exception as e:
        return {
            'response': 'I apologize, but the AI assistant is temporarily unavailable. Please contact Capitol Engineering directly for assistance.',
            'error': str(e)
        }