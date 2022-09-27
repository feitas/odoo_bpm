# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class Sale(models.Model):
    _inherit = ['sale.order']
    
    def btn_start_process(self):
        # get process
        process = self.env['syd_bpm.process'].search([], limit=1)
        if process:
            process.process_group_id.start_process(process, None)
        else:
            raise UserError("没有找到工作流！")