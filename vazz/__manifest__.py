# -*- coding: utf-8 -*-
{
    "name": "Sistema Vazztec",
    "summary": """System Vazztec""",
    "version": '13.0.0.1.0',
    "description": """
    Sistema para el control del local
    ====================""",
    "author": "Andres Vergara",
    "maintainer": "Andres Vergara",
    "website": "",
    "category": "Inventory",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
    ],
    "data": [
        # Security Files
        "security/ir.security.lib.xml",
        "security/ir.model.access.csv",
        # Data Files
        # Sequences
        "data/sequence.xml",
        # Crons
        "data/ir_cron_server.xml",
        # Wizard Files
        "wizards/cancel_wizard.xml",
        "wizards/delivery_wizard.xml",
        # Views
        "views/services.xml",
        "views/services_rol.xml",
        "views/customers.xml",
        "views/phone.xml",
        "views/orders.xml",
        "views/cancel_views.xml",
        "views/assets.xml",
        "views/notifications.xml",
        "views/notifications_type.xml",
        "views/warranty.xml",
        "views/unlocks_type.xml",
        "views/unlocks.xml",
        "views/unlocks_rol.xml",
        "views/equipment_type.xml",
        "views/diagnostic.xml",
        "views/state_history.xml",
        "views/concepts.xml",
        "views/schedule_type.xml",
        "views/schedule.xml",
        "views/product.xml",
        "views/quotation.xml",
        # Views inherit other module
        "views/res_users.xml",
        # Report views
        'report/reports.xml',
        'report/report_quotation.xml',
        'report/service_ticket.xml',
        # Main Menu file
        "views/menu_views.xml",
    ],
    "application": True,
    "installable": True,
    "auto_install": False,
}