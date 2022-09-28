# -*- coding: utf-8 -*-

{
    'name': "销售工作流",

    'summary': """
        With this module you can give a name to a note """,

    'description': """
        With this module you can give a name to a note
    """,
    'license': 'LGPL-3',
    'author': "Feitas",
    'website': "https://www.wffeitas.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale', 'syd_process_maker'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_views.xml',
    ],
    # only loaded in demonstration mode
    
}