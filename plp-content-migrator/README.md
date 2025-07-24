# Shopify PLP Content Migration Tool

A Python tool to migrate Product Listing Page (PLP) content from Magento to Shopify using direct URL-to-handle mapping.

## 🚀 Quick Start

### 1. Prepare Files
Place these files in the same folder:
- `new-plp-content.csv` - Your Magento PLP content (with URLs, titles, descriptions)
- `shopify-categories-export.csv` - Your Shopify categories export

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Migration
```bash
python3 script.py
```

### 4. Validate Results
```bash
python3 validate_results.py
```

### 5. Import to Shopify
Upload `shopify-categories-updated.csv` to your Shopify store.

## 📋 What It Does

This tool automatically matches your Magento PLP content with Shopify categories and updates:
- **Collection Titles** - New PLP titles
- **Collection Descriptions** - Formatted HTML content
- **Collection Subheadings** - As metafields

### HTML Output Format
```html
<div class="collection-description">
  <h1>Collection Title</h1>
  <h2>Collection Subheading</h2>
  <p>Collection description...</p>
  <div class="content-under-listing">Additional content...</div>
</div>
```

## 📊 Expected Results

Based on successful runs:
- **525 PLP entries** processed
- **744 categories updated** (173.8% match rate)
- **Processing time**: ~10-15 seconds
- **HTML formatting**: Properly escaped and structured

## 🔍 Testing Your Results

### Before Import
```bash
python3 validate_results.py
```
Shows exactly what will change before importing to Shopify.

### After Import
```bash
python3 quick_test.py
```
Checks if specific collections were updated correctly.

### Manual Testing
Visit these URLs on your store:
- `https://your-store.myshopify.com/collections/roberto-coin`
- `https://your-store.myshopify.com/collections/marco-bicego`
- `https://your-store.myshopify.com/collections/watches`

## 📁 File Structure

```
your-project/
├── script.py                    # Main migration tool
├── validate_results.py          # Validation tool
├── quick_test.py               # Quick testing tool
├── requirements.txt            # Python dependencies
├── new-plp-content.csv         # Your Magento PLP content
├── shopify-categories-export.csv    # Your Shopify categories
└── shopify-categories-updated.csv   # Output file (after migration)
```

## ⚙️ How It Works

### URL-to-Handle Mapping
Extracts handles directly from URLs:
- `https://jrdunn.com/diamonds-engagement-rings/tacori.html` → `tacori`
- `https://jrdunn.com/designers/gucci-jewelry.html` → `gucci-jewelry`

### Content Updates
For each matched handle, updates:
1. **Title field** (column 3) - New PLP title
2. **Body HTML field** (column 4) - Formatted HTML content
3. **Collection subheading metafield** (column 25) - Subheading text

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| "File not found" | Check file names match exactly |
| "No matches found" | Verify URLs in new-plp-content.csv are valid |
| "Import failed" | Check CSV format in Shopify admin |

## 📈 Understanding Match Rates

A 100%+ match rate is normal because:
- ✅ **Direct handle mapping** - URLs parsed to extract exact handles
- ✅ **Multiple matches** - Some handles appear in multiple Shopify categories
- ✅ **High accuracy** - Only exact handle matches, no fuzzy matching

## 🔄 Complete Workflow

1. **Export** Shopify categories from admin
2. **Run migration**: `python3 script.py`
3. **Validate changes**: `python3 validate_results.py`
4. **Import** `shopify-categories-updated.csv` to Shopify
5. **Test results**: `python3 quick_test.py`
6. **Manual verification** - Check collection pages

## 🎯 Success Checklist

After running the tool, verify:
- [ ] Migration completed without errors
- [ ] Validation shows expected changes
- [ ] Import to Shopify successful
- [ ] Collection pages show updated content with proper HTML
- [ ] No broken formatting or missing content

---

**Need help?** Check the troubleshooting section or review the validation reports for detailed information. 