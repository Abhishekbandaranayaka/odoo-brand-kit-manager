from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    brand_kit_id = fields.Many2one(
        "brand.kit",
        string="Default Brand Kit",
        help="Default brand kit used by this company.",
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    brand_kit_id = fields.Many2one(
        related="company_id.brand_kit_id",
        readonly=False,
        string="Default Brand Kit",
    )

