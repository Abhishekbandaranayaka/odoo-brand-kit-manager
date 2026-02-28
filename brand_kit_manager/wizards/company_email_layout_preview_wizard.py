from markupsafe import escape

from odoo import api, fields, models
from odoo.tools import image_data_uri


DEFAULT_PRIMARY_COLOR = "#0B5FFF"
DEFAULT_SECONDARY_COLOR = "#F4F6FA"


class CompanyEmailLayoutPreviewWizard(models.TransientModel):
    _name = "brand.email.layout.preview.wizard"
    _description = "Company Email Layout Preview Wizard"

    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        readonly=True,
    )
    template_id = fields.Many2one(
        "mail.template",
        string="Email Template",
        required=True,
        domain=[("model_id", "!=", False)],
    )
    template_model = fields.Char(related="template_id.model", readonly=True)
    current_body_html = fields.Html(
        string="Current Template Body",
        compute="_compute_preview_html",
        readonly=True,
    )
    preview_body_html = fields.Html(
        string="Branded Preview",
        compute="_compute_preview_html",
        readonly=True,
    )

    def _get_company_logo_html(self):
        self.ensure_one()
        company = self.company_id
        logo_value = False
        if "logo" in company._fields:
            logo_value = company.logo
        elif "image_1920" in company._fields:
            logo_value = company.image_1920

        if not logo_value:
            return ""

        alt_text = escape(company.name or "Company Logo")
        return (
            f'<img src="{image_data_uri(logo_value)}" alt="{alt_text}" '
            'style="max-height:52px;max-width:200px;display:block;" />'
        )

    def _build_branded_body(self, current_body):
        self.ensure_one()
        company = self.company_id
        primary_color = company.brand_primary_color or DEFAULT_PRIMARY_COLOR
        secondary_color = company.brand_secondary_color or DEFAULT_SECONDARY_COLOR
        header_text = escape(company.name or "")
        footer_html = company.brand_footer_text or ""
        legal_html = company.brand_legal_text or ""
        logo_html = self._get_company_logo_html()

        return (
            '<div data-brand-kit-manager-preview="1" style="font-family:Arial,Helvetica,sans-serif;'
            f'border:1px solid {secondary_color};border-radius:8px;overflow:hidden;">'
            f'<div style="background:{primary_color};color:#ffffff;padding:16px;">'
            f'{logo_html}<div style="margin-top:8px;font-size:16px;font-weight:600;">{header_text}</div>'
            f"</div>"
            f'<div style="padding:20px;background:#ffffff;">{current_body}</div>'
            f'<div style="padding:16px;background:{secondary_color};font-size:13px;">'
            f"{footer_html}"
            f'<div style="margin-top:8px;opacity:0.8;">{legal_html}</div>'
            f"</div>"
            f"</div>"
        )

    @api.depends(
        "template_id",
        "company_id",
        "company_id.brand_primary_color",
        "company_id.brand_secondary_color",
        "company_id.brand_footer_text",
        "company_id.brand_legal_text",
        "company_id.name",
    )
    def _compute_preview_html(self):
        for wizard in self:
            body_html = wizard.template_id.body_html or ""
            wizard.current_body_html = body_html
            wizard.preview_body_html = wizard._build_branded_body(body_html) if body_html else ""
