# -*- coding:utf-8 -*-
# odoo
from odoo import models, fields,api
from odoo.addons.vazz_utils.tools import utils

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

    name = fields.Char(string="Folio de servicio (Express)")
    customer_ids = fields.Many2one(comodel_name="vazz.customers", string="Cliente")
    telephone_cus = fields.Many2one(comodel_name="vazz.customers.phone", string="Teléfono",
    domain = "[('customer_ids','=',customer_ids)]")

    description =  fields.Text(string="Descripción de la falla")
    state = fields.Selection(STATES, default=STATES[0][0], string='Estado del registro')
    cost = fields.Float(string="Precio",tracking=True )
    currency_id = fields.Many2one( 'res.currency', string='Currency')

    # Roles
    is_group_rol002 = fields.Boolean(default=lambda self: self._default_is_group_rol002(),
        compute="_compute_is_group_rol002")

    # Defaults
    @api.model
    def _default_is_group_rol002(self):
        return utils.has_group(self,'vazz.Rol002')

    # compute
    @api.depends('is_group_rol002')
    def _compute_is_group_rol002(self):
        self.is_group_rol002 = utils.has_group(self,'vazz.Rol002')

    @api.model
    def default_get(self, fields):
        res = super(ExpressService, self).default_get(fields)
        currency = self.env['res.currency'].search([('name','=','MXN')])
        if currency:
            res['currency_id'] = currency.id
        return res

    @api.model
    def create(self, vals):
        # Generar nombre
        name_seq = self.env['ir.sequence'].next_by_code('vazz.services.express.sequence')
        if name_seq != False:
            vals['name'] = name_seq
        vals['state'] = 'registered'
        result = super(ExpressService, self).create(vals)
        return result

    # Onchange
    @api.onchange('customer_ids')
    def _onchange_customer_ids(self):
        self.telephone_cus = self.customer_ids.phone.id if self.customer_ids else False