# -*- coding:utf-8 -*-
# odoo
from odoo import models, fields,api, _
from odoo.exceptions import UserError
class Quotation(models.Model):
    _name = 'vazz.quotation'
    _description = 'Cotización'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.depends('product_ids')
    def _compute_total(self):
        # Calculando el total
        for rec in self:
            total_aux = 0
            if rec.product_ids:
                for pro in rec.product_ids:
                    total_aux = total_aux + pro.amount
            rec.total = total_aux

    name = fields.Char(string="Folio", required=True, copy=False, index=True, default=lambda self: _('Nuevo'))
    date = fields.Date(string="Fecha", default=lambda self: fields.datetime.now())
    customer_id = fields.Many2one(comodel_name="vazz.customers", string="Cliente")
    total = fields.Float(string="Total",compute="_compute_total",  store = False)
    product_ids = fields.One2many(comodel_name='vazz.product',inverse_name= 'quotation_id',string="Productos")
    
    currency_id = fields.Many2one( 'res.currency', string='Currency')

    @api.model
    def default_get(self, fields):
        res = super(Quotation, self).default_get(fields)
        currency = self.env['res.currency'].search([('name','=','MXN')])
        if currency:
            res['currency_id'] = currency.id
        return res
    
    @api.model
    def create(self, vals):
        
        is_product = False
        if len(self.product_ids) <= 0:
            if 'product_ids' in vals:
                if vals['product_ids']:
                    is_product = True
                else:
                    is_product = False
            else:
                is_product = False
        else:
            is_product = True

        if is_product == False:
            raise UserError("Agregue por lo menos un producto")

        # Generar folio
        name_seq = self.env['ir.sequence'].next_by_code('vazz.quotation.sequence')
        if name_seq != False:
            vals['name'] = f"CO/{name_seq}"
        
        result = super(Quotation, self).create(vals)
        return result