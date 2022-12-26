# -*- coding:utf-8 -*-
from odoo import fields, models

class CancelOrder(models.Model):
    _name = "vazz.cancel.orders"
    _description = "Cancelación de Solicitud"

    cancel_date = fields.Date(string="Fecha de cancelación", readonly=True)
    comment = fields.Text(string="Motivo de cancelación")

    cancel_request = fields.Many2one(comodel_name="vazz.orders",
        string="Solicitud")

class CancelService(models.Model):
    _name = "vazz.cancel.services"
    _description = "Cancelación de Solicitud"

    cancel_date = fields.Date(string="Fecha de cancelación", readonly=True)
    comment = fields.Text(string="Motivo de cancelación")

    cancel_request = fields.Many2one(comodel_name="vazz.services",
        string="Solicitud")

class CancelWarranty(models.Model):
    _name = "vazz.cancel.warranty"
    _description = "Cancelación de Garantías"

    cancel_date = fields.Date(string="Fecha de perdida", readonly=True)
    comment = fields.Text(string="Motivo de perdida de garantía")

    cancel_request = fields.Many2one(comodel_name="vazz.warranty",
        string="Solicitud")


