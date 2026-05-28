import base64

import werkzeug
from odoo import fields, http
from odoo.http import request

from odoo.addons.dms.controllers.portal import CustomerPortal as DmsCustomerPortal


class CustomerPortal(DmsCustomerPortal):
    """Extend portal controller to check share link expiration."""

    def _dms_check_access(self, model, res_id, access_token=None):
        """Override to check expiration date before granting access."""
        # First check using dms.share.link
        if access_token and model == 'dms.file':
            share_link = request.env['dms.share.link'].sudo().search([
                ('access_token', '=', access_token),
                ('file_id', '=', res_id)
            ], limit=1)
            
            if share_link:
                # Check 1: Permission none
                if share_link.permission == 'none':
                    raise werkzeug.exceptions.Forbidden()
                
                # Check 2: Internal access
                if share_link.access_type == 'internal':
                    if not request.env.user.has_group('base.group_user'):
                        raise werkzeug.exceptions.Forbidden()

                # Check 3: Read permission blocking POST/PUT/DELETE
                if share_link.permission == 'read':
                    if request.httprequest.method != 'GET':
                        raise werkzeug.exceptions.Forbidden()

                # Check expiration
                if share_link.expiration_date and share_link.expiration_date < fields.Date.today():
                    return False
                # Valid share link - grant access
                return request.env[model].sudo().browse(res_id)
        
        # Fall back to default behavior
        return super()._dms_check_access(model, res_id, access_token)

    # ------------------------------------------------------------------
    #  Helpers
    # ------------------------------------------------------------------
    def _get_share_link_or_error(self, token):
        """Return a valid dms.share.link or raise an HTTP error."""
        share_link = request.env['dms.share.link'].sudo().search(
            [('access_token', '=', token)], limit=1,
        )
        if not share_link:
            raise werkzeug.exceptions.NotFound()

        # Expired?
        if (share_link.expiration_date
                and share_link.expiration_date < fields.Date.today()):
            raise werkzeug.exceptions.Gone(
                description="This share link has expired.")

        # Must have write permission to replace a file
        if share_link.permission != 'write':
            raise werkzeug.exceptions.Forbidden(
                description="You do not have permission to replace this file.")

        return share_link

    # ------------------------------------------------------------------
    #  GET  – show the upload form
    # ------------------------------------------------------------------
    @http.route(
        '/dms/share/replace/<string:token>',
        type='http', auth='public', methods=['GET'], website=True,
    )
    def dms_share_replace_form(self, token, **kw):
        """Render a public upload form to replace a shared file."""
        share_link = self._get_share_link_or_error(token)
        return request.render(
            'dms_share_expiration.file_replace_form',
            {'file': share_link.file_id, 'token': token},
        )

    # ------------------------------------------------------------------
    #  POST – handle the replacement upload
    # ------------------------------------------------------------------
    @http.route(
        '/dms/share/replace/<string:token>',
        type='http', auth='public', methods=['POST'], website=True,
        csrf=True,
    )
    def dms_share_replace_submit(self, token, **kw):
        """Process the uploaded file and replace the existing DMS file."""
        share_link = self._get_share_link_or_error(token)

        uploaded = request.httprequest.files.get('replace_file')
        if not uploaded or not uploaded.filename:
            # Re-render the form with a minimal error hint
            return request.render(
                'dms_share_expiration.file_replace_form',
                {
                    'file': share_link.file_id,
                    'token': token,
                    'error': 'Please select a file to upload.',
                },
            )

        file_data = uploaded.read()
        share_link.file_id.sudo().write({
            'name': uploaded.filename,
            'content': base64.b64encode(file_data),
        })

        return request.render(
            'dms_share_expiration.file_replace_success',
            {'file': share_link.file_id},
        )
