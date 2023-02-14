# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, tools
import datetime
from datetime import datetime, date, timedelta
from odoo.tools.translate import _
import calendar
from odoo.exceptions import ValidationError, UserError
import xlrd
import tempfile
import binascii
from operator import attrgetter
from odoo.tools import float_compare
import time
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import logging
import math
import logging
from num2words import num2words

_logger = logging.getLogger(__name__)


class requestRent(models.Model):
    _name = 'res.rent'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Property Rent"
    _rec_name = 'name'

    created_date = fields.Datetime(string="Created on", default=fields.datetime.today())

    _defaults = {
        'created_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    state = fields.Selection(string="State",
                             selection=[('draft', 'Draft'),
                                        ('initial_rent', 'Initial Rent'),
                                        ('operation_approval', 'Operation Approval'),
                                        ('sales_manger', 'Sales Manager Approval'),
                                        ('finance_approval', 'Finance Approval'),
                                        ('rented', 'Rented'),
                                        ], required=False, default='draft')

    approvals_users = fields.Many2many('res.users', compute='get_approvals_users')
    attr_boolean = fields.Boolean(compute='calc_attr_boolean')

    def approval_rent(self):
        users = self.approvals_users
        if users:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
            message_text = f'<strong>Reminder</strong> ' \
                           f'<p>This <a href=%s>Reservation</a> Check Approval On Rent Form</p>' % base_url

            uid = self.env.user

            notification_ids = []
            for user in users:
                notification_ids.append((0, 0, {
                    'res_partner_id': user.partner_id.id,
                    'notification_type': 'inbox'
                }))
            self.message_post(record_name='Reservation',
                              body=message_text,
                              message_type="notification",
                              subtype_xmlid="mail.mt_comment",
                              author_id=uid.partner_id.id,
                              notification_ids=notification_ids)

    def calc_attr_boolean(self):
        for r in self:
            if self.env.user in r.approvals_users:
                r.attr_boolean = True
            else:
                r.attr_boolean = False

    @api.depends('state')
    def get_approvals_users(self):
        for rec in self:
            approval_users = False
            if rec.state == 'draft':
                approval_record = self.env['rent.approvals'].search([('type', '=', 'initial_rent')], limit=1)
                approval_users = [(6, 0, approval_record.users.ids)]
            if rec.state == 'initial_rent':
                approval_record = self.env['rent.approvals'].search([('type', '=', 'operation_approval')], limit=1)
                approval_users = [(6, 0, approval_record.users.ids)]
            if rec.state == 'operation_approval':
                approval_record = self.env['rent.approvals'].search([('type', '=', 'sales_manger')], limit=1)
                approval_users = [(6, 0, approval_record.users.ids)]
            if rec.state == 'sales_manger':
                approval_record = self.env['rent.approvals'].search([('type', '=', 'finance_approval')], limit=1)
                approval_users = [(6, 0, approval_record.users.ids)]
            if rec.state == 'finance_approval':
                approval_record = self.env['rent.approvals'].search([('type', '=', 'rented')], limit=1)
                approval_users = [(6, 0, approval_record.users.ids)]
            rec.approvals_users = approval_users

    def initial_rent(self):
        self.state = 'initial_rent'
        self.approval_rent()

    def operation_approval(self):
        self.state = 'operation_approval'
        self.approval_rent()

    def sales_manger(self):
        self.state = 'sales_manger'
        self.approval_rent()

    def finance_approval(self):
        self.state = 'finance_approval'
        self.approval_rent()
        # self.make_log()

    def rented(self):
        self.state = 'rented'
        self.approval_rent()
        # self.make_log()

    def onchange_method_state(self):
        print("enter herer state ")
        req_id = self.env['history.reservation'].create({
            # 'name':'Initial Contract',
            'date': datetime.now(),
            'name': self.reservation_code,
            'state': self.state,
            'unit_id': self.property_id.id,
            'res_id': self.id,

        })

    name = fields.Char(string="Name", compute="_compute_name_res_and_amen")

    def _compute_name_res_and_amen(self):
        for rec in self:
            if rec.custom_type == "rent":
                rec.name = rec.reservation_code
            elif rec.custom_type == "Accessories":
                rec.name = rec.accessories_code
            else:
                rec.name = rec.reservation_code

    custom_type = fields.Selection(string="Type", selection=[('rent', 'Rent'), ('Accessories', 'Amendment'), ],
                                   required=False, default="rent")
    reservation_code = fields.Char(string="Rent Code", readonly=True, copy=False, store=True)
    accessories_code = fields.Char(string="Accessories Code", readonly=True, copy=False, store=True, tracking=True)
    date = fields.Date(string="Date", required=False, default=fields.Date.today())

    # Accessories
    related_res_id = fields.Many2one(comodel_name="res.rent", string="Related Reservation", required=False,
                                     domain=[('custom_type', '=', 'Reservation')])

    @api.onchange('related_res_id')
    def onchange_method(self):
        if self.related_res_id:
            self.related_unit_id = self.related_res_id.property_id.id
            self.project_id = self.related_res_id.project_id.id
            self.phase_id = self.related_res_id.phase_id.id
            self.sale_person_2_id = self.related_res_id.sale_person_2_id.id
            self.customer_id = self.related_res_id.customer_id.id

    related_unit_id = fields.Many2one('product.product', _('Related Unit '), store=True)

    @api.onchange('date')
    def onchange_date(self):
        if self.date:
            create_group_name = self.env['res.groups'].search(
                [('name', '=', 'Unlock_Date')])
            result = self.env.user.id in create_group_name.users.ids
            if result == False:
                if datetime.strptime(str(self.date), DEFAULT_SERVER_DATE_FORMAT).date() < datetime.now().date():
                    self.update({
                        'date': False
                    })
                    raise ValidationError('Please select a date equal/or greater than the current date')

        # return my_date

    is_eoi = fields.Boolean(string="EOI", )
    project_id = fields.Many2one('project.project', _("Project"), required=False)
    # terms_and_conditions = fields.Text(string="Terms and Conditions", required=False,related='project_id.terms_and_conditions' )
    phase_id = fields.Many2one('project.phase', _('Phase'), required=False)
    # property information
    property_id = fields.Many2one('product.product', _('Property'), required=False)
    property_code = fields.Char(string="Property Code", copy=False, related='property_id.property_code')
    finish_of_property_id = fields.Many2one('property.finished.type', _('Finishing Type'),
                                            related='property_id.finish_of_property_id')
    is_select_all = fields.Boolean(string="Select All", )
    is_select_all_print = fields.Boolean(string="", )

    @api.onchange('is_select_all_print')
    def onchange_method_is_select_all_print(self):
        for rec in self:
            if rec.is_select_all_print == True:
                if rec.payment_strg_ids:
                    for payment in rec.payment_strg_ids:
                        payment.is_print = True

            if rec.is_select_all_print == False:
                if rec.payment_strg_ids:
                    for payment in rec.payment_strg_ids:
                        payment.is_print = False

    @api.onchange('is_select_all')
    def onchange_method_is_select_all(self):
        for rec in self:
            if rec.is_select_all == True:
                if rec.payment_strg_ids:
                    for payment in rec.payment_strg_ids:
                        payment.is_selected_to_action = True

            if rec.is_select_all == False:
                if rec.payment_strg_ids:
                    for payment in rec.payment_strg_ids:
                        payment.is_selected_to_action = False

    unit_ids = fields.Char()

    @api.onchange('project_id')
    def on_change_project(self):
        for rec in self:
            # rec.unit_ids = False
            all_phases = []
            if rec.phase_id.project_id.id != rec.project_id.id:
                rec.phase_id = False
            phases = self.env['project.phase'].search(
                [('project_id', '=', rec.project_id.id)])
            for phase in phases:
                all_phases.append(phase.id)
            return {'domain': {'phase_id': [('id', 'in', all_phases)]}}

    # sales details
    sales_type = fields.Selection([('direct', _("Direct")), ('Broker', _("Broker"))], _('Sales Type'), default='direct')
    broker_id = fields.Many2one(comodel_name="res.partner", string="Broker", required=False,
                                domain=[('is_broker', '=', True)])
    # customer details
    customer_id = fields.Many2one('res.partner', string="Customer")
    address = fields.Char(string="Address", related='customer_id.street')
    phone = fields.Char(string="Phone", related='customer_id.phone')
    mobile = fields.Char(string="Mobile1", related='customer_id.mobile')
    email = fields.Char(string="Email", related='customer_id.email')
    nationality = fields.Char(string="Nationality", related='customer_id.nationality')
    id_def = fields.Char(string="ID", related='customer_id.id_def')
    social_status = fields.Selection(string="Social Status", selection=[('married', 'Married'), ('single', 'Single'), ],
                                     related='customer_id.social_status', required=False, )

    @api.onchange('customer_id')
    def onchange_method_customer_id(self):
        self.id_no = self.customer_id.id_def

    # lead
    lead_id = fields.Many2one('crm.lead', string="Lead")

    # internal information

    # sale_person_id = fields.Many2one(comodel_name="res.users", string="SalesPerson", required=True,default=lambda self: self.env.user )
    # Sales_Teams_id = fields.Many2one(related='sale_person_id.sale_team_id',comodel_name="crm.team", string="Sales Teams", required=True,)
    # manager_tesm_id = fields.Many2one(related='Sales_Teams_id.user_id',comodel_name="res.users", string="Team Leader	", required=True,default=lambda self: self.env.user )
    sale_person_2_id = fields.Many2one(comodel_name="res.partner", string="SalesPerson", )
    Sales_Teams_2_id = fields.Many2one(related='sale_person_2_id.company_team_id', comodel_name="company.team",
                                       string="Company Teams", )
    manager_tesm_2_id = fields.Many2one(related='Sales_Teams_2_id.user_id', comodel_name="res.partner",
                                        string="Team Leader", )
    company_id = fields.Many2one('res.company', string='Company', store=True, readonly=True,
                                 default=lambda self: self.env.company
                                 , change_default=True)
    currency_id = fields.Many2one(string='Currency', store=True, readonly=True,
                                  related='company_id.currency_id', change_default=True)

    # attachment
    id_no = fields.Char(string="Identification No.")
    id_type = fields.Selection([('id', _("ID")), ('passport', _("Passport"))], string="Identification Type")
    id_photo = fields.Binary("Photo ID")

    # request come
    req_reservation_id = fields.Many2one(comodel_name="request.reservation", string="Request Reservation",
                                         required=False, )
    #
    payment_code = fields.Char(string="Payment Code", required=False, )

    # create method
    @api.model
    def create(self, values):
        print(" values ::> ", values)

        values['month_amount2'] = self.month_amount
        if values['custom_type'] == 'rent':
            values['reservation_code'] = self.env['ir.sequence'].next_by_code('real.estate.rent.id.seq.finish')
            values['name'] = self.env['ir.sequence'].next_by_code('real.estate.rent.id.seq.finish')
        elif values['custom_type'] == 'Accessories':
            values['accessories_code'] = self.env['ir.sequence'].next_by_code('real.estate.Accessories.id.seq.finish')
            values['name'] = self.env['ir.sequence'].next_by_code('real.estate.Accessories.id.seq.finish')

        values['payment_code'] = self.env['ir.sequence'].next_by_code('payment.cheque.seq')
        return super(requestRent, self).create(values)

    num_to_word = fields.Char(compute='calc_num_to_word', store=True)

    @api.depends('total_pay', )
    def calc_num_to_word(self):
        for rec in self:
            rec.num_to_word = rec.company_id.currency_id.ar_amount_to_text(rec.total_pay)

    def convert_to_rented(self):
        for rec in self:
            if rec.state in ['draft']:
                # TODO: remove no empty
                # start
                # if rec.id_no == False:
                #     raise ValidationError(_(
                #         "Identification No Empty  !!"))
                #
                # if rec.id_type == False:
                #     raise ValidationError(_(
                #         "Identification Type Empty  !!"))
                # end
                # if rec.id_photo == False:
                #     raise ValidationError(_(
                #         "Photo ID Empty  !!"))
                if rec.payment_strg_ids.ids == []:
                    raise ValidationError(_(
                        "Payment Strategy Empty  !!"))
                if rec.customer_id.id == False:
                    raise ValidationError(_(
                        "Customer Empty  !!"))
                if rec.sale_person_2_id.id == False:
                    raise ValidationError(_(
                        "SalesPerson Empty  !!"))
                res_res = self.env['res.rent'].search([('property_id', '=', rec.property_id.id),
                                                       ('state', 'in', ['rented'])])
                if len(res_res) == 0:
                    rec.state = 'rented'
                    if rec.custom_type == 'rent':
                        rec.property_id.state = 'rented'
                        # rec.req_reservation_id.state = 'reserved'

                    # rec.onchange_method_state()

                else:
                    if rec.custom_type == 'rented':

                        raise ValidationError(_(
                            "Sorry .. you must Create One Reservation Form For Reservation Form for This Property  %s!!") % self.property_id.name)
                    else:
                        rec.state = 'rented'

    def convert_to_block(self):
        for rec in self:
            if rec.state in ['reserved', 'draft']:
                rec.state = 'blocked'
                rec.onchange_method_state()
                rec.req_reservation_id.state = 'blocked'
                # res_res = self.env['res.rent'].search([('property_id', '=', rec.property_id.id),
                #                                      ('state', 'in', ['reserved'])])
                # if len(res_res) != 0:
                rec.property_id.state = 'available'

    def convert_to_draft(self):
        for rec in self:
            if rec.state in ['blocked', 'reserved', 'contracted']:

                rec.state = 'draft'
                rec.onchange_method_state()
                rec.req_reservation_id.state = 'draft'
                res_res = self.env['res.rent'].search([('property_id', '=', rec.property_id.id),
                                                       ('state', 'in', ['reserved'])])
                if len(res_res) != 0:
                    rec.property_id.state = 'available'

    # part payment and lins

    pay_strategy_id = fields.Many2one('account.payment.term', string="Payment Strategy")
    payment_strg_name = fields.Char(string="Payment Strategy", related='pay_strategy_id.name', store=True)
    payment_term_discount = fields.Float(string="Payment Term Discount",
                                         related="pay_strategy_id.payment_term_discount", store=True, digits=(16, 2))
    is_Custom_payment = fields.Boolean(string="Custom Strategy", )

    Description_payment = fields.Text(string="Description Payment Strategy	", required=False, )
    # new_field_ids = fields.One2many(comodel_name="", inverse_name="", string="", required=False, )

    discount = fields.Float(string="Discount Percentage", digits=(16, 15))
    total_discount = fields.Float('Total Discount', compute='_compute_total_discount', store=True)

    property_price = fields.Float(string="Property Price", readonly=True, related='property_id.final_unit_price',
                                  digits=(16, 2))
    net_price = fields.Float(string="Net Price", compute='_calc_net_price', store=True, digits=(16, 2))

    payment_due = fields.Float(string="Payment Due", required=False, compute="_calc_net_price")
    payment_lines = fields.Float(string="Payment Lines", required=False, store=True)
    # @api.depends("req_reservation_id")
    # def _compute_payments(self):
    #     amount = 0
    #     for rec  in self:

    more_discount = fields.Float(string="Discount", required=False, )
    amount_discount = fields.Float(string="Amount Discount", required=False, )

    @api.onchange('amount_discount')
    def onchange_method_amount_discount(self):
        if self.property_price > 0:
            self.more_discount = (self.amount_discount / self.property_price) * 100.0

    @api.onchange('more_discount')
    def onchange_method_more_discount(self):
        self.amount_discount = self.property_price * (self.more_discount / 100.0)

    @api.depends('discount', 'payment_term_discount', 'property_price', 'more_discount')
    def _calc_net_price(self):
        amount = 0
        for record in self:
            print("record.payment_due :: %s", record.payment_due)
            if record.is_Custom_payment == False:
                first_discount = record.property_price - (
                            record.property_price * (record.payment_term_discount / 100.0))
                net_price_first = first_discount - ((
                        first_discount * (record.discount / 100.0))) - amount - record.payment_lines
                record.net_price = net_price_first - (net_price_first * (record.more_discount / 100.0))
            else:
                total = 0
                for line in record.payment_strg_ids:
                    total += line.amount
                net_price_first = total - record.payment_lines
                record.net_price = net_price_first - (net_price_first * (record.more_discount / 100.0))

    @api.depends('discount', 'payment_term_discount')
    def _compute_total_discount(self):
        for record in self:
            record.total_discount = record.discount + record.payment_term_discount

    date_start_installment = fields.Date(string="Start Installment", required=True, default=fields.datetime.today())

    number_day = fields.Integer(string="Number Of day", required=False, )

    @api.onchange('pay_strategy_id', 'discount', 'date_start_installment', 'number_day')
    def _onchange_pay_strategy(self):
        inbound_payments = self.env['account.payment.method'].search([('payment_type', '=', 'inbound')])
        for rec in self:
            payments = []
            for payment in rec.payment_strg_ids:
                payment.write({
                    'reserve_id': False
                })
            if rec.pay_strategy_id and rec.pay_strategy_id.id:
                for payment_line in rec.pay_strategy_id.line_ids:
                    payment_methods = inbound_payments and payment_line.journal_id.inbound_payment_method_ids or \
                                      payment_line.journal_id.outbound_payment_method_ids
                    # if rec.created_date:
                    #     date_order_format = datetime.strptime(rec.created_date+ ' 01:00:00', "%Y-%m-%d %H:%M:%S")
                    # else:
                    print(
                        "datetime.date.today() :: %S", datetime.today()
                    )
                    # date_order_format = rec.date_start_installment
                    date_order_format = rec.date_start_installment
                    payment_date = date_order_format
                    if payment_line.days > 0:
                        _logger.info("enter here :: ")
                        no_months = payment_line.days / 30
                        _logger.info("enter here no_months :: %s", no_months)

                        date_order_day = date_order_format.day
                        date_order_month = date_order_format.month
                        date_order_year = date_order_format.year
                        payment_date = date(date_order_year, date_order_month, date_order_day) + relativedelta(
                            months=math.ceil(no_months))
                    cheque_status = 'draft'

                    if payment_line.deposit:
                        cheque_status = 'received'

                    first_discount = rec.property_price - (
                            rec.property_price * (rec.payment_term_discount / 100.0))
                    net_price = first_discount - (
                            first_discount * (rec.discount / 100.0))
                    net_price = rec.property_price - (
                            rec.property_price * ((rec.discount + rec.payment_term_discount) / 100))

                    # Todo If line is Maintenance Fee
                    if payment_line.add_extension:
                        print("1111")
                        payment_amount = payment_line.value_amount * rec.property_price

                    else:
                        print("2222")
                        payment_amount = payment_line.value_amount * rec.net_price
                    payment_arr = {
                        'amount': payment_amount,
                        'base_amount': payment_amount,
                        'payment_date': payment_date,
                        'journal_id': payment_line.journal_id.id,
                        'description': payment_line.payment_description,
                        'deposite': payment_line.deposit,
                        'cheque_status': cheque_status,
                        'add_extension': payment_line.add_extension,
                        'is_garage': payment_line.is_garage,
                        'is_garage_main': payment_line.is_garage_main,
                        'markting': payment_line.markting,
                        'Waste_insurance': payment_line.Waste_insurance,
                        # 'payment_method_id': payment_methods.id and payment_methods[0].id or False,
                        'property_ids': [(6, 0, [rec.property_id.id])],
                        "is_maintainance": payment_line.add_extension

                    }

                    payments.append((0, 0, payment_arr))
            rec.payment_strg_ids = payments

    def button_delete_lines_selected(self):
        for rec in self:
            if rec.payment_strg_ids:
                for payment in rec.payment_strg_ids:
                    if payment.is_selected_to_action == True:
                        if payment.is_receive == False:
                            payment.unlink()
                        else:
                            raise UserError(_("You Cant Delete Payment Received."))
                for payment in rec.payment_strg_ids:
                    payment.is_selected_to_action = False

    def button_receive_lines_selected(self):
        for rec in self:
            if rec.payment_strg_ids:
                for payment in rec.payment_strg_ids:
                    # if payment.type != 'cash':
                    if payment.is_selected_to_action == True:
                        payment.is_receive = True

                for payment in rec.payment_strg_ids:
                    payment.is_selected_to_action = False

    def generate_report(self):
        if (not self.env.company.logo):
            raise UserError(_("You have to set a logo or a layout for your company."))
        elif (not self.env.company.external_report_layout_id):
            raise UserError(_("You have to set your reports's header and footer layout."))
        data = {}
        counter = 0
        for line in self.payment_strg_ids:
            print("line.is_selected_to_action ", line.is_selected_to_action)
            if line.is_selected_to_action == True:
                counter += 1
                print("counter11", counter)
            print("counter22", counter)
        #
        # if counter > 1:
        #     print("counter",counter)
        #     raise ValidationError(_("Sorry .. you must Select Once line  !!"))
        if counter == 0:
            print("counter", counter)
            raise ValidationError(_("Sorry .. you must Select Once line  !!"))
        for rec in self:
            if rec.payment_strg_ids:
                request_reservation = []
                for payment in rec.payment_strg_ids:
                    if payment.is_selected_to_action == True:
                        payment.is_print = True
                        amount_to_text = rec.company_id.currency_id.ar_amount_to_text(payment.amount)
                        request_reservation.append({
                            'model': 'payment.strg.request',
                            'date': payment.payment_date,
                            'description': payment.description,
                            'amount': payment.amount,
                            'journal_id': payment.journal_id.name,
                            'is_receive': payment.is_receive,
                            'bank_name': payment.bank_name.name,
                            'cheque': payment.cheque,
                            'deposite': payment.deposite,
                            'add_extension': payment.add_extension,
                            'maintainance_fees': payment.maintainance_fees,
                            'customer': rec.customer_id.name,
                            'property': rec.property_id.name,
                            'project': rec.project_id.name,
                            'state_payment': payment.state_payment,
                            'payment_code': payment.payment_code,
                            'amount_to_text': amount_to_text,
                            'company_name_arabic': rec.company_id.name_arabic,
                            'user_name_arabic': rec.create_uid.name_Branch,
                            'notes_cash': rec.notes_cash,
                            'notes_visa': rec.notes_visa,
                            'notes_cheque': rec.notes_cheque,
                            'notes_bank': rec.notes_bank,
                            'receipt_date': payment.receipt_date,
                        })

        data['request_reservation'] = request_reservation
        return self.sudo().env.ref('mabany_real_estate.payment_reservation_report_id').report_action([], data=data)

        # return self.env.ref('add_real_estate.payment_stag_request_id').report_action(
        #     self,
        #     data=datas)

        # for payment in rec.payment_strg_ids:
        #     payment.is_selected_to_action = False

    def create_initial_contract(self):
        account = self.env['account.account'].search([('id', '=', 2)], limit=1)
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)

        total_ins = 0

        for line in self.payment_strg_ids:
            print("line.reserve_id.id,", line.reserve_id.id)
            print("line.reserve_id.id,", line.cheque)
            print("line.reserve_id.id,", line.id)
            # if line.cheque:
            #     strg = self.env['payment.strg'].search([('id', '=', self.payment_strg_ids.ids),('cheque','=',line.cheque),('id','!=',line.id)])
            #     if strg:
            #         raise ValidationError(_('Error !,Number Cheque Duplicate.'))

            if line.is_maintainance == False and line.is_no_enter_total == False:
                total_ins += line.amount

        print("self.env.user.has_group('mabany_real_estate.group_custom_payment') :> ",
              self.env.user.has_group('mabany_real_estate.group_custom_payment'))
        if self.env.user.has_group('mabany_real_estate.group_custom_payment') == False:
            # if  self.user_has_groups('add_real_estate.group_custom_payment'):

            print("total_ins  :> ", total_ins)
            print("total_ins  :> ", round(total_ins))
            print("self.net_price  :> ", self.net_price)
            print("self.net_price  :> ", round(self.net_price))
            if self.pay_strategy_id:
                if round(total_ins) != round(self.net_price):
                    raise ValidationError(_('Error !,The Total installment is not equal The net Price.'))

        lines = []
        print("self.property_id.propert_account_id.id :: %s", self.property_id.propert_account_id.name)
        lines.append((0, 0, {
            'product_id': self.property_id.id,
            'name': self.property_id.name,
            'analytic_account_id': self.property_id.analytic_account_id.id,
            'price_unit': self.net_price,

        }))
        print("lines :: %s", lines)
        req_id = self.env['account.move'].create({
            # 'name':'Initial Contract',
            'date': datetime.now(),
            'invoice_date': datetime.now(),
            'partner_id': self.customer_id.id,
            'ref': self.reservation_code,
            'type': 'out_invoice',
            'is_contract': True,
            'reservation_id': self.id,
            'journal_id': journal.id

        })

        print("req_id :: %s", req_id.id)
        req_id.update({
            # 'move_id': req_id.id,
            'invoice_line_ids': lines,

        })
        view = self.env.ref('mabany_real_estate.view_contract_form')

        return {'name': (
            'Contract'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': req_id.id,
            'views': [
                (view.id, 'form')
            ],
            'view_id': view.id,
            'view_type': 'form',
            'view_mode': 'form',
            'context': {'name': 'Initial Contract'},

        }

    is_create_contract = fields.Boolean(string="Is Request Resveration", compute="_compute_view_button_create")

    def _compute_view_button_create(self):
        for rec in self:
            res = self.env['account.move'].search(
                [('reservation_id', '=', rec.id), ("state", '!=', 'cancel')
                 ], limit=1)

            if len(res) > 0:
                rec.is_create_contract = True
            else:
                rec.is_create_contract = False

            print("rec.is_create_contract :: %s", rec.is_create_contract)

    amount_total = fields.Float(string="Amount", required=False, compute="_compute_amount")
    main_total = fields.Float(string="Maintance", required=False, compute="_compute_amount")
    main_ins = fields.Float(string="Insurance", required=False, compute="_compute_amount")
    marketing_total = fields.Float(string="Marketing", required=False, compute="_compute_amount")
    Waste_insurance_total = fields.Float(string="Waste insurance", required=False, compute="_compute_amount")
    amount_residual = fields.Float(string="Amount Due", required=False, compute="_compute_amount")

    def _compute_amount(self):
        amount = 0
        main_total = 0
        main_ins = 0
        marketing_total = 0
        Waste_insurance_total = 0
        due = 0
        amount_discount = 0
        for rec in self:
            if rec.payment_strg_ids:
                for line in rec.payment_strg_ids:
                    if line.is_maintainance == False and line.is_no_enter_total == False:
                        amount += line.amount
                    if line.is_maintainance == True:
                        main_total += line.amount
                    if line.ins == True:
                        main_ins += line.amount
                    if line.is_maintainance == True:
                        marketing_total += line.amount
                    if line.is_maintainance == True:
                        Waste_insurance_total += line.amount
                    due += line.amount_due
                rec.amount_total = amount
                # amount_discount = rec.amount_total * (rec.more_discount /100.00)
                # rec.amount_discount = amount_discount
                rec.amount_residual = due
                rec.main_total = main_total
                rec.main_ins = main_ins
                rec.marketing_total = marketing_total
                rec.Waste_insurance_total = Waste_insurance_total
            else:
                rec.amount_total = 0
                rec.amount_residual = 0
                rec.main_total = 0
                rec.marketing_total = 0
                rec.Waste_insurance_total = 0
                rec.main_total = main_total
                rec.main_ins = 0
                # rec.amount_discount = 0

    date_annual_increase = fields.Date('Date Annual Increase')
    perc_increase = fields.Float('Percentage')

    bank_name = fields.Many2one('payment.bank', _("Bank Name"))
    # start_cheque = fields.Integer(string="Start", required=False, size=20)
    # end_cheque = fields.Integer(string="End", required=False,size=20 )
    start_cheque = fields.Char(string="Start", required=False, size=20)
    end_cheque = fields.Char(string="End", required=False, size=20)

    amount_ins = fields.Float(string="Amount Ins.", required=False, )

    def create_invoice_rent(self):
        tmp = 0
        for r in self.payment_strg_ids:
            if r.is_selected_to_action == True:
                tmp += r.rent_value
                print('tmp>>>', tmp)
        if tmp > 0:
            res = self.env['account.move'].create({
                'partner_id': self.customer_id.id,
                'move_type': 'out_invoice',
                'invoice_date': date.today(),
                'rent_id': self.id,
                'ref': self.reservation_code,
                'invoice_line_ids': [(0, 0, {
                    'name': 'rent line',
                    'price_unit': tmp,
                    'quantity': 1,
                    'product_id': self.property_id.id,
                })],
            })
            return {'type': 'ir.actions.act_window',
                    'name': _('Invoices'),
                    'res_model': 'account.move',
                    'res_id': res.id,
                    'target': 'current',
                    'view_mode': 'form',
                    }

    def create_invoice_sales(self):
        tmp = 0
        for r in self.payment_strg_ids:
            if r.is_selected_to_action == True:
                tmp += r.difference
                print('tmp>>>', tmp)
        if tmp > 0:
            res = self.env['account.move'].create({
                'partner_id': self.customer_id.id,
                'move_type': 'out_invoice',
                'invoice_date': date.today(),
                'rent_id': self.id,
                'ref': self.reservation_code,
                'invoice_line_ids': [(0, 0, {
                    'name': 'rent line',
                    'price_unit': tmp,
                    'quantity': 1,
                    'product_id': self.property_id.id,
                })],
            })
            return {'type': 'ir.actions.act_window',
                    'name': _('Invoices'),
                    'res_model': 'account.move',
                    'res_id': res.id,
                    'target': 'current',
                    'view_mode': 'form',
                    }

    def update_ins_amount_data(self):
        for line in self.payment_strg_ids:
            if line.is_selected_to_action == True:
                line.amount = self.amount_ins
                line.base_amount = self.amount_ins

    def update_bank_data(self):
        counter = int(self.start_cheque)
        end = int(self.end_cheque)
        print("counter :: %s", counter)
        for line in self.payment_strg_ids:
            if line.is_selected_to_action == True:
                if line.type != 'cash':
                    if int(self.start_cheque) == int(self.end_cheque):
                        line.cheque = int(self.start_cheque)
                    else:
                        line.bank_name = self.bank_name.id
                        if int(self.end_cheque) >= counter:
                            line.cheque = counter
                            counter += 1

    is_release = fields.Boolean(string="Is Release", )
    odoo_reservation_id = fields.Many2one(comodel_name="res.rent", string="Old Reservation", required=False, )

    # payment view
    def action_view_contract_payment(self):
        self.ensure_one()
        action = self.env.ref('mabany_real_estate.Contract_payment_list_action').read()[0]
        action['domain'] = [
            ('rent_id', '=', self.id),
        ]
        print("action %s", action)
        return action

    counter_payment = fields.Integer(string="Counter Payment", required=False, compute="_compute_counter_payment")

    def _compute_counter_payment(self):
        for rec in self:
            contracts = self.env['account.payment'].sudo().search(
                [('rent_id', '=', rec.id)])
            rec.counter_payment = len(contracts)

    counter_contract = fields.Integer(string="Counter Contract", required=False, compute="_compute_counter_contract")

    def _compute_counter_contract(self):
        for rec in self:
            contracts = self.env['account.move'].sudo().search(
                [('rent_id', '=', rec.id), ('move_type', 'in', ['out_invoice'])])
            rec.counter_contract = len(contracts)

    counter_amendments = fields.Integer(string="Counter Contract", required=False, compute="_compute_counter_amen")

    def _compute_counter_amen(self):
        for rec in self:
            contracts = self.env['res.rent'].sudo().search(
                [('related_res_id', '=', rec.id)])
            rec.counter_amendments = len(contracts)

    def action_view_contract_reservation(self):
        self.ensure_one()
        action = self.env.ref('mabany_real_estate.action_move_out_invoice_type_contract').read()[0]
        action['domain'] = [
            ('move_type', 'in', ['out_invoice']),
            ('rent_id', '=', self.id),
        ]
        print("action %s", action)
        return action

    def action_view_contract_Accessories(self):
        self.ensure_one()
        action = self.env.ref('mabany_real_estate.accessories_list_action').read()[0]
        action['domain'] = [
            # ('state', 'in', ['draft','reserved']),
            ('related_res_id', '=', self.id),
        ]
        print("action %s", action)
        return action

    def create_payment_lines_selected(self):
        counter = 0
        # req_id = []
        for line in self.payment_strg_ids:
            if line.is_selected_to_action == True:
                counter += 1
        if counter > 1:
            raise ValidationError(_("Sorry .. you must Select Once line  !!"))
        if counter == 0:
            raise ValidationError(_("Sorry .. you must Select Once line  !!"))
        method = self.env['account.payment.method'].sudo().search([
            ('name', '=', 'Manual')
        ], limit=1)
        method_batch = self.env['account.payment.method'].sudo().search([
            ('name', '=', 'Batch Deposit')
        ], limit=1)
        data_bank = self.env['data.bank.cheque']

        for line in self.payment_strg_ids:
            if line.type == 'cash':
                if line.is_selected_to_action == True and line.is_create_payment == True:
                    raise ValidationError(_("Sorry .. you Create Payment Before  !!"))
                if line.is_selected_to_action == True and line.is_create_payment == False:
                    req_id = self.env['account.payment'].create({
                        'state': 'draft',
                        'date': datetime.now(),
                        'payment_type': 'inbound',
                        'partner_type': 'customer',
                        'partner_id': self.customer_id.id,
                        'amount': line.amount,
                        'journal_id': line.journal_id.id,
                        'payment_method_id': method.id,
                        'rent_id': self.id,
                        'payment_strg_id': line.id,
                        'is_contract': True,
                        'is_payment_lines': True,

                    })
                    print("req_id :: ", req_id)
                    line.is_create_payment = True
                    line.is_pay = True

                    p = []

                    p.append(pay2.id)
                    for rec in pay_strg.payments_ids:
                        p.append(rec.id)

                    line.update({
                        'payments_ids': [(6, 0, p)],
                    })
                    # self.payment_lines = line.amount
                    break
            else:
                if line.is_selected_to_action == True and line.is_create_payment == True:
                    raise ValidationError(_("Sorry .. you Create Payment Before  !!"))
                if line.is_selected_to_action == True and line.is_create_payment == False:
                    print("date.today() :> ", date.today())
                    req_id = self.env['account.payment'].create({
                        'state': 'draft',
                        # 'payment_date': date.today(),
                        'payment_type': 'inbound',
                        'partner_type': 'customer',
                        'partner_id': self.customer_id.id,
                        'amount': line.amount,
                        'journal_id': line.journal_id.id,
                        'payment_method_id': method_batch.id,
                        'rent_id': self.id,
                        'payment_strg_id': line.id,
                        'bank_name': line.bank_name.name,
                        'check_number': line.cheque,
                        'due_date': line.payment_date,
                        'actual_date': line.payment_date,
                        'is_contract': True,
                        'is_payment_lines': True,

                    })
                    print("req_id :: ", req_id)
                    line.is_create_payment = True
                    line.is_pay = True
                    data_bank_id = data_bank.create({
                        'bank_id': line.bank_name.id,
                        'cheque_number': line.cheque,
                        'rent_id': self.id,
                        'payment_id': req_id.id,

                    })
                    l = []
                    p = []
                    l.append(data_bank_id.id)
                    for line2 in line.bank_ids:
                        l.append(line2.id)
                    p.append(req_id.id)
                    for rec in line.payments_ids:
                        p.append(rec.id)
                    line.update({
                        'bank_ids': [(6, 0, l)],
                        'payments_ids': [(6, 0, p)],
                    })
                    # self.payment_lines = line.amount
                    break
        # return {'name': (
        #                     'Payment'),
        #                 'type': 'ir.actions.act_window',
        #                 'res_model': 'account.payment',
        #                 'res_id': req_id.id,
        #                 'view_type': 'form',
        #                 'view_mode': 'form',
        #             }

    # @api.onchange('payment_strg_ids')
    # def _onchange_payment_strg_ids(self):
    #     for rec in self:
    #         total_ins = 0
    #         for line in rec.payment_strg_ids:
    #             if line.is_maintainance== False:
    #                 total_ins += line.amount
    #
    #         if not self.user_has_groups('add_real_estate.group_custom_payment'):
    #             if total_ins != rec.net_price:
    #                 raise ValidationError(_('Error !.'))

    # @api.constrains('payment_strg_ids')
    # def check_payment_strg_ids(self):
    #     total_ins = 0
    #
    #     for line in self.payment_strg_ids:
    #         print("line.reserve_id.id,",line.reserve_id.id)
    #         print("line.reserve_id.id,",line.cheque)
    #         print("line.reserve_id.id,",line.id)
    #         if line.cheque:
    #             strg = self.env['payment.strg'].search([('id', '=', self.payment_strg_ids.ids),('cheque','=',line.cheque),('id','!=',line.id)])
    #             if strg:
    #                 raise ValidationError(_('Error !,Number Cheque Duplicate.'))
    #
    #         if line.is_maintainance == False:
    #             total_ins += line.amount
    #
    #     if not self.user_has_groups('add_real_estate.group_custom_payment'):
    #         print("total_ins  :> ",total_ins)
    #         print("total_ins  :> ",round(total_ins))
    #         print("self.net_price  :> ",self.net_price)
    #         print("self.net_price  :> ",round(self.net_price))
    #         if self.pay_strategy_id:
    #             if round(total_ins) != round(self.net_price):
    #                 raise ValidationError(_('Error !,The Total installment is not equal The net Price.'))
    #

    notes_cash = fields.Text(string="Notes (Cash)", required=False, )
    notes_visa = fields.Text(string="Notes (Visa)", required=False, )
    notes_cheque = fields.Text(string="Notes (Cheque)", required=False, )
    notes_bank = fields.Text(string="Notes (Bank)", required=False, )

    amount_cheques = fields.Float(string="Amount Cheques", required=False, compute="_compute_amount_cheques")

    def _compute_amount_cheques(self):
        for rec in self:
            if rec.payment_strg_ids:
                totol = 0
                for line in rec.payment_strg_ids:
                    if line.state_payment == 'cheque':
                        totol += line.amount

                rec.amount_cheques = totol
            else:
                rec.amount_cheques = 0

    number_ins = fields.Integer(string="", required=False, compute="_compute_number_ins")

    def _compute_number_ins(self):
        for rec in self:
            if rec.payment_strg_ids:
                counter = 0
                for line in rec.payment_strg_ids:
                    if line.state_payment == 'cheque':
                        counter += 1

                rec.number_ins = counter
            else:
                rec.number_ins = 0

    receipt_date = fields.Date(string="Receipt Date", required=False, )

    def update_ins_receipt_date(self):
        for line in self.payment_strg_ids:
            if line.is_selected_to_action == True:
                line.receipt_date = self.receipt_date

    reason = fields.Many2one(comodel_name="cancel.reason.res", string="Reason", required=False, )
    date_cancel_unit = fields.Datetime(string="Cancel Date", required=False, )
    month = fields.Integer('Months', )
    start_date = fields.Date('Start Date', )
    end_date = fields.Date('End Date', compute='calc_end_date', store=True)
    month_amount = fields.Float('Month Amount', )
    percent_of_sale = fields.Float('Percentage Of Sale')
    payment_strg_ids = fields.One2many('payment.strg', 'rent_id')

    def _compute_line_data_for_line_change(self, line, amount, annual_increase):
        journal = self.env['account.journal'].search([
            ('is_notes_receivable', '=', True)], limit=1)
        return {
            'month': line,
            'start_date': self.start_date + relativedelta(months=line - 1),
            'amount': amount,
            'rent_value': amount,
            'state_payment': 'cheque',
            'journal_id': journal.id,
            'payment_date': self.start_date + relativedelta(months=line - 1),
            'percent_of_sale': self.percent_of_sale,
            'rent_id': self._origin.id,
            'annual_increase': annual_increase,

        }

    def calc_rent_lines(self):
        q = [(5, 0, 0)]
        amount = self.month_amount
        annual_increase = 0
        for line in range(1, self.month + 1):
            print("line : ", line)
            data = self._compute_line_data_for_line_change(line, amount, annual_increase)
            if line % 12 == 0:
                amount += (amount * (self.annual_increase / 100))
                annual_increase = self.annual_increase
            print('data>>>>', data)
            q.append((0, 0, data))
        print(q)
        self.payment_strg_ids = q

    @api.depends('start_date', 'month')
    def calc_end_date(self):
        for r in self:
            if r.start_date:
                r.end_date = r.start_date + relativedelta(months=r.month)
            else:
                r.end_date = False

    date_day = fields.Char(compute='_get_date_day')

    def _get_date_day(self):
        for r in self:
            r.date_day = r.start_date.weekday()

    month_day = fields.Date(compute='_get_date_month')
    total_pay = fields.Float(compute='_get_total_pay')
    total_three_pay = fields.Float(compute='_get_total_three_pay')

    def _get_date_month(self):
        for line in range(1, self.month + 1):
            self.month_day = self.start_date + relativedelta(months=line - 1)

    def _get_total_pay(self):
        for r in self:
            r.total_pay = r.month * r.month_amount

    def _get_total_three_pay(self):
        for r in self:
            r.total_three_pay = 3 * r.month_amount

    years = fields.Integer('Years', compute='_calc_years', store=True)

    @api.depends('month')
    def _calc_years(self):
        for rec in self:
            rec.years = int(math.ceil(rec.month / 12))
        print('years>>>', rec.years)

    annual_increase = fields.Float(string="Annual Increase", required=False, )
    # @api.constrains('start_date','end_date','property_id')
    # def constrains_dates(self):
    #     start = self.search([]).mapped('start_date')
    #     end = self.search([]).mapped('end_date')
    #     product = self.search([]).mapped('property_id.id')
    #
    #     res = self.env['res.rent'].search([('start_date','in',start),
    #                                               ('end_date','in',end),
    #                                               ('property_id','in',product),
    #                                            ])
    #     print('resssss>>>',res)
    #     print('self>>>',self.id)
    #     for r in res:
    #         if self.start_date == r.start_date and self.end_date == r.end_date and self.property_id == r.property_id:
    #                 raise ValidationError('This Property Already Rented In This Intervals')

    month_amount2 = fields.Float(
        string='Month_amount2',
        required=False)

    def write(self, vals):
        rslt = super(requestRent, self).write(vals)
        if 'month_amount' in vals:
            history_unit_price_rent = self.env['history.property.unit.price.rent'].create({
                'date': date.today(),
                'unit_price': self.month_amount2,
                'product_id': self.property_id.id,
                'rent_id': self.id,

            })
            if history_unit_price_rent:
                self.month_amount2 = self.month_amount
        return rslt

    rent_type_lines = fields.One2many(
        comodel_name='res.rent.type',
        inverse_name='rent_from_id')

    eng_manage = fields.Boolean(default=False)
    eng_comment = fields.Text('Engineering Comment')
    eng_price = fields.Float('Engineering Cost')
    is_create_eng_cos = fields.Boolean(copy=False)

    def get_counter_bills(self):
        for rec in self:
            count = self.env['account.move'].search_count([('move_type', '=', 'in_invoice'), ('rent_id', '=', rec.id)])
            rec.counter_bills = count

    def action_view_vendor_bills(self):
        self.ensure_one()
        action = self.env.ref('account.action_move_in_invoice_type').read()[0]
        action['domain'] = [
            ('move_type', '=', 'in_invoice'), ('rent_id', '=', self.id)
        ]
        print("action %s", action)
        return action

    def engineering_manage_app(self):
        self.eng_manage = True

    def eng_approval(self):
        self.eng_manage = False

    def create_eng_cost(self):
        self.is_create_eng_cos = True
        res = self.env['account.move'].create({
            'partner_id': self.customer_id.id,
            'move_type': 'out_invoice',
            'rent_id': self.id,
            'invoice_date': date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': self.eng_comment,
                'price_unit': self.eng_price,
                'quantity': 1,
                'product_id': self.property_id.id,
            })],
        })
        return {'type': 'ir.actions.act_window',
                'name': _('Invoices'),
                'res_model': 'account.move',
                'res_id': res.id,
                'target': 'current',
                'view_mode': 'form',
                }

    @api.constrains('rent_type_lines')
    def check_duplicate_rent_type(self):
        mylist = []
        for line in self.rent_type_lines:
            mylist.append(line.rent_type)
        myset = set(mylist)
        if len(mylist) != len(myset):
            raise ValidationError('Can\'t duplicate type')

    def _compute_line_data_for_line_change(self, line, amount, type_line, annual_increase, seq, tax_id, months2):
        journal = self.env['account.journal'].search([
            ('is_notes_receivable', '=', True)], limit=1)
        # tax_amount = 0
        # if tax_id:

        return {
            'month': line,
            # 'month_2': months2,
            'start_date': self.start_date + relativedelta(months=line - 1),
            'amount': amount,
            'rent_value': amount,
            'state_payment': 'cheque',
            'journal_id': journal.id,
            'payment_date': self.start_date + relativedelta(months=line - 1),
            'percent_of_sale': self.percent_of_sale,
            'rent_id': self._origin.id,
            'annual_increase': annual_increase,
            'tax_id': tax_id,

        }

    def insurance_line(self):
        return self.env['payment.strg'].create({
            'amount': self.insurance_amount,
            'rent_id': self.id,
            'start_date': self.date,
            'payment_date': self.date,
            'state_payment': 'cash'
        })

    def deposite_line(self):
        return self.env['payment.strg'].create({
            'amount': self.deposite_amount,
            'rent_id': self.id,
            'start_date': self.date,
            'payment_date': self.date,
            'state_payment': 'cash'
        })

    insurance_amount = fields.Float(related='property_id.insurance_amount')
    deposite_amount = fields.Float(related='property_id.deposite_amount')

    def calc_rent_lines(self):
        q = [(5, 0, 0)]
        amount = self.month_amount
        annual_increase = 0
        amount_with_increase = 0
        for type_line in self.rent_type_lines:
            counter = 0

            months_2 = 13
            # type_name = dict(self.env['res.rent.type']._fields['rent_type'].selection).get(type_line.rent_type)
            for line in range(1, self.month + 1):
                loop = counter // 12
                amount_with_increase = type_line.amount
                print("counter :> ", counter)
                for x in range(loop):
                    increase = amount_with_increase * (self.perc_increase / 100)
                    amount_with_increase = amount_with_increase + increase
                    print("increase :> ", increase)
                    print("amount_with_increase :> ", amount_with_increase)
                # print("line : ", line)
                payment_date = self.start_date + relativedelta(months=line - 1)

                if self.date_annual_increase:
                    data = self._compute_line_data_for_line_change(line, type_line.amount, type_line.rent_type,
                                                                   annual_increase, counter,
                                                                   type_line.tax_id.id, months_2)
                    data['desc'] = type_line.rent_type.name
                    data['rent_type'] = type_line.rent_type.name
                    loop = months_2 // 12
                    amount_with_increase = type_line.amount
                    # years = (self.date_annual_increase - payment_date).days
                    # y = int(-years / 365)
                    if self.date_annual_increase <= payment_date:

                        for x in range(loop):
                            increase = amount_with_increase * (self.perc_increase / 100)
                            amount_with_increase = amount_with_increase + increase
                            print("increase :> ", increase)
                            print("amount_with_increase :> ", amount_with_increase)
                        if months_2 != 0:
                            if months_2 // 12 > 0:
                                # if self.date_annual_increase <= payment_date:
                                # rec.annual_increase = rec.amount + ((rec.rent_id.perc_increase / 100 * (y + 1)) * (rec.amount))
                                # data['rent_value'] = type_line.amount + ((self.perc_increase / 100 * (y + 1)) * (type_line.amount))
                                data['rent_value'] = amount_with_increase
                                data['amount'] = amount_with_increase
                        months_2 += 1
                else:
                    data = self._compute_line_data_for_line_change(line, type_line.amount, annual_increase, counter,
                                                                   type_line.tax_id.id, months_2)
                    data['desc'] = type_line.rent_type.name
                    data['rent_type'] = type_line.rent_type.name
                    if counter != 0:
                        # print("counter :> ",counter)
                        # print("counter :>>>>> ",counter // 12)

                        if counter // 12 > 0:
                            # print("enter Here > ",counter // 12)
                            # data['rent_value'] += (type_line.amount * (self.perc_increase / 100 * (counter // 12))  )
                            data['rent_value'] = amount_with_increase
                            data['amount'] = amount_with_increase

                        # annual_increase = self.annual_increase
                # print('data>>>>', data)

                q.append((0, 0, data))

                counter += 1
        print(q)
        self.payment_strg_ids = q
        self.insurance_line()
        self.deposite_line()

    # number_of_months = fields.Float(
    #     string='Number of months ( Invoice )',
    #     required=False)
    number_of_months = fields.Integer(
        string='Number of months ( Invoice )',
        required=False)

    def create_invoice_rent(self):
        types = []
        lines = []
        res_ids = []

        lines_payment = self.env['payment.strg'].search(
            [('rent_id', '=', self.id), ('month', '=', self.number_of_months)])
        # for r in self.payment_strg_ids:
        #     if r.is_selected_to_action == True:
        #         types.append(r.rent_type)
        #         lines.append(r)

        for line in lines_payment:
            lines.append((0, 0, {
                'name': line.desc,
                'price_unit': line.rent_value,
                'quantity': 1,
                'product_id': self.property_id.id,
                'tax_ids': [(6, 0, [line.tax_id.id])],
            }))
        print("lines :> ", lines)
        res = self.env['account.move'].create({
            'partner_id': self.customer_id.id,
            'move_type': 'out_invoice',
            'invoice_date': date.today(),
            'rent_id': self.id,
            'ref': self.reservation_code,
            'invoice_line_ids': lines

        })
        if res.id:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Invoices'),
                'res_model': 'account.move',
                'domain': [('id', '=', res.id)],
                'target': 'current',
                'view_mode': 'tree,form',
            }

    def create_invoice_sales(self):
        # tmp =0
        # for r in self.payment_strg_ids:
        #     if r.is_selected_to_action == True:
        #         tmp += r.difference
        #         print('tmp>>>',tmp)

        lines_month = self.env['payment.strg.sales.value'].search([('name', '=', self.number_of_months)], limit=1)

        if lines_month:
            res = self.env['account.move'].create({
                'partner_id': self.customer_id.id,
                'move_type': 'out_invoice',
                'invoice_date': date.today(),
                'rent_id': self.id,
                'ref': self.reservation_code,
                'invoice_line_ids': [(0, 0, {
                    'name': 'Sales Value Month ( ' + lines_month.name + ' ) ',
                    'price_unit': lines_month.sales_value_amount,
                    'quantity': 1,
                    'product_id': self.property_id.id,
                })],
            })
            return {'type': 'ir.actions.act_window',
                    'name': _('Invoices'),
                    'res_model': 'account.move',
                    'res_id': res.id,
                    'target': 'current',
                    'view_mode': 'form',
                    }


class ResCurrencyInherit(models.Model):
    _inherit = 'res.currency'

    def ar_amount_to_text(self, amount):
        self.ensure_one()

        def _num2words(number, lang):
            return num2words(number, lang=lang).title()

        if num2words is None:
            logging.getLogger(__name__).warning("The library 'num2words' is missing, cannot render textual amounts.")
            return ""

        formatted = "%.{0}f".format(self.decimal_places) % amount
        parts = formatted.partition('.')
        integer_value = int(parts[0])
        fractional_value = int(parts[2] or 0)

        # lang_code = 'ar_SY'
        # lang = self.env['res.lang'].with_context(active_test=False).search([('code', '=', lang_code)])
        amount_words = tools.ustr('{amt_value} {amt_word}').format(
            amt_value=num2words(integer_value, lang='ar'),
            amt_word='جنيه مصرى لا غير' if self.is_zero(amount - integer_value) else 'جنيها',
        )
        if not self.is_zero(amount - integer_value):
            amount_words += ' ' + _('و') + tools.ustr(' {amt_value} {amt_word}').format(
                amt_value=num2words(fractional_value, lang='ar'),
                amt_word='قرش مصرى لا غير' if fractional_value > 10 else 'قروش فقط لا غير ',
            )
        return amount_words


class ResRentType(models.Model):
    _name = 'res.rent.type'
    _description = 'Rent Type'
    _rec_name = 'rent_type'

    # rent_type = fields.Selection(
    #     selection=[('normal', 'Normal Rent'),
    #                ('main', 'Maintenance'),
    #                ('market', 'Marketing'),
    #                ])

    rent_type = fields.Many2one(
        comodel_name='rent.type.details',
        string='Rent Type',
        required=False)
    amount = fields.Float()

    rent_from_id = fields.Many2one(
        comodel_name='res.rent')

    tax_id = fields.Many2one(related="rent_type.tax_id",
                             comodel_name='account.tax',
                             string='Tax',
                             required=False)


class rentTypeDetails(models.Model):
    _name = 'rent.type.details'

    name = fields.Char(required=1)
    tax_id = fields.Many2one(
        comodel_name='account.tax',
        string='Tax',
        required=False)
    rent = fields.Boolean()
    marketing = fields.Boolean()
    maintaince = fields.Boolean()
