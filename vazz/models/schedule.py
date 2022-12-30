# -*- coding:utf-8 -*-
# odoo
from odoo import models, fields,api, _

STATES = [
    ('draft', 'Borrador'),
    ('pending','Pendiente'),
    ('ok','Listo'),
    ('cancel', 'Cancelado'),
    ('aux', ''),
]

class Schedule(models.Model):
    _name = 'vazz.schedule'
    _description = 'Agenda'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    state = fields.Selection(STATES, default=STATES[0][0], string='Estado del registro B', tracking=True)
    state_aux = fields.Selection(STATES, string='Estado del registro',related="state", store= False)
    name = fields.Char(string="Folio", required=True, copy=False, index=True, default=lambda self: _('Nuevo'))
    service_ids = fields.Many2many(comodel_name="vazz.services", string="Servicios")

    customer_id = fields.Many2one(comodel_name="vazz.customers", string="Cliente",tracking=True)
    telephone_cus = fields.Many2one(comodel_name="vazz.customers.phone", string="Teléfono",tracking=True,
    domain = "[('customer_ids','=',customer_id)]")

    type_schedule_id = fields.Many2one(comodel_name="vazz.schedule.type", string="Tipo de agenda",tracking=True)
    code_schedule = fields.Char(related="type_schedule_id.code")
    date_scheduled = fields.Date(string="Fecha programada",tracking=True)
    hour_scheduled = fields.Char(string="Hora programada",tracking=True)

    addres =  fields.Text(string="Dirección",tracking=True)
    description =  fields.Text(string="Descripción",tracking=True)

    # Pestaña cancelación
    cancel_request = fields.One2many(comodel_name='vazz.cancel.schedule',
        inverse_name="cancel_request", string="Cancelaciones", ondelete = "cascade")

    @api.model
    def create(self, vals):
        """Método que sobrescribe el create del objeto."""
        vals['state'] = 'pending'
        
        # Generar nombre
        name_seq = self.env['ir.sequence'].next_by_code('vazz.schedule.sequence')
        if name_seq != False:
            vals['name'] = f"A/{name_seq}"
        result = super(Schedule, self).create(vals)
        return result
    
    # States
    def _update_state(self, new_state):
        for rec in self:
            rec.state = new_state
    
    def action_cancel(self, comment):
        # Cancelado
        self._update_state('cancel')

    def action_ok(self):
        # Listo
        self._update_state('ok')
    
    def action_pending(self):
        # Pendiente
        self._update_state('pending')
    
    # Wizards
    def cancel_wizard(self):
        product_ids = self.env['vazz.schedule'].browse(self._context.get('active_ids'))
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
                    'model' : 'vazz.schedule',
                },
            }
        }
    
    # Onchange
    @api.onchange('customer_id')
    def _onchange_customer_id(self):
        if self.customer_id:
            self.telephone_cus = self.customer_id.phone.id 
        else:
            self.telephone_cus = False

