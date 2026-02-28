# Odoo Custom Module Foundation

This repository now contains a starter structure for custom Odoo development.

## Project Structure

- `custom_addons/brand_kit_manager`: starter custom module
- `config/odoo.conf.example`: example Odoo config for local development

## Quick Start

1. Ensure Odoo and PostgreSQL are installed.
2. Copy `config/odoo.conf.example` to `config/odoo.conf` and adjust values.
3. Start Odoo with that config.
4. In Odoo UI, update Apps list and install `Brand Kit Manager`.

## Module Included

The `brand_kit_manager` module includes:

- A starter model: `brand.kit`
- Basic menu and action
- Tree, form, and search views
- Access rights for internal users
- A sequence for auto-generated references

