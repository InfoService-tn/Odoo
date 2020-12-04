# -*- encoding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp
import logging
from odoo.tools import float_is_zero

class AccountInvoice(models.Model):
    _inherit = 'account.move'

    payment_mode = fields.Many2one(
        'account.payment.mode',
        string="Mode de paiement"
    )

    amount_timbre = fields.Float(
        string='Droit de timbre',
        readonly=True,
        compute='_compute_amount_timbre'
    )

    total_timbre = fields.Float(
        string='Montant à payé',
        readonly=True,
        compute='_compute_amount_timbre'
    )

    payment_mode_type = fields.Char("Type")

    @api.onchange('payment_mode')
    def _onchange_payment_mode(self):
        for record in self:
            record.payment_mode_type = record.payment_mode.mode_type if record.payment_mode else False
        self._onchange_recompute_dynamic_lines()

    def _timbre(self, amount_total):
        timbre = 0.0
        if self.payment_mode and self.payment_mode.mode_type == "cash":
            timbre = self.env['config.timbre']._timbre(amount_total)
        return timbre

    @api.depends('amount_total')
    def _compute_amount_timbre(self):
        for record in self:
            record.amount_timbre = record._timbre(record.amount_total)
            record.total_timbre = record.amount_total + record.amount_timbre if record.amount_timbre else 0.0

    def _recompute_timbre(self):
        self.ensure_one()
        if self.payment_mode and self.payment_mode.mode_type == 'cash':
            in_draft_mode = self != self._origin
            create_method = in_draft_mode and self.env['account.move.line'].new or self.env['account.move.line'].create

            account_timbre_id = self.env['config.timbre'].search([], limit=1).sale_timbre
            timbre_line_vals = {
                'name': 'Timbre' if self.type == 'out_invoice' else 'Droit de timbre',
                'quantity': 1.0,
                'currency_id': self.currency_id.id if self.currency_id != self.company_id.currency_id else False,
                'account_id': account_timbre_id.id,
                'move_id': self.id,
                'exclude_from_invoice_tab': True,
            }

            existing_timbre_line = self.line_ids.filtered(lambda line: line.account_id == account_timbre_id)
            timbre_line = create_method(timbre_line_vals) if not existing_timbre_line else existing_timbre_line

            existing_lines = self.line_ids.filtered(lambda line: line.account_id != account_timbre_id and \
                                                                 line.account_id.user_type_id.type not in ('receivable', 'payable'))

            if self.type in ('out_invoice', 'in_invoice', 'out_receipt'):
                curr_line = 'credit'
            elif self.type in ('out_refund', 'in_refund', 'in_receipt'):
                curr_line = 'debit'

            curr_amount = sum(existing_lines.mapped(curr_line))
            timbre_line.update({
                curr_line: self.env['config.timbre']._timbre(curr_amount),
                # todo: lorsque la devise est differente de la devise de l'entreprise
                'amount_currency': 0.0,
            })

            others_lines = self.line_ids.filtered(lambda line: line.account_id != account_timbre_id)
            if not others_lines:
                self.line_ids -= existing_timbre_line

            if in_draft_mode:
                timbre_line._onchange_amount_currency()
                timbre_line._onchange_balance()

    def _recompute_dynamic_lines(self, recompute_all_taxes=False, recompute_tax_base_amount=False):
        for invoice in self:
            # verifier la/les taxe(s) avant calcule/recalcule du timbre
            for line in invoice.line_ids:
                if line.recompute_tax_line:
                    recompute_all_taxes = True
                    line.recompute_tax_line = False
                if recompute_all_taxes:
                    invoice._recompute_tax_lines()
                if recompute_tax_base_amount:
                    invoice._recompute_tax_lines(recompute_tax_base_amount=True)

            if invoice.is_invoice(include_receipts=False):
                invoice._recompute_timbre()

        return super(AccountInvoice, self)._recompute_dynamic_lines(recompute_all_taxes, recompute_tax_base_amount)
