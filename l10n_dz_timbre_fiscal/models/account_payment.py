# -*- encoding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging as log

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.onchange('invoice_ids')
    def update_journal_id(self):
        for record in self:
            for invoice in record.invoice_ids:
                if invoice.payment_mode_type == "cash":
                    record.journal_id = self.env['account.journal'].search([('type','=','cash')]).id

class PaymmentMode(models.Model):
    _name = 'account.payment.mode'

    name = fields.Char(
        string="Nom",
        required=True
    )

    mode_type = fields.Selection(
        [('cash', 'Especes'), ('bank', 'Banque')],
        string="Type"
    )