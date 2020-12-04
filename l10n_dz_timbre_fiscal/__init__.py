from . import models

import odoo
from odoo import api, SUPERUSER_ID

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    if 'config.timbre' in env:
        config_timbre = env['config.timbre'].search([])

        # si aucune configuration trouvée, créer une #
        account_id = env['account.account'].search([('code','=','445750')],limit=1).id
		
        if len(config_timbre) == 0:
            # creer une configuration d'importation #
            id_created_config_timbre = env['config.timbre'].create({
       			'name':"Configuration timbre",
				'display_name':"Configuration timbre",
				'tranche': 100.0,
				'prix': 1.0,
				'mnt_min': 500.0,
				'mnt_max': 250000.0,
				'sale_timbre': account_id,
				'purchase_timbre': account_id,
			})