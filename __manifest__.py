# -*- coding: utf-8 -*-
{
    'name': "Rate Approval",

    'summary': """
        Rate Approval of product.
        """,

    'description': """
        Complete Process of Rate Approval of product.
    """,

    'author': "Ergo Ventures",
    'website': "http://www.ergo-ventures.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Rate Approval',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/rate_approval_security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/ready_mix_rate_approval_views.xml',
        'views/block_rate_approval_views.xml',
        'views/rate_approval_navigation.xml',
        'views/resources.xml',
        #'report/rate_approve_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}