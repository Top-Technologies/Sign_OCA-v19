from odoo import models, fields


class DmsFile(models.Model):
    _inherit = 'dms.file'

    share_link_ids = fields.One2many(
        'dms.share.link',
        'file_id',
        string="Share Links"
    )
    share_link_count = fields.Integer(
        string="Share Link Count",
        compute="_compute_share_link_count"
    )

    def _compute_share_link_count(self):
        for record in self:
            record.share_link_count = len(record.share_link_ids)

    def action_create_share_link(self):
        """Open wizard to create a new share link."""
        self.ensure_one()
        return {
            'name': 'Create Share Link',
            'type': 'ir.actions.act_window',
            'res_model': 'dms.share.link.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_file_id': self.id},
        }

    def action_view_share_links(self):
        """View all share links for this file."""
        self.ensure_one()
        return {
            'name': 'Share Links',
            'type': 'ir.actions.act_window',
            'res_model': 'dms.share.link',
            'view_mode': 'list,form',
            'domain': [('file_id', '=', self.id)],
            'context': {'default_file_id': self.id},
        }
