# -*- coding:utf-8 -*-
# odoo
from odoo import models, fields,api, _

TYPEUSER = [
    ('seller', 'Vendedor'),
    ('technical', 'Técnico'),
    ('disabled', 'Desactivado')]

class ResUsers(models.Model):
    _inherit = "res.users"


    type_user_va = fields.Selection(TYPEUSER, string='Tipo de usuario')