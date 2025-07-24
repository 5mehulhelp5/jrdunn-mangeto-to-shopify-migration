# JR Dunn Magento to Shopify Migration

A comprehensive migration toolkit for transferring data from jrdunn.com (Magento) to Shopify. Each folder contains scripts for a specific migration scope, with Matrixify app handling the final import/export process.

## 📋 Migration Scopes

Each folder contains specialized scripts for different data types:

- **`plp-content-migrator/`** - Shopify Collections content (not products)
- **`product-migrator/`** - Product catalog and inventory data
- **`customer-migrator/`** - Customer accounts and order history
- **`content-migrator/`** - Static pages and CMS content
- **`media-migrator/`** - Images, videos, and downloadable files

## 🚀 Workflow

### 1. Export Data from Matrixify
Export data from Shopify via Matrixify app

### 2. Process with Migration Scripts
Each script transforms data into Shopify-compatible format:
- **PLP Content** → Shopify Collections (titles, descriptions, metafields)
- **Products** → Shopify Products (inventory, pricing, variants)
- **Customers** → Shopify Customers (accounts, addresses)
- **Content** → Shopify Pages (CMS content, static blocks)

### 3. Import via Matrixify App
1. **Export** processed CSV files
2. **Upload** to Matrixify app in Shopify
3. **Monitor** import status:
   - 🟢 **Green** = Success
   - 🔴 **Red** = Failed (fix script and retry)

## 🛡️ Matrixify Status

| Status | Action |
|--------|--------|
| 🟢 **Green** | Success - no action needed |
| 🔴 **Red** | Failed - fix script and retry |
| 🟡 **Yellow** | Warnings - review and decide |

## 📖 Documentation

- [Collections Migration](./plp-content-migrator/README.md) - Shopify Collections
- [Product Migration](./product-migrator/README.md) - Product catalog
- [Customer Migration](./customer-migrator/README.md) - Customer data
- [Content Migration](./content-migrator/README.md) - Static pages
