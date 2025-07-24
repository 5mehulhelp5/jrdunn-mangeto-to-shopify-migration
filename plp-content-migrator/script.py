#!/usr/bin/env python3
"""
Magento to Shopify PLP Content Migration Script

This script migrates Product Listing Page (PLP) content from Magento to Shopify
by matching URLs from the PLP content file to Shopify categories and updating
the category metadata with new content.
"""

import csv
import re
import sys
from urllib.parse import urlparse
import logging
import html

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PLPMigrationScript:
    def __init__(self, plp_content_file, shopify_categories_file, output_file):
        self.plp_content_file = plp_content_file
        self.shopify_categories_file = shopify_categories_file
        self.output_file = output_file
        
        # Store the content mappings
        self.plp_content = []
        self.shopify_categories = []
        self.updated_categories = []
        self.content_map = {}  # Map handle to content data
        
        # Statistics
        self.stats = {
            'plp_entries_loaded': 0,
            'shopify_categories_loaded': 0,
            'categories_updated': 0,
            'no_match_found': 0
        }

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

    def clean_field_name(self, field_name):
        """Clean field name by removing quotes, BOM, and extra whitespace."""
        if not field_name:
            return ""
        # Remove BOM, quotes, and whitespace
        cleaned = field_name.replace('\ufeff', '').strip().strip('"').strip("'")
        return cleaned

    def create_html_content(self, title, subheading, description, content_under_listing):
        """Create properly formatted HTML content for the Body HTML field."""
        html_parts = ['<div class="collection-description">']
        
        if title:
            html_parts.append(f'<h1>{html.escape(title)}</h1>')
        
        if subheading:
            html_parts.append(f'<h2>{html.escape(subheading)}</h2>')
        
        if description:
            html_parts.append(f'<p>{html.escape(description)}</p>')
        
        if content_under_listing:
            html_parts.append(f'<div class="content-under-listing">{html.escape(content_under_listing)}</div>')
        
        html_parts.append('</div>')
        return ''.join(html_parts)

    def load_plp_content(self):
        """Load the new PLP content from CSV file and create handle mapping."""
        logger.info("Loading PLP content from CSV...")
        
        try:
            with open(self.plp_content_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                # Clean up field names
                fieldnames = [self.clean_field_name(field) for field in reader.fieldnames]
                logger.info(f"PLP CSV field names: {fieldnames}")
                
                plp_entries = []
                for row in reader:
                    # Clean up the data and field names
                    cleaned_row = {}
                    for key, value in row.items():
                        # Clean the key
                        clean_key = self.clean_field_name(key)
                        cleaned_row[clean_key] = value.strip() if value else ""
                    
                    plp_entries.append(cleaned_row)
                    
                    # Extract handle and create mapping
                    url = cleaned_row.get('URL', '')
                    handle = self.extract_handle_from_url(url)
                    
                    if handle:
                        self.content_map[handle] = {
                            'title': cleaned_row.get('Title', ''),
                            'subheading': cleaned_row.get('Sub-heading', ''),
                            'description': cleaned_row.get('Description', ''),
                            'content_under_listing': cleaned_row.get('Content under product listing', '')
                        }
                        logger.info(f"Mapped handle: '{handle}' -> Title: '{cleaned_row.get('Title', '')}'")
                
                self.plp_content = plp_entries
                self.stats['plp_entries_loaded'] = len(self.plp_content)
                logger.info(f"Loaded {len(self.plp_content)} PLP content entries")
                logger.info(f"Created content map with {len(self.content_map)} entries")
                
        except Exception as e:
            logger.error(f"Error loading PLP content: {e}")
            raise

    def load_shopify_categories(self):
        """Load Shopify categories from CSV file."""
        logger.info("Loading Shopify categories from CSV...")
        
        try:
            with open(self.shopify_categories_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                # Clean up field names
                fieldnames = [self.clean_field_name(field) for field in reader.fieldnames]
                logger.info(f"Shopify CSV field names: {fieldnames[:5]}...")  # Debug
                
                categories = []
                for row in reader:
                    # Clean up the row data and field names
                    cleaned_row = {}
                    for key, value in row.items():
                        # Clean the key
                        clean_key = self.clean_field_name(key)
                        cleaned_row[clean_key] = value.strip() if value else ""
                    categories.append(cleaned_row)
                
                self.shopify_categories = categories
                self.stats['shopify_categories_loaded'] = len(self.shopify_categories)
                logger.info(f"Loaded {len(self.shopify_categories)} Shopify categories")
                
                # Debug: Check first category keys
                if categories:
                    logger.info(f"First category keys: {list(categories[0].keys())[:5]}")
                
        except Exception as e:
            logger.error(f"Error loading Shopify categories: {e}")
            raise

    def update_shopify_categories(self):
        """Update Shopify categories with new PLP content using direct handle mapping."""
        logger.info("Updating Shopify categories with PLP content...")
        
        # Create a copy of shopify categories
        self.updated_categories = [dict(category) for category in self.shopify_categories]
        
        updated_count = 0
        no_match_count = 0
        
        # Process each category
        for i, category in enumerate(self.updated_categories):
            if i == 0:  # Skip header if it exists
                continue
                
            handle = category.get('Handle', '')
            
            if handle in self.content_map:
                content = self.content_map[handle]
                
                logger.info(f"Updating handle: '{handle}'")
                
                # Update Title (column 3 in CSV, 0-indexed)
                if content['title']:
                    category['Title'] = content['title']
                
                # Update Body HTML (column 4) with formatted description
                if content['description']:
                    body_html = self.create_html_content(
                        content['title'],
                        content['subheading'], 
                        content['description'],
                        content['content_under_listing']
                    )
                    category['Body HTML'] = body_html
                
                # Update collection subheading metafield (column 25)
                if content['subheading']:
                    category['Metafield: custom.collection_subheading [single_line_text_field]'] = content['subheading']
                
                updated_count += 1
            else:
                no_match_count += 1
        
        self.stats['categories_updated'] = updated_count
        self.stats['no_match_found'] = no_match_count
        
        logger.info(f"Updated {updated_count} categories with new content")
        logger.info(f"No match found for {no_match_count} categories")

    def save_updated_categories(self):
        """Save the updated Shopify categories to output file."""
        logger.info(f"Saving updated categories to {self.output_file}...")
        
        try:
            if not self.updated_categories:
                logger.error("No categories to save")
                return
            
            fieldnames = self.updated_categories[0].keys()
            
            with open(self.output_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.updated_categories)
            
            logger.info(f"Successfully saved {len(self.updated_categories)} updated categories")
            
        except Exception as e:
            logger.error(f"Error saving updated categories: {e}")
            raise

    def print_statistics(self):
        """Print detailed statistics about the migration."""
        logger.info("=" * 50)
        logger.info("MIGRATION STATISTICS")
        logger.info("=" * 50)
        logger.info(f"PLP entries loaded: {self.stats['plp_entries_loaded']}")
        logger.info(f"Shopify categories loaded: {self.stats['shopify_categories_loaded']}")
        logger.info(f"Categories updated: {self.stats['categories_updated']}")
        logger.info(f"No match found: {self.stats['no_match_found']}")
        if self.stats['plp_entries_loaded'] > 0:
            match_rate = (self.stats['categories_updated'] / len(self.content_map) * 100)
            logger.info(f"Match rate: {match_rate:.1f}%")
        logger.info("=" * 50)

    def run(self):
        """Run the complete migration process."""
        logger.info("Starting PLP content migration from Magento to Shopify...")
        
        try:
            # Load data
            self.load_plp_content()
            self.load_shopify_categories()
            
            # Process and update
            self.update_shopify_categories()
            
            # Print statistics
            self.print_statistics()
            
            # Save results
            self.save_updated_categories()
            
            logger.info("Migration completed successfully!")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise

def main():
    """Main function to run the migration script."""
    # File paths
    plp_content_file = 'new-plp-content.csv'
    shopify_categories_file = 'shopify-categories-export.csv'
    output_file = 'shopify-categories-updated.csv'
    
    # Check if input files exist
    import os
    if not os.path.exists(plp_content_file):
        logger.error(f"PLP content file not found: {plp_content_file}")
        sys.exit(1)
    
    if not os.path.exists(shopify_categories_file):
        logger.error(f"Shopify categories file not found: {shopify_categories_file}")
        sys.exit(1)
    
    # Run migration
    migration = PLPMigrationScript(plp_content_file, shopify_categories_file, output_file)
    migration.run()

if __name__ == "__main__":
    main()
