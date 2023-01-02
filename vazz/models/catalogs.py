# -*- coding:utf-8 -*-
# odoo
from odoo import models, fields,api, _

STATES = [
    ('draft', 'Borrador'),
    ('pending', 'Pendiente'),
    ('in_process', 'En proceso'),
    ('diagnosed', 'Diagnosticado'),
    ('repaired', 'Reparado'),
    ('not_solution', 'Sin Solución'),

    ('done', 'Realizado'),
    ('warehouse', 'En Bodega'),
    ('in_local', 'En local'),
    ('delivered', 'Entregado'),
    ('cancel', 'Cancelado'),
    ('aux', ''),
]

class Assets(models.Model):
    _name = 'vazz.orders.assets'
    _description = 'Anticipos'

    name = fields.Float(string="Anticipo")
    date_delivery = fields.Datetime(string= "Fecha del Anticipo", default=lambda self: fields.datetime.now())
    note =  fields.Text(string="Nota")
    order_id = fields.Many2one(comodel_name="vazz.orders", string="Pedido", ondelete='cascade')
    service_id = fields.Many2one(comodel_name="vazz.services", string="Servicio", ondelete='cascade')
    currency_id = fields.Many2one( 'res.currency', string='Currency')

    @api.model
    def default_get(self, fields):
        res = super(Assets, self).default_get(fields)
        currency = self.env['res.currency'].search([('name','=','MXN')])
        if currency:
            res['currency_id'] = currency.id
        return res

class NotificationsType(models.Model):
    _name = 'vazz.notifications.type'
    _description = 'Tipos de notificaciones'

    name = fields.Char(string="Nnotificación", required= True )

class UnlocksType(models.Model):
    _name = 'vazz.unlocks.type'
    _description = 'Tipos de desbloqueos'

    name = fields.Char(string="Desbloqueo", required= True )

class EquipmentType(models.Model):
    _name = 'vazz.equipment.type'
    _description = 'Tipos de equipos'

    name = fields.Char(string="Equipo", required= True )

class Notifications(models.Model):
    _name = 'vazz.notifications'
    _description = 'Notificaciones'

    type_id = fields.Many2one(comodel_name="vazz.notifications.type", string="Medio de notificación")
    date_notification = fields.Datetime(string= "Fecha de notificación")
    note =  fields.Text(string="Nota")

    order_id = fields.Many2one(comodel_name="vazz.orders", string="Pedido", ondelete='cascade')
    service_id = fields.Many2one(comodel_name="vazz.services", string="Servicio",  ondelete='cascade')

    @api.model
    def create(self, vals):
        result = super(Notifications, self).create(vals)
        return result

class StateHistory(models.Model):
    _name = 'vazz.state.history'
    _description = 'Historial de estados'

    state = fields.Selection(STATES, string='Estado del registro')

    order_id = fields.Many2one(comodel_name="vazz.orders", string="Pedido", ondelete='cascade')
    service_id = fields.Many2one(comodel_name="vazz.services", string="Servicio",  ondelete='cascade')

class ScheduleType(models.Model):
    _name = 'vazz.schedule.type'
    _description = 'Tipos de Agenda'

    name = fields.Char(string="Tipo de agenda", required= True )
    code = fields.Char(string="Code" )

class Product(models.Model):
    _name = 'vazz.product'
    _description = 'Producto'

    @api.depends('quantity','unit_price')
    def _compute_amount(self):
        # Calculando el Importe
        for rec in self:
            quantityAux = 0
            unit_priceAux = 0

            if rec.quantity:
                quantityAux = rec.quantity
            
            if rec.unit_price:
                unit_priceAux = rec.unit_price

            rec.amount = unit_priceAux * quantityAux

    quantity = fields.Integer(string="Cantidad", default=1, tracking=True)
    description = fields.Text(string="Descripción")

    unit_price = fields.Float(string="Precio unitario")
    amount = fields.Float(string="Importe",compute="_compute_amount", store = False)

    currency_id = fields.Many2one( 'res.currency', string='Currency')
    quotation_id = fields.Many2one(comodel_name="vazz.quotation", string="Cotización", tracking=True)

    @api.model
    def default_get(self, fields):
        res = super(Product, self).default_get(fields)
        currency = self.env['res.currency'].search([('name','=','MXN')])
        if currency:
            res['currency_id'] = currency.id
        return res