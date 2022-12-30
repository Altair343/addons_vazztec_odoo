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
            phoneAux = False
            if rec.phones_ids:
                for tel in rec.phones_ids:
                    if tel.is_main == True:
                        phoneAux = tel.id
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
    
    folio = fields.Char(string="Folio", default=lambda self: _('Nuevo'))
    name = fields.Char(string="Nombre completo")
    user_name = fields.Char(string="Nombre", tracking=True)
    surname = fields.Char(string="Primer apellido", tracking=True)
    second_surname = fields.Char(string="Segundo apellido", tracking=True)
    email =  fields.Char(string="Correo")
    addres =  fields.Text(string="Dirreción", tracking=True)
    # phone =  fields.Char(string="Teléfono principal",compute="_compute_phone", store = False)
    phone =  fields.Many2one(comodel_name='vazz.customers.phone', string="Teléfono principal",compute="_compute_phone", store = False)
    phones_ids = fields.One2many(comodel_name='vazz.customers.phone',inverse_name= 'customer_ids', 
        string="Teléfono", ondelete = "cascade")
    count_services = fields.Integer(string="Total de Servicios", compute="_compute_count_services", store = False) 
    
    
    @api.model
    def create(self, vals):
        
        # Armando nombre completo
        nombre = ""
        apellidop = ""
        apellidom = ""
        if 'user_name' in vals:
            nombre = vals['user_name']
        
        if 'surname' in vals:
            apellidop = vals['surname']
        
        if 'second_surname' in vals:
            apellidom = vals['second_surname']
        vals['name'] = f"{nombre} {apellidop} {apellidom}"

        # Buscar que no se repita el nombre


        # Generar folio
        name_seq = self.env['ir.sequence'].next_by_code('vazz.customers.sequence')
        if name_seq != False:
            vals['folio'] = f"C/{name_seq}"

        result = super(Customers, self).create(vals)
        return result

    def write(self,vals):
        
        nombre = ""
        apellidop = ""
        apellidom = False
        if 'user_name' in vals or 'surname' in vals or 'second_surname' in vals:
            if 'user_name' in vals:
                nombre = vals['user_name']
            else:
                if self.user_name:
                    nombre = self.user_name
            
            if 'surname' in vals:
                apellidop = vals['surname']
            else:
                if self.surname:
                    apellidop = self.surname
            
            if 'second_surname' in vals:
                apellidom = vals['second_surname']
            else:
                if self.second_surname:
                    apellidom = self.second_surname
            
            if apellidom == False:
                vals['name'] = f"{nombre} {apellidop}"
            else:
                vals['name'] = f"{nombre} {apellidop} {apellidom}"
        
        res = super(Customers,self).write(vals)
        return res

    # Onchange
    @api.onchange('user_name','surname','second_surname')
    def _onchange_user_name(self):
        nombre = ""
        apellidop = ""
        apellidom = False
        if self.user_name:
            nombre = self.user_name
        if self.surname:
            apellidop = self.surname
        if self.second_surname:
            apellidom = self.second_surname
        
        if apellidom == False:
            self.name= f"{nombre} {apellidop}"
        else:
            self.name= f"{nombre} {apellidop} {apellidom}"
    

    def name_get(self):
        res = []
        for record in self:
            customers = record.env['vazz.customers'].browse([record['id']])
            name = f"{customers.name}"
            
            res.append((record['id'],'%s' % (name)))
        return res


