from odoo import models, fields


class CheckPopup(models.TransientModel):
    _name = "check.popup"
    input_url = fields.Char("Input URL")

    def check_url(self):
        self.ensure_one()
        url = self.input_url
        message = self.env['status.domain'].send_request(url)
        return message

    def add_url(self):
        self.ensure_one()
        url = self.input_url
        message = self.env['status.domain'].add_domain_to_user_list(new_url=url)
        return message
