{
    'name': 'syd_bpmnjs',
    'version': '11.0.1.0.0',
    'summary': '',
    'category': '',
    'author': '',
    'maintainer': '',
    'website': '',
    'license': 'LGPL-3',

    'depends': [
        'web', 'syd_bpm'
    ],

    'data': [

        'views/process_view.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'syd_bpmnjs/static/src/css/*',
            'syd_bpmnjs/static/src/js/*',
        ],
    },
    'qweb': [
        'static/src/xml/template.xml', ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
