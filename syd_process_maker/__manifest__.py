# -*- coding: utf-8 -*-
# Copyright 2018-2019 SayDigital (https://www.saydigital.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': "BPM - ProcessMaker Integration",
    'summary': """
        SayDigital BPM - ProcessMaker""",

    'description': """
         With this module you can manage :
         
         - Process through ProcessMaker
         
        
         
    """,
    'license': 'LGPL-3',
    'author': "SayDigital",
    'website': "http://www.saydigital.it",


    'category': 'project',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['syd_bpm','web'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'datas/datas.xml',
        
        'views/process_views.xml',
        'views/mail_activity_views.xml',
        'views/views.xml',
        'views/process_views.xml',
        'views/dynamice_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'syd_process_maker/static/src/js/*',
        ],
    },
    'qweb': [
    ],
    'installable': True,
    'application': False,
}