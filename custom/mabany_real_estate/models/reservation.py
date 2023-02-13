from odoo import api, fields, models, _
import datetime
from datetime import datetime, date
from odoo.tools.translate import _
from odoo.exceptions import ValidationError, UserError
import time
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import math
import logging

_logger = logging.getLogger(__name__)


class requestReservation(models.Model):
    _name = 'res.reservation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Unit Reservation"
    _rec_name = 'name'

    created_date = fields.Datetime(string="Created on", default=fields.datetime.today())

    expiration_date = fields.Date(string='Expiration Date')

    def expire_reservation(self):
        draft_reservations = self.env['res.reservation'].search([('state', '=', 'draft')])
        for reservation in draft_reservations:
            today = fields.Date.today()
            if reservation.expiration_date:
                if reservation.expiration_date < today:
                    reservation.write({
                        'state': 'blocked'
                    })

    @api.constrains('date', 'expiration_date')
    def dates_constraints(self):
        for rec in self:
            if rec.date and rec.expiration_date:
                if rec.date >= rec.expiration_date:
                    raise ValidationError(_("Expiration Date must be after Date"))

    _defaults = {
        'created_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    state = fields.Selection(string="State",
                             selection=[('draft', 'Draft'),
                                        ('reserved', 'Reserved'),
                                        ('finance_approval', 'Finance Approval'),
                                        ('request_approval', 'Request Approval'),
                                        ('contracted', 'Contracted'),
                                        ('operation_signature', 'Operation Signature'),
                                        ('legal', 'Legal'),
                                        ('finance_delivered', 'Finance Delivered'),
                                        ('engineering_comment', 'Engineering Comment'),
                                        ('co_approval', 'Co Approval'),
                                        ('customer_service', 'Customer Service'),
                                        ('legal_final_accept', 'Legal Final Accept'),
                                        ('blocked', 'Cancelled'),
                                        ], required=False, default='draft')
    approvals_users = fields.Many2many('res.users', compute='get_approvals_users')
    attr_boolean = fields.Boolean(compute='calc_attr_boolean')

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
                approval_record = self.env['reservation.approvals'].search([('type', '=', 'reserved')], limit=1)
                approval_users = [(6, 0, approval_record.users.ids)]
            elif rec.state == 'reserved':
                approval_record = self.env['reservation.approvals'].search([('type', '=', 'finance_approval')], limit=1)
                approval_users = [(6, 0, approval_record.users.ids)]
            elif rec.state == 'finance_approval':
                approval_record = self.env['reservation.approvals'].search([('type', '=', 'request_approval')], limit=1)
                approval_users = [(6, 0, approval_record.users.ids)]
            elif rec.state == 'request_approval':
                approval_record = self.env['reservation.approvals'].search([('type', '=', 'contracted')], limit=1)
                approval_users = [(6, 0, approval_record.users.ids)]
            elif rec.state == 'contracted':
                approval_record = self.env['reservation.approvals'].search([('type', '=', 'operation_signature')],
                                                                           limit=1)
                approval_users = [(6, 0, approval_record.users.ids)]
            elif rec.state == 'operation_signature':
                approval_record = self.env['reservation.approvals'].search([('type', '=', 'legal')], limit=1)
                approval_users = [(6, 0, approval_record.users.ids)]
            elif rec.state == 'legal':
                approval_record = self.env['reservation.approvals'].search([('type', '=', 'finance_delivered')],
                                                                           limit=1)
                approval_users = [(6, 0, approval_record.users.ids)]
            elif rec.state == 'finance_delivered':
                approval_record = self.env['reservation.approvals'].search([('type', '=', 'engineering_comment')],
                                                                           limit=1)
                approval_users = [(6, 0, approval_record.users.ids)]
            elif rec.state == 'engineering_comment':
                approval_record = self.env['reservation.approvals'].search([('type', '=', 'co_approval')], limit=1)
                approval_users = [(6, 0, approval_record.users.ids)]
            elif rec.state == 'co_approval':
                approval_record = self.env['reservation.approvals'].search([('type', '=', 'customer_service')], limit=1)
                approval_users = [(6, 0, approval_record.users.ids)]
            elif rec.state == 'customer_service':
                approval_record = self.env['reservation.approvals'].search([('type', '=', 'legal_final_accept')],
                                                                           limit=1)
                approval_users = [(6, 0, approval_record.users.ids)]
            rec.approvals_users = approval_users

    def approval_reservation(self):
        users = self.approvals_users
        if users:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
            message_text = f'<strong>Reminder</strong> ' \
                           f'<p>This <a href=%s>Reservation</a> Check Approval On Reservation Form</p>' % base_url

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

    def finance_approval(self):
        self.state = 'finance_approval'
        self.approval_reservation()
        self.make_log()

    def request_approval(self):
        self.state = 'request_approval'
        self.approval_reservation()
        self.make_log()

    def contracted(self):
        self.state = 'contracted'
        self.approval_reservation()
        self.make_log()

    def operation_signature(self):
        self.state = 'operation_signature'
        self.approval_reservation()
        self.make_log()

    def legal(self):
        self.state = 'legal'
        self.approval_reservation()
        self.make_log()

    def finance_delivered(self):
        self.state = 'finance_delivered'
        self.approval_reservation()
        self.make_log()

    def co_approval(self):
        self.state = 'co_approval'
        self.approval_reservation()
        self.make_log()

    def customer_service(self):
        self.state = 'customer_service'
        self.approval_reservation()
        self.make_log()

    def legal_final_accept(self):
        self.state = 'legal_final_accept'
        self.approval_reservation()
        self.make_log()

    # def onchange_method_state(self):
    #     print("enter herer state ")
    #     req_id = self.env['history.reservation'].create({
    #         # 'name':'Initial Contract',
    #         'date': datetime.now(),
    #         'name': self.reservation_code,
    #         'state': self.state,
    #         'unit_id': self.property_id.id,
    #         'res_id': self.id,
    #     })

    name = fields.Char(string="Name", compute="_compute_name_res_and_amen")

    def _compute_name_res_and_amen(self):
        for rec in self:
            if rec.custom_type == "Reservation":
                rec.name = rec.reservation_code
            elif rec.custom_type == "Accessories":
                rec.name = rec.accessories_code
            else:
                rec.name = rec.reservation_code

    custom_type = fields.Selection(string="Type",
                                   selection=[('Reservation', 'Reservation'), ('Accessories', 'Amendment'), ],
                                   required=False, default="Reservation")
    reservation_code = fields.Char(string="Reservation Code", readonly=True, copy=False, store=True)
    accessories_code = fields.Char(string="Accessories Code", readonly=True, copy=False, store=True, tracking=True)
    date = fields.Date(string="Date", required=False, default=fields.Date.today())

    # Accessories
    related_res_id = fields.Many2one(comodel_name="res.reservation", string="Related Reservation", required=False,
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

    def available_to_cancel(self):
        if self.available_to_cancel:
            self.check_field = True

    res_log = fields.One2many('res.log', 'res_id')

    def make_log(self):
        self.res_log = [(0, 0,
                         {
                             'user_id': self.env.user.id,
                             'time': datetime.now(),
                             'state': dict(self._fields['state'].selection).get(self.state),
                             'res_id': self.id})]
        # print('ofofoofofofo')
        # self.env['res.log'].create({
        #     'user_id': self.env.user.id,
        #     'time': datetime.datetime.now(),
        #     'state': self.state,
        #     'res_id': self.id
        # })

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
    project_id = fields.Many2one('project.project', _("Project"), related='property_id.project_id')
    # terms_and_conditions = fields.Text(string="Terms and Conditions", required=False,related='project_id.terms_and_conditions' )
    phase_id = fields.Many2one('project.phase', _('Phase'), related='property_id.phase_id', )
    # Unit information
    property_id = fields.Many2one('product.product', _('Property'), required=False,
                                  domain="[('state','=','available')]")
    property_code = fields.Char(string="Unit Code", copy=False, related='property_id.property_code')
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
    sales_type = fields.Selection([('direct', _("Direct")), ('Broker', _("Broker")), ('freelancer', _("Freelancer")),
                                   ('recommendation', _("Recommendation"))], _('Sales Type'), default='direct')
    broker_id = fields.Many2one(comodel_name="res.partner", string="Broker", required=False,
                                domain=[('is_broker', '=', True)])
    company_broker = fields.Many2one(comodel_name="res.partner", string="Company Broker", required=False ,related='broker_id.parent_id',
                                     domain=[('is_broker', '=', True)])
    freelance = fields.Many2one('res.partner')
    recommendation = fields.Many2one('res.partner')
    # customer details
    customer_id = fields.Many2one('res.partner', string="Customer")
    customer_ids = fields.Many2many(comodel_name="res.partner", relation="res_partner_reservation", column1="par",
                                    column2="reservation", string="", )
    address = fields.Char(string="Address", related='customer_id.street')
    phone = fields.Char(string="Phone", related='customer_id.phone')
    mobile = fields.Char(string="Mobile1", related='customer_id.mobile')
    email = fields.Char(string="Email", related='customer_id.email')
    nationality = fields.Char(string="Nationality", related='customer_id.nationality')
    id_def = fields.Char(string="ID", related='customer_id.id_def')
    social_status = fields.Selection(string="Social Status", selection=[('married', 'Married'), ('single', 'Single'), ],
                                     related='customer_id.social_status', required=False, default='single')

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
    manager_tesm_2_id = fields.Many2one(comodel_name="res.partner",
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

        if values['custom_type'] == 'Reservation':
            values['reservation_code'] = self.env['ir.sequence'].next_by_code('real.estate.reservation.id.seq.finish')
            values['name'] = self.env['ir.sequence'].next_by_code('real.estate.reservation.id.seq.finish')
        elif values['custom_type'] == 'Accessories':
            values['accessories_code'] = self.env['ir.sequence'].next_by_code('real.estate.Accessories.id.seq.finish')
            values['name'] = self.env['ir.sequence'].next_by_code('real.estate.Accessories.id.seq.finish')

        values['payment_code'] = self.env['ir.sequence'].next_by_code('payment.cheque.seq')
        return super(requestReservation, self).create(values)

    def convert_to_reserved(self):
        for rec in self:
            # if rec.lead_id:
            #     rec.lead_id.real_revenue_new += self.net_price

            if rec.state in ['draft']:
                if rec.payment_strg_ids.ids == []:
                    raise ValidationError(_(
                        "Payment Strategy Empty  !!"))
                if rec.customer_id.id == False:
                    raise ValidationError(_(
                        "Customer Empty  !!"))
                if rec.sale_person_2_id.id == False:
                    raise ValidationError(_(
                        "SalesPerson Empty  !!"))
                res_res = self.env['res.reservation'].search([('property_id', '=', rec.property_id.id),
                                                              ('state', 'in', ['reserved'])])
                if len(res_res) == 0:
                    if rec.total_rem != 0 and rec.payment_type == 'manual_terms':
                        raise ValidationError(_("There is a remaining value on this unit"))
                    rec.state = 'reserved'
                    if rec.custom_type == 'Reservation':
                        rec.property_id.state = 'reserved'
                        rec.req_reservation_id.state = 'reserved'

                    # rec.onchange_method_state()

                else:
                    if rec.custom_type == 'Reservation':

                        raise ValidationError(_(
                            "Sorry .. you must Create One Reservation Form For Reservation Form for This Unit  %s!!") % self.property_id.name)
                    else:
                        rec.state = 'reserved'

    def convert_to_block(self):
        for rec in self:
            if rec.state in ['reserved', 'draft']:
                rec.state = 'blocked'
                # rec.onchange_method_state()
                rec.req_reservation_id.state = 'blocked'
                # res_res = self.env['res.reservation'].search([('property_id', '=', rec.property_id.id),
                #                                      ('state', 'in', ['reserved'])])
                # if len(res_res) != 0:
                rec.property_id.state = 'available'

    def convert_to_draft(self):
        for rec in self:
            if rec.state in ['blocked', 'reserved', 'contracted']:

                rec.state = 'draft'
                # rec.onchange_method_state()
                rec.req_reservation_id.state = 'draft'
                res_res = self.env['res.reservation'].search([('property_id', '=', rec.property_id.id),
                                                              ('state', 'in', ['reserved'])])
                if len(res_res) != 0:
                    rec.property_id.state = 'available'
        self.make_log()

    # part payment and lins
    payment_type = fields.Selection([('manual_terms', _("Manual Terms")), ('specific_terms', _("Specific Terms"))], )

    pay_strategy_id = fields.Many2one('account.payment.term', string="Payment Strategy")
    payment_strg_name = fields.Char(string="Payment Strategy", related='pay_strategy_id.name', store=True)
    payment_term_discount = fields.Float(string="Payment Term Discount",
                                         related="pay_strategy_id.payment_term_discount", store=True, digits=(16, 2))
    is_Custom_payment = fields.Boolean(string="Custom Strategy", )
    payment_strg_ids = fields.One2many('payment.strg', 'reserve_id', _('Payment'))

    Description_payment = fields.Text(string="Description Payment Strategy	", required=False, )

    discount = fields.Float(string="Discount Percentage", digits=(16, 15))
    total_discount = fields.Float('Total Discount', compute='_compute_total_discount', store=True)

    property_price = fields.Float(string="Unit Price", readonly=True, compute='calc_property_price',store=True,
                                    digits=(16, 2))
    @api.depends('property_id.sales_pricelist','property_id.sales_price')
    def calc_property_price(self):
        for r in self:
            if r.property_id.sales_pricelist > 0:
                r.property_price = r.property_id.sales_pricelist
            else:
                r.property_price = r.property_id.sales_price



    net_price = fields.Float(string="Net Price", compute='_calc_net_price', store=True, digits=(16, 2))

    payment_due = fields.Float(string="Payment Due", required=False, compute="_calc_net_price")
    payment_lines = fields.Float(string="Payment Lines", required=False, store=True)
    # EID EDITS
    payment_term_ids = fields.One2many('payment.term', 'reservation_id')

    def _compute_line_data_for_payment_change(self, line, l, cumulative_amount):
        return {
            'description': line.install_type.name,
            'payment_date': line.first_install_date + relativedelta(
                months=l) if line.first_install_date and line.period == 'monthly' else line.first_install_date + relativedelta(
                months=3 * l) if line.first_install_date and line.period == 'quarter' else line.first_install_date + relativedelta(
                months=12 * l) if line.first_install_date and line.period == 'annual' else line.first_install_date + relativedelta(
                months=6 * l) if line.first_install_date and line.period == 'semiannual' else line.first_install_date if line.first_install_date and line.period == 'once' else False,
            'amount': line.amount,
            'journal_id': line.journal_id,
            'bank_name': line.bank_name,
            'cheque': line.cheque + l,
            'install_type': line.install_type.id,
            'period': line.period,
            'state_payment': 'cheque' if line.journal_id.is_notes_receivable == True else 'bank' if line.journal_id.type == 'cash' else 'bank',
            'reserve_id': self._origin.id,
            'cumulative_amount': cumulative_amount,
            'cumulative_percentage': (
                                             cumulative_amount / self.final_unit_price) * 100 if self.final_unit_price and self.final_unit_price != 0 else 0,
            'collection_percentage': (
                                             line.amount / self.final_unit_price) * 100 if self.final_unit_price and self.final_unit_price != 0 and line.install_type.installment or line.install_type.deposite else 0,
        }

    @api.onchange('payment_term_ids')
    def onchange_question_template(self):
        print(self.id)
        payment = [(5, 0, 0)]
        cumulative_amount = 0
        for line in self.payment_term_ids:
            for l in range(line.no_install):
                if line.install_type.deposite or line.install_type.installment:
                    cumulative_amount += line.amount
                    data = self._compute_line_data_for_payment_change(line, l, cumulative_amount)
                else:
                    data = self._compute_line_data_for_payment_change(line, l, 0)
                print('data>>>>', data)
                payment.append((0, 0, data))
        print(payment)

        self.update({
            'payment_strg_ids': payment,
        })

    @api.depends('property_id.sales_price', 'amount_discount')
    def _get_final_unit_price(self):
        for rec in self:
            rec.final_unit_price = rec.property_id.sales_price - rec.amount_discount

    final_unit_price = fields.Float(string="Unit Price", required=False, compute='_get_final_unit_price', store=True)
    maintenance = fields.Float('Maintenance', compute='_calc_amdents', inverse='_inverse_amdents', store=True)
    utility_fees = fields.Float('Utility Fees', compute='_calc_amdents', inverse='_inverse_amdents', store=True)
    finishing_penalty = fields.Float('Finishing Penalty', compute='_calc_amdents', inverse='_inverse_amdents',
                                     store=True)

    @api.depends('project_id.maintenance_sel', 'project_id.maintenance_percent', 'project_id.maintenance_fixed',
                 'project_id.utility_fees_sel', 'project_id.utility_percent', 'project_id.utility_fixed',
                 'project_id.finishing_penalty_sel', 'project_id.finishing_penalty_percent',
                 'project_id.finishing_penalty_fixed', 'final_unit_price')
    def _calc_amdents(self):
        for rec in self:
            if rec.project_id.maintenance_sel == 'per':
                rec.maintenance = (rec.project_id.maintenance_percent / 100) * rec.final_unit_price
            elif rec.project_id.maintenance_sel == 'fixed':
                rec.maintenance = rec.project_id.maintenance_fixed
            else:
                rec.maintenance = 0

            if rec.project_id.utility_fees_sel == 'per':
                rec.utility_fees = (rec.project_id.utility_percent / 100) * rec.final_unit_price
            elif rec.project_id.utility_fees_sel == 'fixed':
                rec.utility_fees = rec.project_id.utility_fixed
            else:
                rec.utility_fees = 0

            if rec.project_id.finishing_penalty_sel == 'per':
                rec.finishing_penalty = (rec.project_id.finishing_penalty_percent / 100) * rec.final_unit_price
            elif rec.project_id.finishing_penalty_sel == 'fixed':
                rec.finishing_penalty = rec.project_id.finishing_penalty_fixed
            else:
                rec.finishing_penalty = 0

    def _inverse_amdents(self):
        pass

    final_unit_price_rem = fields.Float('Unit price Remaining', compute='_calc_rem', store=True)
    maintenance_rem = fields.Float('Maintenance Remaining', compute='_calc_rem', store=True)
    utility_fees_rem = fields.Float('Utility Fees Remaining', compute='_calc_rem', store=True)
    finishing_penalty_rem = fields.Float('Finishing Penalty Remaining', compute='_calc_rem', store=True)

    @api.depends('maintenance',
                 'final_unit_price',
                 'payment_term_ids.reservation_id',
                 'payment_term_ids.total_amount',
                 'payment_term_ids.install_type.maintenance',
                 'payment_term_ids.install_type.utility_fees',
                 'payment_term_ids.install_type.finishing_penalty',
                 'payment_term_ids.install_type.deposite',
                 'payment_term_ids.install_type.installment')
    def _calc_rem(self):
        for rec in self:
            finishing_penalty = 0
            unit_price = 0
            utility_fees = 0
            maintenance = 0
            for line in rec.payment_term_ids:
                maintenance += line.total_amount if line.install_type.maintenance else 0
                utility_fees += line.total_amount if line.install_type.utility_fees else 0
                finishing_penalty += line.total_amount if line.install_type.finishing_penalty else 0
                unit_price += line.total_amount if line.install_type.deposite or line.install_type.installment else 0
            rec.final_unit_price_rem = rec.final_unit_price - unit_price
            rec.maintenance_rem = rec.maintenance - maintenance
            rec.utility_fees_rem = rec.utility_fees - utility_fees
            rec.finishing_penalty_rem = rec.finishing_penalty - finishing_penalty

    total_amount = fields.Float('Total', compute='calc_total_amount', store=True)
    total_rem = fields.Float('Total Remaining', compute='calc_total_rem', store=True)
    diff = fields.Float('Total diff', compute='calc_total_diff', store=True)

    @api.depends('maintenance', 'utility_fees', 'finishing_penalty', 'final_unit_price', )
    def calc_total_amount(self):
        for rec in self:
            rec.total_amount = rec.maintenance + rec.utility_fees + rec.finishing_penalty + rec.final_unit_price

    @api.depends('maintenance_rem', 'utility_fees_rem', 'finishing_penalty_rem', 'final_unit_price_rem')
    def calc_total_rem(self):
        for rec in self:
            rec.total_rem = rec.maintenance_rem + rec.utility_fees_rem + rec.finishing_penalty_rem + \
                            rec.final_unit_price_rem

    @api.depends('total_rem', 'total_amount')
    def calc_total_diff(self):
        for rec in self:
            rec.diff = rec.total_amount - rec.total_rem

    more_discount = fields.Float(string="Discount", required=False, )
    amount_discount = fields.Float(string="Amount Discount", required=False, )
    eng_manage = fields.Boolean(default=False)
    eng_comment = fields.Html('Engineering Comment')
    extra_item = fields.Text(string="Extra Item", required=False, )

    def engineering_manage_app(self):
        self.eng_manage = True
        self.state = 'engineering_comment'
        self.approval_reservation()
        self.make_log()

    def eng_approval(self):
        self.eng_manage = False

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
            if record.req_reservation_id.id != False:
                print("enetr herer false")
                payments = self.env['account.payment'].search([('request_id', '=', record.req_reservation_id.id)])
                if payments:
                    for line in payments:
                        amount += line.amount

                    record.payment_due = amount
                else:
                    amount = 0
                    record.payment_due = 0
            else:
                amount = 0
                record.payment_due = 0
            print("record.payment_due :: %s", record.payment_due)
            if record.is_Custom_payment == False:

                first_discount = record.property_price - (
                        record.property_price * (record.payment_term_discount / 100.0))
                net_price_first = first_discount - ((
                        first_discount * (record.discount / 100.0))) - amount - record.payment_lines
                # record.amount_discount = net_price_first * (record.more_discount/100.0)
                record.net_price = net_price_first - (net_price_first * (record.more_discount / 100.0))
            else:
                total = 0
                for line in record.payment_strg_ids:
                    total += line.amount
                net_price_first = total - record.payment_lines
                # record.amount_discount = net_price_first * (record.more_discount/100.0)
                record.net_price = net_price_first - (net_price_first * (record.more_discount / 100.0))

    @api.depends('discount', 'payment_term_discount')
    def _compute_total_discount(self):
        for record in self:
            record.total_discount = record.discount + record.payment_term_discount

    date_start_installment = fields.Date(string="Start Installment", default=fields.datetime.today())

    number_day = fields.Integer(string="Number Of day", required=False, )

    @api.onchange('pay_strategy_id', 'discount', 'date_start_installment', 'number_day')
    def _onchange_pay_strategy(self):
        inbound_payments = self.env['account.payment.method'].search([('payment_type', '=', 'inbound')])
        for rec in self:
            payments = []
            cumulative_amount = 0
            for payment in rec.payment_strg_ids:
                payment.write({
                    'reserve_id': False
                })
            if rec.pay_strategy_id and rec.pay_strategy_id.id:
                for payment_line in rec.pay_strategy_id.line_ids:
                    # payment_methods = inbound_payments and payment_line.journal_id.inbound_payment_method_ids or \
                    #                   payment_line.journal_id.outbound_payment_method_ids
                    # if rec.created_date:
                    #     date_order_format = datetime.strptime(rec.created_date+ ' 01:00:00', "%Y-%m-%d %H:%M:%S")
                    # else:
                    print(
                        "datetime.date.today() :: %S", datetime.today()
                    )
                    # date_order_format = rec.date_start_installment
                    if payment_line.is_by_date:
                        date_order_format = payment_line.by_date_shift
                    else:
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
                    # if payment_line.add_extension:
                    #     print("1111")
                    #     payment_amount = round(payment_line.value_amount * rec.property_price)
                    #
                    # else:
                    print("2222")
                    payment_amount = round(payment_line.value_amount * rec.net_price)

                    # if payment_line.is_by_date:
                    #     payment_date = payment_line.by_date_shift
                    cumulative_amount += payment_amount
                    payment_arr = {
                        'amount': round(payment_amount),
                        'base_amount': round(payment_amount),
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
                        "is_maintainance": payment_line.add_extension,
                        'cumulative_amount': cumulative_amount,
                        'cumulative_percentage': (
                                                         cumulative_amount / self.final_unit_price) * 100 if self.final_unit_price and self.final_unit_price != 0 else 0,
                        'collection_percentage': (
                                                         payment_amount / self.final_unit_price) * 100 if self.final_unit_price and self.final_unit_price != 0  else 0,

                    }

                    payments.append((0, 0, payment_arr))
            rec.payment_strg_ids = payments
            # rec.compare_net_price()

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
                            'payment_method': payment.payment_method,
                            'payment_method_from': payment.payment_method_from.name,
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
        self.state = 'contracted'
        self.property_id.state = 'contracted'
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
            'move_type': 'out_invoice',
            'is_contract': True,
            'reservation_id': self.id,
            'journal_id': journal.id

        })

        print("req_id :: %s", req_id.id)
        req_id.update({
            # 'move_id': req_id.id,
            'invoice_line_ids': lines,

        })
        # view = self.env.ref('mabany_real_estate.view_contract_form')

        # return {'name': (
        #     'Contract'),
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'account.move',
        #     'res_id': req_id.id,
        #     'views': [
        #         (view.id, 'form')
        #     ],
        #     'view_id': view.id,
        #     'view_mode': 'form',
        #     'context': {'name': 'Initial Contract'},
        #
        # }

        return {'name': (
            'Contract'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': req_id.id,
            'view_id': False,
            # 'views': [
            #     (view.id, 'form'),
            # ],
            'view_mode': 'form',
            'context': {'default_name': 'Initial Contract'},
        }

    is_create_contract = fields.Boolean(string="Is Request Resveration", compute="_compute_view_button_create")
    check_field = fields.Boolean(default=False)

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
    main_total = fields.Float(string="Maintance And Insurrance", required=False, compute="_compute_amount")
    marketing_total = fields.Float(string="Utility Fees", required=False, compute="_compute_amount")
    Waste_insurance_total = fields.Float(string="Finishing Penalty", required=False, compute="_compute_amount")
    amount_residual = fields.Float(string="Amount Due", required=False, compute="_compute_amount")
    amount_paid = fields.Float(string="Amount Paid", required=False, compute="_compute_amount")

    def _compute_amount(self):
        amount = 0
        main_total = 0
        utility_fees = 0
        finishing_penalty = 0
        due = 0
        amount_discount = 0
        for rec in self:
            if rec.payment_strg_ids:
                for line in rec.payment_strg_ids:
                    if not line.install_type.maintenance and \
                            not line.is_no_enter_total and \
                            not line.install_type.utility_fees and \
                            not line.install_type.finishing_penalty:
                        amount += line.amount
                    if line.install_type.maintenance or line.is_maintainance:
                        main_total += line.amount
                    if line.install_type.utility_fees or line.markting:
                        utility_fees += line.amount
                    if line.install_type.finishing_penalty or line.Waste_insurance:
                        finishing_penalty += line.amount
                    if line.state != 'collected':
                        due += line.amount_due
                rec.amount_total = amount
                # amount_discount = rec.amount_total * (rec.more_discount /100.00)
                # rec.amount_discount = amount_discount
                rec.amount_residual = due
                rec.main_total = main_total
                rec.marketing_total = utility_fees
                rec.Waste_insurance_total = finishing_penalty
                rec.amount_paid = amount - due
            else:
                rec.amount_total = 0
                rec.amount_residual = 0
                rec.main_total = 0
                rec.marketing_total = 0
                rec.Waste_insurance_total = 0
                rec.amount_paid = 0
                # rec.amount_discount = 0

    bank_name = fields.Many2one('payment.bank', _("Bank Name"))
    # start_cheque = fields.Integer(string="Start", required=False, size=20)
    # end_cheque = fields.Integer(string="End", required=False,size=20 )
    start_cheque = fields.Char(string="Start", required=False, size=20)
    end_cheque = fields.Char(string="End", required=False, size=20)

    amount_ins = fields.Float(string="Amount Ins.", required=False, )

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
    odoo_reservation_id = fields.Many2one(comodel_name="res.reservation", string="Old Reservation", required=False, )

    counter_contract = fields.Integer(string="Counter Contract", required=False, compute="_compute_counter_contract")

    def _compute_counter_contract(self):
        for rec in self:
            contracts = self.env['account.move'].sudo().search(
                [('reservation_id', '=', rec.id), ('move_type', '=', 'out_invoice')])
            rec.counter_contract = len(contracts)

    counter_amendments = fields.Integer(string="Counter Contract", required=False, compute="_compute_counter_amen")

    def _compute_counter_amen(self):
        for rec in self:
            contracts = self.env['res.reservation'].sudo().search(
                [('related_res_id', '=', rec.id)])
            rec.counter_amendments = len(contracts)

    def action_view_contract_reservation(self):
        self.ensure_one()
        action = self.env.ref('mabany_real_estate.action_move_out_invoice_type_contract').read()[0]
        action['domain'] = [
            # ('state', 'in', ['draft','reserved']),
            ('reservation_id', '=', self.id),
            ('move_type', '=', 'out_invoice')
        ]
        print("action %s", action)
        return action

    def action_view_contract_Accessories(self):
        # self.ensure_one()
        # action = self.env.ref('mabany_real_estate.accessories_list_action').read()[0]
        # action['domain'] = [
        #     ('state', 'in', ['draft','reserved']),
        # ('related_res_id', '=', self.id),
        # ]
        # print("action %s", action)
        # return action
        return {
            'name': _('Amendments'),
            'view_mode': 'tree,form',
            'res_model': 'res.reservation',
            'type': 'ir.actions.act_window',
            'domain': [('related_res_id', '=', self.id), ('custom_type', '=', 'Accessories')],
            'target': 'current',
        }

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
                        'payment_date': datetime.now(),
                        'payment_type': 'inbound',
                        'partner_type': 'customer',
                        'partner_id': self.customer_id.id,
                        'amount': line.amount,
                        'journal_id': line.journal_id.id,
                        'payment_method_id': method.id,
                        'reservation_id': self.id,
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
                    req_id = self.env['account.payment'].create({
                        'state': 'draft',
                        'payment_date': datetime.now(),
                        'payment_type': 'inbound',
                        'partner_type': 'customer',
                        'partner_id': self.customer_id.id,
                        'amount': line.amount,
                        'journal_id': line.journal_id.id,
                        'payment_method_id': method_batch.id,
                        'reservation_id': self.id,
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
                        'reservation_id': self.id,
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

    # def button_dupliacte(self):
    # todo

    # @api.constrains("net_price", 'payment_strg_ids')
    # def compare_net_price(self):
    #     for rec in self:
    #         amount = 0
    #         if rec.payment_strg_ids:
    #             for line in rec.payment_strg_ids:
    #                 if line.markting == False and line.Waste_insurance == False and line.is_maintainance == False and line.is_no_enter_total == False:
    #                     amount += round(line.amount)
    #         print("Math.Abs(d)", math.trunc(amount))
    #         print("Math.Abs(d)", amount)
    #         print("Math.Abs(d)", math.trunc(rec.net_price))
    #         print("Math.Abs(d)", rec.net_price)
    #         # if round(amount) != round(rec.net_price):
    #         dif = amount - rec.net_price
    #         if not math.isclose(amount, rec.net_price):
    #             if dif > 100:
    #                 raise ValidationError(_("The sum of the Installment must be equal to the unit price"))


class InstallType(models.Model):
    _name = 'install.type'

    name = fields.Char()
    installment = fields.Boolean(default=False)
    deposite = fields.Boolean(default=False)
    maintenance = fields.Boolean(default=False)
    utility_fees = fields.Boolean(default=False)
    finishing_penalty = fields.Boolean(default=False)


class CancelReason(models.Model):
    _name = "cancel.reason.res"

    name = fields.Char('Reason', required=True, translate=True)
