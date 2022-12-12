# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import except_orm, Warning, RedirectWarning, ValidationError


class AccountJournalInherit(models.Model):
    _inherit = 'account.journal'

    multi_cheque_book = fields.Boolean()
    notes_payable = fields.Many2one('account.account')
    deliver_account = fields.Many2one('account.account')
    cheque_books_ids = fields.One2many(comodel_name='cheque.books', inverse_name='account_journal_cheque_id', copy=True)
    book_prefix = fields.Char()
    reveivable_under_collection = fields.Many2one('account.account')
    discount_check_account = fields.Many2one('account.account')
    # loan_account = fields.Many2one('account.account', related='bank_id.account_id', readonly=1)
    is_notes_receivable = fields.Boolean()


    @api.depends('check_manual_sequencing')
    def _get_check_next_number(self):
        print("_get_check_next_number :: ")
        if self.check_sequence_id:
            self.check_next_number = self.check_sequence_id.number_next_actual

        if not self.multi_cheque_book and self.cheque_books_ids:
            cheque_book_object = [r for r in self.cheque_books_ids if r.activate == True]
            if cheque_book_object:
                cheque_book_object = cheque_book_object[0]
                if cheque_book_object.last_use == 0:
                    self.update({'check_next_number': cheque_book_object.start_from})

                else:
                    self.update({'check_next_number': cheque_book_object.last_use + 1})

        else:
            self.check_next_number = 1

    post_at = fields.Selection([('pay_val', 'Payment Validation'), ('bank_rec', 'Bank Reconciliation')], string="Post At", default='pay_val')
