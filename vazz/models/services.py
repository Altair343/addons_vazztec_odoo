# -*- coding:utf-8 -*-
# odoo
from odoo import models, fields,api, _
from odoo.exceptions import ValidationError,UserError

from odoo.addons.vazz_utils.tools import utils

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
    ('aux', ''),
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
    ('not', 'No'),
    ('yes', 'Sí')]

DELIVERY = [
    ('not', 'No entregado'),
    ('yes', 'Entregado')]

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
    def _compute_total_assets_ser(self):
        # Calculando el total de los anticipos
        totalAux = 0
        if self.assets_ids:
            for ass in self.assets_ids:
                totalAux = totalAux + ass.name
        self.total_assets_ser = totalAux
    
    @api.depends('assets_ids','total_assets_ser','total_assets_order')
    def _compute_total_assets(self):
        # Calculando el total de los anticipos
        self.total_assets = self.total_assets_ser + self.total_assets_order

    @api.depends('estimated_cost','total_pay_order','total_concepts')
    def _compute_total(self):
        # Calculando el total a pagar
        for rec in self:
            total_order = 0
            priceAux = 0
            total_aux_order = 0

            total_pay_order = rec.total_pay_order
            if total_pay_order:
                total_order =  total_pay_order
            if rec.estimated_cost:
                priceAux = rec.estimated_cost
            
            total_concepts = rec.total_concepts
            if total_concepts:
                total_aux_order =  total_concepts

            rec.total = priceAux + total_order + total_aux_order

    @api.depends('total','total_assets')
    def _compute_total_pending(self):
        # pendiente por pagar
        self.total_pending = self.total - self.total_assets
    
    @api.depends('notifications_ids')
    def _compute_warning_notify(self):
        for rec in self:
            if rec.notifications_ids:
                if len(rec.notifications_ids) > 0:
                    rec.warning_notify = 'yes'
                else:
                    rec.warning_notify = 'not'
            else:
                rec.warning_notify = 'not'
    
    @api.depends('concepts_ids')
    def _compute_total_concepts(self):
        totalAux = 0
        for con in self.concepts_ids:
            totalAux = totalAux + con.public_price
        self.total_concepts = totalAux


    # Estado de la solicitud
    state = fields.Selection(STATES, default=STATES[0][0], string='Estado del registro', tracking=True)
    state_aux = fields.Selection(STATES, string='Estado del registro',related="state", store= False)
    previous_state = fields.Selection(STATES,string='Estado anterior del registro' )
    name = fields.Char(string="Folio", required=True, copy=False, index=True, 
        default=lambda self: _('Nuevo'))
    date_reception = fields.Datetime(string="Fecha de recepción", default=lambda self: fields.datetime.now())
    date_approximate_delivery = fields.Date(string="Fecha de entrega aproximada")
    date_delibery = fields.Date(string="Fecha de entrega")
    customer_ids = fields.Many2one(comodel_name="vazz.customers", string="Cliente")
    telephone_cus = fields.Many2one(comodel_name="vazz.customers.phone", string="Teléfono",
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
    is_delivery = fields.Selection(DELIVERY, default=DELIVERY[0][0], string='Entrega')
    date_archive = fields.Date()
    is_archive = fields.Selection(REQUEST,default=DELIVERY[0][0], string='Archivado',tracking=True)

    # Costos
    estimated_cost = fields.Float(string="Costo estimado del servicio",tracking=True )
    assets_ids = fields.One2many(comodel_name='vazz.orders.assets',inverse_name= 'service_id', 
        string="Anticipos", ondelete='cascade')
    total_assets_ser = fields.Float(string="Total de anticipos del servicio",compute="_compute_total_assets_ser", store = False)
    total = fields.Float(string="Total a pagar",compute="_compute_total", store = False)
    total_pending = fields.Float(string="Pendiente por pagar",compute="_compute_total_pending", store = False)
    total_assets = fields.Float(string="Total de anticipos",compute="_compute_total_assets", store = False)
    
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
    warning_notify = fields.Selection(REQUEST, string='Aviso',compute="_compute_warning_notify", store = False )
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
    brand = fields.Char(string="Marca")
    model_e = fields.Char(string="Modelo" )
    imei = fields.Char(string="No. de serie / IMEI")
    type_equipment = fields.Many2one(comodel_name="vazz.equipment.type", string="Tipo de equipo")
    password = fields.Char(string="Contraseña del equipo" )
    accessories =  fields.Text(string="Accesorios")

    # Pestaña de historial de estados
    state_history_ids = fields.One2many(comodel_name='vazz.state.history',inverse_name= 'service_id', 
        string="historial de estados")
    
    # Conceptos
    total_concepts = fields.Float(string="Total de los conceptos",compute="_compute_total_concepts", store = False)
    concepts_ids = fields.One2many(comodel_name='vazz.concepts',inverse_name= 'service_id', 
        string="Conceptos")

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

        if 'imei' in vals:
            aux =''
            data = self.env['vazz.services'].search([('imei','=',vals['imei'])])
            if data:
                for ser in data:
                    aux = aux + f"{ser.name},"
                self._notify_chatter(f"El No. de serie/IMEI: {vals['imei']} existe en los siguientes servicios: {aux}")

        vals['state'] = 'pending'
        service_id = self.env['vazz.state.history'].create({
            'state': vals['state'],
            'service_id': self.id})
        vals['state_history_ids'] =  [(4, service_id.id)]

        result = super(Services, self).create(vals)
        return result

    def write(self,vals):

        if 'question_warranty' in vals:
            if vals['question_warranty'] == 'yes':
                is_warranty = False
                if len(self.warranty_ids) <= 0:
                    if 'warranty_ids' in vals:
                        if vals['warranty_ids']:
                            is_warranty = True
                        else:
                            is_book = False
                    else:
                        is_warranty = False
                else:
                    is_warranty = True

                if is_warranty == False:
                    raise UserError("Agregue por lo menos una Garantía")

        if 'imei' in vals:
            aux =''
            data = self.env['vazz.services'].search([('imei','=',vals['imei'])])
            if data:
                for ser in data:
                    aux = aux + f"{ser.name},"
                self._notify_chatter(f"El No. de serie/IMEI: {vals['imei']} existe en los siguientes servicios: {aux}")
        
        res = super(Services,self).write(vals)
        return res

    # States
    def _update_state(self, new_state):
        for rec in self:
            rec.previous_state = rec.state
            rec.state = new_state
            self.env['vazz.state.history'].create({
                'state': new_state,
                'service_id': rec.id})
    
    def action_pending(self):
        # Pendiente
        self._update_state('pending')
    
    def action_process(self):
        # En proceso
        self._update_state('in_process')
    
    def action_diagnosed(self):
        # Diagnosticado
        count = len(self.diagnostic_ids)
        if count <= 0:
            raise UserError("Agregue por lo menos un Diagnóstico")
        
        if not self.technical_id:
            raise UserError("Falta definir el técnico")
            
        self.date_archive = fields.date.today()
        self._update_state('diagnosed')
    
    def action_repaired(self):
        # Reparado
        count = len(self.diagnostic_ids)
        if count <= 0:
            raise UserError("Agregue por lo menos un Diagnóstico")
        
        if not self.technical_id:
            raise UserError("Falta definir el técnico")

        self.date_archive = fields.date.today()
        self._update_state('repaired')
    
    def action_not_solution(self):
        # Sin Solución
        count = len(self.diagnostic_ids)
        if count <= 0:
            raise UserError("Agregue por lo menos un Diagnóstico")
        
        if not self.technical_id:
            raise UserError("Falta definir el técnico")

        self.date_archive = fields.date.today()
        self._update_state('not_solution')

    def action_cancel(self, comment):
        # Cancelado
        self.date_archive = fields.date.today()
        self._update_state('cancel')
    
    def action_delivery_yes(self):
        # Entregado
        is_required = False
        text_required = ""


        if self.total_assets < self.total:
            is_required = True
            text_required = text_required + "- El servicio no ha sido pagado en su totalidad \n"

        if not self.date_delibery:
            is_required = True
            text_required = text_required + "- Agregue la fecha de entrega \n"

        if not self.question_warranty:
            is_required = True
            text_required = text_required + "- Llene el campo ¿El servicio cuenta con garantía? \n"
        
        if is_required == True:
            raise ValidationError(f"{text_required}")

        self.is_delivery = 'yes'
    
    def action_archive(self):
        # Desarchivar
        self.is_archive = 'not'

    # Onchange
    @api.onchange('customer_ids')
    def _onchange_customer_ids(self):
        if self.customer_ids:
            self.telephone_cus = self.customer_ids.phone.id 
        else:
            self.telephone_cus = False

    # Notify
    def _notify_chatter(self, body):
        if self.id:
            utils.create_chatter(self,self.id,body,'vazz.services')

    # Wizards
    def cancel_wizard(self):
        product_ids = self.env['vazz.services'].browse(self._context.get('active_ids'))
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
                    'model' : 'vazz.services',
                },
            }
        }
    
    # Crons
    def _archive_data(self):
        """
        Archivar registros
        """
        model = "vazz.services"
        current_date = fields.date.today()
        services_ids = self.env[model].search([('state','in',('diagnosed','repaired','not_solution','cancel')),('is_delivery','in',('not')),('is_archive','in',('not'))])
        for ser in services_ids:
            if ser.date_archive:
                amountAux = abs(current_date - ser.date_archive).days + 1
                if amountAux >= 40:
                    ser.is_archive = 'yes'
