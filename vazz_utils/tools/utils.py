# -*- coding: utf-8 -*-
# imports
import logging
_logger = logging.getLogger(__name__)

def create_chatter(self,res_id, body,model):
    actual_user = self.env.user
    self.env['mail.message'].create({
        'body': body,
        'res_id': res_id,
        'model': model,
        'record_name':"general",
        'message_type':"notification",
        "subtype_id":1,
        'author_id':actual_user.partner_id.id,
        })

def has_group(self, group_ref):
    """
        Este método es genérico para Vazztec.
        precondiciones:
        El usuario necesita estar dado de alta en un grupo.
        Retorna Verdadero si el usuario se encuentra en el grupo requerido
        parametros:
        Tipo: string
        nombre: rol
        descripción: es el id del rol que se requiere
        ej: 'vazz.Rol001'
    """
    user = self.env.user
    group = self.env.ref(group_ref)
    if group:
        return group.id in user.groups_id.ids
    else:
        return False