from odoo import models, fields, api


class Whitelist(models.Model):
    _name = "whitelist"
    _description = "Whitelist"
    _rec_name = "white_domain"

    white_domain = fields.Char(string="White Domain", required=True)
    """NOTE: change the Security access level to Admin only later"""
    """ => Done, but have not checked"""

    """Ensure the input of whitelist is in correct format"""


