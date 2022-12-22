import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PaymentCheque(models.Model):
    _inherit = 'account.payment'


    def post(self):
        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconciliable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconciliable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.

                ***********************************************************
                    override in case of used chque payment method
                        add cheque validation
                        add to different stage
                                    1 - deliver
                                    2 - collected
        """


        if self.payment_method_code == 'manual':
            return super(PaymentCheque, self).sudo().post()
        ctx_del = self._context.get('delivery_aml')
        ctx_bank = self._context.get('bank_aml')
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>DEEEEEEEEEEEEEELLLLLL ",ctx_del,ctx_bank)

        ctx_del_batch = self._context.get('delivery_aml_batch')
        ctx_bank_batch = self._context.get('bank_aml_batch')
        ctx_discount_batch = self._context.get('discount_check')
        collect_discount = self._context.get('collect_disc_batch')


        ctx_loan_batch = self._context.get('loan_check')
        if self.cheque_books_id:
            if ctx_del == 1 or ctx_bank == 1:
                pass
            else:

                self.get_cheque(from_post=True)

        if ctx_bank:
            if not self.withdrawal_date:
                raise ValidationError('please Enter Withdrawal Date ...')
            self.hide_bank = True
            self.hide_del = True
        if ctx_del:
            if not self.delivery_date:
                raise ValidationError('please Enter Delivery Date ...')
            self.hide_del = True

        for rec in self:

            if not self.cheque_books_id and not collect_discount and not ctx_loan_batch and not ctx_discount_batch and not ctx_bank and not ctx_del and not ctx_bank_batch and not ctx_del_batch:
                if rec.state not in 'draft':
                    raise UserError(_("Only a draft payment can be posted."))

                if any(inv.state != 'open' for inv in rec.reconciled_invoice_ids):
                    raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))
            if ctx_bank_batch:
                if rec.state_check in ['collected']:
                    return True
            if ctx_del_batch:
                if rec.state_check in ['collected', 'under_coll']:
                    return True
            # Use the right sequence to set the name
            if rec.cheque_books_id and rec.cheque_number:
                rec.cheque_books_id.book_state = 'open'
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>11")
                rec.cheque_books_id.used_book = True
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>22")
            if rec.payment_type == 'transfer':
                sequence_code = 'account.payment.transfer'
            else:
                if rec.partner_type == 'customer':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.customer.invoice'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.customer.refund'
                if rec.partner_type == 'supplier':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.supplier.refund'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.supplier.invoice'
            if not collect_discount and not ctx_loan_batch and not ctx_discount_batch and not ctx_bank and not ctx_del and not ctx_bank_batch and not ctx_del_batch:
                rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(
                    sequence_code)
            if not rec.name and rec.payment_type != 'transfer':
                raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

            # Create the journal entry
            # amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)

            default_journal_debit_account = False
            default_journal_credit_account = False
            liq_move = self._get_liquidity_move_line_vals(rec.amount)
            print("liq_move :: ",liq_move)

            payment = rec

            if payment.payment_type in ('outbound', 'transfer'):
                # counterpart_amount = payment.amount
                default_journal_debit_account = payment.journal_id.default_account_id

                # liquidity_line_account = payment.journal_id.default_account_id

                # payment.journal_id.default_account_id = liq_move['account_id']



                # payment.journal_id.default_account_id = default_journal_debit_account
            else:
                # counterpart_amount = -payment.amount
                default_journal_credit_account = payment.journal_id.default_account_id

                # liquidity_line_account = payment.journal_id.default_account_id

                # payment.journal_id.default_account_id = liq_move['account_id']



                # payment.journal_id.default_account_id = default_journal_credit_account

            AccountMove = self.env['account.move'].with_context(default_type='entry')
            dict_val = {'ctx_del':ctx_del,'ctx_bank':ctx_bank,'ctx_del_batch':ctx_del_batch,'ctx_bank_batch':ctx_bank_batch,'ctx_discount_batch':ctx_discount_batch,'collect_discount':collect_discount}
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>dict_valdict_val ",dict_val)
            payment_move_dict = rec.with_context(ctx_del=ctx_del,ctx_bank=ctx_bank,ctx_del_batch=ctx_del_batch,ctx_bank_batch=ctx_bank_batch,ctx_discount_batch=ctx_discount_batch,collect_discount=collect_discount)._prepare_payment_moves()

            #8
            payment_move_dict[0]['journal_id'] = liq_move['journal_id']
            # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>PREPAER",rec._prepare_payment_moves())
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>payment_move_dict ",payment_move_dict)
            # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>payment_move_dict ",payment_move_dict.line_ids)

            move = AccountMove.sudo().create(payment_move_dict)
            print(" move create payment_move",payment_move_dict)

            for line_payment in move.line_ids:
                print("payment id line ",line_payment.payment_id.id)
                line_payment.payment_id = self.id
            move.name = '/'

            for one_move in move:
                for line in one_move.line_ids:
                    if line.account_id.id == liq_move['account_id']:
                        line.name = liq_move['name']
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>JOR MOV1", line.move_id.state)
                        # line.move_id.journal_id = liq_move['journal_id']
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>JOR MOV2")
                    line.date_maturity = rec.actual_date

            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>JOR MOV3 ",move.name)

            move.filtered(lambda move: move.journal_id.post_at != 'bank_rec').sudo().post()

            # move.journal_id.sequence_number_next += 1
            # Update the state / move before performing any reconciliation.
            move_name = self._get_move_name_transfer_separator().join(move.mapped('name'))
            rec.write({'state': 'posted', 'move_name': move_name})

            if rec.payment_type in ('inbound', 'outbound'):
                # ==== 'inbound' / 'outbound' ====
                if rec.reconciled_invoice_ids:
                    (move[0] + rec.reconciled_invoice_ids).line_ids \
                        .filtered(lambda line: not line.reconciled and line.account_id.id == rec._get_destination_account_id())\
                        .reconcile()
            elif rec.payment_type == 'transfer':
                # ==== 'transfer' ====
                move.mapped('line_ids')\
                    .filtered(lambda line: line.account_id == rec.company_id.transfer_account_id)\
                    .reconcile()















            ctx_del = self._context.get('delivery_aml')
            ctx_bank = self._context.get('bank_aml')


            if ctx_bank_batch:
                rec.write({'state_check': 'collected'})
                print("rec.move_date",rec.move_date)
                move.date = rec.ref_coll_batch
            elif ctx_del_batch:
                print("rec.move_date",rec.move_date)
                rec.write({'state_check': 'under_coll'})

                move.date = fields.Date.today()

            elif ctx_del:
                rec.write({'state_check': 'deliver'})
            elif ctx_loan_batch:
                rec.write({'state_check': 'loan'})
            elif ctx_bank or collect_discount:
                rec.write({'state_check': 'collected'})
            elif ctx_discount_batch:
                rec.write({'state_check': 'discount'})

            else:
                if self.cheque_books_id:
                    if self.multi_check_payment:
                        rec.write({'state': 'posted'})
                    else:
                        rec.write({'state': 'posted', 'cheque_number': self.active_cheque_number})
                else:
                    rec.write({'state': 'posted', 'cheque_number': self.active_cheque_number})
            # payment.journal_id.default_account_id = default_journal_debit_account
            # payment.journal_id.default_account_id = default_journal_credit_account
            # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>||||||",rec,rec.state , ' || ',payment.destination_account_id.name)

        # 1/0
        return True

