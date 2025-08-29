"""
Material Database Migration Script - Import materials from CSV files
Imports Blake's comprehensive material database and other specialty lists
"""

import csv
import os
from decimal import Decimal, InvalidOperation
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.material import Material
from app.core.database import SessionLocal


class MaterialImporter:
    """Handle importing materials from various CSV sources"""
    
    def __init__(self):
        self.stats = {
            'total_processed': 0,
            'imported': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
        self.error_log = []
        
    def parse_decimal(self, value: str) -> Optional[float]:
        """Safely parse decimal values from CSV"""
        if not value or value.strip() == '':
            return None
        try:
            # Remove any currency symbols and whitespace
            cleaned = str(value).strip().replace('$', '').replace(',', '')
            return float(Decimal(cleaned))
        except (InvalidOperation, ValueError, TypeError):
            return None
    
    def parse_string(self, value: str) -> str:
        """Clean and parse string values"""
        if not value:
            return ""
        return str(value).strip()
    
    def import_blake_master_list(self, csv_path: str, db: Session) -> Dict[str, int]:
        """Import materials from Blake's master list CSV"""
        print(f"Importing Blake Master List from: {csv_path}")
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        batch_stats = {'processed': 0, 'imported': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
        batch_size = 1000
        current_batch = []
        
        with open(csv_path, 'r', encoding='utf-8-sig', newline='') as file:
            # Detect delimiter
            sample = file.read(1024)
            file.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(file, delimiter=delimiter)
            
            # Map CSV columns to our database fields
            for row_num, row in enumerate(reader, start=2):
                try:
                    batch_stats['processed'] += 1
                    
                    # Extract and clean data from CSV row
                    designation = self.parse_string(row.get('Designation', ''))
                    if not designation:
                        batch_stats['skipped'] += 1
                        continue
                    
                    # Create material data
                    material_data = {
                        'shape_key': designation.upper(),  # Standardize to uppercase
                        'category': self.parse_string(row.get('Category', 'General')),
                        'subcategory': self.parse_string(row.get('Subcategory', '')),
                        'description': self.parse_string(row.get('Material', '')),
                        'specs_standard': self.parse_string(row.get('Specs/Standard', '')),
                        'size_dimensions': self.parse_string(row.get('Size/Dimensions', '')),
                        'schedule_class': self.parse_string(row.get('Schedule/Class', '')),
                        'finish_coating': self.parse_string(row.get('Finish/Coating', '')),
                        'notes': self.parse_string(row.get('Notes', '')),
                        'unit_of_measure': self.parse_string(row.get('UoM', 'each')),
                        'weight_per_uom': self.parse_decimal(row.get('Weight_per_UoM', '')),
                        'base_price_usd': self.parse_decimal(row.get('Base_Price', '')),
                        'sku_part_number': self.parse_string(row.get('SKU/Part', '')),
                        'source_system': 'blake',
                        'price_confidence': 'high' if self.parse_decimal(row.get('Base_Price', '')) else 'missing',
                        'price_status': 'current',
                        'last_price_update': datetime.now(timezone.utc)
                    }
                    
                    current_batch.append(material_data)
                    
                    # Process batch when it's full
                    if len(current_batch) >= batch_size:
                        batch_result = self._process_batch(current_batch, db)
                        self._update_stats(batch_stats, batch_result)
                        current_batch = []
                        print(f"Processed {batch_stats['processed']} materials...")
                        
                except Exception as e:
                    batch_stats['errors'] += 1
                    error_msg = f"Row {row_num}: {str(e)}"
                    self.error_log.append(error_msg)
                    print(f"Error processing row {row_num}: {e}")
        
        # Process remaining materials in final batch
        if current_batch:
            batch_result = self._process_batch(current_batch, db)
            self._update_stats(batch_stats, batch_result)
        
        return batch_stats
    
    def import_hardware_list(self, csv_path: str, db: Session) -> Dict[str, int]:
        """Import hardware materials from CSV"""
        print(f"Importing Hardware List from: {csv_path}")
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        batch_stats = {'processed': 0, 'imported': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
        materials_data = []
        
        with open(csv_path, 'r', encoding='utf-8-sig', newline='') as file:
            reader = csv.DictReader(file)
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    batch_stats['processed'] += 1
                    
                    item = self.parse_string(row.get('item', ''))
                    if not item:
                        batch_stats['skipped'] += 1
                        continue
                    
                    # Create material data for hardware
                    material_data = {
                        'shape_key': item.upper().replace(',', ' -'),  # Clean shape key
                        'category': self.parse_string(row.get('category', 'Hardware')),
                        'subcategory': 'Hardware',
                        'description': item,
                        'specs_standard': self.parse_string(row.get('spec', '')),
                        'size_dimensions': self.parse_string(row.get('spec', '')),  # Use spec as dimensions for hardware
                        'unit_of_measure': self.parse_string(row.get('unit', 'each')),
                        'base_price_usd': self.parse_decimal(row.get('baseline_price_usd', '')),
                        'supplier': self.parse_string(row.get('source', '')),
                        'notes': f"Source: {self.parse_string(row.get('source', ''))} | {self.parse_string(row.get('notes', ''))}",
                        'source_system': 'hardware_list',
                        'price_confidence': 'high',
                        'price_status': 'current',
                        'last_price_update': datetime.now(timezone.utc)
                    }
                    
                    materials_data.append(material_data)
                    
                except Exception as e:
                    batch_stats['errors'] += 1
                    error_msg = f"Hardware row {row_num}: {str(e)}"
                    self.error_log.append(error_msg)
                    print(f"Error processing hardware row {row_num}: {e}")
        
        # Process all hardware materials
        if materials_data:
            batch_result = self._process_batch(materials_data, db)
            self._update_stats(batch_stats, batch_result)
        
        return batch_stats
    
    def import_grating_list(self, csv_path: str, db: Session) -> Dict[str, int]:
        """Import grating materials from Blake's grating CSV"""
        print(f"Importing Grating List from: {csv_path}")
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        batch_stats = {'processed': 0, 'imported': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
        materials_data = []
        
        with open(csv_path, 'r', encoding='utf-8-sig', newline='') as file:
            reader = csv.DictReader(file)
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    batch_stats['processed'] += 1
                    
                    # Build designation from grating specifications
                    material = self.parse_string(row.get('material', ''))
                    style = self.parse_string(row.get('style', ''))
                    series = self.parse_string(row.get('series', ''))
                    depth = self.parse_string(row.get('bearing_bar_depth_in', ''))
                    width = self.parse_string(row.get('panel_width_in', ''))
                    length = self.parse_string(row.get('panel_length_in', ''))
                    
                    if not material or not series:
                        batch_stats['skipped'] += 1
                        continue
                    
                    # Build a meaningful shape key for grating
                    designation = f"GRATING {series}"
                    if depth:
                        designation += f" {depth}\" DEEP"
                    if width and length:
                        designation += f" {width}\"x{length}\""
                    
                    # Create material data for grating
                    material_data = {
                        'shape_key': designation.upper(),
                        'category': 'Grating',
                        'subcategory': self.parse_string(row.get('category', 'Bar Grating')),
                        'description': f"{material} {style} Grating",
                        'specs_standard': material,
                        'size_dimensions': f"{width}\" x {length}\" x {depth}\"" if width and length and depth else '',
                        'finish_coating': self.parse_string(row.get('finish', '')),
                        'unit_of_measure': 'sq ft',
                        'weight_per_uom': None,  # Not provided in this CSV
                        'base_price_usd': None,  # No pricing in this CSV
                        'notes': f"Series: {series}, Bearing Bar Thickness: {self.parse_string(row.get('bearing_bar_thk_in', ''))}\"",
                        'source_system': 'blake_grating',
                        'price_confidence': 'missing',
                        'price_status': 'needs_verification',
                        'last_price_update': datetime.now(timezone.utc)
                    }
                    
                    materials_data.append(material_data)
                    
                except Exception as e:
                    batch_stats['errors'] += 1
                    error_msg = f"Grating row {row_num}: {str(e)}"
                    self.error_log.append(error_msg)
                    print(f"Error processing grating row {row_num}: {e}")
        
        # Process all grating materials
        if materials_data:
            batch_result = self._process_batch(materials_data, db)
            self._update_stats(batch_stats, batch_result)
        
        return batch_stats
    
    def import_frp_list(self, csv_path: str, db: Session) -> Dict[str, int]:
        """Import FRP materials from Blake's FRP CSV"""
        print(f"Importing FRP List from: {csv_path}")
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        batch_stats = {'processed': 0, 'imported': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
        materials_data = []
        
        with open(csv_path, 'r', encoding='utf-8-sig', newline='') as file:
            reader = csv.DictReader(file)
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    batch_stats['processed'] += 1
                    
                    # Use SKU as the designation for FRP materials
                    sku = self.parse_string(row.get('sku', ''))
                    category = self.parse_string(row.get('category', ''))
                    thickness = self.parse_string(row.get('thickness_in', ''))
                    mesh = self.parse_string(row.get('mesh', ''))
                    width = self.parse_string(row.get('panel_width_in', ''))
                    length = self.parse_string(row.get('panel_length_in', ''))
                    
                    if not sku and not category:
                        batch_stats['skipped'] += 1
                        continue
                    
                    # Use SKU if available, otherwise build designation
                    if sku:
                        designation = sku
                    else:
                        designation = f"FRP {thickness}\" {mesh}"
                        if width and length:
                            designation += f" {width}\"x{length}\""
                    
                    # Create material data for FRP
                    material_data = {
                        'shape_key': designation.upper(),
                        'category': 'FRP',
                        'subcategory': category,
                        'description': f"FRP {thickness}\" thick, {mesh} mesh",
                        'specs_standard': self.parse_string(row.get('resin', '')),
                        'size_dimensions': f"{width}\" x {length}\" x {thickness}\"" if width and length and thickness else '',
                        'finish_coating': f"{self.parse_string(row.get('surface', ''))} {self.parse_string(row.get('color', ''))}".strip(),
                        'unit_of_measure': 'sq ft',
                        'weight_per_uom': None,  # Not provided in this CSV
                        'base_price_usd': None,  # No pricing in this CSV
                        'sku_part_number': sku,
                        'notes': f"Mesh: {mesh}, Surface: {self.parse_string(row.get('surface', ''))}, Resin: {self.parse_string(row.get('resin', ''))}",
                        'source_system': 'blake_frp',
                        'price_confidence': 'missing',
                        'price_status': 'needs_verification',
                        'last_price_update': datetime.now(timezone.utc)
                    }
                    
                    materials_data.append(material_data)
                    
                except Exception as e:
                    batch_stats['errors'] += 1
                    error_msg = f"FRP row {row_num}: {str(e)}"
                    self.error_log.append(error_msg)
                    print(f"Error processing FRP row {row_num}: {e}")
        
        # Process all FRP materials
        if materials_data:
            batch_result = self._process_batch(materials_data, db)
            self._update_stats(batch_stats, batch_result)
        
        return batch_stats
    
    def _process_batch(self, materials_data: List[Dict], db: Session) -> Dict[str, int]:
        """Process a batch of materials for database insertion/update"""
        result = {'imported': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
        
        # Process each material individually to avoid batch conflicts
        for material_data in materials_data:
            try:
                # Check if material already exists
                existing = db.query(Material).filter(
                    Material.shape_key == material_data['shape_key']
                ).first()
                
                if existing:
                    # Update existing material with new data if it's from Blake (higher priority)
                    if material_data['source_system'] == 'blake' or existing.source_system == 'manual':
                        for key, value in material_data.items():
                            if key != 'shape_key' and value is not None and value != '':
                                setattr(existing, key, value)
                        result['updated'] += 1
                        # Only print every 100th update to reduce console spam
                        if result['updated'] % 100 == 0:
                            print(f"  Updated {result['updated']} materials so far...")
                    else:
                        result['skipped'] += 1
                else:
                    # Create new material
                    new_material = Material(**material_data)
                    db.add(new_material)
                    result['imported'] += 1
                    # Only print every 100th import to reduce console spam
                    if result['imported'] % 100 == 0:
                        print(f"  Imported {result['imported']} new materials so far...")
                
                # Commit each material individually to avoid batch conflicts
                db.commit()
                    
            except IntegrityError as e:
                db.rollback()
                # This might be a duplicate from within the same batch, skip it
                result['skipped'] += 1
            except Exception as e:
                db.rollback()
                result['errors'] += 1
                error_msg = f"Error processing {material_data.get('shape_key', 'unknown')}: {str(e)}"
                self.error_log.append(error_msg)
                # Only print first 10 errors to avoid spam
                if result['errors'] <= 10:
                    print(f"  Error: {error_msg}")
        
        return result
    
    def _update_stats(self, main_stats: Dict[str, int], batch_stats: Dict[str, int]):
        """Update main statistics with batch results"""
        for key in ['imported', 'updated', 'skipped', 'errors']:
            main_stats[key] += batch_stats[key]
    
    def import_all_materials(self, base_path: str = None) -> Dict[str, any]:
        """Import all material CSV files"""
        if not base_path:
            base_path = "C:/Users/holme/OneDrive/Desktop/Spreadsheet CE"
        
        print("Starting comprehensive material database import...")
        print("=" * 50)
        
        db = SessionLocal()
        total_stats = {
            'files_processed': 0,
            'total_materials': 0,
            'imported': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0,
            'import_time': None
        }
        
        start_time = datetime.now()
        
        try:
            # Define CSV files to import
            csv_files = [
                {
                    'name': 'Blake Master List',
                    'path': os.path.join(base_path, 'BLAKE_MAT_LIST_Master_List.csv'),
                    'method': self.import_blake_master_list
                },
                {
                    'name': 'Blake Grating List',
                    'path': os.path.join(base_path, 'BLAKE_MAT_LIST_Grating_List.csv'),
                    'method': self.import_grating_list
                },
                {
                    'name': 'Blake FRP List',
                    'path': os.path.join(base_path, 'BLAKE_MAT_LIST_FRP_List.csv'),
                    'method': self.import_frp_list
                },
                {
                    'name': 'Hardware List',
                    'path': os.path.join(base_path, 'Hardware_with_Baseline_Prices__preview_.csv'),
                    'method': self.import_hardware_list
                },
            ]
            
            for csv_file in csv_files:
                if os.path.exists(csv_file['path']):
                    print(f"\nProcessing {csv_file['name']}...")
                    file_stats = csv_file['method'](csv_file['path'], db)
                    
                    total_stats['files_processed'] += 1
                    total_stats['total_materials'] += file_stats['processed']
                    total_stats['imported'] += file_stats['imported']
                    total_stats['updated'] += file_stats['updated'] 
                    total_stats['skipped'] += file_stats['skipped']
                    total_stats['errors'] += file_stats['errors']
                    
                    print(f"OK {csv_file['name']}: {file_stats['imported']} imported, {file_stats['updated']} updated, {file_stats['errors']} errors")
                else:
                    print(f"WARNING: {csv_file['name']} file not found: {csv_file['path']}")
            
            end_time = datetime.now()
            total_stats['import_time'] = str(end_time - start_time)
            
            # Generate final report
            print("\n" + "=" * 50)
            print("MATERIAL IMPORT SUMMARY")
            print("=" * 50)
            print(f"Files processed: {total_stats['files_processed']}")
            print(f"Total materials processed: {total_stats['total_materials']:,}")
            print(f"New materials imported: {total_stats['imported']:,}")
            print(f"Materials updated: {total_stats['updated']:,}")
            print(f"Materials skipped: {total_stats['skipped']:,}")
            print(f"Errors encountered: {total_stats['errors']:,}")
            print(f"Import duration: {total_stats['import_time']}")
            
            if self.error_log:
                print(f"\nWARNING: {len(self.error_log)} errors logged")
                if len(self.error_log) <= 20:
                    for error in self.error_log:
                        print(f"  - {error}")
                else:
                    for error in self.error_log[:20]:
                        print(f"  - {error}")
                    print(f"  ... and {len(self.error_log) - 20} more errors")
            
            # Verify final database count
            final_count = db.query(Material).count()
            print(f"\nSUCCESS: Final database contains {final_count:,} materials")
            
        except Exception as e:
            print(f"\nERROR: Import failed: {str(e)}")
            total_stats['errors'] += 1
        finally:
            db.close()
        
        return total_stats


def migrate_materials():
    """Main function to run material migration"""
    importer = MaterialImporter()
    return importer.import_all_materials()


if __name__ == "__main__":
    migrate_materials()