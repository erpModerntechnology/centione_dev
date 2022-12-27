# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class projectPoject(models.Model):
    _inherit = 'project.project'

    city_id = fields.Many2one(comodel_name="res.country.state", string="City", required=False, )
    condition_terms = fields.Text(string="شروط الحجز", required=False, )
    zone = fields.Char(string="منطقه", )
    number_zone = fields.Char(string="رقم قطعه الارض", required=False, )
    condition_terms_broker = fields.Text(string="شروط الحجز (Broker)", required=False, )
    property_account_income_id = fields.Many2one('account.account', company_dependent=True,
        string="Income Account",
        domain="['&', ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
        help="Keep this field empty to use the default value from the product category.")


    units_count = fields.Integer(compute='_compute_units_count', string="Units Count")
    label_units = fields.Char(string='Units', default='Units')

    units_draft_count = fields.Integer(compute='_compute_units_count', string="Units Draft Count")
    label_draft = fields.Char(string='Draft Units ', default='Draft Units ')

    units_request_count = fields.Integer(compute='_compute_units_count', string="Units Request Count")
    label_request = fields.Char(string='Request Units ', default='Request Units ')

    units_approve_count = fields.Integer(compute='_compute_units_count', string="Units Approve Count")
    label_approve = fields.Char(string='Approve Units ', default='Approve Units ')

    units_available_count = fields.Integer(compute='_compute_units_count', string="Units available Count")
    label_available = fields.Char(string='Available Units ', default='Available Units ')

    units_reserved_count = fields.Integer(compute='_compute_units_count', string="Units Reserved Count")
    label_reserved = fields.Char(string='Reserved Units ', default='Reserved Units ')

    units_contracted_count = fields.Integer(compute='_compute_units_count', string="Units Contracted Count")
    label_contracted = fields.Char(string='Contracted Units ', default='Contracted Units ')

    units_blocked_count = fields.Integer(compute='_compute_units_count', string="Units Blocked Count")
    label_blocked = fields.Char(string='Hold Units ', default='Hold Units ')

    units_exception_count = fields.Integer(compute='_compute_units_count', string="Units Exception Count")
    label_exception = fields.Char(string='Exception Units ', default='Exception Units ')

    #####################################################################################
    def _get_project_insights(self):
        for rec in self:
            reservations = self.env['res.reservation'].search([('custom_type', '=', 'Reservation'),
                                                               ('project_id', '=', rec.id),
                                                               ('state', '=', 'reserved')])
            rec.reservation_count = sum(reservations.mapped('amount_total'))

            contracted = self.env['res.reservation'].search([('custom_type', '=', 'Reservation'),
                                                             ('project_id', '=', rec.id),
                                                             ('state', '=', 'contracted')])
            rec.contracted_count = sum(contracted.mapped('amount_total'))

            project_reservations = self.env['res.reservation'].search([('custom_type', '=', 'Reservation'),
                                                                       ('project_id', '=', rec.id)])

            rec.project_amount_due = sum(project_reservations.mapped('amount_residual'))
            rec.project_actual_paid = sum(project_reservations.mapped('amount_paid'))
            rec.project_customers = len(set(project_reservations.mapped('customer_id')))

    def action_view_project_customers(self):
        if self:
            project_reservations = self.env['res.reservation'].search([('custom_type', '=', 'Reservation'),
                                                                       ('project_id', '=', self.id)])
            project_customer_ids = list(set(project_reservations.mapped('customer_id').mapped('id')))
            return {
                'name': 'Project Customers',
                'res_model': 'res.partner',
                'view_mode': 'tree,form',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'domain': [('id', 'in', project_customer_ids)],
            }

    reservation_count = fields.Float(compute='_get_project_insights')
    label_reservation = fields.Char(string='Reservations', default='Reservations')

    contracted_count = fields.Float(compute='_get_project_insights')
    label_reservation_contracted = fields.Char(string='Contracted', default='Contracted')

    project_amount_due = fields.Float(compute='_get_project_insights')
    label_project_amount_due = fields.Char(string='Amount Due', default='Amount Due')

    project_actual_paid = fields.Float(compute='_get_project_insights')
    label_project_actual_paid = fields.Char(string='Actual Paid', default='Actual Paid')

    project_customers = fields.Integer(compute='_get_project_insights')
    label_project_customers = fields.Char(string='Customers', default='Customers')

    # EID NEW Fields
    maintenance_sel = fields.Selection([('per', 'Percentage'), ('fixed', 'Fixed')], 'Maintenance & Insurance Type')
    maintenance_fixed = fields.Float('Maintenance & Insurance')
    maintenance_percent = fields.Float('Maintenance & Insurance %')

    utility_fees_sel = fields.Selection([('per', 'Percentage'), ('fixed', 'Fixed')], 'Utility Fees Type')
    utility_fixed = fields.Float('Utility Fees')
    utility_percent = fields.Float('Utility Fees %')

    finishing_penalty_sel = fields.Selection([('per', 'Percentage'), ('fixed', 'Fixed')],
                                             'Finishing Penalty Type')
    finishing_penalty_fixed = fields.Float('Finishing Penalty')
    finishing_penalty_percent = fields.Float('Finishing Penalty %')

    def _compute_units_count(self):
        for rec in self:
            units_count = self.env['product.product'].search(
                [('project_id', '=', rec.id)])
            units_draft_count = self.env['product.product'].search(
                [('project_id', '=', rec.id), ('state', '=', 'draft')])
            units_request_count = self.env['product.product'].search(
                [('project_id', '=', rec.id), ('state', '=', 'request_available')])
            units_approve_count = self.env['product.product'].search(
                [('project_id', '=', rec.id), ('state', '=', 'approve')])
            units_available_count = self.env['product.product'].search(
                [('project_id', '=', rec.id),('state', '=', 'available')])
            units_reserved_count = self.env['product.product'].search(
                [('project_id', '=', rec.id), ('state', '=', 'reserved')])
            units_contracted_count = self.env['product.product'].search(
                [('project_id', '=', rec.id), ('state', '=', 'contracted')])
            units_blocked_count = self.env['product.product'].search(
                [('project_id', '=', rec.id), ('state', '=', 'blocked')])
            units_exception_count = self.env['product.product'].search(
                [('project_id', '=', rec.id), ('state', '=', 'exception')])
            rec.units_count = len(units_count)
            rec.units_available_count = len(units_available_count)
            rec.units_reserved_count = len(units_reserved_count)
            rec.units_contracted_count = len(units_contracted_count)
            rec.units_blocked_count = len(units_blocked_count)
            rec.units_draft_count = len(units_draft_count)
            rec.units_request_count = len(units_request_count)
            rec.units_approve_count = len(units_approve_count)
            rec.units_exception_count = len(units_exception_count)

    def action_view_units(self):
        self.ensure_one()
        action = self.env.ref('resan_real_estate.act_project_units_all').read()[0]
        print("action %s",action)
        return action
    def action_view_units_draft(self):
        self.ensure_one()
        action = self.env.ref('resan_real_estate.act_project_units_draft').read()[0]
        return action
    def action_view_units_request(self):
        self.ensure_one()
        action = self.env.ref('resan_real_estate.act_project_units_request_available').read()[0]
        return action
    def action_view_units_approve(self):
        self.ensure_one()
        action = self.env.ref('resan_real_estate.act_project_units_approve').read()[0]
        return action
    def action_view_units_available(self):
        self.ensure_one()
        action = self.env.ref('resan_real_estate.act_project_units_available').read()[0]
        return action
    def action_view_units_reserved(self):
        self.ensure_one()
        action = self.env.ref('resan_real_estate.act_project_units_reserved').read()[0]
        return action
    def action_view_units_contracted(self):
        self.ensure_one()
        action = self.env.ref('resan_real_estate.act_project_units_contracted').read()[0]
        return action
    def action_view_units_blocked(self):
        self.ensure_one()
        action = self.env.ref('resan_real_estate.act_project_units_blocked').read()[0]
        return action
    def action_view_units_exception(self):
        self.ensure_one()
        action = self.env.ref('resan_real_estate.act_project_units_exception').read()[0]
        return action


class ProjectPhase(models.Model):
    _name = 'project.phase'

    name = fields.Char('Name',required=True)
    project_id = fields.Many2one('project.project', _('Project'),required=True)
