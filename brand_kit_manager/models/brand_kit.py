import re

from markupsafe import escape

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import image_data_uri


NEW_REFERENCE = "New"
BRAND_KIT_START = "<!-- BRAND_KIT_MANAGER_START -->"
BRAND_KIT_END = "<!-- BRAND_KIT_MANAGER_END -->"
DEFAULT_PRIMARY_COLOR = "#0B5FFF"
DEFAULT_SECONDARY_COLOR = "#F4F6FA"


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
        help="Only selected templates are updated when you click Apply.",
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
                        "preview_body_html": self._build_branded_body(current_body),
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

        updated_count = self._apply_to_templates(self.template_ids)
        return self._display_notification(
            _("Brand Kit Applied"),
            _("Updated %s template(s).") % updated_count,
        )

    def _apply_to_templates(self, templates):
        self.ensure_one()
        updated_count = 0
        for template in templates:
            current_body = template.body_html or ""
            new_body = self._build_branded_body(current_body)
            if new_body != current_body:
                template.write({"body_html": new_body})
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

    def _build_branded_body(self, current_body):
        self.ensure_one()
        base_body = self._strip_existing_brand_kit_wrapper(current_body)
        primary_color = self.primary_color or DEFAULT_PRIMARY_COLOR
        secondary_color = self.secondary_color or DEFAULT_SECONDARY_COLOR
        header_text = escape(self.email_header_text or "")
        footer_html = self.footer_text or ""
        legal_html = self.legal_text or ""
        logo_html = self._get_logo_html()

        return (
            f"{BRAND_KIT_START}"
            f'<div data-brand-kit-manager="1" style="font-family:Arial,Helvetica,sans-serif;'
            f'border:1px solid {secondary_color};border-radius:8px;overflow:hidden;">'
            f'<div style="background:{primary_color};color:#ffffff;padding:16px;">'
            f'{logo_html}<div style="margin-top:8px;font-size:16px;font-weight:600;">{header_text}</div>'
            f"</div>"
            f'<div style="padding:20px;background:#ffffff;">{base_body}</div>'
            f'<div style="padding:16px;background:{secondary_color};font-size:13px;">'
            f"{footer_html}"
            f'<div style="margin-top:8px;opacity:0.8;">{legal_html}</div>'
            f"</div>"
            f"</div>"
            f"{BRAND_KIT_END}"
        )

    def _strip_existing_brand_kit_wrapper(self, body_html):
        body_html = body_html or ""
        pattern = re.compile(
            re.escape(BRAND_KIT_START) + r".*?" + re.escape(BRAND_KIT_END),
            flags=re.S,
        )
        return re.sub(pattern, "", body_html).strip()

    def _get_logo_html(self):
        self.ensure_one()
        logo_value = self.logo
        if not logo_value:
            if "logo" in self.company_id._fields:
                logo_value = self.company_id.logo
            elif "image_1920" in self.company_id._fields:
                logo_value = self.company_id.image_1920

        if not logo_value:
            return ""

        alt_text = escape(self.name or "Brand Logo")
        return (
            f'<img src="{image_data_uri(logo_value)}" alt="{alt_text}" '
            'style="max-height:52px;max-width:200px;display:block;" />'
        )

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
