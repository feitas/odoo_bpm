# -*- coding: utf-8 -*-
# Copyright 2018-2019 SayDigital (https://www.saydigital.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': "BPM - Business Process Management",
    'summary': """
        SayDigital BPM""",

    'description': """
         With this module you can manage :
         
         - Process
         - Automated Activity
         - Manual Activity
         
         
    """,

    'author': "SayDigital",
    'website': "http://www.saydigital.it",
    'license': 'LGPL-3',
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'project',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','base_automation','syd_note_name','syd_dynamic_wizard','syd_history_back'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'views/views.xml',
        'wizard/views.xml',
        'wizard/act_window.xml',
        'views/res_config_settings_views.xml',
        'views/menu.xml',
        
    ],
    'assets': {
        'web.assets_backend': [
            'syd_bpm/static/src/js/bpm_graph_view.js',
            'syd_bpm/static/src/js/bpm_pivot_view.js',
            'syd_bpm/static/src/js/bpm_view_registry.js',
        ],
    },
    'installable': True,
    'application': True,
}