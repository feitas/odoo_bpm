# -*- coding: utf-8 -*-
# Copyright 2018-2019 SayDigital (https://www.saydigital.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from pprint import pprint
from odoo import models, fields, api
from odoo.tools.translate import _
from ...syd_bpm.models.process import BPMInterface
import odoo.exceptions
import odoo
import requests
import json 
import time
import logging
from odoo.exceptions import ValidationError,UserError

_logger = logging.getLogger(__name__)

class ProcessGroup(BPMInterface,models.Model):
    _inherit = 'syd_bpm.process_group'
    
    type= fields.Selection(selection_add=[("ProcessMaker2", "ProcessMaker2")])
   
    pm_url = fields.Char(string='PM Url',required=True)
    pm_workspace = fields.Char(string='PM Workspace',required=True)
    pm_client_id = fields.Char(string='PM Client Id',required=True)
    pm_client_secret = fields.Char(string='PM Client secret',required=True)
    pm_username = fields.Char(string='PM Username',required=True)
    pm_password = fields.Char(string='PM Password',required=True)
    
    pm_user_name = fields.Char(string='Name of the user of PM',required=True)
    pm_access_token = fields.Char()
    
    
    def _call(self, request, query_param=False,jsonobject=dict(), method='GET'):
        auth = {
                'grant_type': 'password',
                'scope': '*',
                'client_id': self.pm_client_id,
                'client_secret': self.pm_client_secret,
                'username': self.pm_username,
                'password': self.pm_password
        }
        result = requests.post(self.pm_url+'/oauth/token', data=auth)
        if (not result.ok):
            raise ValidationError('{}, {}'.format(result.status_code, result.text))
        jsonresult = json.loads(result.content)
        if ('error' in jsonresult) :
            raise ValidationError('{}'.format(result.error_description))
        access_token = jsonresult['access_token']
        self.pm_access_token = access_token if access_token else ''
        headers = {'Authorization': 'Bearer '+access_token}
        
        endresult = ''
        if (method == 'GET'):
            endresult = requests.get(self.pm_url+'/api/1.0/' + request, params = query_param, headers=headers )
        if (method == 'POST'):
            headers.update({'Content-Type': 'application/json'})
            endresult = requests.post(self.pm_url+'/api/1.0/' + request, params = query_param, data = json.dumps(jsonobject), headers=headers)
        if (method == 'PUT'):
            headers.update({'Content-Type': 'application/json'})
            endresult = requests.put(self.pm_url+'/api/1.0/' + request, data = jsonobject, headers=headers)
        if (not bool(endresult) or not endresult.ok):
            raise  UserError(str(endresult.status_code)+"-" + str(endresult.content))
        if bool(endresult.content): 
            if 'json' in endresult.headers['Content-Type']:
                _res = json.loads(endresult.content)
                return _res
            else :
                return endresult.content
        else: 
            return False
    
    @api.model
    def _get_process_list(self):
        process_list = self._call('processes')
        return process_list['data']
    
    @api.model
    def _get_activity_list(self,process_id):
        process_definition = self._call('project/'+process_id)
        tasks = process_definition['diagrams'][0]['activities']
        return tasks
    
    @api.model
    def _get_request_list(self):
        par = {'per_page': 100}
        request_definition = self._call('requests',par)
        requests = request_definition['data']
        _logger.info("------- requests -------- %s" % str(requests))
        return requests

    @api.model
    def _get_group_list(self):
        """ Returns all groups that the user has access to
        :url:/groups
        :param
        :returns: list -- group data
        """
        group_definition = self._call('groups')
        return group_definition['data']
        
    @api.model
    def _get_process_request_list(self, process_id):
        par = {'filter': process_id.name}
        request_definition = self._call('requests',par)
        requests = request_definition['data']
        return requests

    @api.model
    def _get_process_task_list(self, process_id):
        par = {'filter': process_id.name}
        task_definition = self._call('tasks',par)
        tasks = task_definition['data']
        return tasks

    @api.model
    def _get_starting_activity(self,process_id):
        # GET /case/start-cases
        starting_activities = self._call('project/%s/starting-tasks' %process_id )
        return starting_activities
        
    @api.model
    def _get_user_list(self):
        user_definition = self._call('users')
        return user_definition['data']
        
    @api.model
    def _get_export_data_url(self,process_id):
        url_definition = self._call(f'processes/{int(process_id)}/export', method='POST')
        return url_definition

    @api.model
    def _route_case(self,case_id,del_index=False):
        # PUT /cases/{app_uid}/route-case
        
        par = dict()
        if (del_index) : par['del_index'] = del_index
        res =self._call('cases/'+case_id+'/route-case',par,method='PUT')
        
        return True
    
    @api.model
    def _get_current_tasks(self,case):
        #GET cases/{app_uid}/tasks
        #GET /cases/{app_uid}/tasks
        case_id = case['app_uid']
        res =self._call('cases/'+case_id+'/tasks')
        tasklist = []
        if isinstance(res, dict):
            res = [res]
        for task in res :
            if task['status'] in ['TASK_IN_PROGRESS','TASK_PARALLEL'] :
                if (len(task['delegations']) > 0 ):
                    index = 0
                    for ele in task['delegations']:
                        if ele['del_finish_date'] == 'Not finished':
                            break
                        index = index + 1
                    task['del_index'] = task['delegations'][index]['del_index']
                tasklist.insert(0,task)
        return tasklist
    
    
    @api.model
    def _get_process_map(self,process_id):
        #GET /light/process/{pro_uid}/case
        res = self._call('light/process/'+process_id+'/case')
        return res;
      
      
    @api.model
    def _get_case_variables(self,case_id):
        #GET /cases/{app_uid}/variables
        res = self._call('cases/'+case_id+'/variables')
        variable_list = []
        for v in res :
            if (v not in ["SYS_LANG","SYS_SKIN","SYS_SYS","APPLICATION","PROCESS","TASK","INDEX","USER_LOGGED","USR_USERNAME","PIN","APP_NUMBER"]):  
                 variable_list.insert(0,v)
        return variable_list                
     
    @api.model
    def _set_case_variables(self,case_id,data):
        #PUT /cases/{app_uid}/variable   
        res = self._call('cases/'+case_id+'/variable',data,method='PUT')
        return res;
        
    @api.model
    def _get_process_variables(self,process_id):
        #GET /api/1.0/{workspace}/project/{prj_uid}/process-variables
        res = self._call('project/'+process_id+'/process-variables')
        return res
    
    @api.model
    def _get_case_info(self,case_id):
        #GET /cases/{app_uid}
        res = self._call('case/'+case_id)
        return res
    
    @api.model
    def _get_activity_info(self,process_id,activity_id):
        #GET /api/1.0/{workspace}/project/{prj_uid}/activity/{act_uid}
        res = self._call('project/'+process_id+'/activity/'+activity_id)
        return res
    
    @api.model
    def _get_category_info(self,cat_id):
        return self._call(f'process_categories/{cat_id}')
    
    @api.model
    def _get_assign_user(self):
        par = {'filter': self.pm_user_name}
        res = self._call('users',par)
        try:
            return res['data'][0]['id']
        except :
            raise ValidationError(_('No ProcessMaker user to assign task'))
        
    @api.model
    def _get_user_of_task(self,process_id,task_id):
        res = self._call('project/%s/activity/%s/assignee'%(process_id,task_id))
        return res
    
    @api.model
    def _assign_user_to_task(self,process_id,task_id,user_id):
        #/project/{prj_uid}/activity/{act_uid}/assignee
        par = {'aas_uid': user_id, 'aas_type': 'user'}
        res = self._call('project/%s/activity/%s/assignee'%(process_id,task_id),par,method='POST')
        return res
    
    @api.model
    def _cancel_case(self,case_id):
        #/cases/{app_uid}/cancel
        res = self._call('cases/%s/cancel'%(case_id.pm_case_id),method='PUT')
        return res
    
    def start_process(self, process_id, activity_id,related_model=False,related_id=False):
        # POST /cases
        self.ensure_one()
        pm_process_id = process_id.pm_process_id
        # 'node_1' is setted for the 'Node Identifier' in the 'Start Event' element's 'Advanced' option in PM Designer for Process
        par = {'process_id': int(pm_process_id), 'event': 'node_1'}
        res = self._call(f'process_events/{pm_process_id}', query_param=par, method='POST')
        process_id.name = res['name']
        process_id.pm_process_id = res.get('process_id')
        process_id.description = res.get('process')['description']
        process_id.start_events = str(res.get('process')['start_events'])
        _domain = [
            ('name', '=', res.get('name')),
            ('process_id', '=', int(process_id.id)),
            ('pm_activity_id', '=', res.get('id'))
        ]
        request_id = self.env['syd_bpm.activity'].search(_domain, limit=1)
        related_record = self.env[related_model].search([('id','=',int(related_id))]) if related_id else False
        if not request_id:
            _val = {
                'name': '-'.join((res.get('name'),related_record.name)) if related_record else res.get('name'),
                'pm_user':int(res.get('user_id')) if res.get('user_id') else False,
                'pm_callable_id':res.get('callable_id'),
                'type': 'user-case',
                'process_id': process_id.id,
                'user_id': res.get('user_id'),
                'pm_activity_id': res.get('id'),
                'status': res.get('status'),
                'related_model':related_model if related_model else '',
                'related_id':related_id if related_id and isinstance(related_id, str) else False
            }
            request_id = self.env['syd_bpm.activity'].create(_val)
        else:
            request_id.name = '-'.join((res.get('name'),related_record.name)) if related_record else res.get('name')
            request_id.process_id = process_id.id
            request_id.user_id = res.get('user_id')
            request_id.pm_activity_id = res.get('id')
            request_id.pm_user = int(res.get('user_id'))
            request_id.pm_callable_id = res,get('callable_id')
        if related_record:
            related_record.sudo().write({'pm_activity_id':int(request_id.id)})
        # get tasks by process_request_id
        params = {
            'process_request_id': request_id.pm_activity_id
        }
        pm_tasks = self._call(f'tasks', params, method='GET')
        # pprint(pm_tasks)
        if pm_tasks.get('data'):
            for item in pm_tasks.get('data'):
                _domain = [
                    ('pm_case_id', '=', item.get('id')),
                ]
                task = self.env['syd_bpm.case'].search(_domain)
                if not task:
                    _state='in_progress'
                    if item.get('user_id'):
                        user_id=self.env['res.users'].search([('id','=',item.get('user_id'))])
                    if item.get('status') and item.get('status')=='CLOSED':
                        _state = 'cancelled'
                    elif item.get('status') and item.get('status')=='COMPLETED':
                        _state = 'completed'
                    _val = {
                        'pm_case_id': item.get('id'),
                        'name': item.get('element_name'),
                        'process_id': process_id.id,
                        'activity_id':request_id.id,
                        'related_model':related_model,
                        'pm_assigned_to':user_id.id if user_id else False,
                        'related_id':int(related_id) if isinstance(related_id, int) else str(related_id),
                        'state':_state,
                        'pm_element_id':item.get('element_id'),
                        'pm_element_type':item.get('element_type'),
                        'pm_element_name':item.get('element_name'),
                    }
                    self.env['syd_bpm.case'].create(_val)
        else:
            _logger.error(pm_tasks)

        return True
    
    
    def update_processes(self):
        for pgroup in self:
            pm_user_id = self._get_assign_user()
            process_list = self._get_process_list()
            request_list = self._get_request_list()
            role_list = self._get_group_list()
            user_list = self._get_user_list()
            for process in process_list:
                process_id = self.env['syd_bpm.process'].search([('pm_process_id','=',process['id'])],limit=1)
                if not process_id or not process_id.locked:
#                   map = self._get_process_map(process['prj_uid'])
                    pm_category = False
                    if process['process_category_id'] != '':
                        pm_category = self._get_category_info(int(process['process_category_id']))['name']
                    if not process_id:
                        process_id = self.env['syd_bpm.process'].create(
                                                           {'name':process['name'],
                                                            'description':process['description'],
                                                            'pm_process_id':process['id'],
                                                            'process_group_id':pgroup.id,
                                                            'category_id':self.env['syd_bpm.process_category'].get_or_create_category(pm_category)
                                                            }
                                                           )
                    else:
                        process_id.name=process['name']
                        process_id.description = process['description']
                        process_id.start_events = str(process['start_events'])
                        process_id.category_id=self.env['syd_bpm.process_category'].get_or_create_category(pm_category)


            for request in request_list:
                process_id = self.env['syd_bpm.process'].search([('pm_process_id','=',request['process_id'])],limit=1)
                request_id = self.env['syd_bpm.activity'].search([('pm_activity_id','=',request['id']),('process_id','=',int(process_id))],limit=1)
                if not request_id:
                    request_id = self.env['syd_bpm.activity'].create(
                                            {'name':request['name'],
                                            'pm_user':request.get('user_id'),
                                            'type':'user-case',
                                            'process_id':process_id.id,
                                            'user_id':request['user_id'],
                                            'pm_activity_id':request['id'],
                                            'status':request['status'],
                                            }
                                            )
                else:
                    request_id.name=request['name']
                    request_id.process_id = process_id.id
                    request_id.user_id = request['user_id']
                    request_id.pm_activity_id = request['id']
                    request_id.pm_user = request['user_id']

                #     activity_list = self._get_activity_list(process_id.pm_process_id)
                #     act_not_to_delete = []
                #     for activity in activity_list :

                #         activity_id = self.env['syd_bpm.activity'].search([('pm_activity_id','=',activity['act_uid'])],limit=1)

                #         activity_info = self._get_activity_info(process_id.pm_process_id,activity['act_uid'])
                #         if (not activity_id) :
                #             activity_id = self.env['syd_bpm.activity'].create(
                #                                            {'name':activity['act_name'],
                #                                             'description' : activity_info['properties']['tas_description'],
                #                                             'process_id':process_id.id,
                #                                             'pm_activity_id':activity['act_uid']
                #                                             }
                #                                            )
                #         else :
                #             activity_id.name = activity['act_name']
                #             activity_id.description = activity_info['properties']['tas_description']
                #             activity_id.is_start_activity = False

                #         # Assign to a pm user the task if it is unassigned
                #         users = self._get_user_of_task(process_id.pm_process_id,activity['act_uid'])
                #         if not (bool(users)):
                #             self._assign_user_to_task(process_id.pm_process_id,activity['act_uid'],pm_user_id)
                #         act_not_to_delete.insert(0,activity_id.id)
                #     act_to_delete = self.env['syd_bpm.activity'].search([('process_id','=',process_id.id),('id','not in',act_not_to_delete)])
                #     for act in act_to_delete:
                #         act.deprecated = True

                #     process_variables = self._get_process_variables(process_id.pm_process_id)
                #     var_not_to_delete = []
                #     for pvariable in process_variables:
                #         process_object_id = self.env['syd_bpm.process_object'].search([('pm_variable_id','=',pvariable['var_uid'])],limit=1)
                #         if process_object_id:
                #             process_object_id.name = pvariable['var_name']
                #             process_object_id.pm_accepted_values = pvariable['var_accepted_values']
                #             process_object_id.pm_type = pvariable['var_field_type']

                #         else:
                #             self.env['syd_bpm.process_object'].create({
                #                                                  'name':pvariable['var_name'],
                #                                                  'pm_variable_id':pvariable['var_uid'],
                #                                                  'pm_accepted_values':pvariable['var_accepted_values'],
                #                                                  'process_id':process_id.id,
                #                                                  'pm_type':pvariable['var_field_type']
                #                                                  })
                #             process_object_id = self.env['syd_bpm.process_object'].search([('pm_variable_id','=',pvariable['var_uid'])],limit=1)
                #         var_not_to_delete.insert(0,process_object_id.id)
                #     for pv in self.env['syd_bpm.process_object'].search([('process_id','=','process_id.id'),('id','not in',var_not_to_delete)]):
                #         pv.deprecated = True
                # starting_activities = self._get_starting_activity(process_id.pm_process_id)
                # for activity in starting_activities :
                #     act = self.env['syd_bpm.activity'].search([('pm_activity_id','=',activity['act_uid'])],limit=1)
                #     act.is_start_activity = True
                #     acts = self.env['syd_bpm.activity'].search([('process_id','=',process_id.id),('is_start_activity','=',True)])
                #     if (not starting_activities ) :
                #         process.startable = False
                #         acts.is_start_activity = False
            for role in role_list:
                role_id = self.env['syd_bpm.process_role'].get_or_create_process_role(role['name'])
                role_id.pm_group_id = role.get("id")
            pm_user_name_list = [user['username'] for user in user_list]
            odoo_user_list = self.env['res.users'].search([])
            odoo_user_name_list = [user.name for user in odoo_user_list]
            upgrade_val = []
            for odoo_user in odoo_user_list:
                if odoo_user.name not in pm_user_name_list:
                    _email = odoo_user.email if odoo_user.email else ''.join((odoo_user.name,'@noway.com'))
                    par = {'username':odoo_user.name,'email':_email,'status':'ACTIVE','firstname':'email','lastname':'email','password':'88888888'}
                    res = self._call(f'users', jsonobject=par, method='POST')
                    _logger.warning(f'res:{res}')
            pgroup.last_update = fields.Datetime.now()

            return True
    
    @api.model
    def _set_variables(self,case):
        # Da capire cosa succede per i sottoprocessi se setti una variabile del padre
        data = {}
        flag = False
        for v in case.case_object_ids :
            if bool(v.process_object_id.pm_variable_id):
                data[v.name] = v.get_val()
                flag=True
        if flag: 
            case.process_group_id._set_case_variables(case.pm_case_id,data)
            
    @api.model
    def _route_case_from_task(self,task_executed_id):
        case = task_executed_id.case_id
        case.sudo().process_group_id._set_variables(case)
        case_info =  case.process_group_id._get_case_info(case.pm_case_id)
        if (case_info['app_status']=='COMPLETED' and  case.state == 'in_progress') :
            case.state = 'completed'
            if (case.parent_id) :
                case.process_group_id._route_case_from_task(case.parent_task_id)
        else :
            current_tasks_pre = case.process_group_id._get_current_tasks(case_info)
            cid_pre = [ctask['tas_uid'] for ctask in current_tasks_pre]
            
            if (case.process_group_id._route_case(case.pm_case_id,task_executed_id.pm_del_index)) :
                    current_tasks_post = case.process_group_id._get_current_tasks(case_info)
                    cid_post = [ctask['tas_uid'] for ctask in current_tasks_post] 
                    for current_task in current_tasks_post :
                        activity_id = self.env['syd_bpm.activity'].search([('pm_activity_id','=',current_task['tas_uid'])])
                        task_id = self.env['syd_bpm.task_executed'].search([('case_id','=',case.id),('pm_task_id','=',current_task['tas_uid']),('pm_del_index','=',current_task['del_index'])])
                        # per risolvere loop e task paralleli
                        if (not bool(task_id)):
                            self.env['syd_bpm.task_executed'].create(
                                                {
                                                    'name':current_task['tas_title'],
                                                    'pm_task_id':current_task['tas_uid'],
                                                    'pm_del_index':current_task['del_index'],
                                                    'is_task_active' : True,
                                                    'case_id':case.id,
                                                    'date_task_start' : fields.Datetime.now(),
                                                    'activity_id' :activity_id.id
                                                    }
                                                )
                    for current_task in current_tasks_pre :
                            # Task completati
                        if (current_task['tas_uid'] not in cid_post):
                            task_completed = self.env['syd_bpm.task_executed'].search([('pm_task_id','=',current_task['tas_uid']),('case_id','=',case.id,)],limit=1)
                            # TODO
                            task_completed.is_task_active=False
                            task_completed.date_task_end=fields.Datetime.now()
                
            
            
            case_info =  case.process_group_id._get_case_info(case.pm_case_id)
            ## Ad esempio dopo azioni automatiche 
            if (case_info['app_status']=='COMPLETED' and case.state == 'in_progress') :
                case.state = 'completed'
                if (case.parent_id) :
                    case.process_group_id._route_case_from_task(case.parent_task_id)    
    
           
class Process(models.Model):
    _inherit = 'syd_bpm.process'
    
    
    pm_process_id = fields.Char(string='Process Maker Process ID',required=False)
    export_data_url = fields.Char(string='Process Export URL')
    export_data = fields.Char(string='Process Export')

    def test_create_new_process(self):
        if self.pm_process_id:
            self.process_group_id.start_process(self, None)
        data_url_str = self.process_group_id._get_export_data_url(self.pm_process_id)
        if data_url_str:
            self.export_data_url = data_url_str.get('url')
            if self.export_data_url:
                _headers = {'Authorization': 'Bearer '+self.process_group_id.pm_access_token}
                res = requests.get(self.export_data_url, headers=_headers)
                if res.status_code == 200 and res.ok:
                    self.export_data = res.content

   
class Activity(models.Model):
    _inherit = 'syd_bpm.activity'
    
    pm_callable_id = fields.Char(string='Process Maker Node Identifier ID')
    pm_activity_id = fields.Char(string='Process Maker Request ID', required=False)
    pm_user = fields.Char(string="Process Maker User ID")
    related_model = fields.Char(string='Related Model')
    related_id = fields.Char(string='Related Record ID')
    status = fields.Selection([('ACTIVE', 'IN PROGRESS'), ('ERROR', 'ERROR'), ('CANCELED', 'CANCELED'),('COMPLETED', 'COMPLETED')],string='Status', default='ACTIVE')
    
    def start_activity(self):
        pass

    
    
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

    def _compute_is_assigned_to(self):
        for record in self:
            record.is_assigned_to = bool(record.pm_assigned_to.id == self.env.uid)
        

    def confirm_case(self):
        """
        /tasks/{task_id} Update a task
        """
        _data = {
            "status": "COMPLETED",
            "data": {
                "form_input_1": "test"
            }
        }
        if self.process_id:
            res = self.process_id.process_group_id._call(f'tasks/{self.pm_case_id}', jsonobject=json.dumps(_data), method='PUT')
            if res:
                if res.get('status') and res.get('status')=='CLOSED':
                    self.state='completed'
                params = {
                    'process_request_id': int(self.process_id.pm_process_id)
                }
                pm_tasks = self.process_id.process_group_id._call('tasks', params, method='GET')
                if pm_tasks.get('data'):
                    for item in pm_tasks.get('data'):
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
                                'process_id': self.process_id.id,
                                'related_model':self.related_model,
                                'related_id':int(self.related_id) if isinstance(self.related_id, int) else str(self.related_id),
                                'state':_state,
                            }
                            self.env['syd_bpm.case'].create(_val)
                else:
                    _logger.warning(pm_tasks)
            return True
   

class TaskExecuted(models.Model):
    _inherit = 'syd_bpm.task_executed'
    
    
    
    pm_task_id = fields.Char('Activity Id')
    pm_del_index = fields.Integer('Del Index')
    
                                           
    
    def _val_note(self,user_id):
        res = super(TaskExecuted,self)._val_note(user_id)                                          
        res['pm_del_index'] = self.pm_del_index
        return res
    
   
    
    

    

    