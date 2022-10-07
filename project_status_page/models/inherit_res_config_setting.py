from odoo import models, api, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    total_domain = fields.Integer(string="Total Domain", compute="_compute_total_domain")

    @api.depends("company_id")
    def _compute_total_domain(self):
        white_domain_count = self.env['whitelist'].sudo().search_count([])
        for record in self:
            record.total_domain = white_domain_count
