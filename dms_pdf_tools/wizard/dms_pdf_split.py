from odoo import models, fields, api, _
from odoo.exceptions import UserError
import io
import base64
try:
    import pypdf
except ImportError:
    pypdf = None

class DmsPdfSplit(models.TransientModel):
    _name = 'dms.pdf.split'
    _description = 'DMS PDF Split Wizard'

    file_id = fields.Many2one('dms.file', string="File", required=True)
    mode = fields.Selection([
        ('all', 'Split all pages'),
        ('range', 'Extract Pages'),
    ], string="Mode", default='all', required=True)
    page_range = fields.Char(string="Page Range", help="e.g. 1-3, 5, 8-10")

    def _parse_range(self, range_str, max_pages):
        pages = set()
        parts = range_str.split(',')
        for part in parts:
            part = part.strip()
            if '-' in part:
                try:
                    start, end = map(int, part.split('-'))
                    # User input is 1-based, internal is 0-based
                    # Range is inclusive for user: 1-3 means 1, 2, 3
                    if start < 1 or end > max_pages:
                         raise UserError(_("Invalid page range: %s. Max pages: %s", part, max_pages))
                    for i in range(start - 1, end):
                        pages.add(i)
                except ValueError:
                    raise UserError(_("Invalid format in range: %s", part))
            else:
                try:
                    page = int(part)
                    if page < 1 or page > max_pages:
                        raise UserError(_("Invalid page number: %s. Max pages: %s", page, max_pages))
                    pages.add(page - 1)
                except ValueError:
                     raise UserError(_("Invalid format in range: %s", part))
        return sorted(list(pages))

    def action_split(self):
        self.ensure_one()
        if not pypdf:
            raise UserError(_("Please install the 'pypdf' python library."))

        if not self.file_id.content:
            raise UserError(_("The selected file has no content."))

        try:
            # content is base64 string
            file_stream = io.BytesIO(base64.b64decode(self.file_id.content))
            reader = pypdf.PdfReader(file_stream)
            total_pages = len(reader.pages)
            
            parent_directory = self.file_id.directory_id
            base_name = self.file_id.name.rsplit('.', 1)[0]
            
            created_files = self.env['dms.file']

            if self.mode == 'all':
                for i, page in enumerate(reader.pages):
                    writer = pypdf.PdfWriter()
                    writer.add_page(page)
                    
                    output_stream = io.BytesIO()
                    writer.write(output_stream)
                    output_content = base64.b64encode(output_stream.getvalue())

                    new_filename = f"{base_name}_page_{i+1}.pdf"
                    
                    new_file = self.env['dms.file'].create({
                        'name': new_filename,
                        'directory_id': parent_directory.id,
                        'content': output_content,
                        'mimetype': 'application/pdf',
                    })
                    created_files += new_file
            
            elif self.mode == 'range':
                if not self.page_range:
                    raise UserError(_("Please enter a page range."))
                
                selected_indices = self._parse_range(self.page_range, total_pages)
                
                if not selected_indices:
                     raise UserError(_("No pages selected."))
                
                writer = pypdf.PdfWriter()
                for idx in selected_indices:
                    writer.add_page(reader.pages[idx])

                output_stream = io.BytesIO()
                writer.write(output_stream)
                output_content = base64.b64encode(output_stream.getvalue())
                
                # Filename reflects the range roughly or just generic "extracted"
                # If complex range, maybe just "extracted"
                safe_range = self.page_range.replace(',', '_').replace(' ', '')
                new_filename = f"{base_name}_pages_{safe_range}.pdf"

                new_file = self.env['dms.file'].create({
                    'name': new_filename,
                    'directory_id': parent_directory.id,
                    'content': output_content,
                    'mimetype': 'application/pdf',
                })
                created_files += new_file

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Success"),
                    'message': _("Created %s new files.", len(created_files)),
                    'type': 'success',
                    'sticky': False,
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }
            
        except Exception as e:
            raise UserError(_("Error splitting PDF: %s", str(e)))
