from odoo import api, fields, models


NEW_REFERENCE = "New"


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
    logo = fields.Binary(string="Logo", attachment=True)
    primary_color = fields.Char(string="Primary Color")
    secondary_color = fields.Char(string="Secondary Color")
    font_family = fields.Char(string="Font Family")
    note = fields.Text(string="Notes")
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

