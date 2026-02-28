from odoo import api, fields, models
from odoo.tools import is_html_empty


BRAND_LAYOUT_XMLID = "brand_kit_manager.mail_notification_layout_brand_kit"


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

    def _render_with_layout(self, body_html):
        self.ensure_one()
        template = self.template_id
        template_ctx = {
            "message": self.env["mail.message"].sudo().new(
                {"body": body_html or "", "record_name": template.name or ""}
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
            return body_html
        return self.env["mail.render.mixin"]._replace_local_links(rendered)

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
            wizard.preview_body_html = wizard._render_with_layout(body_html) if body_html else ""
