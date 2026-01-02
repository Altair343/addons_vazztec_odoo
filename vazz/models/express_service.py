# -*- coding:utf-8 -*-
# odoo
from odoo import models, fields,api

import logging
_logger = logging.getLogger(__name__)

STATES = [
    ('draft', 'Borrador'),
    ('registered', 'Registrado')
]

class ExpressService(models.Model):
    _name = 'vazz.express.service'
    _description = 'Servicio expréss'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Folio")
    customer_name = fields.Char(string="Nombre completo", tracking=True)
    phone = fields.Char(string="Teléfono", tracking=True)
    description =  fields.Text(string="Descripción de la falla")
    state = fields.Selection(STATES, default=STATES[0][0], string='Estado del registro')

    @api.model
    def create(self, vals):
        # Generar nombre
        name_seq = self.env['ir.sequence'].next_by_code('vazz.services.express.sequence')
        if name_seq != False:
            vals['name'] = name_seq
        vals['state'] = 'registered'
        result = super(ExpressService, self).create(vals)
        return result
