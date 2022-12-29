# -*- coding:utf-8 -*-
# odoo
from odoo import models, fields,api, _
from odoo.exceptions import ValidationError,UserError

import logging
_logger = logging.getLogger(__name__)

STATES = [
    ('draft', 'Borrador'),
    ('pending', 'Pendiente'),
    ('in_process', 'En proceso'),
    ('diagnosed', 'Diagnosticado'),
    ('repaired', 'Reparado'),
    ('not_solution', 'Sin Solución'),

    ('cancel', 'Cancelado'),
]

TYPESERVICES = [
    ('support', 'Soporte'),
    ('unlock', 'Desbloqueo')]

TYPEDELIVERY = [
    ('in_local', 'En el Local'),
    ('home', 'Domicilio')]

TYPEENTRY= [
    ('local', 'Local'),
    ('harvest', 'Recolección'),
    ('home_service', 'Servicio a domicilio'),
    ('remote', 'Remoto (a distancia)')]

REQUEST = [
    ('yes', 'Sí'),
    ('not', 'No')]

class Services(models.Model):
    _name = 'vazz.services'
    _description = 'Servicios'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    @api.depends('orders_ids')
    def _compute_total_pay_order(self):
        totalAux = 0
        for order in self.orders_ids:
            totalAux = totalAux + order.total
        self.total_pay_order = totalAux
    
    @api.depends('orders_ids')
    def _compute_total_assets_order(self):
        totalAux = 0
        for order in self.orders_ids:
            totalAux = totalAux + order.total_assets
        self.total_assets_order = totalAux
    
    @api.depends('assets_ids')
    def _compute_total_assets(self):
        # Calculando el total de los anticipos
        totalAux = 0
        if self.assets_ids:
            for ass in self.assets_ids:
                totalAux = totalAux + ass.name
        self.total_assets = totalAux

    @api.depends('estimated_cost','total_pay_order')
    def _compute_total(self):
        # Calculando el total a pagar
        for rec in self:
            total_order = 0
            priceAux = 0

            total_pay_order = rec.total_pay_order
            if total_pay_order:
                total_order =  total_pay_order
            if rec.estimated_cost:
                priceAux = rec.estimated_cost
            
            rec.total = priceAux + total_order


    # Estado de la solicitud
    state = fields.Selection(STATES, default=STATES[0][0], string='Estado del registro', tracking=True)
    previous_state = fields.Selection(STATES,string='Estado anterior del registro' )
    name = fields.Char(string="Folio", required=True, copy=False, index=True, 
        default=lambda self: _('Nuevo'))
    date_reception = fields.Datetime(string="Fecha de recepción")
    date_approximate_delivery = fields.Date(string="Fecha de entrega aproximada")
    customer_ids = fields.Many2one(comodel_name="vazz.customers", string="Cliente")
    telephone_cus = fields.Many2one(comodel_name="vazz.customers.phone", string="teléfono",
    domain = "[('customer_ids','=',customer_ids)]")
    type_service = fields.Selection(TYPESERVICES, string='Tipo de servicio', tracking=True)
    type_delivery = fields.Selection(TYPEDELIVERY, string='Tipo de entrega solicitada', tracking=True)
    addres =  fields.Text(string="Dirección de entrega")
    description =  fields.Text(string="Descripción de la falla")
    observations =  fields.Text(string="Observaciones")

    type_entry = fields.Selection(TYPEENTRY, string='Tipo de ingreso', tracking=True)
    addres_entry =  fields.Text(string="Dirección de ingreso")

    diagnostic_ids = fields.One2many(comodel_name='vazz.diagnostic',inverse_name= 'service_id', 
        string="Diagnósticos", ondelete='cascade')
    technical_id = fields.Many2one( 'res.users', string='Técnico', domain = "[('type_user_va','=','technical')]")

    # Costos
    estimated_cost = fields.Float(string="Costo estimado",tracking=True )
    assets_ids = fields.One2many(comodel_name='vazz.orders.assets',inverse_name= 'service_id', 
        string="Anticipos", ondelete='cascade')
    total_assets = fields.Float(string="Total de anticipos del servicio",compute="_compute_total_assets", store = False)
    total = fields.Float(string="Total a pagar",compute="_compute_total", store = False)

    # Pestaña de pedidos
    currency_id = fields.Many2one( 'res.currency', string='Currency')
    total_pay_order = fields.Float(string="Total a pagar de pedidos",compute="_compute_total_pay_order", store = False)
    total_assets_order = fields.Float(string="Total de anticipos de pedidos",compute="_compute_total_assets_order", store = False)
    orders_ids = fields.One2many(comodel_name='vazz.orders',inverse_name= 'service_id', 
        string="Pedidos")

    # Pestaña cancelación
    cancel_request = fields.One2many(comodel_name='vazz.cancel.services',
        inverse_name="cancel_request", string="Cancelaciones", ondelete = "cascade")
    
    # Pestaña notificación
    notifications_ids = fields.One2many(comodel_name='vazz.notifications',inverse_name= 'service_id', 
        string="Notificaciones", ondelete='cascade')
    type_notification_id = fields.Many2one(comodel_name="vazz.notifications.type", string="Medio de notificación preferido")

    # Pestaña de garantias
    question_warranty = fields.Selection(REQUEST, string='¿El servicio cuenta con garantía?', tracking=True)
    question_whats =  fields.Text(string="¿Por qué?")
    warranty_ids = fields.One2many(comodel_name='vazz.warranty',inverse_name= 'service_id', 
        string="Garantías", ondelete='cascade')

    # Pestaña de Desbloqueo
    unlocks_ids = fields.One2many(comodel_name='vazz.unlocks',inverse_name= 'service_id', 
        string="Desbloqueos", ondelete='cascade')

    # Pestaña de Equipo
    equipment_ids = fields.One2many(comodel_name='vazz.equipment',inverse_name= 'service_id', 
        string="Equipos", ondelete='cascade')

    # Pestaña de historial de estados
    state_history_ids = fields.One2many(comodel_name='vazz.state.history',inverse_name= 'service_id', 
        string="historial de estados")
        
    @api.model
    def default_get(self, fields):
        res = super(Services, self).default_get(fields)
        currency = self.env['res.currency'].search([('name','=','MXN')])
        if currency:
            res['currency_id'] = currency.id
        return res

    @api.model
    def create(self, vals):
        if vals['type_service'] == 'unlock':
            # Validando que tenga un desbloqueo
            is_unlocks = False
            if len(self.unlocks_ids) <= 0:
                if 'unlocks_ids' in vals:
                    if vals['unlocks_ids']:
                        is_unlocks = True
                    else:
                        is_unlocks = False
                else:
                    is_unlocks = False
                if is_unlocks == False:
                    raise UserError("Agregue por lo menos un desbloqueo")

        # Generar nombre
        name_seq = self.env['ir.sequence'].next_by_code('vazz.services.sequence')
        if name_seq != False:
            vals['name'] = f"S/{name_seq}"

        vals['state'] = 'pending'
        service_id = self.env['vazz.state.history'].create({
            'state': vals['state'],
            'service_id': self.id})
        vals['state_history_ids'] =  [(4, service_id.id)]
        result = super(Services, self).create(vals)
        return result

    # States
    def _update_state(self, new_state):
        for rec in self:
            rec.previous_state = rec.state
            rec.state = new_state
            self.env['vazz.state.history'].create({
                'state': new_state,
                'service_id': rec.id})
            # se crea registro
    
    def action_pending(self):
        # Pendiente
        self._update_state('pending')
    
    def action_process(self):
        # En proceso
        self._update_state('in_process')
    
    def action_diagnosed(self):
        # Diagnosticado
        self._update_state('diagnosed')
    
    def action_repaired(self):
        # Reparado
        self._update_state('repaired')
    
    def action_not_solution(self):
        # Sin Solución
        self._update_state('not_solution')

    def action_cancel(self, comment):
        # Cancelado
        self._update_state('cancel')

    # Onchange
    @api.onchange('customer_ids')
    def _onchange_customer_ids(self):
        if self.customer_ids:
            self.telephone_cus = self.customer_ids.phone.id 
        else:
            self.telephone_cus = False
