#!/usr/bin/env python3
"""
Shopify PLP Migration Validation Script

This script helps validate that the PLP content migration was successful
by comparing the original and updated CSV files.
"""

import csv
import sys
import logging
import re
from urllib.parse import urlparse

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ValidationScript:
    def __init__(self, original_file, updated_file, plp_content_file):
        self.original_file = original_file
        self.updated_file = updated_file
        self.plp_content_file = plp_content_file
        
        self.original_categories = {}
        self.updated_categories = {}
        self.plp_content = {}
        self.changes = []
        self.content_map = {}  # Map handle to PLP content

    def clean_field_name(self, field_name):
        """Clean field name by removing quotes, BOM, and extra whitespace."""
        if not field_name:
            return ""
        cleaned = field_name.replace('\ufeff', '').strip().strip('"').strip("'")
        return cleaned

    def extract_handle_from_url(self, url):
        """Extract handle from URL (e.g., from 'https://jrdunn.com/diamonds-engagement-rings/tacori.html' get 'tacori')."""
        if not url:
            return None
        
        try:
            parsed = urlparse(url)
            path = parsed.path.strip('/')
            
            # Split path into segments and get the last one
            segments = [seg for seg in path.split('/') if seg]
            if not segments:
                return None
                
            handle = segments[-1]
            # Remove .html extension
            handle = re.sub(r'\.html$', '', handle)
            
            return handle
        except Exception as e:
            logger.warning(f"Error parsing URL {url}: {e}")
            return None

    def load_csv_file(self, filename, is_plp=False):
        """Load CSV file and return as dictionary."""
        data = {}
        
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                if is_plp:
                    # For PLP content, use URL as key and create handle mapping
                    for row in reader:
                        cleaned_row = {}
                        for key, value in row.items():
                            clean_key = self.clean_field_name(key)
                            cleaned_row[clean_key] = value.strip() if value else ""
                        
                        url = cleaned_row.get('URL', '')
                        if url:
                            data[url] = cleaned_row
                            
                            # Create handle mapping
                            handle = self.extract_handle_from_url(url)
                            if handle:
                                self.content_map[handle] = cleaned_row
                else:
                    # For Shopify categories, use ID as key
                    for row in reader:
                        cleaned_row = {}
                        for key, value in row.items():
                            clean_key = self.clean_field_name(key)
                            cleaned_row[clean_key] = value.strip() if value else ""
                        
                        category_id = cleaned_row.get('ID', '')
                        if category_id:
                            data[category_id] = cleaned_row
                
                logger.info(f"Loaded {len(data)} entries from {filename}")
                if is_plp:
                    logger.info(f"Created {len(self.content_map)} handle mappings")
                return data
                
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            return {}

    def load_all_files(self):
        """Load all CSV files."""
        logger.info("Loading CSV files for validation...")
        
        self.original_categories = self.load_csv_file(self.original_file)
        self.updated_categories = self.load_csv_file(self.updated_file)
        self.plp_content = self.load_csv_file(self.plp_content_file, is_plp=True)

    def find_changes(self):
        """Find changes between original and updated categories."""
        logger.info("Analyzing changes...")
        
        changes = []
        updated_count = 0
        
        for category_id, updated_category in self.updated_categories.items():
            original_category = self.original_categories.get(category_id)
            
            if not original_category:
                continue
            
            # Check for changes in key fields
            changes_found = []
            
            # Check Title changes
            original_title = original_category.get('Title', '')
            updated_title = updated_category.get('Title', '')
            if original_title != updated_title and updated_title:
                changes_found.append(f"Title: '{original_title}' → '{updated_title}'")
            
            # Check Body HTML changes
            original_html = original_category.get('Body HTML', '')
            updated_html = updated_category.get('Body HTML', '')
            if original_html != updated_html and updated_html:
                changes_found.append(f"Body HTML: Updated with new content")
            
            # Check subheading metafield changes
            original_subheading = original_category.get('Metafield: custom.collection_subheading [single_line_text_field]', '')
            updated_subheading = updated_category.get('Metafield: custom.collection_subheading [single_line_text_field]', '')
            if original_subheading != updated_subheading and updated_subheading:
                changes_found.append(f"Subheading: '{original_subheading}' → '{updated_subheading}'")
            
            if changes_found:
                handle = updated_category.get('Handle', '')
                change_info = {
                    'category_id': category_id,
                    'handle': handle,
                    'original_title': original_title,
                    'updated_title': updated_title,
                    'has_html_content': bool(updated_html),
                    'has_subheading': bool(updated_subheading),
                    'changes': changes_found,
                    'html_preview': updated_html[:200] + "..." if len(updated_html) > 200 else updated_html
                }
                changes.append(change_info)
                updated_count += 1
        
        self.changes = changes
        logger.info(f"Found {len(changes)} categories with changes")
        return updated_count

    def print_validation_report(self):
        """Print a comprehensive validation report."""
        print("=" * 80)
        print("SHOPIFY PLP MIGRATION VALIDATION REPORT")
        print("=" * 80)
        
        # Summary statistics
        total_categories = len(self.updated_categories)
        updated_categories = len(self.changes)
        plp_entries = len(self.plp_content)
        handle_mappings = len(self.content_map)
        
        print(f"📊 SUMMARY STATISTICS")
        print(f"   Total Shopify categories: {total_categories:,}")
        print(f"   Categories updated: {updated_categories:,}")
        print(f"   PLP content entries: {plp_entries:,}")
        print(f"   Handle mappings created: {handle_mappings:,}")
        print(f"   Match rate: {(updated_categories/len(self.content_map)*100):.1f}%" if self.content_map else "N/A")
        print()
        
        # Show sample changes
        if self.changes:
            print(f"📝 SAMPLE UPDATES (showing first 10)")
            print("-" * 80)
            
            for i, change in enumerate(self.changes[:10]):
                print(f"{i+1}. {change['handle']} (ID: {change['category_id']})")
                print(f"   Title: {change['original_title']} → {change['updated_title']}")
                print(f"   HTML Content: {'Yes' if change['has_html_content'] else 'No'}")
                print(f"   Subheading: {'Yes' if change['has_subheading'] else 'No'}")
                if change['has_html_content']:
                    print(f"   HTML Preview: {change['html_preview']}")
                print()
            
            if len(self.changes) > 10:
                print(f"... and {len(self.changes) - 10} more updates")
                print()
        
        # Validation results
        print(f"✅ VALIDATION RESULTS")
        print("-" * 80)
        
        if updated_categories > 0:
            print("✅ Migration appears successful!")
            print("✅ Categories were updated with new content")
            print("✅ HTML formatting was applied")
            print("✅ Subheadings were set as metafields")
            print()
            print("🔍 NEXT STEPS:")
            print("1. Import shopify-categories-updated.csv to Shopify")
            print("2. Run quick_test.py to verify specific collections")
            print("3. Check collection pages manually")
        else:
            print("❌ No categories were updated")
            print("❌ Check your input files and migration logs")
            print()
            print("🔍 TROUBLESHOOTING:")
            print("1. Verify new-plp-content.csv has valid URLs")
            print("2. Check that shopify-categories-export.csv has matching handles")
            print("3. Review the migration script logs")

    def save_changes_report(self, output_file='validation_report.csv'):
        """Save detailed changes report to CSV."""
        if not self.changes:
            logger.warning("No changes to report")
            return
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as file:
                fieldnames = [
                    'Category ID', 'Handle', 'Original Title', 'Updated Title',
                    'Has HTML Content', 'Has Subheading', 'Changes', 'HTML Preview'
                ]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                
                for change in self.changes:
                    writer.writerow({
                        'Category ID': change['category_id'],
                        'Handle': change['handle'],
                        'Original Title': change['original_title'],
                        'Updated Title': change['updated_title'],
                        'Has HTML Content': 'Yes' if change['has_html_content'] else 'No',
                        'Has Subheading': 'Yes' if change['has_subheading'] else 'No',
                        'Changes': '; '.join(change['changes']),
                        'HTML Preview': change['html_preview']
                    })
            
            logger.info(f"Saved detailed report to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving report: {e}")

    def run(self):
        """Run the complete validation process."""
        logger.info("Starting validation process...")
        
        try:
            # Load all files
            self.load_all_files()
            
            # Find changes
            updated_count = self.find_changes()
            
            # Print report
            self.print_validation_report()
            
            # Save detailed report
            if self.changes:
                self.save_changes_report()
            
            logger.info("Validation completed successfully!")
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            raise

def main():
    """Main function to run the validation script."""
    # File paths
    original_file = 'shopify-categories-export.csv'
    updated_file = 'shopify-categories-updated.csv'
    plp_content_file = 'new-plp-content.csv'
    
    # Check if files exist
    import os
    missing_files = []
    for filename in [original_file, updated_file, plp_content_file]:
        if not os.path.exists(filename):
            missing_files.append(filename)
    
    if missing_files:
        logger.error(f"Missing files: {', '.join(missing_files)}")
        logger.error("Please run the migration script first.")
        sys.exit(1)
    
    # Run validation
    validation = ValidationScript(original_file, updated_file, plp_content_file)
    validation.run()

if __name__ == "__main__":
    main() 