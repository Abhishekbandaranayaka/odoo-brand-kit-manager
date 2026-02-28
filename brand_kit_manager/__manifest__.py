{
    "name": "Brand Kit Manager",
    "summary": "Manage company brand kits from a dedicated module",
    "version": "1.0.0",
    "category": "Tools",
    "author": "Your Company",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/brand_kit_sequence.xml",
        "views/brand_kit_views.xml",
        "views/brand_kit_menus.xml",
    ],
    "installable": True,
    "application": True,
}

