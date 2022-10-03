from odoo import models, fields, api
from odoo.tools.translate import _
from ...syd_bpm.models.process import BPMInterface
import odoo.exceptions
import odoo
import requests
import json 
import time
import logging
from odoo.exceptions import ValidationError


class ProcessRoleExt(models.Model):
    _inherit = 'syd_bpm.process_role'

    pm_group_id=fields.Char('Process Group Id')

    @api.model
    def get_or_create_process_role(self,role_name):
        if not role_name:
            return False
        role_id = self.env['syd_bpm.process_role'].search([('name','=',role_name)],limit=1)
        if not role_id:
            role_id = self.env['syd_bpm.process_role'].create({'name':role_name})
        return role_id