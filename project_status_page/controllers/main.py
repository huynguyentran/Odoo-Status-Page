from urllib.parse import urlparse
from openerp import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class Main(http.Controller):
    @http.route('/home', type='http', auth='public', website=True)
    def landing_page(self, **kw):
        return http.request.render('project_status_page.landing_page', {})

    @http.route('/private-domains', type='http', auth='user', website=True)
    def private_domains_page(self, context=None, **kw):
        if context is None:
            user_id = request.session.uid
            context = {'user': user_id,
                       'current_filter': "Current filter shows all websites!"}
        return http.request.render('project_status_page.private_domains_page', context)

    @http.route('/check', type='http', auth='user', website=True)
    def check(self, **kw):
        user_id = request.session.uid
        return_context = {'user': user_id}
        if "url" in kw:
            obj = request.env['status.domain'].sudo().send_request(kw["url"])
            info = obj['params']
            if "data" in info:
                message = info['data']
                return_context.update({'url': message['url'],
                                       'ping': message['ping'],
                                       'status': message['status'],
                                       'last_check': message['last_check']
                                       })
            else:
                return_context.update({'error_message': info['message']})
        path = str(urlparse(request.httprequest.referrer).path)
        if "down" in path:
            request.session.update({'filter': 'Down'})
            return_context.update({'current_filter': "Current filter shows Down websites!"})
            return self.filter_down(return_context)
        elif "up" in path:
            request.session.update({'filter': 'Up'})
            return_context.update({'current_filter': "Current filter shows Up websites!"})
            return self.filter_up(return_context)
        else:
            request.session.update({'filter': 'None'})
            return_context.update({'current_filter': "Current filter shows all websites!"})
            return self.private_domains_page(return_context)

    @http.route('/domain/refresh-all', type='http', auth='user', website=True)
    def refresh_all(self, **kw):
        user_id = request.session.uid
        request.env['res.users'].sudo().check_private_domains(user_id)
        path = urlparse(request.httprequest.referrer).path
        return request.redirect(path)

    @http.route('/domain/add', type='http', auth='user', website=True)
    def add_domain(self, **kw):
        user_id = request.session.uid
        request.env['status.domain'].sudo().add_domain_to_user_list(user_id, kw["url"])
        path = urlparse(request.httprequest.referrer).path
        if request.session.get('filter') == 'None':
            return request.redirect(path)
        elif request.session.get('filter') == 'Up':
            return request.redirect("/domain/" + str(user_id) + "/domains-up")
        else:
            return request.redirect("/domain/" + str(user_id) + "/domains-down")

    @http.route('/domain/<string:user>/toggle-notification', type='http', auth='user', website=True)
    def enable_noti(self, **kw):
        user_id = request.session.uid
        request.env['res.users'].sudo().toggle_email_notification_for_current_user(user_id)
        path = urlparse(request.httprequest.referrer).path
        return request.redirect(path)

    @http.route('/domain/<string:user>/domains-up', type='http', auth='user', website=True)
    def filter_up(self, context=None, **kw):
        user_id = request.session.uid
        if context is None:
            context = {'user': user_id,
                       'current_filter': "Current filter shows Up websites!"}
        return http.request.render('project_status_page.private_domains_page_filter_up', context)

    @http.route('/domain/<string:user>/domains-down', type='http', auth='user', website=True)
    def filter_down(self, context=None, **kw):
        user_id = request.session.uid
        if context is None:
            context = {'user': user_id,
                       'current_filter': "Current filter shows Down websites!"}
        return http.request.render('project_status_page.private_domains_page_filter_down', context)

    @http.route('/domain/<int:web_id>/delete', type='http', auth='user', website=True)
    def delete_domain(self, web_id, **kw):
        user_id = request.session.uid
        path = urlparse(request.httprequest.referrer).path
        if web_id:
            request.env['status.domain'].sudo().unlink_website_from_user(user_id, web_id)
        return request.redirect(path)

    @http.route('/domain/delete_all', type='http', auth='user', website=True)
    def delete_all(self, **kw):
        user_id = request.session.uid
        path = urlparse(request.httprequest.referrer).path
        request.env['status.domain'].sudo().remove_private_domains(user_id)
        return request.redirect(path)

    @http.route('/domain/<int:website_id>/check_domain', type='http', auth='user', website=True)
    def check_domain(self, website_id, **kw):
        path = urlparse(request.httprequest.referrer).path
        if website_id:
            request.env['res.users'].sudo().check_website(website_id)
        return request.redirect(path)


class InheritCustomerPortal(CustomerPortal):
    @http.route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        return request.redirect('/private-domains')
