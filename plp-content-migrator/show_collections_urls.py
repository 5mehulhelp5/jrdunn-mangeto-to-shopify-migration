#!/usr/bin/env python3
"""
Show Collections URLs Script

This script reads the migration results and displays the Shopify collection URLs
for all migrated collections.
"""

import csv
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CollectionsURLGenerator:
    def __init__(self, csv_file, base_url):
        self.csv_file = csv_file
        self.base_url = base_url.rstrip('/')  # Remove trailing slash
        self.collections = []
        self.unique_collections = []
        
    def clean_field_name(self, field_name):
        """Clean field name by removing quotes, BOM, and extra whitespace."""
        if not field_name:
            return ""
        cleaned = field_name.replace('\ufeff', '').strip().strip('"').strip("'")
        return cleaned
    
    def load_collections(self):
        """Load collection handles from the CSV file."""
        logger.info(f"Loading collections from {self.csv_file}...")
        
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                # Clean up field names
                fieldnames = [self.clean_field_name(field) for field in reader.fieldnames]
                logger.info(f"CSV field names: {fieldnames[:5]}...")
                
                collections = []
                seen_handles = set()
                
                for row in reader:
                    # Clean up the row data
                    cleaned_row = {}
                    for key, value in row.items():
                        clean_key = self.clean_field_name(key)
                        cleaned_row[clean_key] = value.strip() if value else ""
                    
                    handle = cleaned_row.get('Handle', '')
                    title = cleaned_row.get('Title', '')
                    
                    if handle and handle != 'Handle':  # Skip header row
                        collections.append({
                            'handle': handle,
                            'title': title,
                            'url': f"{self.base_url}/collections/{handle}"
                        })
                        
                        # Track unique handles
                        if handle not in seen_handles:
                            seen_handles.add(handle)
                            self.unique_collections.append({
                                'handle': handle,
                                'title': title,
                                'url': f"{self.base_url}/collections/{handle}"
                            })
                
                self.collections = collections
                logger.info(f"Loaded {len(self.collections)} total entries")
                logger.info(f"Found {len(self.unique_collections)} unique collections")
                
        except Exception as e:
            logger.error(f"Error loading collections: {e}")
            raise
    
    def print_collections_urls(self, limit=None, unique_only=True):
        """Print all collection URLs."""
        collections_to_show = self.unique_collections if unique_only else self.collections
        collections_to_show = collections_to_show[:limit] if limit else collections_to_show
        
        print("=" * 80)
        print("SHOPIFY COLLECTIONS URLs")
        print("=" * 80)
        print(f"Base URL: {self.base_url}")
        print(f"Total Entries: {len(self.collections)}")
        print(f"Unique Collections: {len(self.unique_collections)}")
        print(f"Showing: {len(collections_to_show)} collections")
        print("=" * 80)
        print()
        
        for i, collection in enumerate(collections_to_show, 1):
            print(f"{i:3d}. {collection['title'] or collection['handle']}")
            print(f"     Handle: {collection['handle']}")
            print(f"     URL: {collection['url']}")
            print()
        
        if limit and len(collections_to_show) > limit:
            remaining = len(self.unique_collections) - limit if unique_only else len(self.collections) - limit
            print(f"... and {remaining} more collections")
            print()
    
    def save_urls_to_file(self, output_file, unique_only=True):
        """Save collection URLs to a text file."""
        collections_to_save = self.unique_collections if unique_only else self.collections
        
        logger.info(f"Saving {len(collections_to_save)} URLs to {output_file}...")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(f"Shopify Collections URLs\n")
                file.write(f"Base URL: {self.base_url}\n")
                file.write(f"Generated from: {self.csv_file}\n")
                file.write(f"Total Entries: {len(self.collections)}\n")
                file.write(f"Unique Collections: {len(self.unique_collections)}\n")
                file.write("=" * 80 + "\n\n")
                
                for i, collection in enumerate(collections_to_save, 1):
                    file.write(f"{i:3d}. {collection['title'] or collection['handle']}\n")
                    file.write(f"     Handle: {collection['handle']}\n")
                    file.write(f"     URL: {collection['url']}\n\n")
            
            logger.info(f"Successfully saved {len(collections_to_save)} URLs to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving URLs: {e}")
            raise
    
    def generate_sample_urls(self, count=10):
        """Generate sample URLs for testing."""
        print("=" * 80)
        print("SAMPLE COLLECTION URLs (for testing)")
        print("=" * 80)
        print()
        
        sample_collections = self.unique_collections[:count]
        
        for i, collection in enumerate(sample_collections, 1):
            print(f"{i}. {collection['url']}")
        
        print()
        print("=" * 80)
    
    def run(self, limit=None, save_to_file=None, show_samples=False, unique_only=True):
        """Run the complete URL generation process."""
        logger.info("Starting collections URL generation...")
        
        try:
            # Load collections
            self.load_collections()
            
            # Print URLs
            self.print_collections_urls(limit, unique_only)
            
            # Save to file if requested
            if save_to_file:
                self.save_urls_to_file(save_to_file, unique_only)
            
            # Show sample URLs if requested
            if show_samples:
                self.generate_sample_urls()
            
            logger.info("URL generation completed successfully!")
            
        except Exception as e:
            logger.error(f"URL generation failed: {e}")
            raise

def main():
    """Main function to run the URL generation script."""
    # Configuration
    csv_file = 'shopify-categories-updated.csv'
    base_url = 'https://zj2y7h-80.myshopify.com'
    output_file = 'collections_urls.txt'
    
    # Check if input file exists
    import os
    if not os.path.exists(csv_file):
        logger.error(f"CSV file not found: {csv_file}")
        sys.exit(1)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Generate Shopify collection URLs from migration results')
    parser.add_argument('--limit', type=int, help='Limit number of URLs to display')
    parser.add_argument('--save', action='store_true', help='Save URLs to file')
    parser.add_argument('--samples', action='store_true', help='Show sample URLs for testing')
    parser.add_argument('--output', default=output_file, help='Output file name')
    parser.add_argument('--all', action='store_true', help='Show all entries (including duplicates)')
    
    args = parser.parse_args()
    
    # Run URL generation
    generator = CollectionsURLGenerator(csv_file, base_url)
    generator.run(
        limit=args.limit,
        save_to_file=args.output if args.save else None,
        show_samples=args.samples,
        unique_only=not args.all
    )

if __name__ == "__main__":
    main() 