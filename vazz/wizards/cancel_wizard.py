#-*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo import api, fields, models

from datetime import date
import logging
_logger = logging.getLogger(__name__)

class CancelWizardLIB(models.TransientModel):
    _name = "vazz.cancel_wizard"
    _description ="Cancelación"

    cancel_date = fields.Date(string="Fecha", readonly=True)
    comment = fields.Text(string="Motivo")

    @api.model
    def default_get(self,fields_list):
        cancel_wizard = super(CancelWizardLIB,self).default_get(fields_list)
        # definir la zona horaria 
        cancel_wizard['cancel_date'] = fields.datetime.now()
        return cancel_wizard

    def confirm_cancel(self):
        model = self._context.get('active_model')
        product_model = self.env[model].browse(self._context.get('active_id'))
    
        if model == 'vazz.orders':
            model_cancel = 'vazz.cancel.orders'
            field_refense = 'cancel_request'
            self._state_change(model,product_model)
        elif model == 'vazz.services':
            model_cancel = 'vazz.cancel.services'
            field_refense = 'cancel_request'
            self._state_change(model,product_model)
        elif model == 'vazz.warranty':
            model_cancel = 'vazz.cancel.warranty'
            field_refense = 'cancel_request'
            self._state_change(model,product_model)
        elif model == 'vazz.schedule':
            model_cancel = 'vazz.cancel.schedule'
            field_refense = 'cancel_request'
            self._state_change(model,product_model)
        else:
            raise UserError('No se encontro el modelo')

        #Se crea el registro segun el modelo anterior
        self.env[model_cancel].create({
            field_refense : product_model.id,
            'cancel_date' : self.cancel_date,
            'comment' : self.comment })

    def _state_change(self,model,product_model):
        if model == 'vazz.orders':
            product_model.action_cancel(self.comment)
        elif model == 'vazz.services':
            product_model.action_cancel(self.comment)
        elif model == 'vazz.warranty':
            product_model.action_lost(self.comment)
        elif model == 'vazz.schedule':
            product_model.action_cancel(self.comment)
        else:
            raise UserError('No Se encontro el modelo : %s |||| %s ||||'%(model,product_model.state))




