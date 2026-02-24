# -*- coding:utf-8 -*-
# 2 : imports of odoo
from odoo import models, fields,api, _
from odoo.exceptions import ValidationError,UserError
# 3 : imports from odoo addons
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

MODEL_VAZZ_SERVICES = "vazz.services"
MODEL_VAZZ_STATE_HISTORY = "vazz.state.history"
TEXT_ADD_AT_LEAST_DIA = "Add at least one Diagnosis."
TEXT_TECHNICIAN = "The technician must be defined."

class Services(models.Model):
    _name = 'vazz.services'
    _description = 'Servicios'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    @api.depends('orders_ids')
    def _compute_total_pay_order(self):
        # total a pagar de pedidos
        total_aux = 0
        for order in self.orders_ids:
            if order.state != 'cancel':
                total_aux = total_aux + order.total
        self.total_pay_order = total_aux

    @api.depends('orders_ids')
    def _compute_total_assets_order(self):
        for rec in self:
            total_aux = 0
            for order in rec.orders_ids:
                # if order.state != 'cancel':
                for ass in order.assets_ids:
                    total_aux = total_aux + ass.name
            rec.total_assets_order = total_aux


    @api.depends('assets_ids')
    def _compute_total_assets_ser(self):
        # Calculando el total de los anticipos
        total_aux = 0
        if self.assets_ids:
            for ass in self.assets_ids:
                total_aux = total_aux + ass.name
        self.total_assets_ser = total_aux
    
    @api.depends('assets_ids','total_assets_ser','total_assets_order')
    def _compute_total_assets(self):
        # Calculando el total de los anticipos
        self.total_assets = self.total_assets_ser + self.total_assets_order

    @api.depends('total_pay_order','total_concepts')
    def _compute_total(self):
        # Calculando el total a pagar
        for rec in self:
            total_order = 0
            total_aux_concepts = 0

            total_pay_order = rec.total_pay_order
            if total_pay_order:
                total_order =  total_pay_order
            
            total_concepts = rec.total_concepts
            if total_concepts:
                total_aux_concepts =  total_concepts

            rec.total = total_order + total_aux_concepts

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
        total_aux = 0
        for con in self.concepts_ids:
            total_aux = total_aux + con.public_price
        self.total_concepts = total_aux


    # Estado de la solicitud
    state = fields.Selection(STATES, default=STATES[0][0], string='Estado del registro', tracking=True)
    state_aux = fields.Selection(STATES, string='Estado del registro',related="state", store= False)
    previous_state = fields.Selection(STATES,string='Estado anterior del registro' )
    name = fields.Char(string="Folio", required=True, copy=False, index=True, 
        default=lambda self: _('Nuevo'))
    date_reception = fields.Datetime(string="Fecha de recepción", default=lambda self: fields.Datetime.now())
    date_approximate_delivery = fields.Date(string="Fecha de entrega aproximada")
    date_delibery = fields.Datetime(string="Fecha de entrega")
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
    is_archive = fields.Selection(REQUEST,default=REQUEST[0][0], string='Archivado',tracking=True)

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
    code_type_notification = fields.Char(related="type_notification_id.code")
    
    # Pestaña de garantias
    question_warranty = fields.Selection(REQUEST, string='¿El servicio cuenta con garantía?', tracking=True)
    question_whats =  fields.Text(string="¿Por qué?")
    warranty_ids = fields.One2many(comodel_name='vazz.warranty',inverse_name= 'service_id', 
        string="Garantías", ondelete='cascade')

    # Pestaña de Desbloqueo
    unlocks_ids = fields.One2many(comodel_name='vazz.unlocks',inverse_name= 'service_id', 
        string="Desbloqueos", ondelete='cascade')

    # Check status express
    question_check_status = fields.Selection(REQUEST,string="Check status ingreso equipo?")
    question_question_check =  fields.Text(string="Motivo")
    check_status_ids = fields.One2many(comodel_name='vazz.check.status',inverse_name= 'service',
        string="Check status express", ondelete='cascade')
    check_status_id = fields.Many2one(comodel_name='vazz.check.status', string="Check status express",
        compute='_compute_last_check_status_id' )

    # Pestaña de Equipo
    brand = fields.Char(string="Marca")
    model_e = fields.Char(string="Modelo" )
    imei = fields.Char(string="No. de serie / IMEI")
    type_equipment = fields.Many2one(comodel_name="vazz.equipment.type", string="Tipo de equipo")
    password = fields.Char(string="Contraseña del equipo" )

    question_acce = fields.Selection(REQUEST, string='¿Tiene accesorios?')
    accessories =  fields.Text(string="Accesorios")

    # Pestaña de historial de estados
    state_history_ids = fields.One2many(comodel_name=MODEL_VAZZ_STATE_HISTORY,inverse_name= 'service_id', 
        string="historial de estados")

    # Conceptos
    total_concepts = fields.Float(string="Total de los conceptos",compute="_compute_total_concepts", store = False)
    concepts_ids = fields.One2many(comodel_name='vazz.concepts',inverse_name= 'service_id', 
        string="Conceptos")

    # Roles
    is_group_rol002 = fields.Boolean(default=lambda self: self._default_is_group_rol002(),
        compute="_compute_is_group_rol002")

    # Migración
    old_id = fields.Integer(string='old_id')

    # compute
    @api.depends('is_group_rol002')
    def _compute_is_group_rol002(self):
        self.is_group_rol002 = utils.has_group(self,'vazz.Rol002')

    @api.depends('check_status_ids')
    def _compute_last_check_status_id(self):
        for record in self:
            request =  False
            for obj in reversed(record.check_status_ids):
                request  = obj.id
                break
            record.check_status_id = request

    # Defaults
    @api.model
    def _default_is_group_rol002(self):
        return utils.has_group(self,'vazz.Rol002')

    @api.model
    def default_get(self, fields):
        res = super(Services, self).default_get(fields)
        currency = self.env['res.currency'].search([('name','=','MXN')])
        if currency:
            res['currency_id'] = currency.id

        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            migration_creation = self._context.get('migration_creation', False)
            if not migration_creation:
                self.validate_unlocks(vals)
                self.validate_question_check_status(vals)

                vals['state'] = 'pending'
                service_id = self.env[MODEL_VAZZ_STATE_HISTORY].create({
                    'state': vals['state'],
                    'service_id': self.id
                })
                vals['state_history_ids'] = [(4, service_id.id)]

        results = super().create(vals_list)

        for result in results:
            result.set_name()
            result.ntf_imei()

        return results

    def write(self,vals):
        migration_creation = self._context.get('migration_creation') if 'migration_creation' in self._context else False
        if not migration_creation:
            self.validate_unlocks(vals)
            self.validate_question_check_status(vals)

            if vals.get('imei'):
                aux =''
                data = self.env[MODEL_VAZZ_SERVICES].search([('imei','=',vals['imei']),('id','!=',self.id)])
                if data:
                    for ser in data:
                        aux = aux + f"{ser.name},"
                    self._notify_chatter(f"El No. de serie/IMEI: {vals['imei']} existe en los siguientes servicios: {aux}")

        res = super(Services,self).write(vals)
        return res

    # Validation create
    def set_name(self):
        """Generate name"""
        name_seq = self.env['ir.sequence'].next_by_code('vazz.services.sequence')
        if name_seq != False:
            self.name = f"S/{name_seq}"

    def ntf_imei(self):
        if self.imei:
            aux =''
            data = self.env[MODEL_VAZZ_SERVICES].search([('imei','=',self.imei),('id','!=',self.id)])
            if data:
                for ser in data:
                    aux = aux + f"{ser.name},"
                mensaje = f"El No. de serie/IMEI: {self.imei} existe en los siguientes servicios: {aux}"
                if self.observations:
                    self.observations = f"{self.observations}, {mensaje}"
                else:
                    self.observations = f"{mensaje}"
                self._notify_chatter(mensaje)

    def validate_question_check_status(self,vals):
        """Validating check status express"""
        if vals.get('question_check_status') == 'yes':
            is_check_status = False
            if len(self.check_status_ids) <= 0:
                if 'check_status_ids' in vals and vals['check_status_ids']:
                    is_check_status = True
                if is_check_status == False:
                    raise UserError(_("Add at least one Express Check Status."))

    def validate_unlocks(self,vals):
        """Validating that it has at least one unlock."""
        if vals.get('type_service') == 'unlock':
            has_existing_unlocks = len(self.unlocks_ids) > 0
            has_new_unlocks = bool(vals.get('unlocks_ids'))
            if not (has_existing_unlocks or has_new_unlocks):
                raise UserError(_("Add at least one unlock."))

    # States
    def _update_state(self, new_state):
        for rec in self:
            rec.previous_state = rec.state
            rec.state = new_state
            self.env[MODEL_VAZZ_STATE_HISTORY].create({
                'state': new_state,
                'service_id': rec.id})
    
    def action_pending(self):
        # Pendiente
        self._update_state('pending')
    
    def action_process(self):
        # En proceso
        if self.imei:
            aux =''
            data = self.env[MODEL_VAZZ_SERVICES].search([('imei','=',self.imei),('id','!=',self.id)])
            if data:
                for ser in data:
                    if ser.id != self.id:
                        aux = aux + f"{ser.name},"
                self._notify_chatter(f"El No. de serie/IMEI: {self.imei} existe en los siguientes servicios: {aux}")
        self._update_state('in_process')
    
    def action_diagnosed(self):
        # Diagnosticado
        count = len(self.diagnostic_ids)
        if count <= 0:
            raise UserError(_(TEXT_ADD_AT_LEAST_DIA))
        
        if not self.technical_id:
            raise UserError(_(TEXT_TECHNICIAN))
            
        self.date_archive = fields.date.today()
        self._update_state('diagnosed')
    
    def action_repaired(self):

        if not self.question_warranty:
            raise UserError(_("Please answer the question “Does the service have a warranty?” in the Warranties tab."))

        if self.question_warranty and self.question_warranty =='yes':
            if len(self.warranty_ids) <= 0:
                raise UserError(_("Add at least one warranty."))

        # Reparado
        count = len(self.diagnostic_ids)
        if count <= 0:
            raise UserError(_(TEXT_ADD_AT_LEAST_DIA))
        
        if not self.technical_id:
            raise UserError(_(TEXT_TECHNICIAN))

        self.date_archive = fields.date.today()
        self._update_state('repaired')
    
    def action_not_solution(self):
        # Sin Solución
        count = len(self.diagnostic_ids)
        if count <= 0:
            raise UserError(_(TEXT_ADD_AT_LEAST_DIA))
        
        if not self.technical_id:
            raise UserError(_(TEXT_TECHNICIAN))

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
        
        if self.state != 'cancel' and len(self.concepts_ids) <= 0:
            is_required = True
            text_required = text_required + "- Add at least one concept."
        if is_required == True:
            raise ValidationError(f"{text_required}")

        return self.delivery_wizard()

    def action_archive(self):
        # Desarchivar
        self.is_archive = 'not'

    def action_delivery(self,total,date_delibery,is_total):
        if is_total == False:
            self.env['vazz.orders.assets'].create({
                'name': total,
                'note': 'Pago generado al entregar',
                'service_id': self.id})
        self.date_delibery = date_delibery
        self.is_delivery = 'yes'

        for order in self.orders_ids:
            order._update_state('delivered')
    
    def action_delivery_cancel(self,date_delibery):
        self.date_delibery = date_delibery
        self.is_delivery = 'yes'


    # Onchange
    @api.onchange('customer_ids')
    def _onchange_customer_ids(self):
        if self.customer_ids:
            self.telephone_cus = self.customer_ids.phone.id
            if self.type_entry == 'harvest' and not self.addres_entry:
                self.addres_entry = self.customer_ids.addres
        else:
            self.telephone_cus = False

    @api.onchange('type_entry')
    def _onchange_type_entry(self):
        if self.type_entry == 'harvest':
            if self.addres_entry:
                self.addres_entry = self.customer_ids.addres
        else:
            self.addres_entry = False
    
    @api.onchange('addres_entry')
    def _onchange_addres_entry(self):
        if self.addres_entry:
            if self.type_delivery == 'home':
                self.addres = self.addres_entry
            else:
                self.addres = False

    @api.onchange('type_delivery')
    def _onchange_type_delivery(self):
        if self.type_delivery:
            if self.type_delivery == 'home':
                self.addres = self.addres_entry
            else:
                self.addres = False

    # Notify
    def _notify_chatter(self, body):
        if self.id:
            utils.create_chatter(self,self.id,body,MODEL_VAZZ_SERVICES)

    # Wizards
    def cancel_wizard(self):
        product_ids = self.env[MODEL_VAZZ_SERVICES].browse(self._context.get('active_ids'))
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
                    'model' : MODEL_VAZZ_SERVICES,
                },
            }
        }
    
    def delivery_wizard(self):
        product_ids = self.env[MODEL_VAZZ_SERVICES].browse(self._context.get('active_ids'))

        if self.total_assets >= self.total:
            is_total = True
        else:
            is_total = False
            
        return {
            'name' : 'Entrega',
            'type' : 'ir.actions.act_window',
            'res_model' : 'vazz.delivery.wizard',
            'view_mode' : 'form',
            'view_type' : 'form',
            'views' : [(False,'form')],
            'view_id' : self.env.ref('vazz.delivery_wizard_vazz_view_form').id,
            'target' : 'new',
            'context' : {
                'default_total_pay': self.total,
                'default_is_total': is_total,
                'default_total_pending': self.total_pending,
                'default_total_assets': self.total_assets,
                'uid' : self._context.get('uid'),
                'default_id' : product_ids,
                'params' : {
                    'id' : self.id,
                    'model' : MODEL_VAZZ_SERVICES,
                },
            }
        }

    # Crons
    def _archive_data(self):
        """
        Archivar registros
        """
        # Día actual
        current_date = fields.date.today()

        # Obtenemos los registros que no esten entregados y archivados
        services_ids = self.env[MODEL_VAZZ_SERVICES].search([('is_delivery','=','not'),('is_archive','=','not')])
        for ser in services_ids:
            if ser.date_archive:
                amount_aux = abs(current_date - ser.date_archive).days + 1
                if ser.state in ('repaired','diagnosed','not_solution'):
                    if amount_aux >= 30:
                        ser.is_archive = 'yes'
                else:
                    if amount_aux >= 90:
                        ser.is_archive = 'yes'

