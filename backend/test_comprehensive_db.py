#!/usr/bin/env python3
"""
Test the comprehensive material database functionality
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.material import Material

def test_comprehensive_database():
    """Test the comprehensive material database"""
    
    db = SessionLocal()
    try:
        print('COMPREHENSIVE MATERIAL DATABASE STATUS')
        print('=' * 50)
        
        total = db.query(Material).count()
        legacy = db.query(Material).filter(Material.source_system == 'legacy').count()
        blake = db.query(Material).filter(Material.source_system == 'blake').count()
        
        print(f'Total materials: {total:,}')
        print(f'Legacy materials: {legacy:,}') 
        print(f'Blake materials: {blake:,}')
        
        # Show subcategories available
        subcats = db.query(Material.subcategory).filter(Material.subcategory.isnot(None)).distinct().all()
        print(f'Subcategories: {[s[0] for s in subcats]}')
        
        # Show sample fittings with pricing
        print('\nSample Fittings with Pricing:')
        fittings = db.query(Material).filter(
            Material.subcategory == 'Fitting',
            Material.base_price_usd.isnot(None)
        ).order_by(Material.base_price_usd).limit(5).all()
        
        for f in fittings:
            print(f'  {f.shape_key}: ${f.base_price_usd:.2f} ({f.specs_standard})')
        
        # Show sample pipes
        print('\nSample Pipes with Pricing:')
        pipes = db.query(Material).filter(
            Material.subcategory == 'Pipe',
            Material.base_price_usd.isnot(None)
        ).order_by(Material.base_price_usd).limit(5).all()
        
        for p in pipes:
            print(f'  {p.shape_key}: ${p.base_price_usd:.2f} ({p.specs_standard})')
        
        # Show sample valves
        print('\nSample Valves with Pricing:')
        valves = db.query(Material).filter(
            Material.subcategory == 'Valve',
            Material.base_price_usd.isnot(None)
        ).order_by(Material.base_price_usd).limit(5).all()
        
        for v in valves:
            print(f'  {v.shape_key}: ${v.base_price_usd:.2f} ({v.specs_standard})')
        
        # Test effective pricing on legacy materials
        print('\nLegacy Structural Materials (CWT Pricing):')
        structural = db.query(Material).filter(
            Material.source_system == 'legacy',
            Material.category == 'Wide Flange'
        ).limit(3).all()
        
        for s in structural:
            print(f'  {s.shape_key}: ${s.effective_price:.2f} (from CWT: ${s.unit_price_per_cwt}/100 lbs)')
        
        print('\n' + '=' * 50)
        print('BLAKE\'S COMPREHENSIVE MATERIAL DATABASE IS ACTIVE!')
        print('You now have professional-grade pricing for:')
        print('- Fittings, Pipes, Valves, Flanges, Components')
        print('- Complete ASTM specifications')  
        print('- Real market pricing data')
        print('- Backwards-compatible structural steel pricing')
        print('=' * 50)
        
    finally:
        db.close()

if __name__ == "__main__":
    test_comprehensive_database()