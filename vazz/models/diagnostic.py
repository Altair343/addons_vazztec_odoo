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

    ('cancel', 'Cancelado'),
    ('aux', ''),
]

class Assets(models.Model):
    _name = 'vazz.diagnostic'
    _description = 'Diagnósticos'

    state = fields.Selection(STATES, string='Estado del servicio')
    name = fields.Text(string="Descripción")
    service_id = fields.Many2one(comodel_name="vazz.services", string="Servicio", ondelete='cascade')
    technical_id = fields.Many2one( 'res.users', string='Técnico', domain = "[('type_user_va','=','technical')]")
    is_main = fields.Boolean(string="Principal") # si esta activo es el principal
    is_edit = fields.Boolean(default = True)
    state_service = fields.Selection(STATES, related="service_id.state", store= False)
    
    @api.model
    def default_get(self, fields):
        res = super(Assets, self).default_get(fields)
        default_state = self._context.get('default_state')
        if default_state:
            res['state'] = default_state
        return res

    @api.model
    def create(self, vals):
        if vals['state'] == 'draft' or vals['state'] == 'aux':
            vals['state'] = 'pending'
        
        if 'service_id' in vals:
            service = self.env['vazz.services'].search([('id','=',vals['service_id'])])
            if service:
                service.diagnostic_ids.is_main = False
                service._update_state(vals['state'])
        vals['is_main'] = True
        vals['is_edit'] = False

        result = super(Assets, self).create(vals)
        return result

    def write(self,vals):
        vals['is_edit'] = False
        res = super(Assets,self).write(vals)
        return res

    # Onchange
    @api.onchange('service_id')
    def _onchange_service_id(self):
        if self.service_id:
            self.technical_id = self.service_id.technical_id.id
            