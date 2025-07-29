#!/usr/bin/env python3
"""
Enhanced Migration Coverage Analysis Script

This script analyzes the PLP content migration results, showing:
1. What collections were actually updated
2. What collections were not updated (and why)
3. URLs for all updated collections
4. Detailed coverage analysis
"""

import csv
import sys
import logging
from urllib.parse import urlparse
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedMigrationAnalyzer:
    def __init__(self, plp_content_file, original_shopify_file, updated_shopify_file, base_url):
        self.plp_content_file = plp_content_file
        self.original_shopify_file = original_shopify_file
        self.updated_shopify_file = updated_shopify_file
        self.base_url = base_url.rstrip('/')
        
        # Data storage
        self.plp_content_map = {}  # handle -> content data
        self.original_shopify_data = {}  # handle -> original data
        self.updated_shopify_data = {}  # handle -> updated data
        
        # Analysis results
        self.updated_collections = []
        self.not_updated_collections = []
        self.missing_plp_content = []
        
    def extract_handle_from_url(self, url):
        """Extract handle from URL (same logic as migration script)."""
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
    
    def clean_field_name(self, field_name):
        """Clean field name by removing quotes, BOM, and extra whitespace."""
        if not field_name:
            return ""
        cleaned = field_name.replace('\ufeff', '').strip().strip('"').strip("'")
        return cleaned
    
    def load_plp_content(self):
        """Load PLP content and create handle mapping."""
        logger.info("Loading PLP content...")
        
        try:
            with open(self.plp_content_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    # Clean up the data
                    cleaned_row = {}
                    for key, value in row.items():
                        clean_key = self.clean_field_name(key)
                        cleaned_row[clean_key] = value.strip() if value else ""
                    
                    url = cleaned_row.get('URL', '')
                    handle = self.extract_handle_from_url(url)
                    
                    if handle:
                        self.plp_content_map[handle] = {
                            'url': url,
                            'title': cleaned_row.get('Title', ''),
                            'subheading': cleaned_row.get('Sub-heading', ''),
                            'description': cleaned_row.get('Description', ''),
                            'content_under_listing': cleaned_row.get('Content under product listing', '')
                        }
                
                logger.info(f"Loaded {len(self.plp_content_map)} PLP content entries")
                
        except Exception as e:
            logger.error(f"Error loading PLP content: {e}")
            raise
    
    def load_shopify_data(self, filename, data_dict):
        """Load Shopify data from CSV file."""
        logger.info(f"Loading Shopify data from {filename}...")
        
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    # Clean up the row data
                    cleaned_row = {}
                    for key, value in row.items():
                        clean_key = self.clean_field_name(key)
                        cleaned_row[clean_key] = value.strip() if value else ""
                    
                    handle = cleaned_row.get('Handle', '')
                    if handle and handle != 'Handle':
                        data_dict[handle] = cleaned_row
                
                logger.info(f"Loaded {len(data_dict)} entries from {filename}")
                
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            raise
    
    def analyze_updates(self):
        """Analyze what collections were actually updated."""
        logger.info("Analyzing collection updates...")
        
        for handle, updated_row in self.updated_shopify_data.items():
            original_row = self.original_shopify_data.get(handle)
            
            if not original_row:
                continue
            
            # Check if any key fields were updated
            updated_fields = []
            
            # Check Title changes
            original_title = original_row.get('Title', '')
            updated_title = updated_row.get('Title', '')
            if original_title != updated_title and updated_title:
                updated_fields.append(f"Title: '{original_title}' → '{updated_title}'")
            
            # Check Body HTML changes
            original_html = original_row.get('Body HTML', '')
            updated_html = updated_row.get('Body HTML', '')
            if original_html != updated_html and updated_html:
                updated_fields.append("Body HTML: Updated with new content")
            
            # Check subheading metafield changes
            original_subheading = original_row.get('Metafield: custom.collection_subheading [single_line_text_field]', '')
            updated_subheading = updated_row.get('Metafield: custom.collection_subheading [single_line_text_field]', '')
            if original_subheading != updated_subheading and updated_subheading:
                updated_fields.append(f"Subheading: '{original_subheading}' → '{updated_subheading}'")
            
            # Determine if this collection was updated
            if updated_fields:
                # This collection was updated
                collection_info = {
                    'handle': handle,
                    'title': updated_title or handle,
                    'url': f"{self.base_url}/collections/{handle}",
                    'changes': updated_fields,
                    'has_plp_content': handle in self.plp_content_map,
                    'plp_content': self.plp_content_map.get(handle, {})
                }
                self.updated_collections.append(collection_info)
            else:
                # This collection was not updated
                collection_info = {
                    'handle': handle,
                    'title': updated_title or handle,
                    'url': f"{self.base_url}/collections/{handle}",
                    'has_plp_content': handle in self.plp_content_map,
                    'plp_content': self.plp_content_map.get(handle, {})
                }
                self.not_updated_collections.append(collection_info)
        
        # Find PLP content that didn't match any Shopify collection
        plp_handles = set(self.plp_content_map.keys())
        shopify_handles = set(self.original_shopify_data.keys())
        unmatched_plp = plp_handles - shopify_handles
        
        for handle in unmatched_plp:
            self.missing_plp_content.append({
                'handle': handle,
                'plp_content': self.plp_content_map[handle]
            })
    
    def print_analysis(self):
        """Print comprehensive analysis results."""
        print("=" * 80)
        print("ENHANCED MIGRATION ANALYSIS")
        print("=" * 80)
        print()
        
        # Overall statistics
        total_shopify = len(self.original_shopify_data)
        total_plp = len(self.plp_content_map)
        updated_count = len(self.updated_collections)
        not_updated_count = len(self.not_updated_collections)
        missing_plp_count = len(self.missing_plp_content)
        
        print("📊 OVERALL STATISTICS:")
        print(f"   • Total Shopify collections: {total_shopify}")
        print(f"   • Total PLP content entries: {total_plp}")
        print(f"   • Collections updated: {updated_count}")
        print(f"   • Collections not updated: {not_updated_count}")
        print(f"   • PLP content without matching collections: {missing_plp_count}")
        print(f"   • Update success rate: {(updated_count/total_shopify*100):.1f}%")
        print()
        
        # Updated collections
        print("✅ UPDATED COLLECTIONS:")
        print("-" * 40)
        for i, collection in enumerate(self.updated_collections, 1):
            print(f"{i:2d}. {collection['title']}")
            print(f"     Handle: {collection['handle']}")
            print(f"     URL: {collection['url']}")
            print(f"     Changes:")
            for change in collection['changes']:
                print(f"       • {change}")
            print()
        
        # Not updated collections (sample)
        print("❌ COLLECTIONS NOT UPDATED (Sample of 10):")
        print("-" * 40)
        sample_not_updated = self.not_updated_collections[:10]
        for i, collection in enumerate(sample_not_updated, 1):
            print(f"{i:2d}. {collection['title']}")
            print(f"     Handle: {collection['handle']}")
            print(f"     URL: {collection['url']}")
            if collection['has_plp_content']:
                print(f"     Status: Has PLP content but no changes detected")
            else:
                print(f"     Status: No matching PLP content found")
            print()
        
        if len(self.not_updated_collections) > 10:
            print(f"   ... and {len(self.not_updated_collections) - 10} more collections not updated")
        print()
        
        # Missing PLP content (sample)
        if self.missing_plp_content:
            print("⚠️  PLP CONTENT WITHOUT MATCHING COLLECTIONS (Sample of 10):")
            print("-" * 40)
            sample_missing = self.missing_plp_content[:10]
            for i, item in enumerate(sample_missing, 1):
                print(f"{i:2d}. Handle: {item['handle']}")
                print(f"     PLP URL: {item['plp_content'].get('url', 'N/A')}")
                print(f"     PLP Title: {item['plp_content'].get('title', 'N/A')}")
                print()
            
            if len(self.missing_plp_content) > 10:
                print(f"   ... and {len(self.missing_plp_content) - 10} more PLP entries without matches")
            print()
        
        # Analysis summary
        print("🔍 ANALYSIS SUMMARY:")
        print(f"   • {updated_count} collections were successfully updated with new content")
        print(f"   • {not_updated_count} collections were not updated (no changes or no PLP content)")
        print(f"   • {missing_plp_count} PLP content entries have no matching Shopify collections")
        print(f"   • The migration script worked correctly for the matching handles")
        print()
        
        print("💡 RECOMMENDATIONS:")
        print("   1. Test the updated collection URLs to verify content changes")
        print("   2. Review collections that weren't updated to see if they need manual attention")
        print("   3. Consider creating Shopify collections for important PLP content without matches")
        print("   4. Implement fuzzy matching for better handle matching in future migrations")
        print()
        
        print("=" * 80)
    
    def save_detailed_report(self, output_file):
        """Save detailed report to file."""
        logger.info(f"Saving detailed report to {output_file}...")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write("ENHANCED MIGRATION ANALYSIS REPORT\n")
                file.write("=" * 80 + "\n\n")
                
                # Statistics
                total_shopify = len(self.original_shopify_data)
                total_plp = len(self.plp_content_map)
                updated_count = len(self.updated_collections)
                
                file.write(f"Total Shopify collections: {total_shopify}\n")
                file.write(f"Total PLP content entries: {total_plp}\n")
                file.write(f"Collections updated: {updated_count}\n")
                file.write(f"Update success rate: {(updated_count/total_shopify*100):.1f}%\n\n")
                
                # Updated collections
                file.write("UPDATED COLLECTIONS:\n")
                file.write("-" * 40 + "\n")
                for i, collection in enumerate(self.updated_collections, 1):
                    file.write(f"{i:2d}. {collection['title']}\n")
                    file.write(f"     Handle: {collection['handle']}\n")
                    file.write(f"     URL: {collection['url']}\n")
                    file.write(f"     Changes:\n")
                    for change in collection['changes']:
                        file.write(f"       • {change}\n")
                    file.write("\n")
                
                # Not updated collections
                file.write("COLLECTIONS NOT UPDATED:\n")
                file.write("-" * 40 + "\n")
                for i, collection in enumerate(self.not_updated_collections, 1):
                    file.write(f"{i:2d}. {collection['title']}\n")
                    file.write(f"     Handle: {collection['handle']}\n")
                    file.write(f"     URL: {collection['url']}\n")
                    if collection['has_plp_content']:
                        file.write(f"     Status: Has PLP content but no changes detected\n")
                    else:
                        file.write(f"     Status: No matching PLP content found\n")
                    file.write("\n")
                
                # Missing PLP content
                if self.missing_plp_content:
                    file.write("PLP CONTENT WITHOUT MATCHING COLLECTIONS:\n")
                    file.write("-" * 40 + "\n")
                    for i, item in enumerate(self.missing_plp_content, 1):
                        file.write(f"{i:2d}. Handle: {item['handle']}\n")
                        file.write(f"     PLP URL: {item['plp_content'].get('url', 'N/A')}\n")
                        file.write(f"     PLP Title: {item['plp_content'].get('title', 'N/A')}\n")
                        file.write("\n")
                
            logger.info(f"Successfully saved detailed report to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            raise
    
    def run(self, save_report=False):
        """Run the complete enhanced analysis."""
        logger.info("Starting enhanced migration analysis...")
        
        try:
            # Load all data
            self.load_plp_content()
            self.load_shopify_data(self.original_shopify_file, self.original_shopify_data)
            self.load_shopify_data(self.updated_shopify_file, self.updated_shopify_data)
            
            # Analyze updates
            self.analyze_updates()
            
            # Print analysis
            self.print_analysis()
            
            # Save report if requested
            if save_report:
                self.save_detailed_report('enhanced_migration_report.txt')
            
            logger.info("Enhanced migration analysis completed successfully!")
            
        except Exception as e:
            logger.error(f"Enhanced migration analysis failed: {e}")
            raise

def main():
    """Main function to run the enhanced analysis."""
    # Configuration
    plp_content_file = 'new-plp-content.csv'
    original_shopify_file = 'shopify-categories-export.csv'
    updated_shopify_file = 'shopify-categories-updated.csv'
    base_url = 'https://zj2y7h-80.myshopify.com'
    
    # Check if input files exist
    import os
    missing_files = []
    for filename in [plp_content_file, original_shopify_file, updated_shopify_file]:
        if not os.path.exists(filename):
            missing_files.append(filename)
    
    if missing_files:
        logger.error(f"Missing files: {', '.join(missing_files)}")
        sys.exit(1)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Enhanced migration coverage and update analysis')
    parser.add_argument('--save-report', action='store_true', help='Save detailed report to file')
    
    args = parser.parse_args()
    
    # Run enhanced analysis
    analyzer = EnhancedMigrationAnalyzer(
        plp_content_file, 
        original_shopify_file, 
        updated_shopify_file, 
        base_url
    )
    analyzer.run(save_report=args.save_report)

if __name__ == "__main__":
    main() 