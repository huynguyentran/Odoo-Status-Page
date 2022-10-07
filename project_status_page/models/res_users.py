from odoo import models, fields, api
from odoo.tools import split_every

CHUNK_SIZE = 5


class Users(models.Model):
    _inherit = "res.users"

    url_ids = fields.Many2many("status.domain", string="url")
    notification_enabled = fields.Boolean(default=False, string="Notification Enabled?")
    total_subscribed_domain = fields.Integer(
        string="Total Subscribed Domain", compute="_compute_total_subscribed_domain"
    )

    @api.depends("url_ids")
    def _compute_total_subscribed_domain(self):
        for record in self:
            record.total_subscribed_domain = len(record.url_ids)

    def check_private_domains(self, user_id=None):
        current_uid = user_id
        if not user_id:
            current_uid = self._context.get('uid')

        user = self.env['res.users'].browse(current_uid)
        for rec in user.url_ids:
            rec.send_request(rec.url)

    def check_website(self, website_id):
        website = self.env['status.domain'].browse(website_id)
        website.send_request(website.url)

    def refresh_all_and_send_notification(self):
        all_domains = self.env['status.domain'].search([])
        email_template = self.env.ref('project_status_page.email_template_for_subscribers')

        before_update = {}
        for chunk in split_every(CHUNK_SIZE, all_domains.ids):
            for domain in self.env['status.domain'].browse(chunk):
                before_update[domain.url] = domain.status
                domain.send_request(domain.url)
            self.env.cr.commit()

        after_updated = self.env['status.domain'].search([])
        domains_with_changed_status = {}
        for domain in after_updated:
            if before_update[domain.url] != domain.status:
                domains_with_changed_status[domain.url] = domain.status

        enabled_noti_user = self.env['res.users'].search([('notification_enabled', '=', 'True')])
        for user in enabled_noti_user:
            websites_to_notify_user = []
            for url in user.url_ids:
                if url.url in domains_with_changed_status:
                    single_website = {"url": url.url, "status": url.status}
                    websites_to_notify_user.append(single_website)

            if len(websites_to_notify_user) > 0:
                email_template.email_from = self.env.company.email
                email_template.email_to = user.email
                ctx = dict(self.env.context)
                ctx.update(
                    {
                        'domains_list': websites_to_notify_user
                    }
                )
                email_template.with_context(ctx).send_mail(self.id, force_send=True)

    def toggle_email_notification_for_current_user(self, user_id):
        user = self.env['res.users'].browse(user_id)
        if user.notification_enabled:
            user.notification_enabled = False
        else:
            user.notification_enabled = True
