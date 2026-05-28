import uuid
from odoo import models, fields, api


class DmsShareLink(models.Model):
    _name = 'dms.share.link'
    _description = 'DMS Share Link'
    _order = 'create_date desc'

    name = fields.Char(string="Name", compute="_compute_name", store=True)
    file_id = fields.Many2one(
        'dms.file',
        string="File",
        required=True,
        ondelete='cascade',
        index=True
    )
    access_token = fields.Char(
        string="Access Token",
        required=True,
        readonly=True,
        index=True,
        default=lambda self: str(uuid.uuid4())
    )
    expiration_date = fields.Date(
        string="Expiration Date",
        help="Leave empty for no expiration"
    )
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
    recipient_email = fields.Char(string="Recipient Email")
    created_by_id = fields.Many2one(
        'res.users',
        string="Created By",
        default=lambda self: self.env.user,
        readonly=True
    )
    is_expired = fields.Boolean(
        string="Expired",
        compute="_compute_is_expired",
        store=True
    )
    share_url = fields.Char(
        string="Share URL",
        compute="_compute_share_url"
    )

    @api.depends('file_id.name', 'recipient_email')
    def _compute_name(self):
        for record in self:
            if record.recipient_email:
                record.name = f"{record.file_id.name} → {record.recipient_email}"
            else:
                record.name = f"{record.file_id.name} (Share Link)"

    @api.depends('expiration_date')
    def _compute_is_expired(self):
        today = fields.Date.today()
        for record in self:
            if record.expiration_date:
                record.is_expired = record.expiration_date < today
            else:
                record.is_expired = False

    def _compute_share_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            record.share_url = f"{base_url}/my/dms/file/{record.file_id.id}/download?access_token={record.access_token}"

    def regenerate_token(self):
        """Regenerate the access token for this share link."""
        for record in self:
            record.access_token = str(uuid.uuid4())
        return True
