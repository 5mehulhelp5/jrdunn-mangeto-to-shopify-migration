#!/usr/bin/env python3
"""
Show Updated Collections URLs Script

This script shows only the collections that were actually updated with new content
by comparing the original and updated CSV files.
"""

import csv
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UpdatedCollectionsURLGenerator:
    def __init__(self, original_csv, updated_csv, base_url):
        self.original_csv = original_csv
        self.updated_csv = updated_csv
        self.base_url = base_url.rstrip('/')
        self.updated_collections = []
        
    def clean_field_name(self, field_name):
        """Clean field name by removing quotes, BOM, and extra whitespace."""
        if not field_name:
            return ""
        cleaned = field_name.replace('\ufeff', '').strip().strip('"').strip("'")
        return cleaned
    
    def load_csv_data(self, filename):
        """Load CSV data and return as dictionary with handle as key."""
        data = {}
        
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
                        data[handle] = cleaned_row
                
                logger.info(f"Loaded {len(data)} entries from {filename}")
                return data
                
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            return {}
    
    def find_updated_collections(self):
        """Find collections that were actually updated."""
        logger.info("Loading original and updated CSV files...")
        
        original_data = self.load_csv_data(self.original_csv)
        updated_data = self.load_csv_data(self.updated_csv)
        
        logger.info("Comparing collections to find updates...")
        
        updated_collections = []
        
        for handle, updated_row in updated_data.items():
            original_row = original_data.get(handle)
            
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
            
            # If any fields were updated, add to list
            if updated_fields:
                updated_collections.append({
                    'handle': handle,
                    'title': updated_title or handle,
                    'url': f"{self.base_url}/collections/{handle}",
                    'changes': updated_fields
                })
        
        self.updated_collections = updated_collections
        logger.info(f"Found {len(updated_collections)} collections with updates")
    
    def print_updated_collections(self, limit=None):
        """Print updated collections with their changes."""
        collections_to_show = self.updated_collections[:limit] if limit else self.updated_collections
        
        print("=" * 80)
        print("UPDATED SHOPIFY COLLECTIONS")
        print("=" * 80)
        print(f"Base URL: {self.base_url}")
        print(f"Total Updated Collections: {len(self.updated_collections)}")
        print(f"Showing: {len(collections_to_show)} collections")
        print("=" * 80)
        print()
        
        for i, collection in enumerate(collections_to_show, 1):
            print(f"{i:3d}. {collection['title']}")
            print(f"     Handle: {collection['handle']}")
            print(f"     URL: {collection['url']}")
            print(f"     Changes:")
            for change in collection['changes']:
                print(f"       • {change}")
            print()
        
        if limit and len(self.updated_collections) > limit:
            print(f"... and {len(self.updated_collections) - limit} more updated collections")
            print()
    
    def save_updated_urls_to_file(self, output_file):
        """Save updated collection URLs to a text file."""
        logger.info(f"Saving {len(self.updated_collections)} updated URLs to {output_file}...")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(f"Updated Shopify Collections URLs\n")
                file.write(f"Base URL: {self.base_url}\n")
                file.write(f"Generated from: {self.original_csv} vs {self.updated_csv}\n")
                file.write(f"Total Updated Collections: {len(self.updated_collections)}\n")
                file.write("=" * 80 + "\n\n")
                
                for i, collection in enumerate(self.updated_collections, 1):
                    file.write(f"{i:3d}. {collection['title']}\n")
                    file.write(f"     Handle: {collection['handle']}\n")
                    file.write(f"     URL: {collection['url']}\n")
                    file.write(f"     Changes:\n")
                    for change in collection['changes']:
                        file.write(f"       • {change}\n")
                    file.write("\n")
            
            logger.info(f"Successfully saved {len(self.updated_collections)} updated URLs to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving URLs: {e}")
            raise
    
    def generate_sample_urls(self, count=10):
        """Generate sample URLs for testing."""
        print("=" * 80)
        print("SAMPLE UPDATED COLLECTION URLs (for testing)")
        print("=" * 80)
        print()
        
        sample_collections = self.updated_collections[:count]
        
        for i, collection in enumerate(sample_collections, 1):
            print(f"{i}. {collection['url']}")
        
        print()
        print("=" * 80)
    
    def run(self, limit=None, save_to_file=None, show_samples=False):
        """Run the complete updated collections URL generation process."""
        logger.info("Starting updated collections URL generation...")
        
        try:
            # Find updated collections
            self.find_updated_collections()
            
            # Print updated collections
            self.print_updated_collections(limit)
            
            # Save to file if requested
            if save_to_file:
                self.save_updated_urls_to_file(save_to_file)
            
            # Show sample URLs if requested
            if show_samples:
                self.generate_sample_urls()
            
            logger.info("Updated collections URL generation completed successfully!")
            
        except Exception as e:
            logger.error(f"Updated collections URL generation failed: {e}")
            raise

def main():
    """Main function to run the updated collections URL generation script."""
    # Configuration
    original_csv = 'shopify-categories-export.csv'
    updated_csv = 'shopify-categories-updated.csv'
    base_url = 'https://zj2y7h-80.myshopify.com'
    output_file = 'updated_collections_urls.txt'
    
    # Check if input files exist
    import os
    missing_files = []
    for filename in [original_csv, updated_csv]:
        if not os.path.exists(filename):
            missing_files.append(filename)
    
    if missing_files:
        logger.error(f"Missing files: {', '.join(missing_files)}")
        sys.exit(1)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Generate URLs for collections that were actually updated')
    parser.add_argument('--limit', type=int, help='Limit number of URLs to display')
    parser.add_argument('--save', action='store_true', help='Save URLs to file')
    parser.add_argument('--samples', action='store_true', help='Show sample URLs for testing')
    parser.add_argument('--output', default=output_file, help='Output file name')
    
    args = parser.parse_args()
    
    # Run updated collections URL generation
    generator = UpdatedCollectionsURLGenerator(original_csv, updated_csv, base_url)
    generator.run(
        limit=args.limit,
        save_to_file=args.output if args.save else None,
        show_samples=args.samples
    )

if __name__ == "__main__":
    main() 