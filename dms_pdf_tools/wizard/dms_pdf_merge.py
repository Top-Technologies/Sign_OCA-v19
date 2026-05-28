from odoo import models, fields, api, _
from odoo.exceptions import UserError
import io
import base64
try:
    import pypdf
except ImportError:
    pypdf = None

class DmsPdfMerge(models.TransientModel):
    _name = 'dms.pdf.merge'
    _description = 'DMS PDF Merge Wizard'

    file_ids = fields.Many2many('dms.file', string="Files to Merge")
    new_filename = fields.Char(string="New Filename", default="merged_document.pdf", required=True)

    @api.model
    def default_get(self, fields):
        res = super(DmsPdfMerge, self).default_get(fields)
        active_ids = self.env.context.get('active_ids')
        if active_ids and self.env.context.get('active_model') == 'dms.file':
            res['file_ids'] = [(6, 0, active_ids)]
        return res

    def action_merge(self):
        self.ensure_one()
        if not pypdf:
            raise UserError(_("Please install the 'pypdf' python library."))
        
        if not self.file_ids:
             raise UserError(_("No files selected to merge."))

        writer = pypdf.PdfWriter()

        # Sort files by name or keep selection order? 
        # Many2many doesn't strictly preserve order, usually ID order.
        # User might want specific order. For simple version, just ID order.
        # Or better, sort by name.
        sorted_files = self.file_ids.sorted('name')

        for file_record in sorted_files:
            if not file_record.content:
                continue # Skip empty files
            
            try:
                file_stream = io.BytesIO(base64.b64decode(file_record.content))
                reader = pypdf.PdfReader(file_stream)
                for page in reader.pages:
                    writer.add_page(page)
            except Exception as e:
                raise UserError(_("Error reading file %s: %s", file_record.name, str(e)))

        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_content = base64.b64encode(output_stream.getvalue())

        # Determine parent directory from first file
        first_file = sorted_files[0]
        directory_id = first_file.directory_id if first_file else False
        
        if not directory_id:
             raise UserError(_("Could not determine directory."))

        self.env['dms.file'].create({
            'name': self.new_filename,
            'directory_id': directory_id.id,
            'content': output_content,
            'mimetype': 'application/pdf',
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Success"),
                'message': _("Files merged successfully."),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
