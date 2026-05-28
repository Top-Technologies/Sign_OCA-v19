from odoo import models, fields, api


class DmsShareLinkWizard(models.TransientModel):
    _name = 'dms.share.link.wizard'
    _description = 'Create Share Link Wizard'

    file_id = fields.Many2one('dms.file', string="File", required=True)
    expiration_date = fields.Date(string="Expiration Date")
    access_type = fields.Selection(
        [('internal', 'Internal Users'), ('public', 'Anyone with the link')],
        string="Access Type",
        default='public',
        required=True
    )
    permission = fields.Selection(
        [('none', 'None'), ('read', 'View'), ('write', 'Edit')],
        string="Permission",
        default='read',
        required=True
    )
    recipient_email = fields.Char(string="Recipient Email (optional)")
    share_link = fields.Many2one('dms.share.link', string="Generated Link", readonly=True)
    share_url = fields.Char(string="Share URL", related='share_link.share_url', readonly=True)

    def action_create_link(self):
        """Create a new share link."""
        self.ensure_one()
        share_link = self.env['dms.share.link'].create({
            'file_id': self.file_id.id,
            'expiration_date': self.expiration_date,
            'access_type': self.access_type,
            'permission': self.permission,
            'recipient_email': self.recipient_email,
        })
        self.share_link = share_link.id
        # Reopen wizard to show the generated link
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'dms.share.link.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
