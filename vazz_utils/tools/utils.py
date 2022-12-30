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