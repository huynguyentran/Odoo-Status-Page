from datetime import datetime
from urllib.parse import urlparse

import requests
import validators

from odoo import _, api, fields, models


class Domain(models.Model):
    _name = "status.domain"
    _description = "The websites model for Project Status Page"
    _rec_name = "url"

    url = fields.Char(string="URL", required=True)
    ping = fields.Integer(string="Ping")
    status = fields.Char(string="Status", default="Up")
    last_check = fields.Datetime(string="Last check")
    subscriber_ids = fields.Many2many("res.users", string="Subscriber")
    total_followers = fields.Integer(string="Followers", compute="_compute_total_follower", store=True)
    default_page = fields.Boolean(default=False, string="Is default domain?")

    @api.depends("subscriber_ids")
    def _compute_total_follower(self):
        for record in self:
            record.total_followers = len(record.subscriber_ids)

    def send_request(self, web_url=None):
        """Send request here will automatically save the URL into database"""
        # self.ensure_one()

        if web_url is None:
            url = self.url
        else:
            url = self._remove_slash_from_url_end(web_url)

        valid, message = self.validate_url(url)

        if not valid:
            return self.valid_helper(message)

        self.last_check = datetime.now()
        context = {'url': url, 'ping': -1, 'status': "N/A", "last_check": datetime.now()}
        try:
            # use requests.head to get the TTFB
            # If we use requests.head, we can't resolve for website that is not .com

            # Can't send request to .net websites, change back to requests.get

            # r = requests.head(url, allow_redirects=True, timeout=30)
            r = requests.get(url, allow_redirects=True, timeout=15)
            self.ping = int(r.elapsed.total_seconds() * 1000)
            context["ping"] = int(r.elapsed.total_seconds() * 1000)
            code = r.status_code

            """code is None means Website can not be reached -> display "Website is down!" is not accurate"""

            if code < 400:
                self.status = "Up"
                context["status"] = "Up"
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "message": "Website is up!",
                        "type": "success",
                        "sticky": False,
                        "data": context,
                    },
                }
            else:
                context["status"] = "Down"
                return self.notification_website_down(context)
        except:
            return self.notification_website_down(context)

    def validate_url(self, url):
        url = url.strip()
        valid = False

        # check if input is in incorrect format
        if not validators.url(url):
            return valid, "Please enter an URL with a valid format, e.g: https://www.google.com"
        else:
            parsed_url = urlparse(url)
            path = parsed_url.path
            # check if input has path
            if path != "/" and path != "":
                return valid, "URL should not contains path, do you mean: " + str(parsed_url.scheme) + "://" + str(
                    parsed_url.hostname)
            # NOTE: if the domain does not have ".com", it will be an error, but it still pass the checking statement
            else:
                hostname = parsed_url.hostname
                allowed, result = self.check_whitelist(hostname)
                # If the input is not in whitelist
                if not allowed:
                    return valid, result

                valid = True
                return valid, "Success"

    def garbage_collector(self):
        # no_follower_domains = self.env['status.domain'].search([('total_followers', '=', 0)])
        no_follower_domains = self.env['status.domain'].search(
            [('total_followers', '=', 0), ('default_page', '=', False)])
        for rec in no_follower_domains:
            rec.unlink()

    def check_whitelist(self, hostname):
        domain = '.'.join(hostname.split('.')[-2:])
        valid = False

        if self.env["whitelist"].search_count([("white_domain", "=", domain)]) == 0:
            return valid, "Input URL is not allowed, please try a different URL!"

        valid = True
        return valid, "Input allowed"

    def add_domain_to_user_list(self, user_id=None, new_url=""):
        new_url = self._remove_slash_from_url_end(new_url)

        current_uid = user_id
        if not user_id:
            current_uid = self._context.get('uid')

        rec = self.env['status.domain'].search([('url', '=', new_url)])
        if rec:
            rec.write({'subscriber_ids': [(4, current_uid)]})
            rec.send_request(rec.url)
        else:
            vals = {
                'url': new_url,
                'subscriber_ids': [(4, current_uid)],
            }
            rec = self.env['status.domain'].create(vals)
            rec.send_request(new_url)

    def valid_helper(self, input_message):
        """This to reduce repeated code"""
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "message": _(input_message),
                "type": "warning",
                "sticky": False,
            },
        }

    def notification_website_down(self, context):
        self.status = "Down"
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "message": "Website is down!",
                "type": "warning",
                "sticky": False,
                "data": context,
            },
        }

    def _remove_slash_from_url_end(self, url):
        if url[-1] == "/":
            url = url.rstrip(url[-1])
        return url

    def unlink_website_from_user(self, website_id):
        context = self._context
        current_uid = context.get('uid')
        website = self.env['status.domain'].sudo().browse(website_id)
        website.write({'subscriber_ids': [(3, current_uid)]})

    def remove_private_domains(self, user_id=None,):
        current_uid = user_id
        if not user_id:
            current_uid = self._context.get('uid')
        user = self.env['res.users'].browse(current_uid)
        for rec in user.url_ids:
            website = self.env['status.domain'].sudo().browse(rec.id)
            website.write({'subscriber_ids': [(3, current_uid)]})

    def unlink_website_from_user(self, user_id=None, website_id=''):
        current_uid = user_id
        if not user_id:
            context = self._context
            current_uid = context.get('uid')
        website = self.env['status.domain'].sudo().browse(website_id)
        website.write({'subscriber_ids': [(3, current_uid)]})
