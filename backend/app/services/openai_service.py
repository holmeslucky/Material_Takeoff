"""
Capitol Engineering Company - OpenAI Integration Service
Enhanced proposal generation and takeoff assistance using GPT-4o-mini
"""

import openai
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.core.config import settings

class OpenAIService:
    """Service for OpenAI GPT-4o-mini integration"""
    
    def __init__(self):
        # Initialize OpenAI client with your API key
        openai.api_key = settings.openai_api_key
        self.model = settings.openai_model  # gpt-4o-mini
        self.company_profile = {
            'company_name': settings.company_name,
            'address': settings.company_address,
            'phone': settings.company_phone,
            'mobile': settings.company_mobile,
            'website': settings.company_website,
        }
    
    async def generate_enhanced_proposal(
        self,
        project_data: Dict[str, Any],
        takeoff_entries: List[Dict[str, Any]],
        template_type: str = "professional",
        special_requirements: Optional[str] = None,
        optimization_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate AI-enhanced proposal using GPT-4o-mini
        Optimized for cost efficiency while maintaining quality
        """
        
        # Prepare project summary for AI
        project_summary = self._prepare_project_summary(project_data, takeoff_entries, optimization_data)
        
        # Create AI prompt
        prompt = self._create_proposal_prompt(
            project_summary, template_type, special_requirements, optimization_data
        )
        
        try:
            # Call OpenAI API with gpt-4o-mini for cost efficiency
            response = await self._call_openai_api(
                prompt,
                max_tokens=2000,  # Optimized for cost
                temperature=0.3   # Lower temperature for professional consistency
            )
            
            # Parse and enhance the response
            enhanced_proposal = self._process_ai_response(response, project_data, takeoff_entries)
            
            return {
                'enhanced_proposal': enhanced_proposal,
                'ai_metadata': {
                    'model_used': self.model,
                    'tokens_used': response.get('usage', {}).get('total_tokens', 0),
                    'cost_estimate': self._estimate_cost(response.get('usage', {})),
                    'generated_at': datetime.now().isoformat()
                },
                'project_data': project_data,
                'company_info': self.company_profile
            }
            
        except Exception as e:
            # Fallback to basic proposal if AI fails
            return {
                'enhanced_proposal': self._generate_fallback_proposal(project_data, takeoff_entries),
                'ai_metadata': {
                    'error': str(e),
                    'fallback_used': True,
                    'generated_at': datetime.now().isoformat()
                },
                'project_data': project_data,
                'company_info': self.company_profile
            }
    
    def _prepare_project_summary(self, project_data: Dict, entries: List[Dict], optimization_data: Optional[Dict] = None) -> str:
        """Prepare concise project summary for AI processing"""
        
        total_weight = sum(entry.get('total_weight_tons', 0) for entry in entries)
        original_cost = sum(entry.get('total_price', 0) for entry in entries)
        total_cost = optimization_data.get('total_cost', original_cost) if optimization_data else original_cost
        
        # Categorize materials
        categories = {}
        for entry in entries:
            cat = entry.get('category', 'Other')
            if cat not in categories:
                categories[cat] = {'count': 0, 'weight': 0}
            categories[cat]['count'] += 1
            categories[cat]['weight'] += entry.get('total_weight_tons', 0)
        
        summary = f"""
Project: {project_data.get('name', 'Steel Fabrication')}
Client: {project_data.get('client', 'Client')}
Location: {project_data.get('location', 'TBD')}

Steel Components:
- Total Weight: {total_weight:.2f} tons
- Total Components: {len(entries)}
- Estimated Material Cost: ${total_cost:,.2f}
"""
        
        # Add optimization information if available
        if optimization_data:
            savings = original_cost - total_cost
            waste_pct = optimization_data.get('waste_percentage', 0)
            purchases = optimization_data.get('purchases', 0)
            summary += f"""

Material Optimization Results:
- Original Material Cost: ${original_cost:,.2f}
- Optimized Material Cost: ${total_cost:,.2f}
- Cost Savings: ${savings:,.2f}
- Material Waste: {waste_pct:.1f}%
- Purchase Orders Required: {purchases}
- Optimization ensures minimal waste and accurate drop costs
"""
        
        summary += "\n\nMaterial Breakdown:\n"""
        
        for category, data in categories.items():
            summary += f"- {category}: {data['count']} pieces, {data['weight']:.2f} tons\n"
        
        return summary.strip()
    
    def _create_proposal_prompt(
        self, 
        project_summary: str, 
        template_type: str,
        special_requirements: Optional[str],
        optimization_data: Optional[Dict] = None
    ) -> str:
        """Create AI prompt for proposal generation"""
        
        optimization_note = ""
        if optimization_data:
            optimization_note = f"""

IMPORTANT: This proposal includes AI-powered material optimization that minimizes waste and reduces costs. 
The pricing reflects optimized material purchasing with {optimization_data.get('waste_percentage', 0):.1f}% waste factored in.
All material drops and waste costs are included in the quoted price - no surprises or additional charges.
"""
        
        base_prompt = f"""
You are a professional proposal writer for {self.company_profile['company_name']}, a certified steel fabrication company in Phoenix, Arizona. 

Create a compelling, professional proposal for the following steel fabrication project:

{project_summary}{optimization_note}

Company Information:
- {self.company_profile['company_name']}
- Address: {self.company_profile['address']}
- Phone: {self.company_profile['phone']} • Mobile: {self.company_profile['mobile']}
- Website: {self.company_profile['website']}
- AISC Certified Fabricator
- AWS Certified Welding Facility

Requirements:
1. Professional tone appropriate for construction industry
2. Highlight Capitol Engineering's expertise and certifications
3. Include value proposition and competitive advantages
4. Address project timeline and delivery
5. Include professional terms and conditions
6. Emphasize quality, safety, and compliance
"""

        if template_type == "executive":
            base_prompt += """
Format as an executive summary proposal focusing on:
- High-level project overview
- Key benefits and value
- Timeline and investment
- Next steps
Keep it concise but compelling (800-1000 words).
"""
        elif template_type == "technical":
            base_prompt += """
Format as a technical proposal focusing on:
- Detailed scope of work
- Technical specifications and standards
- Quality control procedures
- Safety protocols
- Material certifications
Include technical details appropriate for engineers (1000-1200 words).
"""
        else:  # professional (default)
            base_prompt += """
Format as a comprehensive professional proposal including:
- Project overview and scope
- Company qualifications
- Timeline and deliverables
- Investment and terms
- Next steps
Balance technical detail with business focus (900-1100 words).
"""
        
        if special_requirements:
            base_prompt += f"""

Special Project Requirements:
{special_requirements}

Please address these specific requirements in the proposal.
"""
        
        base_prompt += """

Important: 
- Use professional construction industry language
- Include specific mention of AISC and AWS certifications
- Emphasize Capitol Engineering's Phoenix location advantage
- End with clear next steps and contact information
- Keep the tone confident but not overselling
"""
        
        return base_prompt
    
    async def _call_openai_api(
        self, 
        prompt: str, 
        max_tokens: int = 2000,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """Call OpenAI API with optimized settings for gpt-4o-mini"""
        
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional proposal writer for {self.company_profile['company_name']}, a certified steel fabrication company. Write compelling, accurate proposals that win business."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            return {
                'content': response.choices[0].message.content,
                'usage': response.usage
            }
            
        except Exception as e:
            raise Exception(f"OpenAI API call failed: {str(e)}")
    
    def _process_ai_response(
        self, 
        response: Dict[str, Any], 
        project_data: Dict,
        takeoff_entries: List[Dict]
    ) -> str:
        """Process and enhance AI response"""
        
        ai_content = response.get('content', '')
        
        # Add project-specific details that AI might miss
        enhanced_content = ai_content
        
        # Ensure proper company branding
        if self.company_profile['company_name'] not in enhanced_content:
            enhanced_content = enhanced_content.replace(
                "Capitol Engineering Company", 
                self.company_profile['company_name']
            )
        
        # Add generation timestamp
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        enhanced_content += f"\n\n---\nProposal generated on {timestamp} using AI-enhanced technology.\n"
        enhanced_content += f"Capitol Engineering Company - Professional Steel Fabrication"
        
        return enhanced_content
    
    def _generate_fallback_proposal(
        self, 
        project_data: Dict,
        takeoff_entries: List[Dict]
    ) -> str:
        """Generate basic proposal if AI fails"""
        
        total_weight = sum(entry.get('total_weight_tons', 0) for entry in entries)
        total_cost = sum(entry.get('total_price', 0) for entry in entries)
        
        return f"""
STEEL FABRICATION PROPOSAL

{self.company_profile['company_name']}
{self.company_profile['address']}
Phone: {self.company_profile['phone']} • Mobile: {self.company_profile['mobile']}

PROJECT: {project_data.get('name', 'Steel Fabrication Project')}
CLIENT: {project_data.get('client', 'Valued Client')}
DATE: {datetime.now().strftime("%B %d, %Y")}

We are pleased to provide this proposal for steel fabrication services.

PROJECT SUMMARY:
- Total Steel Weight: {total_weight:.2f} tons
- Number of Components: {len(takeoff_entries)}
- Estimated Investment: ${total_cost:,.2f}

Capitol Engineering Company is an AISC Certified Fabricator with over 20 years of experience serving the Phoenix metropolitan area. We provide quality steel fabrication services with a commitment to safety, precision, and on-time delivery.

Thank you for considering Capitol Engineering Company for your project needs.

Contact: {self.company_profile['phone']}
Website: {self.company_profile['website']}
"""
    
    def _estimate_cost(self, usage: Dict[str, Any]) -> float:
        """Estimate API cost based on token usage for gpt-4o-mini"""
        
        # gpt-4o-mini pricing (approximate)
        input_tokens = usage.get('prompt_tokens', 0)
        output_tokens = usage.get('completion_tokens', 0)
        
        # Pricing per 1K tokens (estimated for gpt-4o-mini)
        input_cost_per_1k = 0.00015  # $0.15 per 1K tokens
        output_cost_per_1k = 0.0006  # $0.60 per 1K tokens
        
        input_cost = (input_tokens / 1000) * input_cost_per_1k
        output_cost = (output_tokens / 1000) * output_cost_per_1k
        
        return round(input_cost + output_cost, 6)
    
    async def suggest_materials(self, project_description: str, limit: int = 5) -> List[str]:
        """AI-powered material suggestions based on project description"""
        
        prompt = f"""
Based on this steel fabrication project description, suggest the most appropriate steel shapes and materials:

Project: {project_description}

Provide 3-5 specific steel shape recommendations (like W12X26, PL1/2X12, L6X4X1/2, etc.) that would commonly be used for this type of project. 

Format as a simple list of shape keys, one per line.
Focus on the most common and practical choices for a steel fabrication shop.
"""
        
        try:
            response = await self._call_openai_api(
                prompt,
                max_tokens=200,  # Keep it short for cost efficiency
                temperature=0.2   # Lower temperature for consistent suggestions
            )
            
            # Parse suggestions
            suggestions = response.get('content', '').strip().split('\n')
            suggestions = [s.strip() for s in suggestions if s.strip()]
            
            return suggestions[:limit]
            
        except:
            # Fallback suggestions
            return ['W12X26', 'PL1/2X12', 'L4X4X1/2', 'HSS6X6X1/4', 'C12X20.7']
    
    async def optimize_takeoff(self, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """AI-powered takeoff optimization suggestions"""
        
        # Prepare entry summary
        entry_summary = []
        for entry in entries[:10]:  # Limit for cost efficiency
            entry_summary.append(
                f"{entry.get('qty')} x {entry.get('shape_key')} @ {entry.get('length_ft')}ft"
            )
        
        prompt = f"""
Review this steel takeoff for potential optimizations:

{chr(10).join(entry_summary)}

Provide 2-3 brief suggestions for:
1. Material consolidation opportunities
2. Length optimization
3. Fabrication efficiency improvements

Keep suggestions practical and specific to steel fabrication.
Format as numbered list, max 300 words.
"""
        
        try:
            response = await self._call_openai_api(
                prompt,
                max_tokens=400,
                temperature=0.3
            )
            
            return {
                'suggestions': response.get('content', ''),
                'tokens_used': response.get('usage', {}).get('total_tokens', 0),
                'cost_estimate': self._estimate_cost(response.get('usage', {}))
            }
            
        except Exception as e:
            return {
                'suggestions': 'AI optimization temporarily unavailable. Review takeoff manually for consolidation opportunities.',
                'error': str(e)
            }
    
    def get_usage_stats(self) -> Dict[str, str]:
        """Get OpenAI service information"""
        return {
            'model': self.model,
            'api_configured': bool(settings.openai_api_key),
            'company': self.company_profile['company_name'],
            'features': [
                'Enhanced Proposal Generation',
                'Smart Material Suggestions', 
                'Takeoff Optimization',
                'Professional AI Writing'
            ]
        }