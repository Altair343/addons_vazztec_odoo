# -*- coding:utf-8 -*-
# 1 : imports of python lib
import logging
# 2 : imports of odoo
from odoo import models, fields,api, _
# 3 : imports from odoo addons

TEXT_CON_DETALLES = "Con detalles"
TEXT_NO_COMPROBABLE = "No comprobable"

class CheckStatus(models.Model):
    _name = 'vazz.check.status'
    _description = 'Check status express'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    service = fields.Many2one(string = "No. Folio: S:", comodel_name='vazz.services',tracking=True)
    name = fields.Char(string="Folio", related = "service.name")
    # Detalles
    # Valor referencia normal 1.0A - 3.0A
    amperage = fields.Char(string="Amperaje de carga (A):", tracking=True)
    permanent = fields.Boolean(string="Fijo", tracking=True)
    variable = fields.Boolean(string="Variable", tracking=True)
    doesnt_charge = fields.Boolean(string="No carga", tracking=True)

    # ¿Enciende?
    turn_on_yes = fields.Boolean(string="Si", tracking=True)
    turn_on_not = fields.Boolean(string="No", tracking=True)
    turn_on_details = fields.Boolean(string=TEXT_CON_DETALLES, tracking=True)
    turn_on_not_verifiable = fields.Boolean(string=TEXT_NO_COMPROBABLE, tracking=True)

    # ¿Da imagen?
    gives_image_yes = fields.Boolean(string="Si", tracking=True)
    gives_image_not = fields.Boolean(string="No", tracking=True)
    damaged = fields.Boolean(string="Dañada", tracking=True)

    # ¿Da señal?
    signal_yes = fields.Boolean(string="Si", tracking=True)
    signal_not = fields.Boolean(string="No", tracking=True)
    signal_not_verifiable = fields.Boolean(string=TEXT_NO_COMPROBABLE, tracking=True)

    # Altavoz
    speaker_yes = fields.Boolean(string="Si", tracking=True)
    speaker_not = fields.Boolean(string="No", tracking=True)
    speaker_details = fields.Boolean(string=TEXT_CON_DETALLES, tracking=True)
    speaker_not_verifiable = fields.Boolean(string=TEXT_NO_COMPROBABLE, tracking=True)

    # Micrófono
    microphone_yes = fields.Boolean(string="Si", tracking=True)
    microphone_not = fields.Boolean(string="No", tracking=True)
    microphone_details = fields.Boolean(string=TEXT_CON_DETALLES, tracking=True)
    microphone_not_verifiable = fields.Boolean(string=TEXT_NO_COMPROBABLE, tracking=True)

    # Bocina de llamadas
    call_horn_yes = fields.Boolean(string="Si", tracking=True)
    call_horn_not = fields.Boolean(string="No", tracking=True)
    call_horn_details = fields.Boolean(string=TEXT_CON_DETALLES, tracking=True)
    call_horn_not_verifiable = fields.Boolean(string=TEXT_NO_COMPROBABLE, tracking=True)

    # Cámaras
    cameras_yes = fields.Boolean(string="Si", tracking=True)
    cameras_not = fields.Boolean(string="No", tracking=True)
    cameras_details = fields.Boolean(string=TEXT_CON_DETALLES, tracking=True)
    cameras_not_verifiable = fields.Boolean(string=TEXT_NO_COMPROBABLE, tracking=True)

    # Sensor huella
    does_not_apply = fields.Boolean(string="No aplica", tracking=True)
    sensor_yes = fields.Boolean(string="Si", tracking=True)
    sensor_not = fields.Boolean(string="No", tracking=True)
    sensor_details = fields.Boolean(string=TEXT_CON_DETALLES, tracking=True)
    sensor_not_verifiable = fields.Boolean(string=TEXT_NO_COMPROBABLE, tracking=True)

    # Signos visibles
    dust_dirt = fields.Boolean(string="Polvo / suciedad", tracking=True)
    moisture_sulfate = fields.Boolean(string="Humedad / sulfato", tracking=True)
    scrapes_bumps = fields.Boolean(string="Raspones / Golpes", tracking=True)
    dubbings = fields.Boolean(string="Dobladuras", tracking=True)

    # Contacto físico de los botones 
    normal = fields.Boolean(string="Normal", tracking=True)
    with_details = fields.Boolean(string="Con detalles", tracking=True)
    without_button = fields.Boolean(string="Sin algún botón", tracking=True)


    # == Constrains

    # == Onchange
    # ====  Amperaje  ====
    @api.onchange('permanent')
    def onchange_permanent(self):
        for rec in self:
            if rec.permanent == True:
                if rec.variable == True:
                    rec.variable = False
                if rec.doesnt_charge == True:
                    rec.doesnt_charge = False

    @api.onchange('variable')
    def onchange_variable(self):
        for rec in self:
            if rec.variable == True:
                if rec.permanent == True:
                    rec.permanent = False
                if rec.doesnt_charge == True:
                    rec.doesnt_charge = False

    @api.onchange('doesnt_charge')
    def onchange_doesnt_charge(self):
        for rec in self:
            if rec.doesnt_charge == True:
                if rec.permanent == True:
                    rec.permanent = False
                if rec.variable == True:
                    rec.variable = False

    # ====  ¿Enciende?  ====
    @api.onchange('turn_on_yes')
    def onchange_turn_on_yes(self):
        for rec in self:
            if rec.turn_on_yes == True:
                if rec.turn_on_not == True:
                    rec.turn_on_not = False
                if rec.turn_on_details == True:
                    rec.turn_on_details = False
                if rec.turn_on_not_verifiable == True:
                    rec.turn_on_not_verifiable = False

    @api.onchange('turn_on_not')
    def onchange_turn_on_not(self):
        for rec in self:
            if rec.turn_on_not == True:
                if rec.turn_on_yes == True:
                    rec.turn_on_yes = False
                if rec.turn_on_details == True:
                    rec.turn_on_details = False
                if rec.turn_on_not_verifiable == True:
                    rec.turn_on_not_verifiable = False

    @api.onchange('turn_on_details')
    def onchange_turn_on_details(self):
        for rec in self:
            if rec.turn_on_details == True:
                if rec.turn_on_yes == True:
                    rec.turn_on_yes = False
                if rec.turn_on_not == True:
                    rec.turn_on_not = False
                if rec.turn_on_not_verifiable == True:
                    rec.turn_on_not_verifiable = False

    @api.onchange('turn_on_not_verifiable')
    def onchange_turn_on_not_verifiable(self):
        for rec in self:
            if rec.turn_on_not_verifiable == True:
                if rec.turn_on_not == True:
                    rec.turn_on_not = False
                if rec.turn_on_details == True:
                    rec.turn_on_details = False
                if rec.turn_on_yes == True:
                    rec.turn_on_yes = False

    # ====  ¿Da imagen?  ====
    @api.onchange('gives_image_yes')
    def onchange_gives_image_yes(self):
        for rec in self:
            if rec.gives_image_yes == True:
                if rec.gives_image_not == True:
                    rec.gives_image_not = False
                if rec.damaged == True:
                    rec.damaged = False

    @api.onchange('gives_image_not')
    def onchange_gives_image_not(self):
        for rec in self:
            if rec.gives_image_not == True:
                if rec.gives_image_yes == True:
                    rec.gives_image_yes = False
                if rec.damaged == True:
                    rec.damaged = False

    @api.onchange('damaged')
    def onchange_damaged(self):
        for rec in self:
            if rec.damaged == True:
                if rec.gives_image_yes == True:
                    rec.gives_image_yes = False
                if rec.gives_image_not == True:
                    rec.gives_image_not = False

    # ====  ¿Da señal?  ====
    @api.onchange('signal_yes')
    def onchange_signal_yes(self):
        for rec in self:
            if rec.signal_yes == True:
                if rec.signal_not == True:
                    rec.signal_not = False
                if rec.signal_not_verifiable == True:
                    rec.signal_not_verifiable = False

    @api.onchange('signal_not')
    def onchange_signal_not(self):
        for rec in self:
            if rec.signal_not == True:
                if rec.signal_yes == True:
                    rec.signal_yes = False
                if rec.signal_not_verifiable == True:
                    rec.signal_not_verifiable = False

    @api.onchange('signal_not_verifiable')
    def onchange_signal_not_verifiable(self):
        for rec in self:
            if rec.signal_not_verifiable == True:
                if rec.signal_yes == True:
                    rec.signal_yes = False
                if rec.signal_not == True:
                    rec.signal_not = False

    # ====  Altavoz  ====
    @api.onchange('speaker_yes')
    def onchange_speaker_yes(self):
        for rec in self:
            if rec.speaker_yes == True:
                if rec.speaker_not == True:
                    rec.speaker_not = False
                if rec.speaker_details == True:
                    rec.speaker_details = False
                if rec.speaker_not_verifiable == True:
                    rec.speaker_not_verifiable = False

    @api.onchange('speaker_not')
    def onchange_speaker_not(self):
        for rec in self:
            if rec.speaker_not == True:
                if rec.speaker_yes == True:
                    rec.speaker_yes = False
                if rec.speaker_details == True:
                    rec.speaker_details = False
                if rec.speaker_not_verifiable == True:
                    rec.speaker_not_verifiable = False

    @api.onchange('speaker_details')
    def onchange_speaker_details(self):
        for rec in self:
            if rec.speaker_details == True:
                if rec.speaker_yes == True:
                    rec.speaker_yes = False
                if rec.speaker_not == True:
                    rec.speaker_not = False
                if rec.speaker_not_verifiable == True:
                    rec.speaker_not_verifiable = False

    @api.onchange('speaker_not_verifiable')
    def onchange_speaker_not_verifiable(self):
        for rec in self:
            if rec.speaker_not_verifiable == True:
                if rec.speaker_yes == True:
                    rec.speaker_yes = False
                if rec.speaker_not == True:
                    rec.speaker_not = False
                if rec.speaker_details == True:
                    rec.speaker_details = False

    # ====  Micrófono  ====
    @api.onchange('microphone_yes')
    def onchange_microphone_yes(self):
        for rec in self:
            if rec.microphone_yes == True:
                if rec.microphone_not == True:
                    rec.microphone_not = False
                if rec.microphone_details == True:
                    rec.microphone_details = False
                if rec.microphone_not_verifiable == True:
                    rec.microphone_not_verifiable = False

    @api.onchange('microphone_not')
    def onchange_microphone_not(self):
        for rec in self:
            if rec.microphone_not == True:
                if rec.microphone_yes == True:
                    rec.microphone_yes = False
                if rec.microphone_details == True:
                    rec.microphone_details = False
                if rec.microphone_not_verifiable == True:
                    rec.microphone_not_verifiable = False

    @api.onchange('microphone_details')
    def onchange_microphone_details(self):
        for rec in self:
            if rec.microphone_details == True:
                if rec.microphone_yes == True:
                    rec.microphone_yes = False
                if rec.microphone_not == True:
                    rec.microphone_not = False
                if rec.microphone_not_verifiable == True:
                    rec.microphone_not_verifiable = False

    @api.onchange('microphone_not_verifiable')
    def onchange_microphone_not_verifiable(self):
        for rec in self:
            if rec.microphone_not_verifiable == True:
                if rec.microphone_yes == True:
                    rec.microphone_yes = False
                if rec.microphone_not == True:
                    rec.microphone_not = False
                if rec.microphone_details == True:
                    rec.microphone_details = False

    # ====  Bocina de llamadas  ====
    @api.onchange('call_horn_yes')
    def onchange_call_horn_yes(self):
        for rec in self:
            if rec.call_horn_yes == True:
                if rec.call_horn_not == True:
                    rec.call_horn_not = False
                if rec.call_horn_details == True:
                    rec.call_horn_details = False
                if rec.call_horn_not_verifiable == True:
                    rec.call_horn_not_verifiable = False

    @api.onchange('call_horn_not')
    def onchange_call_horn_not(self):
        for rec in self:
            if rec.call_horn_not == True:
                if rec.call_horn_yes == True:
                    rec.call_horn_yes = False
                if rec.call_horn_details == True:
                    rec.call_horn_details = False
                if rec.call_horn_not_verifiable == True:
                    rec.call_horn_not_verifiable = False

    @api.onchange('call_horn_details')
    def onchange_call_horn_details(self):
        for rec in self:
            if rec.call_horn_details == True:
                if rec.call_horn_yes == True:
                    rec.call_horn_yes = False
                if rec.call_horn_not == True:
                    rec.call_horn_not = False
                if rec.call_horn_not_verifiable == True:
                    rec.call_horn_not_verifiable = False

    @api.onchange('call_horn_not_verifiable')
    def onchange_call_horn_not_verifiable(self):
        for rec in self:
            if rec.call_horn_not_verifiable == True:
                if rec.call_horn_yes == True:
                    rec.call_horn_yes = False
                if rec.call_horn_not == True:
                    rec.call_horn_not = False
                if rec.call_horn_details == True:
                    rec.call_horn_details = False

    # ====  Cámaras  ====
    @api.onchange('cameras_yes')
    def onchange_cameras_yes(self):
        for rec in self:
            if rec.cameras_yes == True:
                if rec.cameras_not == True:
                    rec.cameras_not = False
                if rec.cameras_details == True:
                    rec.cameras_details = False
                if rec.cameras_not_verifiable == True:
                    rec.cameras_not_verifiable = False

    @api.onchange('cameras_not')
    def onchange_cameras_not(self):
        for rec in self:
            if rec.cameras_not == True:
                if rec.cameras_yes == True:
                    rec.cameras_yes = False
                if rec.cameras_details == True:
                    rec.cameras_details = False
                if rec.cameras_not_verifiable == True:
                    rec.cameras_not_verifiable = False

    @api.onchange('cameras_details')
    def onchange_cameras_details(self):
        for rec in self:
            if rec.cameras_details == True:
                if rec.cameras_yes == True:
                    rec.cameras_yes = False
                if rec.cameras_not == True:
                    rec.cameras_not = False
                if rec.cameras_not_verifiable == True:
                    rec.cameras_not_verifiable = False

    @api.onchange('cameras_not_verifiable')
    def onchange_cameras_not_verifiable(self):
        for rec in self:
            if rec.cameras_not_verifiable == True:
                if rec.cameras_yes == True:
                    rec.cameras_yes = False
                if rec.cameras_not == True:
                    rec.cameras_not = False
                if rec.cameras_details == True:
                    rec.cameras_details = False

    # ====  Sensor huella  ====
    @api.onchange('does_not_apply')
    def onchange_does_not_apply(self):
        for rec in self:
            if rec.does_not_apply == True:
                if rec.sensor_yes == True:
                    rec.sensor_yes = False
                if rec.sensor_not == True:
                    rec.sensor_not = False
                if rec.sensor_details == True:
                    rec.sensor_details = False
                if rec.sensor_not_verifiable == True:
                    rec.sensor_not_verifiable = False

    @api.onchange('sensor_yes')
    def onchange_sensor_yes(self):
        for rec in self:
            if rec.sensor_yes == True:
                if rec.does_not_apply == True:
                    rec.does_not_apply = False
                if rec.sensor_not == True:
                    rec.sensor_not = False
                if rec.sensor_details == True:
                    rec.sensor_details = False
                if rec.sensor_not_verifiable == True:
                    rec.sensor_not_verifiable = False

    @api.onchange('sensor_not')
    def onchange_sensor_not(self):
        for rec in self:
            if rec.sensor_not == True:
                if rec.does_not_apply == True:
                    rec.does_not_apply = False
                if rec.sensor_yes == True:
                    rec.sensor_yes = False
                if rec.sensor_details == True:
                    rec.sensor_details = False
                if rec.sensor_not_verifiable == True:
                    rec.sensor_not_verifiable = False

    @api.onchange('sensor_details')
    def onchange_sensor_details(self):
        for rec in self:
            if rec.sensor_details == True:
                if rec.does_not_apply == True:
                    rec.does_not_apply = False
                if rec.sensor_yes == True:
                    rec.sensor_yes = False
                if rec.sensor_not == True:
                    rec.sensor_not = False
                if rec.sensor_not_verifiable == True:
                    rec.sensor_not_verifiable = False

    @api.onchange('sensor_not_verifiable')
    def onchange_sensor_not_verifiable(self):
        for rec in self:
            if rec.sensor_not_verifiable == True:
                if rec.does_not_apply == True:
                    rec.does_not_apply = False
                if rec.sensor_yes == True:
                    rec.sensor_yes = False
                if rec.sensor_not == True:
                    rec.sensor_not = False
                if rec.sensor_details == True:
                    rec.sensor_details = False

    # ====  Contacto físico de los botones ====
    @api.onchange('normal')
    def onchange_normal(self):
        for rec in self:
            if rec.normal == True:
                if rec.with_details == True:
                    rec.with_details = False
                if rec.without_button == True:
                    rec.without_button = False

    @api.onchange('with_details')
    def onchange_with_details(self):
        for rec in self:
            if rec.with_details == True:
                if rec.normal == True:
                    rec.normal = False
                if rec.without_button == True:
                    rec.without_button = False

    @api.onchange('without_button')
    def onchange_without_button(self):
        for rec in self:
            if rec.without_button == True:
                if rec.normal == True:
                    rec.normal = False
                if rec.with_details == True:
                    rec.with_details = False

    # == Compute

    # == CRUD methods