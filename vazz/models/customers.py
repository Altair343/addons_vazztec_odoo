# -*- coding:utf-8 -*-
from odoo import models, fields,api, _

class Customers(models.Model):
    _name = 'vazz.customers'
    _description = 'Clientes'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.depends('phones_ids')
    def _compute_phone(self):
        # buscar el teléfono principal
        for rec in self:
            phoneAux = ''
            if rec.phones_ids:
                for tel in rec.phones_ids:
                    if tel.is_main == True:
                        phoneAux = tel.name
                        break
            rec.phone = phoneAux

    @api.depends('user_name','user_name','email','addres','phones_ids')
    def _compute_count_services(self):
        countAux = 0
        model = "vazz.services"
        services = self.env[model].search([('customer_ids','=',self.id)])
        if services:
            countAux = len(services)
        self.count_services = countAux
    
    name = fields.Char(string="Folio", default=lambda self: _('Nuevo'))
    user_name = fields.Char(string="Nombre completo")
    email =  fields.Char(string="Correo")
    addres =  fields.Text(string="Dirreción")
    phone =  fields.Char(string="Teléfono principal",compute="_compute_phone", store = False)
    phones_ids = fields.One2many(comodel_name='vazz.customers.phone',inverse_name= 'customer_ids', 
        string="Teléfono", ondelete = "cascade")
    count_services = fields.Integer(string="Total de Servicios", compute="_compute_count_services", store = False) 
    
    
    @api.model
    def create(self, vals):
        
        # Generar nombre
        name_seq = self.env['ir.sequence'].next_by_code('vazz.customers.sequence')
        if name_seq != False:
            vals['name'] = f"C/{name_seq}"

        result = super(Customers, self).create(vals)
        return result


    def name_get(self):
        res = []
        for record in self:
            customers = record.env['vazz.customers'].browse([record['id']])
            name = f"{customers.user_name}"
            
            res.append((record['id'],'%s' % (name)))
        return res


