{
    'name': 'DMS Share Expiration',
    'version': '19.0.2.0.0',
    'category': 'Document Management',
    'summary': 'Create share links with individual expiration dates',
    'description': """
        This module extends OCA DMS with per-recipient share links.
        
        Features:
        - Create multiple share links per file
        - Each link has its own unique token
        - Set individual expiration dates per link
        - Track who you shared with (optional recipient email)
        - Links automatically become invalid after expiration
    """,
    'author': 'Top-Tech',
    'depends': ['dms'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/dms_share_wizard_views.xml',
        'views/dms_file_views.xml',
        'views/dms_share_templates.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
