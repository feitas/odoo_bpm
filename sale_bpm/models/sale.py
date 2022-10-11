# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class Sale(models.Model):
    _inherit = ['sale.order']
    
    pm_process_id = fields.Many2one('syd_bpm.process',string="PM Related Process Name")
    pm_activity_id = fields.Many2one('syd_bpm.activity',string="Related Activity")
    # case_ids = fields.One2many('syd_bpm.case','order_id',string="Cases")
    def btn_start_process(self):
        # get process
        self.ensure_one()
        process = self.env['syd_bpm.process'].search([('id','=',self.pm_process_id.id)])
        if process:
            process.process_group_id.start_process(process, None,related_model=self._name, related_id=self.id)
        else:
            raise UserError("没有找到工作流！")