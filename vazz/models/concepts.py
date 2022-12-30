# -*- coding:utf-8 -*-
# odoo
from odoo import models, fields,api, _

class Concepts(models.Model):
    _name = 'vazz.concepts'
    _description = 'Conceptos'

    name = fields.Char(string="Concepto")
    description = fields.Text(string="Descripción (opcional)")
    currency_id = fields.Many2one( 'res.currency', string='Currency')
    public_price = fields.Float(string="Precio")
    service_id = fields.Many2one(comodel_name="vazz.services", string="Servicio", tracking=True)

    @api.model
    def default_get(self, fields):
        res = super(Concepts, self).default_get(fields)
        currency = self.env['res.currency'].search([('name','=','MXN')])
        if currency:
            res['currency_id'] = currency.id
        return res
