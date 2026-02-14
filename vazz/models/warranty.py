# -*- coding:utf-8 -*-
# python
# odoo
from odoo import models, fields,api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

STATES = [
    ('draft','Borrador'),
    ('active','Activa'),
    ('expired','Caducada'),
]

VALIDITY = [
    ('valid','Valido'),
    ('lost','Perdido'),
]

MODEL_VAZZ_WARRANTY = "vazz.warranty"

class Customers(models.Model):
    _name = 'vazz.warranty'
    _description = 'Garantías'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"
    
    @api.depends('date_start','date_end')
    def _compute_amount_days(self):
        # Calculando el total a pagar
        amount_aux = 0
        date_start = self.date_start
        date_end = self.date_end
        if date_start and date_end:
            amount_aux = abs(date_start - date_end).days + 1

        self.amount_days = amount_aux

    state = fields.Selection(STATES, default=STATES[0][0], string='Estado del registro', tracking=True)
    name = fields.Char(string="Folio", required=True, copy=False, index=True, default=lambda self: _('Nuevo'))
    service_id = fields.Many2one(comodel_name="vazz.services", string="Servicio", tracking=True)
    customer_id = fields.Many2one(comodel_name="vazz.customers", string="Cliente")
    validity = fields.Selection(VALIDITY, default=VALIDITY[0][0], string='Validéz', tracking=True)
    date_start = fields.Date(string="Fecha de inicio", tracking=True)
    date_end = fields.Date(string="Fecha fin", tracking=True)
    amount_days = fields.Integer(string="Cantidad de días",store=False, compute="_compute_amount_days") 

    description =  fields.Text(string="Descripción")
    type_register = fields.Char(string="tipo de registro", store= False)

    # Pestaña cancelación
    cancel_request = fields.One2many(comodel_name='vazz.cancel.warranty',
        inverse_name="cancel_request", string="Cancelaciones", ondelete = "cascade")

    @api.model
    def default_get(self, fields):
        res = super(Customers, self).default_get(fields)
        type_register = self._context.get('type_register')
        if type_register:
            res['type_register'] = type_register
        else:
            res['type_register'] = 'order'
        return res

    @api.model
    def create(self, vals):
        """Método que sobrescribe el create del objeto."""
        vals['state'] = 'active'

        if 'date_start' in vals:
            date_start = vals['date_start']
        else:
            raise UserError("Agrege la fecha de inicio")
        
        if 'date_end' in vals:
            date_end = vals['date_end']
        else:
            raise UserError("Agrege la fecha fin")
        
        if date_end < date_start:
            raise UserError("La fecha fin debe ser mayor o igual a la fecha de inicio de la garantía")
        
        # Generar nombre
        name_seq = self.env['ir.sequence'].next_by_code('vazz.warranty.sequence')
        if name_seq != False:
            vals['name'] = f"G/{name_seq}"
        result = super(Customers, self).create(vals)
        return result

    # Onchange
    @api.onchange('service_id')
    def _onchange_service_id(self):
        if self.service_id:
            self.customer_id = self.service_id.customer_ids.id
    
    # States
    def _update_state(self, new_state):
        for rec in self:
            rec.state = new_state

    def action_lost(self, comment):
        # Garantía perdida
        self.validity= 'lost'
    
    def action_valid(self):
        # Garantía valida
        self.validity= 'valid'
    

    # Crons
    def _warranty_expired(self):
        """
        Caducar garantías  activas que ya pasó su fecha de cobertura
        """
        # _logger.info("Cron Caducar garantías  activas que ya pasó su fecha de cobertura")
        current_date = fields.date.today()
        warranties = self.env[MODEL_VAZZ_WARRANTY].search([('state','=','active')])

        for war in warranties:
            if war.date_end < current_date:
                war._update_state('expired')


    # Wizards
    def cancel_lost(self):
        product_ids = self.env[MODEL_VAZZ_WARRANTY].browse(self._context.get('active_ids'))
        return {
            'name' : 'Solicitud de perdida',
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
                    'model' : MODEL_VAZZ_WARRANTY,
                },
            }
        }