# -*- coding:utf-8 -*-
# odoo
from odoo import models, fields,api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

STATES = [
    ('draft','Borrador'),
    ('pending','Pendiente'),
    ('done', 'Realizado'),
    ('warehouse', 'En Bodega'),
    ('in_local', 'En local'),
    ('delivered', 'Entregado'),
    ('cancel', 'Cancelado'),

    ('aux', ''),
]

class Order(models.Model):
    _name = 'vazz.orders'
    _description = 'Pedidos'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"
    
    @api.depends('assets_ids')
    def _compute_total_assets(self):
        # Calculando el total de los anticipos
        totalAux = 0
        if self.assets_ids:
            for ass in self.assets_ids:
                totalAux = totalAux + ass.name
        self.total_assets = totalAux

    @api.depends('amount','public_price')
    def _compute_total(self):
        # Calculando el total a pagar
        for rec in self:
            amountAux = 1
            priceAux = 0

            public_price= rec.public_price
            amount = rec.amount 

            if amount:
                amountAux = amount
            if public_price:
                priceAux = public_price

            totalAux = amountAux * priceAux
            rec.total = totalAux

    @api.depends('total','total_assets')
    def _compute_total_pending(self):
        self.total_pending = self.total - self.total_assets


    # Estado de la solicitud
    state = fields.Selection(STATES, default=STATES[0][0], string='Estado del registro', tracking=True)
    previous_state = fields.Selection(STATES,string='Estado anterior del registro' )

    name = fields.Char(string="Folio", required=True, copy=False, index=True, default=lambda self: _('Nuevo'))
    service_id = fields.Many2one(comodel_name="vazz.services", string="Servicio", tracking=True)
    customer_id = fields.Many2one(comodel_name="vazz.customers", string="Cliente")
    tracking_number = fields.Char(string="No. de rastreo")
    
    amount = fields.Integer(string="Cantidad", default=1, tracking=True) 
    public_price = fields.Float(string="Precio público por unidad",tracking=True )
    assets_ids = fields.One2many(comodel_name='vazz.orders.assets',inverse_name= 'order_id', 
        string="Anticipos", ondelete='cascade')
    total_assets = fields.Float(string="Total de anticipos",compute="_compute_total_assets", store = False)
    total = fields.Float(string="Total a pagar",compute="_compute_total", store = False)
    total_pending = fields.Float(string="Pendiente por pagar",compute="_compute_total_pending", store = False)

    date_approximate_delivery = fields.Date(string="Fecha de entrega aproximada de inicio")
    date_approx_del_end = fields.Date(string="Fecha de entrega aproximada fin")
    date_arrival = fields.Date(string="Fecha de llegada", tracking=True)

    date_delivery = fields.Datetime(string= "Fecha de entrega al cliente",tracking=True)
    description =  fields.Text(string="Descripción", tracking=True)

    currency_id = fields.Many2one( 'res.currency', string='Currency')
    type_register = fields.Char(string="tipo de registro", store= False)
    
    # Pestaña Notificaciones
    notifications_ids = fields.One2many(comodel_name='vazz.notifications',inverse_name= 'order_id', 
        string="Notificaciones", ondelete='cascade')

    # Pestaña cancelación
    cancel_request = fields.One2many(comodel_name='vazz.cancel.orders',
        inverse_name="cancel_request", string="Cancelaciones", ondelete = "cascade")

    # Pestaña de historial de estados
    state_history_ids = fields.One2many(comodel_name='vazz.state.history',inverse_name= 'order_id', 
        string="historial de estados")

    @api.model
    def default_get(self, fields):
        res = super(Order, self).default_get(fields)
        currency = self.env['res.currency'].search([('name','=','MXN')])
        if currency:
            res['currency_id'] = currency.id

        type_register = self._context.get('type_register')
        if type_register:
            res['type_register'] = type_register
        else:
            res['type_register'] = 'order'
        return res

    @api.model
    def create(self, vals):
        """Método que sobrescribe el create del objeto."""

        # if 'service_id' not in vals:
        #     # Validando que tenga un anticipo
        #     is_assets = False
        #     if len(self.assets_ids) <= 0:
        #         if 'assets_ids' in vals:
        #             if vals['assets_ids']:
        #                 is_assets = True
        #             else:
        #                 is_assets = False
        #         else:
        #             is_assets = False
        #         if is_assets == False:
        #             raise UserError("Agregue por lo menos un Anticipo al pedido")

        vals['state'] = 'pending'
        vals['previous_state'] = 'draft'

        # Generar nombre
        name_seq = self.env['ir.sequence'].next_by_code('vazz.orders.sequence')
        if name_seq != False:
            vals['name'] = f"P/{name_seq}"
        result = super(Order, self).create(vals)
        return result


    # Onchange
    @api.onchange('service_id')
    def _onchange_service_id(self):
        if self.service_id:
            self.customer_id = self.service_id.customer_ids.id
            self.date_approximate_delivery = self.service_id.date_approximate_delivery


    # States
    def _update_state(self, new_state):
        for rec in self:
            rec.previous_state = rec.state
            rec.state = new_state

    def action_done(self):
        # Realizado
        if not self.tracking_number:
            raise UserError("Agregue el número de rastreo")
        self._update_state('done')

    def action_warehouse(self):
        # En Bodega
        if not self.date_arrival:
            raise UserError("Agregue la fecha de llegada")
        self._update_state('warehouse')

    def action_local(self):
        # En local
        self._update_state('in_local')

    def action_delivered(self):
        # Entregado
        if not self.date_delivery:
            raise UserError("Agregue la fecha de entrega al cliente")

        if self.total_assets < self.total:
            raise UserError("El pedido no ha sido pagado en su totalidad")

        self._update_state('delivered')

    def action_cancel(self, comment):
        # Cancelado
        self._update_state('cancel')
    

    # Wizards
    def cancel_wizard(self):
        product_ids = self.env['vazz.orders'].browse(self._context.get('active_ids'))
        return {
            'name' : 'Solicitud de Cancelación',
            'type' : 'ir.actions.act_window',
            'res_model' : 'vazz.cancel_wizard',
            'view_mode' : 'form',
            'view_type' : 'form',
            'views' : [(False,'form')],
            'view_id' : self.env.ref('vazz.cancel_request_vazz_view_form').id,
            'target' : 'new',
            'context' : {
                'uid' : self._context.get('uid'),
                'default_id' : product_ids,
                'params' : {
                    'id' : self.id,
                    'model' : 'vazz.orders',
                },
            }
        }




