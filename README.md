# Brand Kit Manager (Odoo 19)

`brand_kit_manager` is an Odoo 19 module for unified email branding.

## Features

- Brand kit per company (`brand.kit`): logo, primary/secondary color, header text, footer text, legal text.
- Preview wizard before applying changes.
- Safe apply flow that sets branded layout without hard-overwriting template bodies.
- Settings integration and company-level default brand kit.
- Administration-only management permissions.

## Repository Structure

- `brand_kit_manager/`: module source
- `brand_kit_manager/static/description/`: Odoo Apps listing assets
- `config/odoo.conf.example`: local configuration sample

## Odoo Apps Listing Assets

Cover images are included for Odoo Apps scan:

- `brand_kit_manager/static/description/thumbnail.png`
- `brand_kit_manager/static/description/banner.png`
- `brand_kit_manager/static/description/screenshots/brand_kit_manager_cover.png`

## Local Run

1. Ensure Odoo 19 and PostgreSQL are installed.
2. Put this repository path in `addons_path`.
3. Upgrade/install module:
   - `odoo-bin -c odoo.conf -d <db_name> -u brand_kit_manager`
4. Open Apps, update app list, and test Brand Kit flows.
