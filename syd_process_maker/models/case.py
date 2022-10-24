# -*- coding: utf-8 -*-
# Copyright 2022-2023 Feitas (https://www.wffeitas.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import json 
import logging

import odoo
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError,UserError

from .process import TimeConverterDate

_logger = logging.getLogger(__name__)


class Case(models.Model):
    _inherit = 'syd_bpm.case'
    
    pm_assigned_to = fields.Many2one('res.users',string="Assigned To")
    pm_case_id = fields.Char(string='Process Maker Task ID', required=False)
    activity_id = fields.Many2one('syd_bpm.activity',string="Activity")
    pm_element_id = fields.Char(string='Process Maker Element ID')
    pm_element_type = fields.Char(string='Process Maker Element Type')
    pm_element_name = fields.Char(string='Process Maker Element Name')
    related_model = fields.Char(string='Related Model')
    related_id = fields.Char(string='Related Record ID')
    is_assigned_to = fields.Boolean(string='Is Assigned To',compute='_compute_is_assigned_to')
    odoo_activity_id = fields.Many2one("mail.activity", string="Mail Activity")

    def _compute_is_assigned_to(self):
        for record in self:
            record.is_assigned_to = bool(record.pm_assigned_to.id == self.env.uid)

    def create(self, vals):
        case =  super(Case, self).create(vals)
        _vals = {
            "res_name": "",
            "date_deadline": case.date_deadline,
            "activity_type_id": self.env['ir.model.data']._xmlid_to_res_id('mail.mail_activity_data_todo', raise_if_not_found=False),
            "user_id": case.pm_assigned_to.id,
            "summary": "",
            "res_id": int(case.related_id),
            "res_model_id": self.env['ir.model'].search([('model', '=', case.related_model)]).id
        }
        if case.activity_id and "-" in case.activity_id.name:
            _vals.update({"res_name": case.activity_id.name.split('-')[1]})
        
        activity = self.env['mail.activity'].create(_vals)
        print(activity)
        case.write({'odoo_activity_id': activity.id})
        return case


    def confirm_case(self, result="pass"):
        """
        /tasks/{task_id} Update a task
        """
        # TODO 通过process_id找到对应Process的Dynamic Form, 在Dynamic Form找到同名的Case并获取所需的字段
        if result not in ['pass', 'refuse']:
            raise ValidationError("审批结论传值错误，必须是pass或者refuse！")
            
        _data = {
            "status": "COMPLETED",
            "data": {
                "result": result
            }
        }
        if self.process_id:
            res = self.process_id.process_group_id._call(f'tasks/{self.pm_case_id}', jsonobject=json.dumps(_data), method='PUT')
            if res:
                if res.get('status') and res.get('status')=='CLOSED':
                    self.state='completed'
                params = {
                    'process_request_id': int(self.activity_id.pm_activity_id)
                }
                pm_tasks = self.process_id.process_group_id._call('tasks', params, method='GET')
                if pm_tasks.get('data'):
                    for item in pm_tasks.get('data'):
                        print(item)
                        _domain = [
                            ('pm_case_id', '=', item.get('id')),
                        ]
                        task = self.env['syd_bpm.case'].search(_domain)
                        if not task:
                            _state='in_progress'
                            if item.get('status') and item.get('status')=='CLOSED':
                                _state = 'cancelled'
                            elif item.get('status') and item.get('status')=='COMPLETED':
                                _state = 'completed'
                            _val = {
                                'pm_case_id': item.get('id'),
                                'name': item.get('element_name'),
                                'activity_id': self.activity_id.id,
                                'process_id': self.process_id.id,
                                'related_model':self.related_model,
                                'related_id':int(self.related_id) if isinstance(self.related_id, int) else str(self.related_id),
                                'state':_state,
                                'date_deadline': TimeConverterDate(item.get("due_at")),
                            }
                            _user = self.env['res.users'].search([('pm_user_id', '=', item.get('user_id'))])

                            if _user:
                                _val.update({'pm_assigned_to': _user.id})
                            else:
                                _val.update({'pm_assigned_to': self.env['res.users'].search([],limit=1).id})
                            self.env['syd_bpm.case'].create(_val)
                else:
                    _logger.warning(pm_tasks)
            else:
                _logger.warning("更细task没有成功...")
            return True
   