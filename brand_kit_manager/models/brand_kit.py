from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import is_html_empty


NEW_REFERENCE = "New"
BRAND_LAYOUT_XMLID = "brand_kit_manager.mail_notification_layout_brand_kit"


class BrandKit(models.Model):
    _name = "brand.kit"
    _description = "Brand Kit"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(
        string="Reference",
        required=True,
        copy=False,
        readonly=True,
        default=NEW_REFERENCE,
        tracking=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    logo = fields.Image(string="Logo", attachment=True)
    primary_color = fields.Char(string="Primary Color")
    secondary_color = fields.Char(string="Secondary Color")
    footer_text = fields.Html(string="Footer Text")
    legal_text = fields.Html(string="Legal Text")
    email_header_text = fields.Char(string="Email Header Text")
    template_ids = fields.Many2many(
        "mail.template",
        "brand_kit_template_rel",
        "brand_kit_id",
        "template_id",
        string="Templates To Apply",
        domain=[("model_id", "!=", False)],
        help="Only selected templates are assigned to the Brand Kit email layout.",
    )
    note = fields.Text(string="Internal Notes")
    active = fields.Boolean(default=True, tracking=True)

    _sql_constraints = [
        (
            "brand_kit_name_company_unique",
            "unique(name, company_id)",
            "Brand kit name must be unique per company.",
        ),
        (
            "brand_kit_code_unique",
            "unique(code)",
            "Brand kit reference must be unique.",
        ),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        sequence = self.env["ir.sequence"]
        for vals in vals_list:
            if not vals.get("code") or vals["code"] == NEW_REFERENCE:
                vals["code"] = sequence.next_by_code("brand.kit") or NEW_REFERENCE
        return super().create(vals_list)

    def action_load_recommended_templates(self):
        self.ensure_one()
        templates = self._get_recommended_templates()
        if not templates:
            raise UserError(
                _(
                    "No recommended templates were found. Install Sales/Accounting/Purchase "
                    "apps or pick templates manually."
                )
            )
        self.template_ids = [(6, 0, templates.ids)]
        return self._display_notification(
            _("Templates Loaded"),
            _("Loaded %s recommended templates.") % len(templates),
        )

    def action_preview(self):
        self.ensure_one()
        templates = self.template_ids or self._get_recommended_templates()
        if not templates:
            raise UserError(_("Select at least one template before previewing."))

        line_values = []
        for template in templates:
            current_body = template.body_html or ""
            line_values.append(
                (
                    0,
                    0,
                    {
                        "template_id": template.id,
                        "current_body_html": current_body,
                        "preview_body_html": self._render_template_with_layout(
                            template,
                            current_body,
                        ),
                    },
                )
            )

        wizard = self.env["brand.kit.preview.wizard"].create(
            {
                "brand_kit_id": self.id,
                "line_ids": line_values,
            }
        )
        view = self.env.ref(
            "brand_kit_manager.view_brand_kit_preview_wizard_form",
            raise_if_not_found=False,
        )
        return {
            "name": _("Brand Kit Preview"),
            "type": "ir.actions.act_window",
            "res_model": "brand.kit.preview.wizard",
            "res_id": wizard.id,
            "view_mode": "form",
            "view_id": view.id if view else False,
            "target": "new",
        }

    def action_apply_to_email_templates(self):
        self.ensure_one()
        if not self.template_ids:
            raise UserError(_("Select at least one template to apply changes."))

        self._sync_company_brand_fields()
        updated_count = self._apply_layout_to_templates(self.template_ids)
        return self._display_notification(
            _("Brand Kit Applied"),
            _("Assigned branded layout to %s template(s).") % updated_count,
        )

    def _sync_company_brand_fields(self):
        self.ensure_one()
        company_values = {}
        if self.primary_color:
            company_values["brand_primary_color"] = self.primary_color
        if self.secondary_color:
            company_values["brand_secondary_color"] = self.secondary_color
        if self.footer_text:
            company_values["brand_footer_text"] = self.footer_text
        if self.legal_text:
            company_values["brand_legal_text"] = self.legal_text

        if company_values:
            self.company_id.write(company_values)

    def _apply_layout_to_templates(self, templates):
        self.ensure_one()
        if "email_layout_xmlid" not in self.env["mail.template"]._fields:
            raise UserError(
                _("This Odoo version does not support assigning email layouts to templates.")
            )

        updated_count = 0
        for template in templates:
            if template.email_layout_xmlid != BRAND_LAYOUT_XMLID:
                template.write({"email_layout_xmlid": BRAND_LAYOUT_XMLID})
                updated_count += 1
        return updated_count

    def _get_recommended_templates(self):
        xmlids = [
            "sale.email_template_edi_sale",
            "sale.email_template_edi_sale_done",
            "account.email_template_edi_invoice",
            "purchase.email_template_edi_purchase",
            "purchase.email_template_edi_purchase_done",
            "stock.mail_template_data_delivery_confirmation",
        ]
        templates = self.env["mail.template"].browse()
        for xmlid in xmlids:
            record = self.env.ref(xmlid, raise_if_not_found=False)
            if record and record._name == "mail.template":
                templates |= record
        return templates

    def _render_template_with_layout(self, template, current_body):
        self.ensure_one()
        template_ctx = {
            "message": self.env["mail.message"].sudo().new(
                {
                    "body": current_body or "",
                    "record_name": template.name or self.name,
                }
            ),
            "subtype": self.env["mail.message.subtype"].sudo(),
            "model_description": template.model_id.display_name
            if template.model_id
            else (template.model or ""),
            "record": self.company_id,
            "record_name": False,
            "subtitles": False,
            "company": self.company_id,
            "email_add_signature": False,
            "signature": "",
            "website_url": "",
            "is_html_empty": is_html_empty,
            "email_notification_allow_header": True,
            "email_notification_force_header": True,
            "email_notification_allow_footer": True,
            "email_notification_force_footer": True,
        }
        rendered = self.env["ir.qweb"]._render(
            BRAND_LAYOUT_XMLID,
            template_ctx,
            minimal_qcontext=True,
            raise_if_not_found=False,
        )
        if not rendered:
            return current_body
        return self.env["mail.render.mixin"]._replace_local_links(rendered)

    def _display_notification(self, title, message):
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "success",
                "title": title,
                "message": message,
                "sticky": False,
            },
        }
