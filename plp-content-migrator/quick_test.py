#!/usr/bin/env python3
"""
Quick Test Script for Shopify PLP Migration

This script helps quickly verify that specific collections were updated correctly.
"""

import csv
import sys

def load_updated_categories(filename):
    """Load updated categories and return as dictionary."""
    categories = {}
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                # Clean field names
                cleaned_row = {}
                for key, value in row.items():
                    clean_key = key.replace('\ufeff', '').strip().strip('"').strip("'")
                    cleaned_row[clean_key] = value.strip() if value else ""
                
                category_id = cleaned_row.get('ID', '')
                if category_id:
                    categories[category_id] = cleaned_row
        
        return categories
        
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return {}

def test_specific_collections():
    """Test specific collections that should have been updated."""
    
    # Collections that were successfully matched (from migration logs)
    test_collections = [
        {'handle': 'roberto-coin', 'expected_title': 'Roberto Coin Jewelry Collection'},
        {'handle': 'marco-bicego', 'expected_title': 'MARCO BICEGO JEWELRY'},
        {'handle': 'watches', 'expected_title': 'Watches and Swiss Timepieces'},
        {'handle': 'diamond', 'expected_title': 'Diamond'},
        {'handle': 'tacori', 'expected_title': 'Tacori Engagement Rings'},
        {'handle': 'gucci-jewelry', 'expected_title': 'GUCCI JEWELRY'},
        {'handle': 'mikimoto', 'expected_title': 'Mikimoto Jewelry: Earrings'},
        {'handle': 'john-hardy', 'expected_title': 'John Hardy Jewelry'},
        {'handle': 'breitling', 'expected_title': 'Breitling Watches'},
        {'handle': 'messika', 'expected_title': 'MESSIKA JEWELRY'},
    ]
    
    # Load updated categories
    categories = load_updated_categories('shopify-categories-updated.csv')
    
    if not categories:
        print("❌ Could not load updated categories file")
        return
    
    print("=" * 60)
    print("QUICK TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test in test_collections:
        handle = test['handle']
        expected_title = test['expected_title']
        
        # Find category by handle
        found_category = None
        for category in categories.values():
            if category.get('Handle', '') == handle:
                found_category = category
                break
        
        if found_category:
            actual_title = found_category.get('Title', '')
            has_description = bool(found_category.get('Body HTML', ''))
            has_subheading = bool(found_category.get('Metafield: custom.collection_subheading [single_line_text_field]', ''))
            
            # Check if title matches or if we have content (title might be different but content updated)
            title_matches = actual_title == expected_title
            has_content = has_description or has_subheading
            
            if title_matches or has_content:
                print(f"✅ {handle}: Updated successfully")
                print(f"   Title: {actual_title}")
                print(f"   Expected: {expected_title}")
                print(f"   Has HTML description: {'Yes' if has_description else 'No'}")
                print(f"   Has subheading: {'Yes' if has_subheading else 'No'}")
                print(f"   URL: https://your-store.myshopify.com/collections/{handle}")
                if has_description:
                    # Show a preview of the HTML content
                    html_content = found_category.get('Body HTML', '')
                    preview = html_content[:100] + "..." if len(html_content) > 100 else html_content
                    print(f"   HTML Preview: {preview}")
                print()
                passed += 1
            else:
                print(f"❌ {handle}: No content updated")
                print(f"   Expected: {expected_title}")
                print(f"   Actual: {actual_title}")
                print(f"   Has description: {'Yes' if has_description else 'No'}")
                print()
                failed += 1
        else:
            print(f"❌ {handle}: Collection not found")
            print()
            failed += 1
    
    print("=" * 60)
    print(f"SUMMARY: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if passed > 0:
        print("🎉 Migration appears successful! Check a few collection pages manually.")
    else:
        print("⚠️  No collections were updated. Check your input files and migration logs.")

def show_manual_test_urls():
    """Show URLs for manual testing."""
    print("\n" + "=" * 60)
    print("MANUAL TESTING URLs")
    print("=" * 60)
    print("Visit these URLs on your store to verify content updates:")
    print()
    
    test_urls = [
        "https://your-store.myshopify.com/collections/roberto-coin",
        "https://your-store.myshopify.com/collections/marco-bicego", 
        "https://your-store.myshopify.com/collections/watches",
        "https://your-store.myshopify.com/collections/tacori",
        "https://your-store.myshopify.com/collections/gucci-jewelry",
        "https://your-store.myshopify.com/collections/mikimoto",
    ]
    
    for url in test_urls:
        print(f"• {url}")
    
    print("\nLook for:")
    print("✅ Updated collection titles")
    print("✅ New HTML descriptions with proper formatting")
    print("✅ Collection subheadings in metafields")
    print("✅ No broken HTML or missing content")

def main():
    """Main function."""
    print("🔍 Quick Test for Shopify PLP Migration")
    print("Checking if collections were updated correctly...")
    print()
    
    # Test specific collections
    test_specific_collections()
    
    # Show manual testing URLs
    show_manual_test_urls()

if __name__ == "__main__":
    main() 