# Copyright © 2022 Novobi, LLC
# See LICENSE file for full copyright and licensing details.

{
    "name": "Project Status Page",
    "summary": "Novobi: Project Status Page for US interns 2022",
    "version": "1.0.0",
    "category": "Tools",
    "website": "https://novobi.com",
    "author": "Novobi, LLC",
    "license": "OPL-1",
    "depends": [
        "base", "mail", "website", "contacts",
    ],
    "excludes": [],
    "data": [
        # ============================== DATA =================================
        'data/email_template_data.xml',

        # ============================== SECURITY ===========================
        'security/status_page_groups.xml',
        'security/ir.model.access.csv',

        # ============================== VIEWS ================================
        'views/status_page_user_views.xml',
        'views/status_page_domain_views.xml',
        'views/cron.xml',
        'views/garbage_collector.xml',
        'views/setting_view_inherited.xml',
        'views/whitelist_view.xml',
        'views/landing_page.xml',
        'views/private_domains_page.xml',
        'views/private_domains_page_filter_up.xml',
        'views/private_domains_page_filter_down.xml',
        'views/inherited_frontend_layout.xml',

        # ============================== WIZARDS ============================
        'wizards/check_popup_views.xml',
        # ============================== REPORT =============================

    ],
    "application": True,
    "installable": True,
}
