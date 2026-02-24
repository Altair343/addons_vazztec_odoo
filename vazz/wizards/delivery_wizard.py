#-*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo import api, fields, models


class DeliveryWizard(models.TransientModel):
    _name = "vazz.delivery.wizard"
    _description ="Cancelación"

    date_delibery = fields.Datetime(string="Fecha de entrega")
    total_pay = fields.Float(string="Total a pagar")
    total_pending = fields.Float(string="Pendiente por pagar")
    total_assets = fields.Float(string="Total de anticipos")
    currency_id = fields.Many2one('res.currency', string='Currency')
    total = fields.Float(string="Pago")
    is_total = fields.Boolean( string="ya esta pagado")



    @api.model
    def default_get(self,fields_list):
        res = super(DeliveryWizard,self).default_get(fields_list)
        res['date_delibery'] = fields.Datetime.now()

        currency = self.env['res.currency'].search([('name','=','MXN')])
        if currency:
            res['currency_id'] = currency.id
        
        default_total_pay = self._context.get('default_total_pay')
        if default_total_pay:
            res['total_pay'] = default_total_pay
        
        total_pending = self._context.get('default_total_pending')
        if total_pending:
            res['total_pending'] = total_pending
        
        total_assets = self._context.get('default_total_assets')
        if total_assets:
            res['total_assets'] = total_assets

        is_total = self._context.get('default_is_total')
        if is_total:
            res['is_total'] = is_total
        return res

    def confirm_delivery(self):
        model = self._context.get('active_model')
        product_model = self.env[model].browse(self._context.get('active_id'))

        if product_model.state =='cancel':
            product_model.action_delivery_cancel(self.date_delibery)
        else:
            if self.total >= product_model.total_pending:
                product_model.action_delivery(self.total,self.date_delibery,self.is_total)
            else:
                raise UserError('El pago no cubre lo pendiente')