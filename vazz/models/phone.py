# -*- coding:utf-8 -*-
# odoo
from odoo import models, fields,api, _

class Phone(models.Model):
    _name = 'vazz.customers.phone'
    _description = 'Teléfono'

    name = fields.Char(string="Teléfono")
    customer_ids = fields.Many2one(comodel_name="vazz.customers", string="Cliente", ondelete='cascade')
    is_main = fields.Boolean( string="Principal") # si esta activo es el principal

    @api.model
    def default_get(self, fields):
        res = super(Phone, self).default_get(fields)
        request_id = self._context.get('request_id')
        if request_id:
            res['customer_ids'] = self._context.get('request_id')
        return res

    @api.model
    def create(self, vals):

        if 'customer_ids' in vals:
            customer = self.env['vazz.customers'].search([('id','=',vals['customer_ids'])])
            if customer:
                customer.phones_ids.is_main = False
        vals['is_main'] = True

        result = super(Phone, self).create(vals)
        return result
    
    def button_is_main(self):
        for cus in self.customer_ids:
            for tel in cus.phones_ids:
                if tel.id == self.id:
                    tel.is_main = True
                else:
                    tel.is_main = False