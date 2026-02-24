# -*- coding:utf-8 -*-
# odoo
from odoo import models, fields,api, _

class Unlocks(models.Model):
    _name = 'vazz.unlocks'
    _description = 'Desbloqueos'

    name = fields.Char(string="Folio", required=True, copy=False, index=True, 
        default=lambda self: _('Nuevo'))
    
    service_id = fields.Many2one(comodel_name="vazz.services", string="Servicio")
    customer_id = fields.Many2one(comodel_name="vazz.customers", string="Cliente")
    type_id = fields.Many2one(comodel_name="vazz.unlocks.type", string="Tipo de desbloqueo")
    type_register = fields.Char(string="tipo de registro", store= False)

    @api.model
    def default_get(self, fields):
        res = super(Unlocks, self).default_get(fields)
        type_register = self._context.get('type_register')
        if type_register:
            res['type_register'] = type_register
        else:
            res['type_register'] = 'order'
        return res
        
    @api.model
    def create(self, vals):
        # Generar nombre
        name_seq = self.env['ir.sequence'].next_by_code('vazz.unlocks.sequence')
        if name_seq != False:
            vals['name'] = f"D/{name_seq}"
        result = super(Unlocks, self).create(vals)
        return result

    # Onchange
    @api.onchange('service_id')
    def _onchange_service_id(self):
        if self.service_id:
            self.customer_id = self.service_id.customer_ids.id