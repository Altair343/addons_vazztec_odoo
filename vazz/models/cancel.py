# -*- coding:utf-8 -*-
from odoo import fields, models

TEXT_DATE = "Fecha de cancelación"
TEXT_REASON = "Motivo de cancelación"

class CancelOrder(models.Model):
    _name = "vazz.cancel.orders"
    _description = "Cancelación de Solicitud"

    cancel_date = fields.Date(string=TEXT_DATE, readonly=True)
    comment = fields.Text(string=TEXT_REASON)

    cancel_request = fields.Many2one(comodel_name="vazz.orders",
        string="Solicitud")

class CancelService(models.Model):
    _name = "vazz.cancel.services"
    _description = "Cancelación de Solicitud"

    cancel_date = fields.Date(string=TEXT_DATE, readonly=True)
    comment = fields.Text(string=TEXT_REASON)

    cancel_request = fields.Many2one(comodel_name="vazz.services",
        string="Solicitud")

class CancelWarranty(models.Model):
    _name = "vazz.cancel.warranty"
    _description = "Cancelación de Garantías"

    cancel_date = fields.Date(string="Fecha de perdida", readonly=True)
    comment = fields.Text(string="Motivo de perdida de garantía")

    cancel_request = fields.Many2one(comodel_name="vazz.warranty",
        string="Solicitud")

class CancelSchedule(models.Model):
    _name = "vazz.cancel.schedule"
    _description = "Cancelación de Agenda"

    cancel_date = fields.Date(string=TEXT_DATE, readonly=True)
    comment = fields.Text(string=TEXT_REASON)

    cancel_request = fields.Many2one(comodel_name="vazz.schedule",
        string="Solicitud")


