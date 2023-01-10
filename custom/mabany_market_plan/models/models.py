from odoo import models, fields, api


class VisitRegistrationCard(models.Model):
    _inherit = 'visit.registration.card'

    market_plan_id = fields.Many2one(comodel_name="market.plan", string="Campaign Source")


class CRMStage(models.Model):
    _inherit = 'crm.stage'

    is_unqualified = fields.Boolean(string="Unqualified")


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    market_plan_id = fields.Many2one(comodel_name="market.plan", string="Campaign",
                                     tracking=True, domain=[('state', '=', 'active')])


class OnlineChannel(models.Model):
    _name = 'online.channel'
    _rec_name = 'online_channel'

    online_channel = fields.Char(string="Online Channel")


class MarketPlanning(models.Model):
    _name = 'market.plan'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    state = fields.Selection(selection=[
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('complete', 'Complete'),
    ], string='Status', required=True, readonly=True, copy=False,
        tracking=True, default='planning')
    name = fields.Char(string="", required=False, )
    platform_id = fields.Many2one(comodel_name="platform.plan", string="Platform", required=False, )
    category_id = fields.Many2one(comodel_name="category.plan", string="Category", required=False, )
    type_id = fields.Many2one(comodel_name="type.plan", string="Type", required=False, )
    target_id = fields.Many2one(comodel_name="target.plan", string="Target", required=False, )
    ads_name = fields.Text(string="Ads Name", required=False, )
    ads_link = fields.Char(string="Ads Link", required=False, )
    ads_marketing_cost = fields.Float(string="Ads Marketing Cost", required=False, )
    # lead_cost = fields.Float(string="Lead Cost", required=False, compute="_compute_lead_cost")
    planned_leads = fields.Float(string="Planned Leads", required=False, )
    unqualified_leads = fields.Float(string="Unqualified Leads", required=False, compute='_compute_unqualified_leads')
    won_leads = fields.Float(string="Won Leads", required=False, compute='_compute_won_leads')
    # visit_leads = fields.Float(string="visit Leads", required=False, compute='_compute_visit_leads')
    total_leads = fields.Float(string="Total Leads", required=False, compute='_compute_total_leads')
    start_palnned_date = fields.Date(string="Start Planned Date", required=False, )
    end_palnned_date = fields.Date(string="End Planned Date", required=False, )
    start_actual_date = fields.Date(string="Start Actual Date", required=False, )
    end_actual_date = fields.Date(string="End Actual Date", required=False, )
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    owner_id = fields.Char(string="Owner", required=False,)
    project_id = fields.Many2one(comodel_name="project.project", string="Project", required=False, )
    # lead_type_id = fields.Many2one(comodel_name="lead.type.plan", string="Lead Type", required=False, )
    cust_sales_type = fields.Selection([
        ('direct', 'Direct'),
        ('indirect', 'Indirect'),
    ], string="Sales Type", default='direct')
    channel_type = fields.Selection([
        ('online_channel', ' Online Channel'),
        ('offline_channel', 'Offline Channel'),
    ], string="Source", default='online_channel')
    online_channel = fields.Many2one('online.channel', string='Online Sub Source')

    def activate_plan(self):
        for rec in self:
            rec.state = 'active'

    def complete_plan(self):
        for rec in self:
            rec.state = 'complete'

    def _compute_unqualified_leads(self):
        for rec in self:
            leads = self.env['crm.lead'].search([('market_plan_id', '=', rec.id)])
            total_meeting = 0
            for lead in leads:
                if lead.stage_id.is_unqualified:
                    total_meeting += 1

            rec.unqualified_leads = total_meeting

    def _compute_won_leads(self):
        for rec in self:
            leads = self.env['crm.lead'].search([('market_plan_id', '=', rec.id)])
            total_meeting = 0
            for lead in leads:
                if lead.stage_id.is_won:
                    total_meeting += 1

            rec.won_leads = total_meeting

    # def _compute_visit_leads(self):
    #     for rec in self:
    #         leads = self.env['crm.lead'].search([('market_plan_id', '=', rec.id)])
    #         total_meeting = 0
    #         for lead in leads:
    #             if lead.is_visit:
    #                 total_meeting += 1
    #
    #         rec.visit_leads = total_meeting

    def _compute_total_leads(self):
        for rec in self:
            leads = self.env['crm.lead'].search([])
            total_meeting = 0
            for r in self:
                for lead in leads:
                    if r.name == lead.market_plan_id.name:
                        total_meeting += 1

            rec.total_leads = total_meeting

    # def _compute_lead_cost(self):
    #     for rec in self:
    #         if rec.actual_lead_count > 0:
    #             rec.lead_cost = rec.ads_marketing_cost / rec.actual_lead_count
    #         else:
    #             rec.lead_cost = 0.0

    def action_unqualified_lead_view(self):

        self.ensure_one()
        action = self.env.ref('crm.crm_lead_action_pipeline').read()[0]
        # leads = self.env['crm.lead'].search([])
        # for lead in leads:
        action['domain'] = [
            # ('state', 'in', ['posted', 'paid']),
            ('market_plan_id', '=', self.id),
            ('type', '=', 'opportunity'),
            ('stage_id.is_unqualified', '=', True),
            # ('is_actual', '=', True),
            # ('stage_id.name', '=', 'Follow Up'),
            # (lead.stage_id.name, '=', 'Follow Up'),
        ]
        return action

    def action_won_lead_view(self):
        self.ensure_one()
        action = self.env.ref('crm.crm_lead_action_pipeline').read()[0]
        # leads = self.env['crm.lead'].search([])
        # for lead in leads:
        action['domain'] = [
            # ('state', 'in', ['posted', 'paid']),
            ('market_plan_id', '=', self.id),
            ('type', '=', 'opportunity'),
            # ('is_won', '=', True),
            ('stage_id.name', '=', 'Won'),
            # (lead.stage_id.is_won, '=', True),
        ]
        return action

    # def action_visit_lead_view(self):
    #     self.ensure_one()
    #     action = self.env.ref('crm.crm_lead_action_pipeline').read()[0]
    #     action['domain'] = [
    #         # ('state', 'in', ['posted', 'paid']),
    #         ('market_plan_id', '=', self.id),
    #         ('type', '=', 'opportunity'),
    #         ('is_visit', '=', True),
    #     ]
    #     return action

    def action_total_leads_view(self):
        self.ensure_one()
        action = self.env.ref('crm.crm_lead_action_pipeline').read()[0]
        action['domain'] = [
            # ('state', 'in', ['posted', 'paid']),
            ('market_plan_id', '=', self.id),
            # ('type', '=', 'opportunity'),
            # ('stage_id.name', '=', ['|', 'Won', 'Follow Up']),
            # ('stage_id.name', '=', 'Won'),
        ]
        return action

    # actual_lead_count = fields.Integer('# Actual Lead', compute='_compute_actual_lead_count')
    # visit_lead_count = fields.Integer('# Visit', compute='_compute_actual_lead_count')

    # def _compute_actual_lead_count(self):
    #
    #     for rec in self:
    #         leads = self.env['crm.lead'].search([('market_plan_id', '=', rec.id), ('type', '=', 'opportunity')])
    #         total_meeting = 0
    #         rec.actual_lead_count = len(leads)
    #         for lead in leads:
    #             if lead.is_visit:
    #                 total_meeting += 1
    #
    #         rec.visit_lead_count = total_meeting

    date = fields.Date(string='date', default=fields.Date.context_today, required=True)


class PlatformModel(models.Model):
    _name = 'platform.plan'

    name = fields.Char(string=" Name ", required=True, )


class CategoryModel(models.Model):
    _name = 'category.plan'

    name = fields.Char(string=" Name ", required=True, )


class TypeModel(models.Model):
    _name = 'type.plan'

    name = fields.Char(string=" Name ", required=True, )


class TargetModel(models.Model):
    _name = 'target.plan'

    name = fields.Char(string=" Name ", required=True, )
