import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta




class PaymentCheque(models.Model):
    _inherit = 'account.payment'

    cheque_books_id = fields.Many2one(comodel_name='cheque.books', domain=lambda self: self.get_cheque_number())

    cheque_number = fields.Integer(copy=False)
    state_check = fields.Selection([('draft', 'Draft'), ('posted', 'Posted'), ('deliver', 'Deliver'),
                              ('under_coll', 'Under collection'),
                              ('collected', 'Withdrawal'),
                              ('insured', 'Insured'),
                              ('sent', 'Sent'), ('reconciled', 'Reconciled'),
                              ('cancelled', 'Cancelled'),
                              ('discount', 'Discount'),
                              ('loan', 'Loan'),
                              ('refund_from_discount', "Refund From Discount"),
                              ('refunded_from_notes', 'Refund Notes Receivable'),
                              ('refunded_under_collection', 'Refund Under collection'),
                              ('check_refund', 'Refunded')],
                             readonly=True, default='draft', copy=False, string="Check Status ")
    move_name = fields.Char(string='Journal Entry Name', readonly=True,
        default=False, copy=False,
        help="Technical field holding the number given to the journal entry, automatically set when the statement line is reconciled then stored to set the same number again if the line is cancelled, set to draft and re-processed again.")
    payment_difference_handling = fields.Selection([('open', 'Keep open'), ('reconcile', 'Mark invoice as fully paid')], default='open', string="Payment Difference Handling", copy=False)
    due_date = fields.Date()
    actual_date = fields.Date()
    hide_del = fields.Boolean()
    hide_bank = fields.Boolean()
    # active_cheque_number = fields.Integer(related='journal_id.check_next_number')
    active_cheque_number = fields.Char(related='journal_id.check_next_number')
    active_cheque = fields.Boolean()
    # bank_id = fields.Many2one(comodel_name='account.journal')
    bank_name = fields.Char()
    check_number_2 = fields.Char(store=True  ,readonly=False,string="Check Number" )
    check_type = fields.Char()
    move_date = fields.Date()
    multi_select = fields.Boolean()
    refund_date = fields.Date()
    delivery_date = fields.Date()
    withdrawal_date = fields.Date()
    multi_check_payment = fields.Boolean(related='journal_id.multi_cheque_book')
    # cheque_number_rel = fields.Char(compute='get_cheque_number_name')
    cheque_number_rel = fields.Char()
    refund_delivery_date = fields.Date()
    loan_date = fields.Date()
    ref_coll_batch = fields.Date()
    batch_state = fields.Selection(related='batch_payment_id.state', default='draft')
    refund_notes_date = fields.Date(string='Refund Under collection Date', readonly=True)

    destination_account_id = fields.Many2one('account.account', compute='_compute_destination_account_id', readonly=False,store=False)

    @api.onchange('payment_type', 'payment_method_id', 'journal_id')
    def reset_draft_payment(self):
        for rec in self:
            if rec.state == 'draft':
                rec.due_date = False
                rec.actual_date = False
                rec.bank_name = False
                # rec.check_number = False

    @api.constrains('payment_type', 'payment_method_id')
    def notes_receivable_payment_journal(self):
        for rec in self:
            if rec.payment_type == 'inbound' and rec.payment_method_code == 'batch_deposit':
                if rec.journal_id.is_notes_receivable == False:
                    raise ValidationError('Payment Journal Is Not Notes Receivable Journal!')

    @api.onchange('multi_check_payment', 'cheque_books_id')
    def get_cheque_number_name(self):
        if self.journal_id:
            bank_account = self.journal_id
        else:
            if 'params' in self._context:
                if 'id' in self._context['params']:
                    obj = self.env['account.payment'].browse(self._context['params']['id'])
                    bank_account = obj.journal_id
        if self.cheque_books_id:
            if not bank_account.multi_cheque_book:
                if bank_account.cheque_books_ids:
                    cheque_book_object = [r for r in bank_account.cheque_books_ids if r.activate == True][0]
                    if self.state == 'draft':
                        self.cheque_number_rel = str(self.active_cheque_number)
                    # elif cheque_book_object.book_state != 'open' and self.state == 'draft':
                    #     self.cheque_number_rel = str(self.active_cheque_number )

                    else:
                        self.cheque_number_rel = str(self.cheque_number)
            else:
                self.active_cheque_number = self.cheque_number
        else:
            self.cheque_number_rel = False
            return False
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.CHECK",self.cheque_books_id , self.cheque_number_rel)


    def button_open_batch_payment(self):
        ''' Redirect the user to the batch payments containing this payment.
        :return:    An action on account.batch.payment.
        '''
        self.ensure_one()
        compose_form = self.env.ref('check_management_15.account_payment_batch_deposite_inherit_form_id')
        return {
            'name': _("Batch Payment"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.batch.payment',
            'context': {'create': False},
            'view_mode': 'form',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'res_id': self.batch_payment_id.id,
        }
    collect_bank = fields.Many2one('account.journal',related='batch_payment_id.bank_id')


    @api.onchange('due_date')
    def get_default_actual_date(self):
        if self.due_date:
            self.actual_date = self.due_date

    @api.onchange('cheque_books_id')
    def get_cheque_book(self):
        print("get_cheque_book :: : ")
        if self.cheque_books_id:

            self.active_cheque = self.cheque_books_id.activate
            check_use = self.env['account.payment'].search(
                [('cheque_books_id', '=', self.cheque_books_id.id), ('state', '=', 'posted'), ('state_check', 'in', ['posted','under_coll','collected'])])
            self.cheque_number = len(check_use) + 1
            check_use_before = self.env['account.payment'].search(
                [('cheque_books_id', '=', self.cheque_books_id.id),('cheque_number','=',len(check_use) + 1), ('state', '=', 'posted'),
                 ('state_check', 'in', ['posted', 'under_coll', 'collected','deliver'])])
            if check_use_before:
                self.cheque_number = len(check_use) + 2

        else:

            self.cheque_number = 0

    # @api.onchange('payment_type','journal_id')
    # def default_cheque_book(self):
    #     self.cheque_books_id = None


    def get_cheque_number(self):

        """""
            default domain for cheque book

            :return list of cheque books in the domain depends on the input of journal

        """

        bank_account = False
        if self.journal_id:
            bank_account = self.journal_id
        else:
            if 'params' in self._context:
                if 'id' in self._context['params']:
                    obj = self.env['account.payment'].browse(self._context['params']['id'])
                    bank_account = obj.journal_id

        if bank_account:
            if not bank_account.multi_cheque_book:
                if bank_account.cheque_books_ids:
                    cheque_book_object = [r for r in bank_account.cheque_books_ids if r.activate == True]
                    if cheque_book_object:
                        return [('id', '=', cheque_book_object[0].id)]
            else:
                if bank_account.cheque_books_ids:
                    cheque_book_object = [r.id for r in bank_account.cheque_books_ids]
                    return [('id', 'in', cheque_book_object)]

    @api.onchange('payment_method_id', 'journal_id')
    def get_cheque_number_from_onchange(self):

        """""
            default domain for cheque book

            :return list of cheque books in the domain depends on the input of journal

        """

        bank_account = False
        if self.journal_id:
            bank_account = self.journal_id
        self.get_cheque_book()

        if bank_account:
            if not bank_account.multi_cheque_book:
                if bank_account.cheque_books_ids:
                    cheque_book_object = [r for r in bank_account.cheque_books_ids if r.activate == True]
                    if cheque_book_object:
                        cheque_book_object = cheque_book_object[0]
                        if cheque_book_object.book_state == 'done' and self.payment_method_code == 'check_printing':
                            raise ValidationError(
                                'The Check Book ({}) Is Ending, Please Deactivate It or Select Another Journal'.format(
                                    cheque_book_object.name))
                        self.update({'cheque_books_id': cheque_book_object.id})
                        return {'domain': {'cheque_books_id': [('id', '=', cheque_book_object.id)]}}
                else:
                    return {'domain': {'cheque_books_id': [('id', '=', -1)]}}

            else:
                if bank_account.cheque_books_ids:
                    cheque_book_object = [r.id for r in bank_account.cheque_books_ids]
                    return {'domain': {'cheque_books_id': [('id', 'in', cheque_book_object)]}}
                else:
                    return {'domain': {'cheque_books_id': [('id', '=', -1)]}}

        else:
            return {'domain': {'cheque_books_id': [('id', '=', -1)]}}

    @api.constrains('cheque_number')
    def get_cheque(self, from_post=False):

        """""
                get cheque number and validate
                                            1 - if cheque used or not
                                            2 - if cheque valid to in multi cheque book's mood
        """
        print("enter get_cheque")
        bank_account = self.journal_id
        if self.payment_method_code == 'manual':
            return False
        if bank_account:
            print("enter get_cheque 2")
            if not bank_account.multi_cheque_book:
                if bank_account.cheque_books_ids and self.payment_method_code == 'check_printing':
                    cheque_book_object = [r for r in bank_account.cheque_books_ids if r.activate == True]
                    if cheque_book_object:
                        cheque_book_object = cheque_book_object[0]
                    else:
                        raise ValidationError(
                            'Please Activate One Check Book or Make Your bank Account ({}) In Multi Check Mood'.format(
                                bank_account.name))
                    bank_account._get_check_next_number()
                    if cheque_book_object.last_use == 0 and from_post:
                        cheque_book_object.last_use = cheque_book_object.start_from
                    else:
                        if self.state == 'draft' and from_post:
                            bank_account.validate_cheque_book()
                            last_u = cheque_book_object.last_use
                            cheque_book_object.write({'last_use': bank_account.check_next_number})

            else:
                if bank_account.cheque_books_ids:

                    cheque_book_object = [r for r in bank_account.cheque_books_ids if r.id == self.cheque_books_id.id][
                        0]

                    if int(self.cheque_number) > cheque_book_object.end_in or int(
                            self.cheque_number) < cheque_book_object.start_from:
                        raise ValidationError(
                            'the number must be in between {} and {}'.format(cheque_book_object.start_from,
                                                                             cheque_book_object.end_in))
                    else:
                        used_cheque_length = self.env['account.payment'].search(
                            [('journal_id', '=', self.journal_id.id),
                             ('cheque_books_id', '=', self.cheque_books_id.id),
                             ('state_check', 'in', ['posted', 'deliver', 'collected'])]
                        )
                        cheque_book_length = self.cheque_books_id.end_in - self.cheque_books_id.start_from + 1

                        # if len(used_cheque_length)  > 0:
                        #     raise ValidationError(
                        #         "{} Is Ending, Please Open New One !".format(self.cheque_books_id.name))

    def write(self, vals):
        for rec in self:
            if 'cheque_books_id' in vals:
                check_id = vals['cheque_books_id']
            else:
                check_id = rec.cheque_books_id.id
            if 'cheque_number' in vals:
                if check_id:
                    ap_obj = rec.env['account.payment'].search(
                        [('cheque_books_id', '=', check_id), ('cheque_number', '=', int(vals['cheque_number'])),
                         ('state', '!=', 'draft')])
                    if ap_obj:
                        raise ValidationError('this Check Number is already used or this payment is posted ')

            for r in rec:
                if r.state == 'draft' and r.payment_method_code != 'check_printing':
                    vals['cheque_books_id'] = None
            if 'batch_payment_id' in vals:
                if vals['batch_payment_id']:
                    bd = self.env['account.batch.payment'].browse(vals['batch_payment_id'])
                    if bd.state != 'draft':
                        raise ValidationError(
                            'you can\'t add new check within this batch deposite since it\'s not in new stage')
            return super(PaymentCheque, self).write(vals)

    @api.onchange('payment_method_line_id')
    def hide_bank_buttons(self):
        print("hide_bank_buttons")
        if self.payment_method_code != 'check_printing':
            self.hide_bank = True
            self.hide_del = True

        else:
            self.hide_bank = False
            self.hide_del = False

    # check real working

    def delete_check_from_batch(self):
        if self.batch_payment_id.state == 'draft':
            self.write({'batch_payment_id': False})
        else:
            raise ValidationError('you can\'t delete line in batch not in draft state')

    def refund_payable(self):
        """"
            refunded of send check moves
            
        """""
        refund = self._context.get('refund')
        refund_delivery = self._context.get('refund_delivery')

        if refund:

            if not self.refund_date:
                raise ValidationError('Please Enter Refund Date')
            if self.state not in ['posted']:
                raise ValidationError(
                    "Can't create reverse entry for this payment since it's not in post or refunded from under collection state")
            if self.partner_type != 'customer':
                aml = self.env['account.move.line'].search(
                    [('payment_id', '=', self.id), ('debit', '>', 0), ('move_id.ref', 'not ilike', 'reversal of:'),
                     ('account_id', '=', self.partner_id.property_account_payable_id.id)])
            else:
                aml = self.env['account.move.line'].search(
                    [('payment_id', '=', self.id), ('debit', '>', 0), ('move_id.ref', 'not ilike', 'reversal of:'),
                     ('account_id', '=', self.partner_id.property_account_receivable_id.id)])

            aml_rec = self.env['account.move.line'].search(
                [('payment_id', '=', self.id), ('debit', '>', 0),
                 ('move_id.ref', 'not ilike', 'reversal of:')])

            for j in aml_rec:
                if self.state_check == 'refunded_under_collection':
                    break
                if j.debit > 0:
                    reconciled = self.env['account.partial.reconcile'].search([('debit_move_id', '=', j.id)])
                if j.credit > 0:
                    reconciled = self.env['account.partial.reconcile'].search([('credit_move_id', '=', j.id)])
                if reconciled:
                    raise ValidationError(
                        "A reconciled action has done for this payment unreconcile it to complete refund action")

            move = self.env['account.move'].browse(aml.move_id.id)
            default_values_list = []
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>MOVEEEE ",move)

            default_values_list.append({
                    'ref': _('Reversal of: %s') % (move.name) ,
                    'date':  self.refund_date or self.move_date or self.actual_date,
                    'journal_id': aml.journal_id.id,
                })

            move = move._reverse_moves(
                    default_values_list)

            # move.reverse_moves(
            #     self.refund_date or self.move_date or self.actual_date,
            #     aml.journal_id or False)

            # move = self.env['account.move'].browse(move.id)
            for k in move.line_ids:
                k.payment_id = self.id
            move.action_post()
            self.state_check = 'check_refund'
            self.hide_bank = True
            self.hide_del = True
            return True

        if refund_delivery:
            if not self.refund_delivery_date:
                raise ValidationError('Please Enter Deliver Refund Date')
            if self.state_check not in ['deliver']:
                raise ValidationError(
                    "Can't Create Reverse Entry For This Payment Since It's Not In Post or Refunded From Under collection State")

            self.hide_del = False
            aml = self.env['account.move.line'].search(
                [('payment_id', '=', self.id), ('credit', '>', 0), ('move_id.ref', 'not ilike', 'reversal of:'),
                 ('account_id', '=', self.journal_id.deliver_account.id)])

            aml_rec = self.env['account.move.line'].search(
                [('payment_id', '=', self.id), ('debit', '>', 0),
                 ('move_id.ref', 'not ilike', 'reversal of:')])

            for j in aml_rec:
                if self.state_check == 'refunded_under_collection':
                    break
                if j.debit > 0:
                    reconciled = self.env['account.partial.reconcile'].search([('debit_move_id', '=', j.id)])
                if j.credit > 0:
                    reconciled = self.env['account.partial.reconcile'].search([('credit_move_id', '=', j.id)])
                if reconciled:
                    raise ValidationError(
                        "A reconciled action has done for this payment unreconcile it to complete refund action")
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",aml)
            move = self.env['account.move'].browse(aml[0].move_id.id)
            default_values_list = []
            default_values_list.append({
                    'ref': _('Reversal of: %s,') % (move.name,) ,
                    'date': self.refund_delivery_date or self.actual_date,
                    # 'invoice_date': move.is_invoice(include_receipts=True) and (self.date or move.date) or False,
                    'journal_id': aml[0].journal_id.id,
                })

            move = move._reverse_moves(
                    default_values_list)

            # move.reverse_moves(
            #     self.refund_delivery_date or self.actual_date,
            #     aml[0].journal_id or False)

            # move = self.env['account.move'].browse(move)
            for k in move.line_ids:
                k.payment_id = self.id
            move.action_post()
            self.state_check = 'posted'
            return True

    def refund_notes(self):

        """""
            refunded of receive check moves 
        
        """""


        refund_notes_batch = self._context.get('ref_notes_batch')
        refund_under_collect_batch = self._context.get('ref_und_coll_batch')
        if refund_notes_batch:

            if not self.move_date:
                raise ValidationError('Please Enter Refund Notes Date')
            else:
                print("else refund notes batch")
                if self.state_check not in ['posted', 'refunded_under_collection']:
                    raise ValidationError(
                        "Can't create reverse entry for this payment since it's not in post or refunded from under collection state")
                # aml = self.move_line_ids.filtered(
                #     lambda r: r.debit > 0
                #     )
                aml = self.env['account.move.line'].search(
                    [('payment_id', '=', self.id), ('debit', '>', 0), ('name', '=', 'Receive Money (Batch Deposit)'),
                     ('move_id.ref', 'not ilike', 'reversal of:')])
                print("aml :> ",aml)
                # aml_rec = self.move_line_ids.filtered(
                #     lambda r: r.credit > 0
                #     )
                aml_rec = self.env['account.move.line'].search(
                    [('payment_id', '=', self.id), ('credit', '>', 0),
                     ('move_id.ref', 'not ilike', 'reversal of:')])

                for j in aml_rec:
                    if self.state_check == 'refunded_under_collection':
                        break
                    if j.debit > 0:
                        reconciled = self.env['account.partial.reconcile'].search([('debit_move_id', '=', j.id)])
                    if j.credit > 0:
                        reconciled = self.env['account.partial.reconcile'].search([('credit_move_id', '=', j.id)])
                    if reconciled:
                        raise ValidationError(
                            "A reconciled action has done for this payment unreconcile it to complete refund action")

                default_values_list = []


                move = self.env['account.move'].browse(aml.move_id.id)
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>MOVE refund notes res  ",move)



                default_values_list.append({
                    'ref': _('Reversal of: %s,') % (move.name,) ,
                    # 'date': self.actual_date or move.actual_date,
                    'date': self.move_date or self.actual_date,
                    # 'invoice_date': move.is_invoice(include_receipts=True) and (self.date or move.date) or False,
                    'journal_id': aml.journal_id.id,
                })

                move = move._reverse_moves(
                    default_values_list)

                move = self.env['account.move'].browse(move.id)



                # for k in move.line_ids:
                #     k.payment_id = self.id
                #     print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>After reserve ",k,k.payment_id)
                for line_payment in move.line_ids:
                    print("paynment id line ththt ", line_payment.payment_id.id)
                    line_payment.payment_id = self.id
                move.action_post()
                self.state_check = 'refunded_from_notes'
                return True
        if refund_under_collect_batch:
            if not self.ref_coll_batch:
                raise ValidationError('Please Enter Refunded Date')
            else:
                aml = self.env['account.move.line'].search(
                    [('payment_id', '=', self.id), ('name', '=', 'Under collection')], limit=1)
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>AML ",aml)
                default_values_list = []

                move = self.env['account.move'].browse(aml[0].move_id.id)


                default_values_list.append({
                    'ref': _('Reversal of: %s,') % (move.name,) ,
                    # 'date': self.actual_date or move.actual_date,
                    'date': self.ref_coll_batch or self.actual_date,
                    # 'invoice_date': move.is_invoice(include_receipts=True) and (self.date or move.date) or False,
                    'journal_id': aml[0].move_id.journal_id.id,
                })

                move = move._reverse_moves(
                    default_values_list)
                # move = self.env['account.move'].browse(move.id)

                for k in move.line_ids:
                    k.payment_id = self.id
                move.action_post()
                self.state_check = 'refunded_under_collection'
                return True

    def refund_discount(self):

        """""
            refunded of Discount check moves 

        """""

        if not self.ref_coll_batch:
            raise ValidationError('Please Enter Refund Date')
        refund_discount_batch = self._context.get('ref_disc_batch')

        if refund_discount_batch:
            if self.state_check not in ['loan', 'discount']:
                raise ValidationError(
                    "Can't create reverse entry for this payment since it's not in discount or loan state")
            aml = self.env['account.move.line'].search(
                [('payment_id', '=', self.id), ('debit', '>', 0), ('name', '=', 'Discount Check'),
                 ('move_id.ref', 'not ilike', 'reversal of:')])

            aml_rec = self.env['account.move.line'].search(
                [('payment_id', '=', self.id), ('credit', '>', 0),
                 ('move_id.ref', 'not ilike', 'reversal of:')])

            for j in aml_rec:
                if self.state_check == 'loan':
                    break
                if j.debit > 0:
                    reconciled = self.env['account.partial.reconcile'].search([('debit_move_id', '=', j.id)])
                if j.credit > 0:
                    reconciled = self.env['account.partial.reconcile'].search([('credit_move_id', '=', j.id)])
                if reconciled:
                    raise ValidationError(
                        "A reconciled action has done for this payment unreconcile it to complete refund action")

            move = self.env['account.move'].browse(aml[0].move_id.id)
            default_values_list = []
            default_values_list.append({
                    'ref': _('Reversal of: %s,') % (move.name,) ,
                    'date': self.ref_coll_batch , #self.move_date or self.actual_date,
                    # 'invoice_date': move.is_invoice(include_receipts=True) and (self.date or move.date) or False,
                    'journal_id': aml[0].journal_id.id,
                })

            move = move._reverse_moves(
                    default_values_list)
            # move = move.reverse_moves(self.move_date or self.actual_date,aml[0].journal_id or False)
            # move = self.env['account.move'].browse(move)
            for k in move.line_ids:
                k.payment_id = self.id
            move.action_post()
            self.state_check = 'refund_from_discount'
            return True



    def delivery_aml(self):
        self.with_context(delivery_aml=1).sudo().post()


    def post(self,date_under_collect=None):
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
        if self.is_internal_transfer == True:
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

                # move.date = fields.Date.today()
                if date_under_collect:
                    move.date = date_under_collect

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

    def _prepare_payment_moves(self):
        print("_prepare_payment_moves : ")
        ''' Prepare the creation of journal entries (account.move) by creating a list of python dictionary to be passed
        to the 'create' method.

        Example 1: outbound with write-off:

        Account             | Debit     | Credit
        ---------------------------------------------------------
        BANK                |   900.0   |
        RECEIVABLE          |           |   1000.0
        WRITE-OFF ACCOUNT   |   100.0   |

        Example 2: internal transfer from BANK to CASH:

        Account             | Debit     | Credit
        ---------------------------------------------------------
        BANK                |           |   1000.0
        TRANSFER            |   1000.0  |
        CASH                |   1000.0  |
        TRANSFER            |           |   1000.0

        :return: A list of Python dictionary to be passed to env['account.move'].sudo().create.
        '''


        all_move_vals = []
        for payment in self:
            if payment.payment_method_code == 'manual':
                return super(PaymentCheque, self)._prepare_payment_moves()
            if payment.is_internal_transfer == True:
                return super(PaymentCheque, self)._prepare_payment_moves()

            liq_move = payment._get_liquidity_move_line_vals(payment.amount)

            lig_account_id = self.env['account.account'].browse(liq_move['account_id'])
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ", lig_account_id.name)
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>important deliver account ", lig_account_id)

            company_currency = payment.company_id.currency_id
            move_names = payment.move_name.split(
                payment._get_move_name_transfer_separator()) if payment.move_name else None

            # inbound_account = self.env['account.payment.method.line'].search([
            #     ('id', '=', payment.journal_id.inbound_payment_method_line_ids.ids)
            #     , ('journal_id', '=', payment.journal_id.id)
            #     , ('payment_method_id', '=', payment.payment_method_line_id.payment_method_id.id)
            # ], limit=1)
            # print("inbound_account",inbound_account)
            print("outgoing_account",payment.journal_id.inbound_payment_method_line_ids.ids)
            print("outgoing_account", payment.journal_id.id)
            print("outgoing_account",payment.payment_method_line_id.payment_method_id.id)

            outgoing_account = self.env['account.payment.method.line'].search([
                ('id', 'in', payment.journal_id.outbound_payment_method_line_ids.ids)
                , ('journal_id', '=', payment.journal_id.id)
                , ('payment_method_id', '=', payment.payment_method_line_id.payment_method_id.id)
            ], limit=1)
            print("outgoing_account",outgoing_account)


            # Compute amounts.
            write_off_amount = payment.payment_difference_handling == 'reconcile' and -payment.payment_difference or 0.0
            if payment.payment_type in ('outbound', 'transfer'):
                counterpart_amount = payment.amount
                liquidity_line_account = lig_account_id  # payment.journal_id.default_debit_account_id
                # liquidity_line_account = outgoing_account.payment_account_id  # payment.journal_id.default_debit_account_id
            else:
                counterpart_amount = -payment.amount
                liquidity_line_account = lig_account_id  # payment.journal_id.default_credit_account_id
                # liquidity_line_account = outgoing_account.payment_account_id  # payment.journal_id.default_credit_account_id

            # Manage currency.
            if payment.currency_id == company_currency:
                # Single-currency.
                balance = counterpart_amount
                write_off_balance = write_off_amount
                counterpart_amount = write_off_amount = 0.0
                currency_id = False
            else:
                # Multi-currencies.
                balance = payment.currency_id._convert(counterpart_amount, company_currency, payment.company_id,
                                                       payment.date)
                write_off_balance = payment.currency_id._convert(write_off_amount, company_currency, payment.company_id,
                                                                 payment.date)
                currency_id = payment.currency_id.id

            # Manage custom currency on journal for liquidity line.
            if payment.journal_id.currency_id and payment.currency_id != payment.journal_id.currency_id:
                # Custom currency on journal.
                if payment.journal_id.currency_id == company_currency:
                    # Single-currency
                    liquidity_line_currency_id = False
                else:
                    liquidity_line_currency_id = payment.journal_id.currency_id.id
                liquidity_amount = company_currency._convert(
                    balance, payment.journal_id.currency_id, payment.company_id, payment.date)
            else:
                # Use the payment currency.
                liquidity_line_currency_id = currency_id
                liquidity_amount = counterpart_amount

            # Compute 'name' to be used in receivable/payable line.
            rec_pay_line_name = ''
            if payment.payment_type == 'transfer':
                rec_pay_line_name = payment.name
            else:
                if payment.partner_type == 'customer':
                    if payment.payment_type == 'inbound':
                        rec_pay_line_name += _("Customer Payment")
                    elif payment.payment_type == 'outbound':
                        rec_pay_line_name += _("Customer Credit Note")
                elif payment.partner_type == 'supplier':
                    if payment.payment_type == 'inbound':
                        rec_pay_line_name += _("Vendor Credit Note")
                    elif payment.payment_type == 'outbound':
                        rec_pay_line_name += _("Vendor Payment")
                if payment.reconciled_invoice_ids:
                    rec_pay_line_name += ': %s' % ', '.join(payment.reconciled_invoice_ids.mapped('name'))

            # Compute 'name' to be used in liquidity line.
            if payment.payment_type == 'transfer':
                liquidity_line_name = _('Transfer to %s') % payment.destination_journal_id.name
            else:
                liquidity_line_name = payment.name

            # ==== 'inbound' / 'outbound' ====
            # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ",liquidity_line_account.name , payment._get_destination_account_id().name )
            # 1/0
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>|||<<", payment._get_destination_account_id())
            date = False
            if self._context.get('ctx_del', False):
                date = self.delivery_date
            elif self._context.get('ctx_bank', False):
                date = self.withdrawal_date
            elif self._context.get('ctx_del_batch', False):
                date = self.batch_payment_id.date
            elif self._context.get('bank_aml_batch', False):
                date = self.ref_coll_batch
            print(
                ">>>>>>>>>>>>>>>>>>>>>>>>>payment._get_destination_account_id()payment._get_destination_account_id() ",
                payment._get_destination_account_id())
            print("payemtn dsdf ",payment.id)
            print("payment._get_destination_account_id()",payment._get_destination_account_id())
            print("liquidity_line_account.id ",liquidity_line_account.id)
            # print("payment.writeoff_account_id.id ",payment.writeoff_account_id.id)
            move_vals = {
                'date': date or payment.payment_date,
                'ref': payment.ref,
                'journal_id': payment.journal_id.id,
                'currency_id': payment.journal_id.currency_id.id or payment.company_id.currency_id.id,
                'partner_id': payment.partner_id.id,
                'line_ids': [
                    # Receivable / Payable / Transfer line.
                    (0, 0, {
                        'name': rec_pay_line_name,
                        'amount_currency': counterpart_amount + write_off_amount if currency_id else 0.0,
                        'currency_id': currency_id,
                        'debit': balance + write_off_balance > 0.0 and balance + write_off_balance or 0.0,
                        'credit': balance + write_off_balance < 0.0 and -balance - write_off_balance or 0.0,
                        'date_maturity': date or payment.payment_date,
                        'partner_id': payment.partner_id.commercial_partner_id.id,
                        'account_id': payment._get_destination_account_id(),
                        'payment_id': payment.id,
                    }),
                    # Liquidity line.
                    (0, 0, {
                        'name': liquidity_line_name,
                        'amount_currency': -liquidity_amount if liquidity_line_currency_id else 0.0,
                        'currency_id': liquidity_line_currency_id,
                        'debit': balance < 0.0 and -balance or 0.0,
                        'credit': balance > 0.0 and balance or 0.0,
                        'date_maturity': date or payment.payment_date,
                        'partner_id': payment.partner_id.commercial_partner_id.id,
                        'account_id': liquidity_line_account.id,
                        'payment_id': payment.id,
                    }),
                ],
            }
            print("move_vals : ",move_vals)
            if write_off_balance:
                # Write-off line.
                move_vals['line_ids'].append((0, 0, {
                    'name': payment.writeoff_label,
                    'amount_currency': -write_off_amount,
                    'currency_id': currency_id,
                    'debit': write_off_balance < 0.0 and -write_off_balance or 0.0,
                    'credit': write_off_balance > 0.0 and write_off_balance or 0.0,
                    'date_maturity': date or payment.payment_date,
                    'partner_id': payment.partner_id.commercial_partner_id.id,
                    'account_id': liquidity_line_account.id,
                    'payment_id': payment.id,
                }))

            # 'account_id': payment.writeoff_account_id.id,
            #نشوف حسين قيها مش هننسى
            if move_names:
                move_vals['name'] = move_names[0]

            print("move_vals ::: ",move_vals)
            all_move_vals.append(move_vals)
            print("all_move_vals ::: ",all_move_vals)

            # ==== 'transfer' ====
            if payment.payment_type == 'transfer':
                journal = payment.destination_journal_id

                # Manage custom currency on journal for liquidity line.
                if journal.currency_id and payment.currency_id != journal.currency_id:
                    # Custom currency on journal.
                    liquidity_line_currency_id = journal.currency_id.id
                    transfer_amount = company_currency._convert(balance, journal.currency_id, payment.company_id,
                                                                payment.date)
                else:
                    # Use the payment currency.
                    liquidity_line_currency_id = currency_id
                    transfer_amount = counterpart_amount

                transfer_move_vals = {
                    'date': payment.payment_date,
                    'ref': payment.ref,
                    'partner_id': payment.partner_id.id,
                    'journal_id': payment.destination_journal_id.id,
                    'line_ids': [
                        # Transfer debit line.
                        (0, 0, {
                            'name': payment.name,
                            'amount_currency': -counterpart_amount if currency_id else 0.0,
                            'currency_id': currency_id,
                            'debit': balance < 0.0 and -balance or 0.0,
                            'credit': balance > 0.0 and balance or 0.0,
                            'date_maturity': payment.payment_date,
                            'partner_id': payment.partner_id.commercial_partner_id.id,
                            'account_id': payment.company_id.transfer_account_id.id,
                            'payment_id': payment.id,
                        }),
                        # Liquidity credit line.
                        (0, 0, {
                            'name': _('Transfer from %s') % payment.journal_id.name,
                            'amount_currency': transfer_amount if liquidity_line_currency_id else 0.0,
                            'currency_id': liquidity_line_currency_id,
                            'debit': balance > 0.0 and balance or 0.0,
                            'credit': balance < 0.0 and -balance or 0.0,
                            'date_maturity': payment.payment_date,
                            'partner_id': payment.partner_id.commercial_partner_id.id,
                            'account_id': payment.destination_journal_id.default_credit_account_id.id,
                            'payment_id': payment.id,
                        }),
                    ],
                }

                if move_names and len(move_names) == 2:
                    transfer_move_vals['name'] = move_names[1]

                all_move_vals.append(transfer_move_vals)
                print("all_move_vals : : ",all_move_vals)
        return all_move_vals

    def _create_payment_entry(self, amount):

        collect_discount = self._context.get('collect_disc_batch')
        if collect_discount:
            return self.sudo().create_move_line_collect_discount(amount)
        else:
            return super(PaymentCheque, self)._create_payment_entry(amount)
        return move

    def create_move_line_collect_discount(self, amount):
        """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
                   Return the journal entry.
               """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        invoice_currency = False
        if self.reconciled_invoice_ids and all([x.currency_id == self.reconciled_invoice_ids[0].currency_id for x in self.reconciled_invoice_ids]):
            # if all the invoices selected share the same currency, record the paiement in that currency too
            invoice_currency = self.reconciled_invoice_ids[0].currency_id
        debit, credit, amount_currency, currency_id = aml_obj.with_context(
            date=self.payment_date).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id,
                                                          invoice_currency)

        move = self.env['account.move'].sudo().create(self._get_move_vals())
        loan = (self.batch_payment_id.bank_id.bank_id.loan_percentage / 100) * amount

        discount_check = self.batch_payment_id.bank_id.discount_check_account.id

        if not discount_check:
            raise ValidationError(
                "Your Bank journal {} doesn't have discount check account".format(self.batch_payment_id.bank_id.name))
        counterpart_aml_dict = {'invoice_id': False, 'payment_id': self.id,
                                'amount_currency': False, 'partner_id': self.partner_id.id,
                                'account_id': discount_check,
                                'currency_id': currency_id, 'credit': amount * -1, 'name': 'Collect Loan',
                                'journal_id': move.journal_id.id,
                                'debit': 0.0, 'move_id': move.id}

        # Write line corresponding to invoice payment

        counterpart_aml = aml_obj.sudo().create(counterpart_aml_dict)

        # Reconcile with the invoices
        if self.payment_difference_handling == 'reconcile' and self.payment_difference:

            writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
            amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(
                self.payment_difference, self.currency_id, self.company_id.currency_id, invoice_currency)[2:]
            # the writeoff debit and credit must be computed from the invoice residual in company currency
            # minus the payment amount in company currency, and not from the payment difference in the payment currency
            # to avoid loss of precision during the currency rate computations. See revision 20935462a0cabeb45480ce70114ff2f4e91eaf79 for a detailed example.
            total_residual_company_signed = sum(invoice.residual_company_signed for invoice in self.reconciled_invoice_ids)
            total_payment_company_signed = self.currency_id.with_context(date=self.payment_date).compute(self.amount,
                                                                                                         self.company_id.currency_id)
            if self.reconciled_invoice_ids[0].type in ['in_invoice', 'out_refund']:
                amount_wo = total_payment_company_signed - total_residual_company_signed
            else:
                amount_wo = total_residual_company_signed - total_payment_company_signed
            # Align the sign of the secondary currency writeoff amount with the sign of the writeoff
            # amount in the company currency
            if amount_wo > 0:
                debit_wo = amount_wo
                credit_wo = 0.0
                amount_currency_wo = abs(amount_currency_wo)
            else:
                debit_wo = 0.0
                credit_wo = -amount_wo
                amount_currency_wo = -abs(amount_currency_wo)
            writeoff_line['name'] = self.writeoff_label
            writeoff_line['account_id'] = self.writeoff_account_id.id
            writeoff_line['debit'] = debit_wo
            writeoff_line['credit'] = credit_wo
            writeoff_line['amount_currency'] = amount_currency_wo
            writeoff_line['currency_id'] = currency_id
            writeoff_line = aml_obj.sudo().create(writeoff_line)
            if counterpart_aml['debit'] or writeoff_line['credit']:
                counterpart_aml['debit'] += credit_wo - debit_wo
            if counterpart_aml['credit'] or writeoff_line['debit']:
                counterpart_aml['credit'] += debit_wo - credit_wo
            counterpart_aml['amount_currency'] -= amount_currency_wo

        # Write counterpart lines
        if not self.currency_id.is_zero(self.amount):
            if not self.currency_id != self.company_id.currency_id:
                amount_currency = 0

            loan_account = self.batch_payment_id.bank_id.loan_account.id
            bank_account = self.batch_payment_id.bank_id.default_account_id.id
            if not loan_account:
                raise ValidationError(
                    "Your Bank journal {} doesn't have A Loan account".format(loan_account))
            if not bank_account:
                raise ValidationError(
                    "Your Bank journal {} doesn't have defaul credit account".format(bank_account))
            liquidity_aml_dict_1 = {'invoice_id': False, 'payment_id': self.id,
                                    'amount_currency': False, 'partner_id': self.partner_id.id,
                                    'account_id': loan_account,
                                    'currency_id': currency_id, 'credit': 0.0, 'name': 'pay Loan',
                                    'journal_id': move.journal_id.id,
                                    'debit': loan * -1, 'move_id': move.id}

            liquidity_aml_dict_2 = {'invoice_id': False, 'payment_id': self.id,
                                    'amount_currency': False, 'partner_id': self.partner_id.id,
                                    'account_id': bank_account,
                                    'currency_id': currency_id, 'credit': 0.0, 'name': 'collect check amount',
                                    'journal_id': move.journal_id.id, 'debit': (amount * -1) + loan, 'move_id': move.id}

            aml_obj.sudo().create(liquidity_aml_dict_1)
            aml_obj.sudo().create(liquidity_aml_dict_2)

        # validate the payment
        print("payment ::: ",move)
        move.sudo().post()

        # reconcile the invoice receivable/payable line(s) with the payment
        self.reconciled_invoice_ids.register_payment(counterpart_aml)
        return move

    def _get_last_journal(self):
        if self.partner_type == 'customer':
            aml_objs = self.env['account.move.line'].search([('payment_id', '=', self.id), ('debit', '>', 0), (
                'account_id', '!=', self.partner_id.property_account_receivable_id.id)])
        else:
            aml_objs = self.env['account.move.line'].search([('payment_id', '=', self.id),
                                                             ('credit', '>', 0),
                                                             ('account_id', '!=',
                                                              self.partner_id.property_account_payable_id.id)],order="id desc")

        if aml_objs:
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>AMLLLLLLLL OBJSSSS",aml_objs)
            return aml_objs[0].account_id.id
        else:
            return False

    def _get_last_journal_batch(self):
        if self.partner_type == 'customer':
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.0")
            if self.payment_method_code == 'batch_payment':
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.1")
                if self.state_check!= 'under_coll':
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.2")
                    aml_objs = self.env['account.move.line'].search(
                        [('payment_id', '=', self.id), ('journal_id', '=', self.journal_id.id), ('debit', '>', 0)])
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.3")
                else:
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.4")
                    aml_objs = self.env['account.move.line'].search([('name','ilike','under'),('payment_id', '=', self.id), ('debit', '>', 0)])
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.5")
                last_index = len(aml_objs)-1
                if aml_objs:
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.6",aml_objs)
                    return aml_objs[0].account_id.id, aml_objs[0].name
                else:
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.7")
                    return False
            else:
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.8")
                aml_objs = self.env['account.move.line'].search([('payment_id', '=', self.id), ('credit', '>', 0)])
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.9",aml_objs)
                last_index = len(aml_objs)-1
                if aml_objs:
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.10")
                    return aml_objs[0].account_id.id, aml_objs[0].name
                else:
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.11")
                    return False
        else:
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.12")
            if self.payment_method_code == 'batch_payment':

                if self.state_check != 'under_coll':
                    aml_objs = self.env['account.move.line'].search(
                        [('payment_id', '=', self.id), ('journal_id', '=', self.journal_id.id), ('debit', '>', 0)])
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.13 ",aml_objs)
                    # 1/0
                else:
                    aml_objs = self.env['account.move.line'].search([('payment_id', '=', self.id), ('debit', '>', 0)])
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.14 ",aml_objs)
                    # 2/0
                if aml_objs:
                    return aml_objs[0].account_id.id, aml_objs[0].name
                else:
                    return False
            else:
                aml_objs = self.env['account.move.line'].search([('payment_id', '=', self.id), ('debit', '>', 0)])
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.15 ",aml_objs)
                # 3/0
                if aml_objs:
                    return aml_objs[0].account_id.id, aml_objs[0].name
                else:
                    return False

    #@api.one
    @api.depends('payment_type', 'partner_type', 'partner_id')
    def _compute_destination_account_id(self):
        """""
            override _compute_destination_account_id to add 3 different destination if payment method is cheque
                    1-first journal item to payable vendor account
                    2-second one to notes payable accounts from bank account
                    3-third to delivery account from bank account


        """

        for pay in self:
            if pay.is_internal_transfer == True:
                self.destination_account_id = False
                if pay.is_internal_transfer:
                    pay.destination_account_id = pay.journal_id.company_id.transfer_account_id
                elif pay.partner_type == 'customer':
                    # Receive money from invoice or send money to refund it.
                    if pay.partner_id:
                        pay.destination_account_id = pay.partner_id.with_company(
                            pay.company_id).property_account_receivable_id
                    else:
                        pay.destination_account_id = self.env['account.account'].search([
                            ('company_id', '=', pay.company_id.id),
                            ('internal_type', '=', 'receivable'),
                            ('deprecated', '=', False),
                        ], limit=1)
                elif pay.partner_type == 'supplier':
                    # Send money to pay a bill or receive money to refund it.
                    if pay.partner_id:
                        pay.destination_account_id = pay.partner_id.with_company(
                            pay.company_id).property_account_payable_id
                    else:
                        pay.destination_account_id = self.env['account.account'].search([
                            ('company_id', '=', pay.company_id.id),
                            ('internal_type', '=', 'payable'),
                            ('deprecated', '=', False),
                        ], limit=1)

        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>||||11")

        for rec in self:
            if rec.is_internal_transfer == False:
                ctx_loan_batch = rec._context.get('loan_check')
                des_batch_account = rec._get_last_journal_batch()
                des_account = rec._get_last_journal()

                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",des_batch_account , ' || ',des_account)

                # if rec.invoice_ids and (not des_batch_account or not des_account):
                #     rec.destination_account_id = rec.invoice_ids[0].account_id.id
                if rec.payment_type == 'transfer':
                    if not rec.company_id.transfer_account_id.id:
                        raise UserError(_('Transfer account not defined on the company.'))
                    rec.destination_account_id = rec.company_id.transfer_account_id.id
                elif rec.partner_id:

                    if rec.partner_type == 'customer':
                        print("sadadasdada")
                        if rec.payment_method_code == 'batch_payment' and rec._get_last_journal_batch():
                            print("sadadasdada222")
                            print("sadadasdada222 : ",des_batch_account[0])
                            account_obj = self.env['account.account']
                            account_des_batch_account = account_obj.search([('id', '=', des_batch_account[0])], limit=1)
                            print("rec.destination_account_id : ",account_des_batch_account)
                            print("rec.destination_account_id : ",rec.destination_account_id)
                            if not  rec.destination_account_id :
                                rec.destination_account_id = account_des_batch_account
                            # print(".>>>>>>>>>>>>>>>>>>>>>>>>>>>>",des_batch_account[0])
                            #run when create debosit and click first multi under collection

                            #also run after second click of approve
                            # 1/0
                        # elif rec.payment_method_code == 'check' :
                        elif rec._get_last_journal_batch():
                            print("dddddddddddddddddddddddddddddddd")
                            rec.destination_account_id = des_batch_account[0]
                            # 2/0
                        else:
                            rec.destination_account_id = rec.partner_id.property_account_receivable_id.id
                            #run when create payment and click validate
                            # 3/0
                        if ctx_loan_batch:
                            loan_bank = rec.batch_payment_id.bank_id.loan_account.id
                            if not loan_bank:
                                raise ValidationError(
                                    "Your Bank journal {} doesn't have A Loan account".format(
                                        rec.batch_payment_id.bank_id.name))
                            rec.destination_account_id = loan_bank
                            # 4/0

                    else:
                        print("1234")

                        if ctx_loan_batch:
                            print("1234_")
                            loan_bank = rec.batch_payment_id.bank_id.loan_account.id
                            if not loan_bank:
                                raise ValidationError(
                                    "Your Bank journal {} doesn't have A Loan account".format(
                                        rec.batch_payment_id.bank_id.name))
                            rec.destination_account_id = loan_bank

                        elif rec.cheque_books_id:
                            print("1234_1")

                            if des_account:
                                print("1234_1_1")

                                rec.destination_account_id = rec.journal_id.notes_payable.id
                            else:
                                print("1234_1_2")
                                rec.destination_account_id = rec.partner_id.property_account_payable_id.id


                        else:
                            print("1234_2")
                            if rec.payment_method_code == 'batch_payment' and rec._get_last_journal_batch():
                                rec.destination_account_id = des_batch_account[0]
                            else:
                                rec.destination_account_id = rec.partner_id.property_account_payable_id.id

    def _get_destination_account_id(self):
        """""
            override _compute_destination_account_id to add 3 different destination if payment method is cheque
                    1-first journal item to payable vendor account
                    2-second one to notes payable accounts from bank account
                    3-third to delivery account from bank account


        """
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>||||22")

        for rec in self:
            ctx_loan_batch = rec._context.get('loan_check')

            des_batch_account = rec._get_last_journal_batch()
            des_account = rec._get_last_journal()

            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",des_batch_account , ' || ',des_account)

            # if rec.invoice_ids and (not des_batch_account or not des_account):
            #     # rec.destination_account_id = rec.invoice_ids[0].account_id.id
            #     return rec.invoice_ids[0].account_id.id
            if rec.payment_type == 'transfer':
                if not rec.company_id.transfer_account_id.id:
                    raise UserError(_('Transfer account not defined on the company.'))
                # rec.destination_account_id = rec.company_id.transfer_account_id.id
                return rec.company_id.transfer_account_id.id
            elif rec.partner_id:

                if rec.partner_type == 'customer':

                    if rec.payment_method_code == 'batch_payment' and rec._get_last_journal_batch():
                        # rec.destination_account_id = des_batch_account[0]
                        print(".>>>>>>>>>>>>>>>>>>>>>>>>>>>>",des_batch_account[0])
                        # 1/0
                        return des_batch_account[0]
                        #run when create debosit and click first multi under collection

                        #also run after second click of approve

                    # elif rec.payment_method_code == 'check' :
                    elif rec._get_last_journal_batch():
                        # rec.destination_account_id = des_batch_account[0]
                        # 2/0
                        return des_batch_account[0]

                    else:
                        # rec.destination_account_id = rec.partner_id.property_account_receivable_id.id
                        # 3/0
                        return rec.partner_id.property_account_receivable_id.id
                        #run when create payment and click validate

                    if ctx_loan_batch:
                        loan_bank = rec.batch_payment_id.bank_id.loan_account.id
                        if not loan_bank:
                            raise ValidationError(
                                "Your Bank journal {} doesn't have A Loan account".format(
                                    rec.batch_payment_id.bank_id.name))
                        # rec.destination_account_id = loan_bank
                        # 4/0
                        return loan_bank


                else:

                    if ctx_loan_batch:
                        loan_bank = rec.batch_payment_id.bank_id.loan_account.id
                        if not loan_bank:
                            raise ValidationError(
                                "Your Bank journal {} doesn't have A Loan account".format(
                                    rec.batch_payment_id.bank_id.name))
                        # rec.destination_account_id = loan_bank
                        return loan_bank

                    elif rec.cheque_books_id:

                        if des_account:
                            # rec.destination_account_id = des_account
                            return des_account
                        else:
                            # rec.destination_account_id = rec.partner_id.property_account_payable_id.id
                            return rec.partner_id.property_account_payable_id.id


                    else:
                        if rec.payment_method_code == 'batch_payment' and rec._get_last_journal_batch():
                            # rec.destination_account_id = des_batch_account[0]
                            return des_batch_account[0]
                        else:
                            # rec.destination_account_id = rec.partner_id.property_account_payable_id.id
                            return rec.partner_id.property_account_payable_id.id

    def _get_liquidity_move_line_vals(self, amount):

        """""
           override _get_liquidity_move_line_vals to add 3 different source if payment method is cheque
                   1-first journal notes payable accounts from bank account
                   2-second one to delivery account from bank account
                   3-third to default journal debit or credit


       """

        name = self.name
        if self.payment_type == 'transfer':
            name = _('Transfer to %s') % self.destination_journal_id.name

        vals = {
            'name': name,
            'account_id': self.payment_type in ('outbound',
                                                'transfer') and self.journal_id.default_account_id.id or self.journal_id.default_account_id.id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }

        if self.cheque_books_id:
            ctx_del = self._context.get('delivery_aml')
            ctx_bank = self._context.get('bank_aml')

            if ctx_del:
                vals = {
                    'name': str(self.cheque_books_id.account_journal_cheque_id.bank_acc_number) + '-' + str(
                        self.cheque_books_id.name) + '-' + str(self.cheque_number),
                    'account_id': self.payment_type in (
                        'outbound') and self.cheque_books_id.account_journal_cheque_id.deliver_account.id,
                    'journal_id': self.journal_id.id,
                    'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
                }

            elif ctx_bank:
                vals = {
                    'name': str(self.cheque_books_id.account_journal_cheque_id.bank_acc_number) + '-' + str(
                        self.cheque_books_id.name) + '-' + str(self.cheque_number),
                    'account_id': self.payment_type in ('outbound',
                                                        'transfer') and self.journal_id.default_account_id.id or self.journal_id.default_account_id.id,
                    'journal_id': self.journal_id.id,
                    'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
                }

            else:

                vals = {
                    'name': str(self.cheque_books_id.account_journal_cheque_id.bank_acc_number) + '-' + str(
                        self.cheque_books_id.name) + '-' + str(self.cheque_number),
                    'account_id': self.payment_type in (
                        'outbound') and self.cheque_books_id.account_journal_cheque_id.notes_payable.id,
                    'journal_id': self.journal_id.id,
                    'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
                }
        # If the journal has a currency specified, the journal item need to be expressed in this currency

        if self.payment_method_code == 'batch_payment':
            ctx_del_batch = self._context.get('delivery_aml_batch')
            ctx_bank_batch = self._context.get('bank_aml_batch')
            ctx_discount_batch = self._context.get('discount_check')
            ctx_loan_batch = self._context.get('loan_check')

            if ctx_del_batch:
                if not self.batch_payment_id.bank_id.reveivable_under_collection:
                    raise ValidationError(
                        "Your Bank journal {} doesn't have A Receivable Under collection account".format(
                            self.batch_payment_id.bank_id.name))

                vals = {
                    'name': "Under collection",
                    'account_id': self.batch_payment_id.bank_id.reveivable_under_collection.id,
                    'journal_id': self.batch_payment_id.bank_id.id,
                    'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
                }
            elif ctx_discount_batch:
                if not self.batch_payment_id.bank_id.discount_check_account:
                    raise ValidationError(
                        "Your Bank journal {} doesn't have A Receivable Discount Check Account account".format(
                            self.batch_payment_id.bank_id.name))

                vals = {
                    'name': "Discount Check",
                    'account_id': self.batch_payment_id.bank_id.discount_check_account.id,
                    'journal_id': self.batch_payment_id.bank_id.id,
                    'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
                }
            elif ctx_loan_batch:
                if not self.batch_payment_id.bank_id.loan_account:
                    raise ValidationError(
                        "Your Bank journal {} doesn't have A Loan account".format(self.batch_payment_id.bank_id.name))

                vals = {
                    'name': "Receive Loan",
                    'account_id': self.batch_payment_id.bank_id.default_account_id.id,
                    'journal_id': self.batch_payment_id.bank_id.id,
                    'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
                }
            elif ctx_bank_batch:
                if not self.batch_payment_id.bank_id:
                    raise ValidationError(
                        "Your Register Payment Doesn't Have A Bank To Collect Check In".format(self.journal_id.name))

                vals = {
                    'name': "collection Checks",
                    'account_id': self.batch_payment_id.bank_id.default_account_id.id,
                    'journal_id': self.batch_payment_id.bank_id.id,
                    'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
                }


            else:

                vals = {
                    'name': "Receive Money (Batch Deposit)",
                    'account_id': self.payment_type in ('outbound',
                                                        'transfer') and self.journal_id.default_account_id.id or self.journal_id.default_account_id.id,
                    'journal_id': self.journal_id.id,
                    'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
                }
        if self.journal_id.currency_id and self.currency_id != self.journal_id.currency_id:
            amount = self.currency_id.with_context(date=self.payment_date).compute(amount, self.journal_id.currency_id)
            debit, credit, amount_currency, dummy = self.env['account.move.line'].with_context(
                date=self.payment_date).compute_amount_fields(amount, self.journal_id.currency_id,
                                                              self.company_id.currency_id)
            vals.update({
                'amount_currency': amount_currency,
                'currency_id': self.journal_id.currency_id.id,
            })

        return vals

    def _get_counterpart_move_line_vals(self, invoice=False):

        """"
            override _get_counterpart_move_line_vals to add different label if payment method is cheque


        """
        ctx_del = self._context.get('delivery_aml')
        ctx_bank = self._context.get('bank_aml')

        if self.payment_type == 'transfer':
            name = self.name
        else:
            name = ''
            if self.partner_type == 'customer':
                if self.payment_type == 'inbound':
                    name += _("Customer Payment")
                elif self.payment_type == 'outbound':
                    name += _("Customer Credit Note")
            elif self.partner_type == 'supplier':
                if self.payment_type == 'inbound':
                    name += _("Vendor Credit Note")
                elif self.payment_type == 'outbound':
                    if ctx_bank or ctx_del:
                        name += str(self.cheque_books_id.account_journal_cheque_id.bank_acc_number) + '-' + str(
                            self.cheque_books_id.name) + '-' + str(self.cheque_number)
                    else:
                        name += _("Vendor Payment")
            if invoice:
                name += ': '
                for inv in invoice:
                    if inv.move_id:
                        name += inv.number + ', '
                name = name[:len(name) - 2]

        if self.payment_method_code == 'batch_payment' and self._get_last_journal_batch():
            name = self._get_last_journal_batch()[1]

        return {
            'name': name,
            'account_id': self._get_destination_account_id(),
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }

    def _get_move_vals(self, journal=None):

        """ Return dict to create the payment move
        """

        refund = self._context.get('refund')
        refund_delivery = self._context.get('refund_delivery')
        ctx_bank_batch = self._context.get('bank_aml_batch')
        ctx_del_batch = self._context.get('delivery_aml_batch')
        ctx_del = self._context.get('delivery_aml')
        ctx_bank = self._context.get('bank_aml')
        collect_disc_batch = self._context.get('collect_disc_batch')
        loan_check = self._context.get('loan_check')
        discount_all = self._context.get('discount_check')
        refund_discount = self._context.get('refund_discount')
        ref_desc_batch = self._context.get('ref_desc_batch')
        journal = journal or self.journal_id
        if ctx_bank_batch or refund_discount or collect_disc_batch or ctx_del_batch or loan_check or discount_all:
            journal = self.batch_payment_id.bank_id

        if not journal.sequence_id:
            raise UserError(_('The Journal %s Does Not Have A Sequence, Please Specify One.') % journal.name)
        if not journal.sequence_id.active:
            raise UserError(_('The sequence of journal %s is deactivated.') % journal.name)
        name = self.move_name or journal.with_context(ir_sequence_date=self.payment_date).sequence_id.next_by_id()

        ref = False

        if self.batch_payment_id:
            ref = self.batch_payment_id.name

        if collect_disc_batch or ref_desc_batch:
            date = self.ref_coll_batch
            return {
                'name': name,
                'date': date or self.move_date or self.payment_date,
                'ref': ref or self.ref or '',
                'company_id': self.company_id.id,
                'journal_id': self.batch_payment_id.bank_id.id,
            }

        if ctx_bank_batch:
            date = self.ref_coll_batch
            return {
                'name': name,
                'date': date or self.move_date or self.payment_date,
                'ref': ref or self.ref or '',
                'company_id': self.company_id.id,
                'journal_id': journal.id,
            }

        if loan_check:
            date = self.loan_date
            return {
                'name': name,
                'date': date or self.move_date or self.payment_date,
                'ref': ref or self.ref or '',
                'company_id': self.company_id.id,
                'journal_id': journal.id,
            }
        if discount_all:
            date = self.batch_payment_id.date
            return {
                'name': name,
                'date': date or self.move_date or self.payment_date,
                'ref': ref or self.ref or '',
                'company_id': self.company_id.id,
                'journal_id': journal.id,
            }

        if refund:
            date = self.refund_date
            return {
                'name': name,
                'date': date or self.move_date or self.payment_date,
                'ref': ref or self.ref or '',
                'company_id': self.company_id.id,
                'journal_id': journal.id,
            }

        if refund_delivery:
            date = self.refund_delivery_date
            return {
                'name': name,
                'date': date or self.move_date or self.payment_date,
                'ref': ref or self.ref or '',
                'company_id': self.company_id.id,
                'journal_id': journal.id,
            }

        if ctx_del_batch:
            date = self.batch_payment_id.date
            return {
                'name': name,
                'date': date or self.move_date or self.payment_date,
                'ref': ref or self.ref or '',
                'company_id': self.company_id.id,
                'journal_id': journal.id,
            }

        if ctx_del:
            date = self.delivery_date
            return {
                'name': name,
                'date': date or self.move_date or self.payment_date,
                'ref': ref or self.ref or '',
                'company_id': self.company_id.id,
                'journal_id': journal.id,
            }
        if ctx_bank:
            date = self.withdrawal_date
            return {
                'name': name,
                'date': date or self.move_date or self.payment_date,
                'ref': ref or self.ref or '',
                'company_id': self.company_id.id,
                'journal_id': journal.id,
            }

        if self.move_date:
            return {
                'name': name,
                'date': self.move_date,
                'ref': ref or self.ref or '',
                'company_id': self.company_id.id,
                'journal_id': journal.id,
            }

        else:
            return {
                'name': name,
                'date': self.payment_date,
                'ref': ref or self.ref or '',
                'company_id': self.company_id.id,
                'journal_id': journal.id,
            }


    def button_journal_entries_custom(self):
        return {
            'name': _('Journal Items'),
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('payment_id', 'in', self.ids)],
        }

    def _seek_for_lines(self):
        ''' Helper used to dispatch the journal items between:
        - The lines using the temporary liquidity account.
        - The lines using the counterpart account.
        - The lines being the write-off lines.
        :return: (liquidity_lines, counterpart_lines, writeoff_lines)
        '''
        self.ensure_one()

        liquidity_lines = self.env['account.move.line']
        counterpart_lines = self.env['account.move.line']
        writeoff_lines = self.env['account.move.line']

        print("payment_method_id", self.payment_method_id.ids)
        inbound_account = self.env['account.payment.method.line'].search([
            ('id', '=', self.journal_id.inbound_payment_method_line_ids.ids)
            , ('journal_id', '=', self.journal_id.id)
            , ('payment_method_id', '=', self.payment_method_line_id.payment_method_id.id)
        ], limit=1)

        outgoing_account = self.env['account.payment.method.line'].search([
            ('id', '=', self.journal_id.outbound_payment_method_line_ids.ids)
            , ('journal_id', '=', self.journal_id.id)
            , ('payment_method_id', '=', self.payment_method_line_id.payment_method_id.id)
        ], limit=1)
        print("inbound_account", inbound_account)
        print("outgoing_account", outgoing_account)
        for line in self.move_id.line_ids:
            if line.account_id in self._get_valid_liquidity_accounts_custom():
                liquidity_lines += line
            elif line.account_id.internal_type in (
                    'receivable', 'payable') or line.partner_id == line.company_id.partner_id:
                counterpart_lines += line
            else:
                writeoff_lines += line
        print("liquidity_lines :> ", liquidity_lines)
        return liquidity_lines, counterpart_lines, writeoff_lines

    def _get_valid_liquidity_accounts_custom(self):
        return (
            self.journal_id.notes_payable,
            self.journal_id.default_account_id,
            self.payment_method_line_id.payment_account_id,
            self.journal_id.company_id.account_journal_payment_debit_account_id,
            self.journal_id.company_id.account_journal_payment_credit_account_id,
            self.journal_id.inbound_payment_method_line_ids.payment_account_id,
            self.journal_id.outbound_payment_method_line_ids.payment_account_id,
        )



    # -------------------------------------------------------------------------
    # SYNCHRONIZATION account.payment <-> account.move
    # -------------------------------------------------------------------------

    def _synchronize_from_moves(self, changed_fields):
        ''' Update the account.payment regarding its related account.move.
        Also, check both models are still consistent.
        :param changed_fields: A set containing all modified fields on account.move.
        '''
        if self._context.get('skip_account_move_synchronization'):
            return

        for pay in self.with_context(skip_account_move_synchronization=True):

            # After the migration to 14.0, the journal entry could be shared between the account.payment and the
            # account.bank.statement.line. In that case, the synchronization will only be made with the statement line.
            if pay.move_id.statement_line_id:
                continue

            move = pay.move_id
            move_vals_to_write = {}
            payment_vals_to_write = {}

            if 'journal_id' in changed_fields:
                if pay.journal_id.type not in ('bank', 'cash'):
                    raise UserError(_("A payment must always belongs to a bank or cash journal."))

            if 'line_ids' in changed_fields:
                all_lines = move.line_ids
                liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()
                print("liquidity_lines len : ",len(liquidity_lines))
                print("counterpart_lines len : ",len(counterpart_lines))
                print("counterpart_lines  : ",counterpart_lines)
                print("liquidity_lines : ",liquidity_lines)
                # print("liquidity_lines : ",liquidity_lines.account_id.id)

                # if self.payment_method_code == 'check_printing' and liquidity_lines.account_id.id == self.journal_id.default_account_id.id:
                #         print("enter cond")
                #         liquidity_lines.account_id = self.journal_id.notes_payable.id
                #         liquidity_lines.currency_id = self.journal_id.currency_id.id
                if pay.payment_method_code == 'check_printing'   :
                        print("enter cond new test")
                        print("enter cond new test",pay.journal_id)
                        print("enter cond new test",pay.journal_id)
                        print("enter cond new test",pay.journal_id.notes_payable)
                        liquidity_lines.account_id = pay.journal_id.notes_payable.id
                        liquidity_lines.currency_id = pay.currency_id.id
                        liquidity_lines.update({
                            'account_id': pay.journal_id.notes_payable.id,
                            'currency_id': pay.currency_id.id,
                        })
                        print("liquidity_lines : ", liquidity_lines.account_id.id)

                if pay.payment_method_code == 'batch_payment':
                        print("enter cond 2")
                        liquidity_lines.account_id = pay.journal_id.default_account_id.id
                        liquidity_lines.currency_id = pay.currency_id.id
                        liquidity_lines.name        = 'Receive Money (Batch Deposit)'
                print("liquidity_lines : ",liquidity_lines.account_id.id)
                print("liquidity_lines : ",liquidity_lines.currency_id)

                # if len(liquidity_lines) != 1 or len(counterpart_lines) != 1:
                #     raise UserError(_(
                #         "The journal entry %s reached an invalid state relative to its payment.\n"
                #         "To be consistent, the journal entry must always contains:\n"
                #         "- one journal item involving the outstanding payment/receipts account.\n"
                #         "- one journal item involving a receivable/payable account.\n"
                #         "- optional journal items, all sharing the same account.\n\n"
                #     ) % move.display_name)

                if writeoff_lines and len(writeoff_lines.account_id) != 1:
                    raise UserError(_(
                        "The journal entry %s reached an invalid state relative to its payment.\n"
                        "To be consistent, all the write-off journal items must share the same account."
                    ) % move.display_name)

                if any(line.currency_id != all_lines[0].currency_id for line in all_lines):
                    raise UserError(_(
                        "The journal entry %s reached an invalid state relative to its payment.\n"
                        "To be consistent, the journal items must share the same currency."
                    ) % move.display_name)

                if any(line.partner_id != all_lines[0].partner_id for line in all_lines):
                    raise UserError(_(
                        "The journal entry %s reached an invalid state relative to its payment.\n"
                        "To be consistent, the journal items must share the same partner."
                    ) % move.display_name)

                if counterpart_lines.account_id.user_type_id.type == 'receivable':
                    partner_type = 'customer'
                else:
                    partner_type = 'supplier'
                if liquidity_lines:
                    liquidity_amount = liquidity_lines.amount_currency

                    move_vals_to_write.update({
                        'currency_id': liquidity_lines.currency_id.id,
                        'partner_id': liquidity_lines.partner_id.id,
                    })
                    payment_vals_to_write.update({
                        'amount': abs(liquidity_amount),
                        'payment_type': 'inbound' if liquidity_amount > 0.0 else 'outbound',
                        'partner_type': partner_type,
                        'currency_id': liquidity_lines.currency_id.id,
                        'destination_account_id': counterpart_lines.account_id.id,
                        'partner_id': liquidity_lines.partner_id.id,
                    })

            move.write(move._cleanup_write_orm_values(move, move_vals_to_write))
            pay.write(move._cleanup_write_orm_values(pay, payment_vals_to_write))

    def action_post(self):
        ''' draft -> posted '''
        if self.is_internal_transfer != True:
            self.move_id._post(soft=False)
            self.state_check= 'posted'
        elif self.is_internal_transfer == True :
            self.move_id._post(soft=False)

            self.filtered(
                lambda pay: pay.is_internal_transfer and not pay.paired_internal_transfer_payment_id
            )._create_paired_internal_transfer_payment()


    @api.model
    def _get_move_name_transfer_separator(self):
        return '§§'



    @api.depends('payment_type', 'journal_id')
    def _compute_payment_method_line_fields(self):
        for pay in self:
            pay.available_payment_method_line_ids = pay.journal_id._get_available_payment_method_lines(pay.payment_type)
            print("here stop")

            to_exclude = []
            print("here stop 1")
            if to_exclude:
                print("here stop 2")
                pay.available_payment_method_line_ids = pay.available_payment_method_line_ids.filtered(lambda x: x.code not in to_exclude)
            if pay.payment_method_line_id.id not in pay.available_payment_method_line_ids.ids:
                print("here stop 3")
                # In some cases, we could be linked to a payment method line that has been unlinked from the journal.
                # In such cases, we want to show it on the payment.
                pay.hide_payment_method_line = False
            else:
                print("here stop 4")
                pay.hide_payment_method_line = len(pay.available_payment_method_line_ids) == 1 and pay.available_payment_method_line_ids.code == 'manual'

    def _get_payment_method_codes_to_exclude(self):
        # can be overriden to exclude payment methods based on the payment characteristics
        self.ensure_one()
        return []
    def customer_cheques_payment(self):
        customer_cheque_due_alert = self.env['ir.config_parameter'].get_param('check_management_15.customer_cheque_due_alert')
        today = date.today()
        end_date = today - relativedelta(days=int(customer_cheque_due_alert))
        print('end_date',end_date)
        print('today',today)
        return {
            'name': _('Customer Cheques Due'),
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'domain': [('due_date', '>=', end_date),('payment_method_id.payment_type','=','inbound'),('state_check','not in',('collected','refunded_from_notes'))],
        }
    def vendor_cheques_payment(self):
        customer_cheque_due_alert = self.env['ir.config_parameter'].get_param('check_management_15.vendor_cheque_due_alert')
        today = date.today()
        end_date = today - relativedelta(days=int(customer_cheque_due_alert))
        print('end_date',end_date)
        print('today',today)
        return {
            'name': _('Customer Cheques Due'),
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'domain': [('due_date', '>=', end_date),('payment_method_id.payment_type','=','outbound'),('state_check','not in',('collected','refunded_from_notes'))],
        }
    notification_check = fields.Boolean(default=False,copy=False)
    def _cron_payment_notification(self):
        customer_cheque_due_alert = self.env['ir.config_parameter'].get_param('check_management_15.vendor_cheque_due_alert')
        today = date.today()
        end_date = today - relativedelta(days=int(customer_cheque_due_alert))
        records = self.env['account.payment'].search([('due_date', '>=', end_date),('payment_method_id.payment_type','in',['outbound','inbound']),('notification_check','=',False),('state_check','not in',('collected','refunded_from_notes'))])
        for r in records:
            users = self.env.ref('check_management_15.payment_notification').users
            if users:
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                base_url += '/web#id=%d&view_type=form&model=%s' % (r.id, r._name)
                message_text = f'<strong>Reminder</strong> ' \
                               f'<p>Check This <a href=%s>Payment</a></p>' % base_url

                uid = self.env.user

                notification_ids = []
                for user in users:
                    notification_ids.append((0, 0, {
                        'res_partner_id': user.partner_id.id,
                        'notification_type': 'inbox'
                    }))
                r.message_post(record_name='Payment',
                                  body=message_text,
                                  message_type="notification",
                                  subtype_xmlid="mail.mt_comment",
                                  author_id=uid.partner_id.id,
                                  notification_ids=notification_ids)
                r.notification_check = True


class settings(models.TransientModel):
    _inherit = 'res.config.settings'
    customer_cheque_due_alert = fields.Integer('Customer Cheques Due Alert')
    vendor_cheque_due_alert = fields.Integer('Vendor Cheques Due Alert')

    def set_values(self):
        res = super(settings, self).set_values()
        self.env['ir.config_parameter'].set_param('check_management_15.customer_cheque_due_alert', self.customer_cheque_due_alert)
        self.env['ir.config_parameter'].set_param('check_management_15.vendor_cheque_due_alert', self.vendor_cheque_due_alert)
        return res

    @api.model
    def get_values(self):
        res = super(settings, self).get_values()
        customer_cheque_due_alert = self.env['ir.config_parameter'].get_param('check_management_15.customer_cheque_due_alert')
        vendor_cheque_due_alert = self.env['ir.config_parameter'].get_param('check_management_15.vendor_cheque_due_alert')
        res.update(
            customer_cheque_due_alert=customer_cheque_due_alert,
            vendor_cheque_due_alert=vendor_cheque_due_alert
        )
        return res
