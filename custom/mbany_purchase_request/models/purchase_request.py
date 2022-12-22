from odoo import models, fields, api,_
from odoo.exceptions import ValidationError



_STATES = [
    ("draft", "Draft"),
    ("requester", "Requester"),
    ("head_of_dep", "Head Of Department"),
    ("budget_control", "Budget Control"),
    ("finance_section_head", "Finance Section Head"),
    ("done", "Done"),
]


class PurchaseRequest(models.Model):

    _name = "purchase.request"
    _description = "Purchase Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    @api.model
    def _company_get(self):
        return self.env["res.company"].browse(self.env.company.id)


    @api.model
    def _get_default_name(self):
        return self.env["ir.sequence"].next_by_code("purchase.request")
    @api.model
    def _get_product(self):
        return self.env["product.product"].search([('payment','=',True)],limit=1)


    @api.depends("state")
    def _compute_is_editable(self):
        for rec in self:
            if rec.state in ("requester", "head_of_dep", "budget_control","finance_section_head","done"):
                rec.is_editable = False
            else:
                rec.is_editable = True


    name = fields.Char(
        string="Request Reference",
        required=True,
        default=lambda self: _("New"),
        tracking=True,
    )
    type = fields.Selection([('purchase','Purchase'),('custody','Custody')],string='Type')
    date_request = fields.Date(
        string="Request date",
        help="Date when the user initiated the request.",
        default=fields.Date.context_today,
        tracking=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        required=False,
        tracking=True,
        default = _company_get,

    )
    journal_id = fields.Many2one('account.journal','Journal')
    amount = fields.Float('Amount')

    line_ids = fields.One2many(
        comodel_name="purchase.request.line",
        inverse_name="request_id",
        string="Products to Purchase",
        readonly=False,
        copy=True,
        tracking=True,
    )
    # product_id = fields.Many2one(
    #     comodel_name="product.product",
    #     string="Product",
    #     readonly=True,
    #     default=_get_product,
    # )

    item_id = fields.Many2one(
        comodel_name="item.code",
        string="Item Code",
    )
    state = fields.Selection(
        selection=_STATES,
        string="Status",
        index=True,
        tracking=True,
        required=True,
        copy=False,
        default="draft",
    )
    is_editable = fields.Boolean(compute="_compute_is_editable", readonly=True)
    employee = fields.Many2one('hr.employee',default=lambda self: self.env.user.employee_id)
    department = fields.Many2one('hr.department',related='employee.department_id')

    def copy(self, default=None):
        default = dict(default or {})
        self.ensure_one()
        default.update({"state": "draft", "name": self._get_default_name()})
        return super(PurchaseRequest, self).copy(default)


    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self._get_default_name()
        request = super(PurchaseRequest, self).create(vals)
        return request
    def approval_request(self):
        users = self.approvals_users
        if users:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
            message_text = f'<strong>Reminder</strong> ' \
                           f'<p>This <a href=%s>PR</a> Check Approval On Purchase Request</p>' % base_url

            uid = self.env.user

            notification_ids = []
            for user in users:
                notification_ids.append((0, 0, {
                    'res_partner_id': user.partner_id.id,
                    'notification_type': 'inbox'
                }))
            self.message_post(record_name='Invoice',
                              body=message_text,
                              message_type="notification",
                              subtype_xmlid="mail.mt_comment",
                              author_id=uid.partner_id.id,
                              notification_ids=notification_ids)

    def request(self):
        self.state = 'requester'
    def head_dep(self):
        self.state = 'head_of_dep'
        self.approval_request()
    def budget_control(self):
        self.state = 'budget_control'
        self.approval_request()
    def finance_section_head(self):
        self.state = 'finance_section_head'
        self.approval_request()

    approvals_users = fields.Many2many('res.users', compute='get_approvals_users')
    attr_boolean = fields.Boolean(compute='calc_attr_boolean')
    def calc_attr_boolean(self):
        for r in self:
            if self.env.user in r.approvals_users:
                r.attr_boolean = True
            else:
                r.attr_boolean = False

    delivery_purchase_count = fields.Integer(compute='Calc_delivery_purchase_count')

    def Calc_delivery_purchase_count(self):
        for r in self:
            r.delivery_purchase_count = self.env['purchase.order'].search_count([('origin','=',r.name)])
    delivery_payment_count = fields.Integer(compute='Calc_delivery_payment_count')

    def Calc_delivery_payment_count(self):
        for r in self:
            r.delivery_payment_count = self.env['account.payment'].search_count([('ref','=',r.name)])

    def delivery_purchases_action(self):
        return {
            'name': _('Purchases'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'domain': [('origin', '=', self.name)],
            'target': 'current',

        }
    def delivery_payment_action(self):
        self.ensure_one()
        return {
            'name': 'Payments',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'domain': [('ref', '=', self.name)],
            'target': 'current',

        }

    done = fields.Boolean(default=False, compute='calc_done',copy=False)
    @api.depends('line_ids.done')
    def calc_done(self):
        for r in self:
            if all(line.done == True  for line in r.line_ids):
                r.done = True
            else:
                r.done = False
    def create_payment(self):
        payment = self.env['account.payment'].create({
            'amount': self.amount,
            'payment_type': 'outbound',
            'journal_id': self.journal_id.id,
            'date': self.date_request,
            'ref':self.name,
            'partner_type':'supplier',
            'partner_id': self.employee.address_home_id.id,
            'payment_method_line_id': self.env['account.payment.method.line'].search([('code','=','manual'),('journal_id','=',self.journal_id.id),('payment_type','=','outbound')]).id
        })
        item = self.env['account.move.line'].search([('payment_id','=',payment.id),('debit','>',0)],limit=1)
        item.item_id = self.item_id
        item.account_id = self.env['account.account'].sudo().search([('custody','=',True)],limit=1).id
        # payment.destination_account_id = self.env['account.account'].sudo().search([('custody','=',True)],limit=1).id
        payment.action_post()
        self.state = 'done'

    @api.depends('state')
    def get_approvals_users(self):
        for rec in self:
            approval_users = False
            if rec.state == 'requester':
                approval_record = self.env['res.approvals'].search([('type', '=', 'head_of_dep'),('department','=',rec.department.id)], limit=1)
                approval_users = [(6, 0, approval_record.users.ids)]
            elif rec.state == 'head_of_dep':
                approval_record = self.env['res.approvals'].search([('type', '=', 'budget_control'),('department','=',rec.department.id)], limit=1)
                approval_users = [(6, 0, approval_record.users.ids)]
            elif rec.state == 'budget_control':
                approval_record = self.env['res.approvals'].search([('type', '=', 'finance_section_head'),('department','=',rec.department.id)], limit=1)
                approval_users = [(6, 0, approval_record.users.ids)]
            rec.approvals_users = approval_users









class PurchaseRequestLine(models.Model):

    _name = "purchase.request.line"
    _description = "Purchase Request Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    product_qty = fields.Float(
        string="Quantity", tracking=True, digits="Product Unit of Measure"
    )
    request_id = fields.Many2one(
        comodel_name="purchase.request",
        string="Purchase Request",
        ondelete="cascade",
        readonly=True,
        index=True,
        auto_join=True,
    )
    item_id = fields.Many2one('item.code')
    product_id = fields.Many2one('product.product')
    unit_price = fields.Float('Unit Price')
    subtotal = fields.Float('Subtotal',compute='calc_subtotal',store=True)
    budget_palanned = fields.Float('Budget Planned',compute='calc_budget')
    consumed = fields.Float('Consumed',compute='calc_budget')
    remained = fields.Float('Remained',compute='calc_budget')
    type = fields.Selection([('reclass','Reclass'),('carry_forward','Carry Forward'),('carry_back','Carry Back')])
    check = fields.Boolean(default=False)
    done = fields.Boolean(default=False,copy=False)
    @api.depends('unit_price','product_qty')
    def calc_subtotal(self):
        for r in self:
            r.subtotal = r.unit_price * r.product_qty
    @api.constrains('consumed','budget_palanned')
    def constraint_budget(self):
        if self.consumed > self.budget_palanned:
            raise ValidationError("Must Select Consumed less Than Or Equal Budget Planned")
    @api.constrains('subtotal','remained')
    def constraint_budget(self):
        if self.subtotal > self.remained:
            raise ValidationError("Must Select Subtotal less Than Or Equal Remained")



    def calc_budget(self):
        for r in self:
            budget = self.env['crossovered.budget.lines'].search([('date_from','<=',r.request_id.date_request),('date_to','>=',r.request_id.date_request),('item_id','=',r.item_id.id)],limit=1)
            r.budget_palanned = budget.planned_amount
            acc_ids = budget.general_budget_id.account_ids.ids
            date_to = budget.date_to
            date_from = budget.date_from
            if budget.analytic_account_id.id:
                analytic_line_obj = self.env['account.analytic.line']
                domain = [('account_id', '=', budget.analytic_account_id.id),
                          ('date', '>=', date_from),
                          ('date', '<=', date_to),
                          ('item_id', '=', budget.item_id.id)
                          ]
                if acc_ids:
                    domain += [('general_account_id', 'in', acc_ids)]

                where_query = analytic_line_obj._where_calc(domain)
                analytic_line_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT SUM(amount) from " + from_clause + " where " + where_clause

            else:
                aml_obj = self.env['account.move.line']
                domain = [('account_id', 'in',
                           budget.general_budget_id.account_ids.ids),
                          ('date', '>=', date_from),
                          ('date', '<=', date_to),
                          ('move_id.state', '=', 'posted'),
                          ('item_id','=',budget.item_id.id)
                          ]
                where_query = aml_obj._where_calc(domain)
                aml_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT sum(credit)-sum(debit) from " + from_clause + " where " + where_clause

            self.env.cr.execute(select, where_clause_params)
            consumed = (self.env.cr.fetchone()[0]) or 0.0
            r.consumed = abs(consumed)
            r.remained = r.budget_palanned - r.consumed

class BudgetLine(models.Model):

    _inherit = "crossovered.budget.lines"

    item_id = fields.Many2one('item.code')

    def _compute_practical_amount(self):
        for line in self:
            acc_ids = line.general_budget_id.account_ids.ids
            date_to = line.date_to
            date_from = line.date_from
            if line.analytic_account_id.id:
                analytic_line_obj = self.env['account.analytic.line']
                domain = [('account_id', '=', line.analytic_account_id.id),
                          ('date', '>=', date_from),
                          ('date', '<=', date_to),
                          ('item_id', '=', line.item_id.id)
                          ]
                if acc_ids:
                    domain += [('general_account_id', 'in', acc_ids)]

                where_query = analytic_line_obj._where_calc(domain)
                analytic_line_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT SUM(amount) from " + from_clause + " where " + where_clause

            else:
                aml_obj = self.env['account.move.line']
                domain = [('account_id', 'in',
                           line.general_budget_id.account_ids.ids),
                          ('date', '>=', date_from),
                          ('date', '<=', date_to),
                          ('move_id.state', '=', 'posted'),
                          ('item_id','=',line.item_id.id)
                          ]
                where_query = aml_obj._where_calc(domain)
                aml_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT sum(credit)-sum(debit) from " + from_clause + " where " + where_clause

            self.env.cr.execute(select, where_clause_params)
            line.practical_amount = self.env.cr.fetchone()[0] or 0.0

    def action_open_budget_entries(self):
        if self.analytic_account_id:
            # if there is an analytic account, then the analytic items are loaded
            action = self.env['ir.actions.act_window']._for_xml_id('analytic.account_analytic_line_action_entries')
            action['domain'] = [('account_id', '=', self.analytic_account_id.id),
                                ('date', '>=', self.date_from),
                                ('date', '<=', self.date_to),
                                ('item_id', '=', self.item_id.id)

                                ]
            if self.general_budget_id:
                action['domain'] += [('general_account_id', 'in', self.general_budget_id.account_ids.ids)]
        else:
            # otherwise the journal entries booked on the accounts of the budgetary postition are opened
            action = self.env['ir.actions.act_window']._for_xml_id('account.action_account_moves_all_a')
            action['domain'] = [('account_id', 'in',
                                 self.general_budget_id.account_ids.ids),
                                ('date', '>=', self.date_from),
                                ('date', '<=', self.date_to),
                                ('item_id', '=', self.item_id.id)
                                ]
        return action











