from odoo import _, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    brand_primary_color = fields.Char(
        string="Brand Primary Color",
        default="#0B5FFF",
        help="Primary brand color used in outgoing emails.",
    )
    brand_secondary_color = fields.Char(
        string="Brand Secondary Color",
        default="#F4F6FA",
        help="Secondary brand color used in outgoing emails.",
    )
    brand_footer_text = fields.Html(
        string="Brand Footer Text",
        help="Footer content shown in branded emails.",
    )
    brand_legal_text = fields.Html(
        string="Brand Legal Text",
        help="Legal/disclaimer content shown in branded emails.",
    )
    brand_email_header_text = fields.Char(
        string="Brand Email Header Text",
        help="Short header text shown in branded email notifications.",
    )

    brand_kit_id = fields.Many2one(
        "brand.kit",
        string="Default Brand Kit",
        help="Default brand kit used by this company.",
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    brand_primary_color = fields.Char(
        related="company_id.brand_primary_color",
        readonly=False,
        string="Brand Primary Color",
    )
    brand_secondary_color = fields.Char(
        related="company_id.brand_secondary_color",
        readonly=False,
        string="Brand Secondary Color",
    )
    brand_footer_text = fields.Html(
        related="company_id.brand_footer_text",
        readonly=False,
        string="Brand Footer Text",
    )
    brand_legal_text = fields.Html(
        related="company_id.brand_legal_text",
        readonly=False,
        string="Brand Legal Text",
    )
    brand_email_header_text = fields.Char(
        related="company_id.brand_email_header_text",
        readonly=False,
        string="Brand Email Header Text",
    )

    brand_kit_id = fields.Many2one(
        related="company_id.brand_kit_id",
        readonly=False,
        string="Default Brand Kit",
    )

    def action_open_email_layout_preview(self):
        self.ensure_one()
        wizard = self.env["brand.email.layout.preview.wizard"].create(
            {"company_id": self.company_id.id}
        )
        view = self.env.ref(
            "brand_kit_manager.view_company_email_layout_preview_wizard_form",
            raise_if_not_found=False,
        )
        return {
            "name": _("Email Layout Preview"),
            "type": "ir.actions.act_window",
            "res_model": "brand.email.layout.preview.wizard",
            "res_id": wizard.id,
            "view_mode": "form",
            "view_id": view.id if view else False,
            "target": "new",
        }
