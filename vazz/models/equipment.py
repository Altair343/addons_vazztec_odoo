# -*- coding:utf-8 -*-
# odoo
from odoo import models, fields,api, _

class Equipment(models.Model):
    _name = 'vazz.equipment'
    _description = 'Equipos'

    # name = fields.Char(string="Nombre del equipo", required= True )

    brand = fields.Char(string="Marca")
    model_e = fields.Char(string="Modelo" )
    imei = fields.Char(string="No. de serie / IMEI")
    type_equipment = fields.Many2one(comodel_name="vazz.equipment.type", string="Tipo de equipo")

    password = fields.Char(string="Contraseña del equipo" )
    accessories =  fields.Text(string="Accesorios")
    note =  fields.Text(string="Nota")

    service_id = fields.Many2one(comodel_name="vazz.services", string="Servicio", ondelete='cascade')
    