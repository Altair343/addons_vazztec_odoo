# -*- coding:utf-8 -*-
# odoo
from odoo import models, fields,api, _

class Assets(models.Model):
    _name = 'vazz.diagnostic'
    _description = 'Diagnósticos'

    name = fields.Text(string="Descripción")
    service_id = fields.Many2one(comodel_name="vazz.services", string="Servicio", ondelete='cascade')
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