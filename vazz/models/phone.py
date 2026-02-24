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
        else:
            customer_id  = self._context.get('default_customer_ids')
            if customer_id:
                res['customer_ids'] = self._context.get('default_customer_ids')
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('customer_ids'):
                customer = self.env['vazz.customers'].search([('id','=',vals.get('customer_ids'))])
                if customer:
                    customer.phones_ids.is_main = False
            vals['is_main'] = True

        result = super(Phone, self).create(vals_list)
        return result
    
    def button_is_main(self):
        for cus in self.customer_ids:
            for tel in cus.phones_ids:
                if tel.id == self.id:
                    tel.is_main = True
                else:
                    tel.is_main = False
    
    def name_get(self):
        res = []
        for record in self:
            customers = record.env['vazz.customers.phone'].browse([record['id']])
            name = f"{customers.name}"
            
            res.append((record['id'],'%s' % (name)))
        return res