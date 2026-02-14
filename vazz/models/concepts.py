# -*- coding:utf-8 -*-
# odoo
from odoo import models, fields,api, _

class Concepts(models.Model):
    _name = 'vazz.concepts'
    _description = 'Concepts'

    name = fields.Char(string="Concept")
    description = fields.Text(string="Description (optional)")
    currency_id = fields.Many2one( 'res.currency', string='Currency')
    public_price = fields.Float(string="Price")
    service_id = fields.Many2one(comodel_name="vazz.services", string="Service", tracking=True)

    @api.model
    def default_get(self, fields):
        res = super(Concepts, self).default_get(fields)
        currency = self.env['res.currency'].search([('name','=','MXN')])
        if currency:
            res['currency_id'] = currency.id
        return res
