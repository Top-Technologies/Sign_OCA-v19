# Copyright 2023-2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SignOcaTemplateGenerateMulti(models.TransientModel):
    _name = "sign.oca.template.generate.multi"
    _description = "Generate signature requests"

    def _default_dms_directory(self):
        template_id = self.env.context.get("default_template_id")
        if not template_id:
            return False
        template = self.env["sign.oca.template"].browse(template_id)
        return template.dms_directory_id if template else False

    def _default_filename(self):
        template_id = self.env.context.get("default_template_id")
        if not template_id:
            return False
        template = self.env["sign.oca.template"].browse(template_id)
        return template.name if template else False

    model = fields.Char(
        readonly=True, default=lambda self: self.env.context.get("model", False)
    )
    template_id = fields.Many2one(
        comodel_name="sign.oca.template",
        domain="[('model', '=', model)]",
        required=True,
    )
    filename = fields.Char(default=_default_filename)
    dms_directory_id = fields.Many2one("dms.directory", default=_default_dms_directory)
    message = fields.Html()
    is_employee_document = fields.Boolean(string="Is Employee Document?")
    employee_id = fields.Many2one("hr.employee", string="Employee")

    def _ensure_employee_dms_directory(self, employee):
        dms_dir_model = self.env['dms.directory'].sudo()
        hr_dir = dms_dir_model.search([('name', '=', 'HR'), ('is_root_directory', '=', True)], limit=1)
        if not hr_dir:
            hr_dir = dms_dir_model.search([('name', '=', 'HR')], limit=1)
            if not hr_dir:
                storage = self.env['dms.storage'].search([], limit=1)
                hr_dir = dms_dir_model.create({
                    'name': 'HR',
                    'is_root_directory': True,
                    'storage_id': storage.id,
                })
        emp_folder = dms_dir_model.search([('name', '=', 'Employee Folder'), ('parent_id', '=', hr_dir.id)], limit=1)
        if not emp_folder:
            emp_folder = dms_dir_model.create({
                'name': 'Employee Folder',
                'parent_id': hr_dir.id,
            })
        emp_dir = dms_dir_model.search([('name', '=', employee.name), ('parent_id', '=', emp_folder.id)], limit=1)
        if not emp_dir:
            emp_dir = dms_dir_model.create({
                'name': employee.name,
                'parent_id': emp_folder.id,
            })
        return emp_dir

    def _prepare_sign_oca_request_vals(self):
        vals = []
        dms_dir_id_base = self.dms_directory_id.id if self.dms_directory_id else self.template_id.dms_directory_id.id
        if self.is_employee_document and self.employee_id:
            emp_dir = self._ensure_employee_dms_directory(self.employee_id)
            dms_dir_id_base = emp_dir.id

        for item in self.env[self.model].browse(self.env.context.get("active_ids")):
            request_vals = self.template_id._prepare_sign_oca_request_vals_from_record(item)
            request_vals["name"] = self.filename or self.template_id.name
            request_vals["filename"] = self.filename or self.template_id.name
            request_vals["dms_directory_id"] = dms_dir_id_base
            vals.append(request_vals)
        return vals

    @api.onchange("template_id")
    def _onchange_template_id(self):
        if self.template_id and not self.dms_directory_id:
            self.dms_directory_id = self.template_id.dms_directory_id
        if self.template_id and not self.filename:
            self.filename = self.template_id.name

    def _generate(self):
        return self.env["sign.oca.request"].create(
            self._prepare_sign_oca_request_vals()
        )

    def generate(self):
        requests = self._generate()
        for request in requests:
            request.action_send(message=self.message)
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "sign_oca.sign_oca_request_act_window"
        )
        action["domain"] = [("id", "in", requests.ids)]
        return action
