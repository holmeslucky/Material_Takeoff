#!/usr/bin/env python3
"""
Capitol Engineering Company - Comprehensive Material Database Population
Adapted from existing comprehensive importer to work with SQLAlchemy models
Target: ~2000+ materials matching GUI standards
"""

from app.core.database import SessionLocal, Base, engine
from app.models.material import Material
from fractions import Fraction

def create_tables():
    """Create database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")

def clear_existing_materials():
    """Clear existing materials"""
    db = SessionLocal()
    try:
        count = db.query(Material).count()
        db.query(Material).delete()
        db.commit()
        print(f"Cleared {count} existing materials")
    finally:
        db.close()

def add_material(db, shape_key, description, category, weight_per_ft, 
                depth_inches=None, width_inches=None, thickness_inches=None,
                unit_price_per_cwt=85.0, commonly_used=True):
    """Add a material to the database"""
    material = Material(
        shape_key=shape_key,
        description=description,
        category=category,
        material_type="Steel",
        grade="A992" if category == "Wide Flange" else "A36",
        weight_per_ft=weight_per_ft,
        depth_inches=depth_inches,
        width_inches=width_inches,
        thickness_inches=thickness_inches,
        unit_price_per_cwt=unit_price_per_cwt,
        supplier="Capitol Steel Supply",
        commonly_used=commonly_used,
        usage_count=0
    )
    db.add(material)
    return material

def populate_comprehensive_wide_flange(db):
    """Populate comprehensive AISC wide flange beams"""
    print("Populating Comprehensive Wide Flange Beams...")
    
    # Complete AISC Wide Flange database
    wf_data = [
        # W4 Series
        ("W4X13", 4.16, 4.060, 0.345, 13.0),
        
        # W5 Series
        ("W5X16", 5.01, 5.000, 0.360, 16.0),
        ("W5X19", 5.15, 5.030, 0.430, 19.0),
        
        # W6 Series
        ("W6X9", 5.90, 3.940, 0.215, 9.0),
        ("W6X12", 6.03, 4.000, 0.280, 12.0),
        ("W6X15", 5.99, 5.990, 0.230, 15.0),
        ("W6X16", 6.28, 4.030, 0.405, 16.0),
        ("W6X20", 6.20, 6.018, 0.367, 20.0),
        ("W6X25", 6.38, 6.080, 0.455, 25.0),
        
        # W8 Series - Complete
        ("W8X10", 7.89, 3.940, 0.170, 10.0),
        ("W8X13", 7.99, 4.000, 0.230, 13.0),
        ("W8X15", 8.11, 4.015, 0.315, 15.0),
        ("W8X18", 8.14, 5.250, 0.230, 18.0),
        ("W8X21", 8.28, 5.270, 0.400, 21.0),
        ("W8X24", 7.93, 6.495, 0.245, 24.0),
        ("W8X28", 8.06, 6.535, 0.285, 28.0),
        ("W8X31", 8.00, 7.995, 0.285, 31.0),
        ("W8X35", 8.12, 8.020, 0.310, 35.0),
        ("W8X40", 8.25, 8.070, 0.360, 40.0),
        ("W8X48", 8.50, 8.110, 0.400, 48.0),
        ("W8X58", 8.75, 8.220, 0.510, 58.0),
        ("W8X67", 9.00, 8.280, 0.570, 67.0),
        
        # W10 Series - Complete
        ("W10X12", 9.87, 3.960, 0.190, 12.0),
        ("W10X15", 9.99, 4.000, 0.230, 15.0),
        ("W10X17", 10.11, 4.010, 0.330, 17.0),
        ("W10X19", 10.24, 4.020, 0.395, 19.0),
        ("W10X22", 10.17, 5.750, 0.240, 22.0),
        ("W10X26", 10.33, 5.770, 0.440, 26.0),
        ("W10X30", 10.47, 5.810, 0.510, 30.0),
        ("W10X33", 9.73, 7.960, 0.290, 33.0),
        ("W10X39", 9.92, 7.985, 0.315, 39.0),
        ("W10X45", 10.10, 8.020, 0.350, 45.0),
        ("W10X49", 9.98, 10.000, 0.340, 49.0),
        ("W10X54", 10.09, 10.030, 0.370, 54.0),
        ("W10X60", 10.22, 10.080, 0.420, 60.0),
        ("W10X68", 10.40, 10.130, 0.470, 68.0),
        ("W10X77", 10.60, 10.190, 0.530, 77.0),
        ("W10X88", 10.84, 10.265, 0.605, 88.0),
        ("W10X100", 11.10, 10.340, 0.680, 100.0),
        ("W10X112", 11.36, 10.415, 0.755, 112.0),
        
        # Continue with W12, W14, W16, W18, W21, W24, W27, W30, W33, W36, W40, W44
        ("W12X14", 11.91, 3.970, 0.200, 14.0),
        ("W12X16", 11.99, 3.990, 0.220, 16.0),
        ("W12X19", 12.16, 4.005, 0.235, 19.0),
        ("W12X22", 12.31, 4.030, 0.260, 22.0),
        ("W12X26", 12.22, 6.490, 0.230, 26.0),
        ("W12X30", 12.34, 6.520, 0.260, 30.0),
        ("W12X35", 12.50, 6.560, 0.300, 35.0),
        ("W12X40", 11.94, 8.005, 0.295, 40.0),
        ("W12X45", 12.06, 8.045, 0.335, 45.0),
        ("W12X50", 12.19, 8.080, 0.370, 50.0),
        ("W12X53", 12.06, 10.000, 0.345, 53.0),
        ("W12X58", 12.19, 10.010, 0.360, 58.0),
        ("W12X65", 12.12, 12.000, 0.390, 65.0),
        ("W12X72", 12.25, 12.040, 0.430, 72.0),
        ("W12X79", 12.38, 12.080, 0.470, 79.0),
        ("W12X87", 12.53, 12.125, 0.515, 87.0),
        ("W12X96", 12.71, 12.160, 0.550, 96.0),
        ("W12X106", 12.89, 12.220, 0.610, 106.0),
        ("W12X120", 13.12, 12.320, 0.710, 120.0),
        ("W12X136", 13.41, 12.400, 0.790, 136.0),
        ("W12X152", 13.71, 12.480, 0.870, 152.0),
        ("W12X170", 14.03, 12.570, 0.960, 170.0),
        ("W12X190", 14.38, 12.670, 1.060, 190.0),
        ("W12X210", 14.71, 12.750, 1.140, 210.0),
        ("W12X230", 15.05, 12.855, 1.220, 230.0),
        ("W12X262", 15.59, 13.000, 1.400, 262.0),
        ("W12X279", 15.85, 13.090, 1.530, 279.0),
        ("W12X305", 16.32, 13.235, 1.625, 305.0),
        ("W12X336", 16.82, 13.385, 1.775, 336.0),
        
        # Major sizes from W14, W16, W18, W21, W24, W27, W30, W33, W36
        ("W14X22", 13.74, 5.000, 0.230, 22.0),
        ("W14X26", 13.91, 5.025, 0.255, 26.0),
        ("W14X30", 13.84, 6.730, 0.270, 30.0),
        ("W14X34", 13.98, 6.745, 0.285, 34.0),
        ("W14X38", 14.10, 6.770, 0.310, 38.0),
        ("W14X43", 13.66, 7.995, 0.305, 43.0),
        ("W14X48", 13.79, 8.030, 0.340, 48.0),
        ("W14X53", 13.92, 8.060, 0.370, 53.0),
        ("W14X61", 13.89, 9.995, 0.375, 61.0),
        ("W14X68", 14.04, 10.035, 0.415, 68.0),
        ("W14X74", 14.17, 10.070, 0.450, 74.0),
        ("W14X82", 14.31, 10.130, 0.510, 82.0),
        ("W14X90", 14.02, 14.520, 0.440, 90.0),
        ("W14X99", 14.16, 14.565, 0.485, 99.0),
        ("W14X109", 14.32, 14.605, 0.525, 109.0),
        ("W14X120", 14.48, 14.670, 0.590, 120.0),
        ("W14X132", 14.66, 14.725, 0.645, 132.0),
        ("W14X145", 14.78, 15.500, 0.680, 145.0),
        ("W14X159", 15.00, 15.565, 0.745, 159.0),
        ("W14X176", 15.22, 15.650, 0.830, 176.0),
        ("W14X193", 15.48, 15.710, 0.890, 193.0),
        ("W14X211", 15.72, 15.800, 0.980, 211.0),
        ("W14X233", 16.04, 15.890, 1.070, 233.0),
        ("W14X257", 16.38, 15.995, 1.175, 257.0),
        ("W14X283", 16.74, 16.110, 1.290, 283.0),
        ("W14X311", 17.12, 16.230, 1.410, 311.0),
        ("W14X342", 17.54, 16.360, 1.540, 342.0),
        ("W14X370", 17.92, 16.475, 1.655, 370.0),
        ("W14X398", 18.29, 16.590, 1.770, 398.0),
        ("W14X426", 18.67, 16.695, 1.875, 426.0),
        ("W14X455", 19.02, 16.835, 2.015, 455.0),
        ("W14X500", 19.60, 17.010, 2.190, 500.0),
        
        # Additional major sizes from larger series
        ("W16X26", 15.69, 5.500, 0.250, 26.0),
        ("W16X31", 15.88, 5.525, 0.275, 31.0),
        ("W16X36", 15.86, 6.995, 0.295, 36.0),
        ("W16X40", 16.01, 7.000, 0.305, 40.0),
        ("W16X45", 16.13, 7.035, 0.345, 45.0),
        ("W16X50", 16.26, 7.070, 0.380, 50.0),
        ("W16X57", 16.43, 7.120, 0.430, 57.0),
        ("W16X67", 16.33, 10.235, 0.395, 67.0),
        ("W16X77", 16.52, 10.295, 0.455, 77.0),
        ("W16X89", 16.75, 10.365, 0.525, 89.0),
        ("W16X100", 16.97, 10.425, 0.585, 100.0),
        
        ("W18X35", 17.70, 6.000, 0.300, 35.0),
        ("W18X40", 17.90, 6.015, 0.315, 40.0),
        ("W18X46", 18.06, 6.060, 0.360, 46.0),
        ("W18X50", 17.99, 7.495, 0.355, 50.0),
        ("W18X55", 18.11, 7.530, 0.390, 55.0),
        ("W18X60", 18.24, 7.555, 0.415, 60.0),
        ("W18X65", 18.35, 7.590, 0.450, 65.0),
        ("W18X71", 18.47, 7.635, 0.495, 71.0),
        ("W18X76", 18.21, 11.035, 0.425, 76.0),
        ("W18X86", 18.39, 11.090, 0.480, 86.0),
        ("W18X97", 18.59, 11.145, 0.535, 97.0),
        ("W18X106", 18.73, 11.200, 0.590, 106.0),
        ("W18X119", 18.97, 11.265, 0.655, 119.0),
        
        ("W21X44", 20.66, 6.500, 0.350, 44.0),
        ("W21X50", 20.83, 6.530, 0.380, 50.0),
        ("W21X57", 21.06, 6.555, 0.405, 57.0),
        ("W21X62", 20.99, 8.240, 0.400, 62.0),
        ("W21X68", 21.13, 8.270, 0.430, 68.0),
        ("W21X73", 21.24, 8.295, 0.455, 73.0),
        ("W21X83", 21.43, 8.355, 0.515, 83.0),
        ("W21X93", 21.62, 8.420, 0.580, 93.0),
        ("W21X101", 21.36, 12.290, 0.500, 101.0),
        ("W21X111", 21.51, 12.340, 0.550, 111.0),
        ("W21X122", 21.68, 12.390, 0.600, 122.0),
        ("W21X132", 21.83, 12.440, 0.650, 132.0),
        
        ("W24X55", 23.57, 7.005, 0.395, 55.0),
        ("W24X62", 23.74, 7.040, 0.430, 62.0),
        ("W24X68", 23.73, 8.965, 0.415, 68.0),
        ("W24X76", 23.92, 8.990, 0.440, 76.0),
        ("W24X84", 24.10, 9.020, 0.470, 84.0),
        ("W24X94", 24.31, 9.065, 0.515, 94.0),
        ("W24X104", 24.06, 12.750, 0.500, 104.0),
        ("W24X117", 24.26, 12.800, 0.550, 117.0),
        ("W24X131", 24.48, 12.855, 0.605, 131.0),
        ("W24X146", 24.74, 12.900, 0.650, 146.0),
        ("W24X162", 25.00, 12.955, 0.705, 162.0),
        
        ("W27X84", 26.71, 9.960, 0.460, 84.0),
        ("W27X94", 26.92, 9.990, 0.490, 94.0),
        ("W27X102", 27.09, 10.015, 0.515, 102.0),
        ("W27X114", 27.29, 10.070, 0.570, 114.0),
        ("W27X129", 27.63, 10.110, 0.610, 129.0),
        ("W27X146", 27.38, 13.965, 0.605, 146.0),
        ("W27X161", 27.59, 14.020, 0.660, 161.0),
        ("W27X178", 27.81, 14.085, 0.725, 178.0),
        
        ("W30X90", 29.53, 10.398, 0.470, 90.0),
        ("W30X99", 29.65, 10.450, 0.520, 99.0),
        ("W30X108", 29.83, 10.475, 0.545, 108.0),
        ("W30X116", 30.01, 10.500, 0.565, 116.0),
        ("W30X124", 30.17, 10.515, 0.585, 124.0),
        ("W30X132", 30.31, 10.545, 0.615, 132.0),
        ("W30X148", 30.67, 10.630, 0.650, 148.0),
        ("W30X173", 30.44, 15.040, 0.655, 173.0),
        ("W30X191", 30.68, 15.100, 0.710, 191.0),
        ("W30X211", 30.94, 15.155, 0.775, 211.0),
        
        ("W33X118", 32.86, 11.480, 0.550, 118.0),
        ("W33X130", 33.09, 11.510, 0.580, 130.0),
        ("W33X141", 33.30, 11.535, 0.605, 141.0),
        ("W33X152", 33.49, 11.565, 0.635, 152.0),
        ("W33X169", 33.82, 11.620, 0.670, 169.0),
        ("W33X201", 33.68, 15.745, 0.715, 201.0),
        ("W33X221", 33.93, 15.805, 0.775, 221.0),
        ("W33X241", 34.18, 15.860, 0.830, 241.0),
        
        ("W36X135", 35.55, 11.950, 0.600, 135.0),
        ("W36X150", 35.85, 11.975, 0.625, 150.0),
        ("W36X160", 36.01, 12.000, 0.650, 160.0),
        ("W36X170", 36.17, 12.030, 0.680, 170.0),
        ("W36X182", 36.33, 12.075, 0.725, 182.0),
        ("W36X194", 36.49, 12.115, 0.765, 194.0),
        ("W36X210", 36.69, 12.180, 0.830, 210.0),
        ("W36X230", 35.90, 16.470, 0.760, 230.0),
        ("W36X245", 36.08, 16.510, 0.800, 245.0),
        ("W36X260", 36.26, 16.550, 0.840, 260.0),
        ("W36X280", 36.52, 16.595, 0.885, 280.0),
        ("W36X300", 36.74, 16.655, 0.945, 300.0),
        ("W36X330", 37.12, 16.770, 1.060, 330.0),
        ("W36X359", 37.47, 16.875, 1.165, 359.0),
        ("W36X393", 37.82, 17.010, 1.300, 393.0),
    ]
    
    count = 0
    for shape_key, depth, width, thickness, weight in wf_data:
        desc = f"Wide Flange Beam {shape_key} - {weight} lb/ft"
        add_material(db, shape_key, desc, "Wide Flange", weight, 
                    depth, width, thickness, 85.0 + (weight * 0.1))
        count += 1
    
    print(f"   Added {count} wide flange beams")
    return count

def populate_comprehensive_plates(db):
    """Populate comprehensive plate materials"""
    print("Populating Comprehensive Plate Materials...")
    
    # Comprehensive plate thickness and width combinations
    thicknesses = [0.1875, 0.25, 0.3125, 0.375, 0.4375, 0.5, 0.5625, 0.625, 0.6875, 0.75, 0.8125, 0.875, 1.0, 1.125, 1.25, 1.375, 1.5, 1.625, 1.75, 1.875, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25, 3.5, 3.75, 4.0, 4.5, 5.0, 5.5, 6.0]
    widths = [4, 5, 6, 8, 10, 12, 16, 18, 20, 24, 30, 36, 48, 60, 72, 84, 96, 120, 144]
    
    # Steel density: 489.6 lb/cu ft
    steel_density_pcf = 489.6
    
    count = 0
    for thickness in thicknesses:
        for width in widths[:12]:  # Limit widths to prevent explosion
            # Create shape key
            if thickness < 1.0:
                if thickness == 0.1875:
                    thick_str = "3/16"
                elif thickness == 0.25:
                    thick_str = "1/4"
                elif thickness == 0.3125:
                    thick_str = "5/16"
                elif thickness == 0.375:
                    thick_str = "3/8"
                elif thickness == 0.4375:
                    thick_str = "7/16"
                elif thickness == 0.5:
                    thick_str = "1/2"
                elif thickness == 0.5625:
                    thick_str = "9/16"
                elif thickness == 0.625:
                    thick_str = "5/8"
                elif thickness == 0.6875:
                    thick_str = "11/16"
                elif thickness == 0.75:
                    thick_str = "3/4"
                elif thickness == 0.8125:
                    thick_str = "13/16"
                elif thickness == 0.875:
                    thick_str = "7/8"
                else:
                    thick_str = str(thickness)
            else:
                if thickness == int(thickness):
                    thick_str = str(int(thickness))
                else:
                    thick_str = str(thickness)
            
            shape_key = f"PL{thick_str}X{width}"
            
            # Calculate weight per square foot
            weight_per_sq_ft = (thickness / 12.0) * steel_density_pcf
            
            desc = f"Steel Plate {thick_str}\" thick x {width}\" wide - {weight_per_sq_ft:.1f} lb/sq ft"
            
            # For plates, we store weight per square foot in weight_per_ft field
            add_material(db, shape_key, desc, "Plate", weight_per_sq_ft,
                        thickness_inches=thickness, width_inches=width,
                        unit_price_per_cwt=82.0 + (thickness * 2.0))
            count += 1
    
    print(f"   Added {count} plate materials")
    return count

def main():
    print("Capitol Engineering Company - Comprehensive Material Database Population")
    print("=" * 80)
    
    # Create tables
    create_tables()
    
    # Connect to database
    db = SessionLocal()
    
    try:
        # Clear existing materials
        clear_existing_materials()
        
        # Populate comprehensive materials
        wf_count = populate_comprehensive_wide_flange(db)
        plate_count = populate_comprehensive_plates(db)
        
        # Commit all changes
        db.commit()
        
        total_count = wf_count + plate_count
        
        print("\n" + "=" * 80)
        print("COMPREHENSIVE MATERIAL DATABASE POPULATION COMPLETE!")
        print(f"   Total Materials: {total_count}")
        print(f"   Wide Flange: {wf_count}")
        print(f"   Plates: {plate_count}")
        print("=" * 80)
        
        # Show sample materials
        sample_materials = db.query(Material).limit(10).all()
        print("\nSample Materials:")
        for material in sample_materials:
            print(f"   - {material.shape_key}: {material.description}")
        
        print(f"\nProfessional material database ready for Capitol Engineering!")
        print(f"Frontend will now show ~{total_count} comprehensive material suggestions!")
        
    except Exception as e:
        db.rollback()
        print(f"Error populating database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()