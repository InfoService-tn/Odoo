# -*- coding: utf-8 -*-
{
    'name': "Algeria - Timbre",
    'summary': """ This is the module to manage the Fiscal timbre for Algeria in odoo 11 """,
    "contributors": [
        "1 <Djamel Eddine YAGOUB>",
        "2 <Nassim REFES>",
        "3 <Kamel BENCHEHIDA>",
    ],
    'author': "IGPro",
    'website': "https://igpro-online.net",
    'depends': [
        'base',
        'account'
    ],
    'data': [
        'views/configuration_timbre.xml',
        'views/account_move.xml',
        'views/account_move_report.xml',
        'security/ir.model.access.csv',
    ],

    # les proprités d'installation #
    'installable': True,
    'auto_install': False,
    'application': False,
    'post_init_hook': "post_init_hook",
}