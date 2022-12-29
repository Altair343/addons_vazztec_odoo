# -*- coding:utf-8 -*-
# odoo
from odoo import models, fields,api, _

class Assets(models.Model):
    _name = 'vazz.diagnostic'
    _description = 'Diagnósticos'

    name = fields.Text(string="Descripción")
    service_id = fields.Many2one(comodel_name="vazz.services", string="Servicio", ondelete='cascade')
    technical_id = fields.Many2one( 'res.users', string='Técnico', domain = "[('type_user_va','=','technical')]")
    is_main = fields.Boolean(string="Principal") # si esta activo es el principal

    @api.model
    def create(self, vals):
        if 'service_id' in vals:
            service = self.env['vazz.services'].search([('id','=',vals['service_id'])])
            if service:
                service.diagnostic_ids.is_main = False
        vals['is_main'] = True
        result = super(Assets, self).create(vals)
        return result
    
    # Onchange
    @api.onchange('service_id')
    def _onchange_service_id(self):
        if self.service_id:
            self.technical_id = self.service_id.technical_id.id
            