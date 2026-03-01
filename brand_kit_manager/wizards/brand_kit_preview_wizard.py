from odoo import fields, models


class BrandKitPreviewWizard(models.TransientModel):
    _name = "brand.kit.preview.wizard"
    _description = "Brand Kit Preview Wizard"

    brand_kit_id = fields.Many2one("brand.kit", required=True, readonly=True)
    line_ids = fields.One2many(
        "brand.kit.preview.wizard.line",
        "wizard_id",
        string="Template Previews",
        readonly=True,
    )


class BrandKitPreviewWizardLine(models.TransientModel):
    _name = "brand.kit.preview.wizard.line"
    _description = "Brand Kit Preview Wizard Line"

    wizard_id = fields.Many2one(
        "brand.kit.preview.wizard",
        required=True,
        ondelete="cascade",
    )
    template_id = fields.Many2one("mail.template", required=True, readonly=True)
    model_name = fields.Char(related="template_id.model", string="Applies To", readonly=True)
    subject = fields.Char(related="template_id.subject", readonly=True)
    current_body_html = fields.Html(readonly=True)
    preview_body_html = fields.Html(readonly=True)
