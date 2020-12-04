# -*- encoding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from math import ceil
import logging as log

class ConfigTimbre(models.Model):
    _name = 'config.timbre'

    name = fields.Char(
        string="Nom", 
        required=True
    )

    tranche = fields.Float(
        string="Tranche", 
        required=True, 
        default=0.0,
    )

    prix = fields.Float(
        string="Prix", 
        required=True, 
        default=0.0,
    )

    # comptes contreparties vente
    sale_timbre = fields.Many2one(
        comodel_name='account.account', 
        string="Compte contrepartie vente"
    )

    # comptes contreparties achat
    purchase_timbre = fields.Many2one(
        comodel_name='account.account', 
        string="Compte contrepartie achat"
    )

    # Montant Minimal TTC
    mnt_min = fields.Float(
        string="Montant minimal", 
        required=True, 
        default=0.0,
    )

    # Montant Maximal TTC
    mnt_max = fields.Float(
        string="Montant maximal", 
        required=True, 
        default=0.0,
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Le nom doit être unique par entreprise!'),
    ]

    @api.model
    def _timbre(self, montant):
        montant_avec_timbre = 0.0
        config_timbre_id  = self.env['config.timbre'].search([], limit=1)
        
        if not config_timbre_id :
            raise UserError(_('Pas de configuration du calcul Timbre.'))
        
        if montant >= config_timbre_id.mnt_min and montant <= config_timbre_id.mnt_max:
            if config_timbre_id.tranche:
                montant_avec_timbre = (montant * config_timbre_id.prix) / config_timbre_id.tranche
        if montant > config_timbre_id.mnt_max:
            if config_timbre_id.tranche:
                montant_avec_timbre = (config_timbre_id.mnt_max * config_timbre_id.prix) / config_timbre_id.tranche
        
        return montant_avec_timbre
    
    @api.onchange('tranche', 'prix', 'mnt_min', 'mnt_max')
    def chek_negative_values(self):
        for record in self:
            if record.tranche < 0:
                record.update({'tranche': (record.tranche * -1),})
            if record.prix < 0:
                record.update({'prix': (record.prix * -1),})
            if record.mnt_min < 0:
                record.update({'mnt_min': (record.mnt_min * -1),})
            if record.mnt_max < 0:
                record.update({'mnt_max': (record.mnt_max * -1),})