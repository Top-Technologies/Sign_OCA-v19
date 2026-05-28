# Copyright 2024 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "DMS User Role",
    "version": "19.0.1.0.0",
    "category": "Document Management",
    "website": "https://github.com/OCA/dms",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "depends": ["dms", "base_user_role"],
    "installable": True,
    "data": [
        "views/dms_access_group_views.xml",
    ],
    "maintainers": ["victoralmau"],
}
