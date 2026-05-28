{
    'name': 'DMS PDF Tools',
    'version': '19.0.1.0.0',
    'category': 'Document Management',
    'summary': 'Split and Merge PDFs in DMS',
    'description': """
        This module adds tools to Split and Merge PDF files in the OCA DMS.
        Requires 'pypdf' python library.
    """,
    'author': 'Top-Tech',
    'depends': ['dms'],
    'external_dependencies': {'python': ['pypdf']},
    'data': [
        'security/ir.model.access.csv',
        'wizard/dms_pdf_split_views.xml',
        'wizard/dms_pdf_merge_views.xml',
        'views/dms_file_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
