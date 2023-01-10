# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import re

#############################################


class Users(models.Model):
    _inherit = 'res.users'

    is_salesperson = fields.Boolean(string="Salesperson")


class PhoneMixin(models.AbstractModel):
    _inherit = 'mail.thread.phone'

    def _search_phone_mobile_search(self, operator, value):
        value = value.strip()
        if len(value) < 3:
            raise UserError(_('Please enter at least 3 characters when searching a Phone/Mobile number.'))

        pattern = r'[\s\\./\(\)\-]'
        if value.startswith('+') or value.startswith('00'):
            # searching on +32485112233 should also finds 0032485112233 (and vice versa)
            # we therefore remove it from input value and search for both of them in db
            query = f"""
                SELECT model.id
                FROM {self._table} model
                WHERE
                    model.phone IS NOT NULL AND (
                        REGEXP_REPLACE(model.phone, %s, '', 'g') ILIKE %s OR
                        REGEXP_REPLACE(model.phone, %s, '', 'g') ILIKE %s
                    ) OR
                    model.mobile IS NOT NULL AND (
                        REGEXP_REPLACE(model.mobile, %s, '', 'g') ILIKE %s OR
                        REGEXP_REPLACE(model.mobile, %s, '', 'g') ILIKE %s
                    )OR
                    model.secondary_phone IS NOT NULL AND (
                        REGEXP_REPLACE(model.secondary_phone, %s, '', 'g') ILIKE %s OR
                        REGEXP_REPLACE(model.secondary_phone, %s, '', 'g') ILIKE %s
                    )OR
                    model.international_phone IS NOT NULL AND (
                        REGEXP_REPLACE(model.international_phone, %s, '', 'g') ILIKE %s OR
                        REGEXP_REPLACE(model.international_phone, %s, '', 'g') ILIKE %s
                    );
            """
            term = re.sub(pattern, '', value[1 if value.startswith('+') else 2:]) + '%'
            self._cr.execute(query, (
                pattern, '00' + term,
                pattern, '+' + term,
                pattern, '00' + term,
                pattern, '+' + term,
                pattern, '00' + term,
                pattern, '+' + term,
                pattern, '00' + term,
                pattern, '+' + term
            ))
        else:
            query = f"""
                SELECT model.id
                FROM {self._table} model
                WHERE
                    REGEXP_REPLACE(model.phone, %s, '', 'g') ILIKE %s OR
                    REGEXP_REPLACE(model.mobile, %s, '', 'g') ILIKE %s OR
                    REGEXP_REPLACE(model.secondary_phone, %s, '', 'g') ILIKE %s OR
                    REGEXP_REPLACE(model.international_phone, %s, '', 'g') ILIKE %s;
            """
            term = '%' + re.sub(pattern, '', value) + '%'
            self._cr.execute(query, (
                pattern, term,
                pattern, term,
                pattern, term,
                pattern, term
            ))
        res = self._cr.fetchall()
        if not res:
            return [(0, '=', 1)]
        return [('id', 'in', [r[0] for r in res])]


class CommissionType(models.Model):
    _name = 'commission.type'
    _rec_name = 'name'
    _description = 'Commission Type'

    name = fields.Char(string='Name', required=True)


class ReassignedReason(models.Model):
    _name = 'reassigned.reason'
    _rec_name = 'name'
    _description = 'Reassigned Reason'

    name = fields.Char(string='Name', required=True)


class PreferredDistrict(models.Model):
    _name = 'preferred.district'
    _rec_name = 'name'
    _description = 'Preferred district'

    name = fields.Char(required=True)
    city_id = fields.Many2one(comodel_name="res.country.state", string="City", required=True)


class UnitView(models.Model):
    _name = 'unit.view'
    _rec_name = 'name'
    _description = 'Unit View'

    name = fields.Char(required=True)


class SupportCall(models.Model):
    _name = 'support.call'
    _rec_name = 'name'
    _description = 'Support Call'

    name = fields.Char(string='Name', required=True)


class SupportReservation(models.Model):
    _name = 'support.reservation'
    _rec_name = 'name'
    _description = 'Support Reservation'

    name = fields.Char(string='Name', required=True)


class SupportVisit(models.Model):
    _name = 'support.visit'
    _rec_name = 'name'
    _description = 'Support Visit'

    name = fields.Char(string='Name', required=True)


class SupportContract(models.Model):
    _name = 'support.contract'
    _rec_name = 'name'
    _description = 'Support Contract'

    name = fields.Char(string='Name', required=True)


class ClientRequest(models.Model):
    _name = 'client.request'
    _rec_name = 'name'
    _description = 'Client Request'

    name = fields.Char(string='Name', required=True)
    is_lost = fields.Boolean(string="Lost")


class ClientRequestType(models.Model):
    _name = 'client.request.type'
    _rec_name = 'name'
    _description = 'Client Request Type'

    name = fields.Char(string='Name', required=True)


class ClientInterested(models.Model):
    _name = 'client.interested'
    _rec_name = 'name'
    _description = 'Client Interested'

    name = fields.Char(string='Name', required=True)


class CallStatus(models.Model):
    _name = 'call.status'
    _rec_name = 'name'
    _description = 'Call Status'

    name = fields.Char(string='Name', required=True)


class RequestStage(models.Model):
    _name = 'request.stage'
    _rec_name = 'name'
    _description = 'Request Stage'

    name = fields.Char(string='Name', required=True)


############################################

class BrokerStatus(models.Model):
    _name = 'broker.status'
    _rec_name = 'name'
    _description = 'Broker Status'

    name = fields.Char(string='Name')


class BrokerType(models.Model):
    _name = 'broker.type'
    _rec_name = 'name'
    _description = 'Broker Type'

    name = fields.Char(string='Name')


class BrokerCategory(models.Model):
    _name = 'broker.category'
    _rec_name = 'name'
    _description = 'Broker Category'

    name = fields.Char(string='Name')


class Partner(models.Model):
    _inherit = 'res.partner'

    is_broker = fields.Boolean(string="Is Broker ?")
    commission_rate = fields.Float(string="Commission Rate %")
    broker_status_id = fields.Many2one(comodel_name="broker.status", string="Broker Status")
    broker_type_id = fields.Many2one(comodel_name="broker.type", string="Broker Type")
    broker_category_id = fields.Many2one(comodel_name="broker.category", string="Category of Broker")
    contract_period = fields.Char(string="Contract Period")
    experience_year = fields.Char(string="Year of Experience")
    contract_date = fields.Date(string="Contract Date")
    secondary_phone = fields.Char(string="Secondary Phone")
    international_phone = fields.Char(string="International Phone")

    def get_broker_leads(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Opportunities',
            'view_mode': 'tree,form',
            'res_model': 'crm.lead',
            'domain': ['|', ('broker_id', '=', self.id), ('broker_agent_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def get_broker_opportunities_count(self):
        for record in self:
            record.broker_opportunities_count = self.env['crm.lead'].search_count(
                ['|', ('broker_id', '=', self.id), ('broker_agent_id', '=', self.id)])

    broker_opportunities_count = fields.Integer(compute='get_broker_opportunities_count')

    @api.constrains('secondary_phone', 'international_phone')
    def mobile_phone_constrains(self):
        for rec in self:
            if rec.secondary_phone:
                if len(rec.secondary_phone) < 11:
                    raise ValidationError(_('Secondary Number must be not less 11 digits'))
            if rec.international_phone:
                if len(rec.international_phone) < 11:
                    raise ValidationError(_('International Number must be not less 11 digits'))


class OutdoorLocation(models.Model):
    _name = 'outdoor.location'
    _rec_name = 'name'
    _description = 'Outdoor Location'

    name = fields.Char(string='Name', required=True)


class Channel(models.Model):
    _name = 'utm.channel'
    _inherit = 'utm.source'


class Organization(models.Model):
    _name = 'res.organization'
    _rec_name = 'name'
    _description = 'Organization'

    name = fields.Char(string='Name', required='True')


class UnqualifiedReason(models.Model):
    _name = 'unqualified.reason'
    _rec_name = 'name'
    _description = 'Unqualified Reason'

    name = fields.Char(string='Name', required='True')


class TransferredResale(models.Model):
    _name = 'transferred.resale'
    _rec_name = 'name'
    _description = 'Transferred Resale'

    name = fields.Char(string='Name', required='True')
    

class UnitType(models.Model):
    _name = 'unit.type'
    _rec_name = 'name'
    _description = 'Unit Type'

    name = fields.Char(string='Name', required='True')


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    user_id = fields.Many2one(
        'res.users', string='Salesperson', default=lambda self: self.env.user,
        domain="['&', ('share', '=', False), ('company_ids', 'in', user_company_ids), ('is_salesperson', '=', True)]",
        check_company=True, index=True, tracking=True)

    def create_visit(self):
        self.ensure_one()
        visit_id = self.env['visit.registration.card'].create({
            'lead_id': self.id,
            'partner_id': self.partner_id.id,
            'campaign_id': self.campaign_id.id,
            'channel_ids': self.channel_ids.ids,
            'sub_channel_ids': self.sub_channel_ids.ids,
            'source_ids': self.source_ids.ids,
            'sub_source_ids': self.sub_source_ids.ids,

        })

        return {'name': 'Visit',
                'type': 'ir.actions.act_window',
                'res_model': 'visit.registration.card',
                'res_id': visit_id.id,
                'view_type': 'form',
                'view_mode': 'form',
                }

    def get_visits(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Visits',
            'view_mode': 'tree,form',
            'res_model': 'visit.registration.card',
            'domain': [('lead_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def compute_visits_count(self):
        for record in self:
            record.visits_count = self.env['visit.registration.card'].search_count(
                [('lead_id', '=', self.id)])

    visits_count = fields.Integer(compute='compute_visits_count')
    is_duplicated = fields.Boolean(string="Is duplicated?", store=True, default=False)
    function = fields.Char(string="Job Position", related='partner_id.function')
    mobile_no = fields.Char(string="Mobile No.", related='partner_id.mobile')
    secondary_phone = fields.Char(string="Secondary Phone",
                                  compute='_compute_secondary_phone', inverse='_inverse_secondary_phone',
                                  readonly=False,
                                  store=True)
    international_phone = fields.Char(string="International Phone",
                                      compute='_compute_international_phone', inverse='_inverse_international_phone',
                                      readonly=False, store=True)

    @api.depends('partner_id.secondary_phone')
    def _compute_secondary_phone(self):
        for lead in self:
            if lead.partner_id.secondary_phone:
                lead.secondary_phone = lead.partner_id.secondary_phone

    def _inverse_secondary_phone(self):
        for lead in self:
            lead.partner_id.secondary_phone = lead.secondary_phone

    @api.depends('partner_id.international_phone')
    def _compute_international_phone(self):
        for lead in self:
            if lead.partner_id.international_phone:
                lead.international_phone = lead.partner_id.international_phone

    def _inverse_international_phone(self):
        for lead in self:
            lead.partner_id.international_phone = lead.international_phone

    @api.constrains('phone', 'secondary_phone', 'international_phone')
    def mobile_phone_constrains(self):
        for rec in self:
            leads = self.env['crm.lead'].search([('id', '!=', rec.id)])
            if rec.phone:
                if len(rec.phone) < 11:
                    raise ValidationError(_('Primary Number must be not less 11 digits'))
                similar_leads = leads.search(['|', '|', ('phone', '=', rec.phone), ('secondary_phone', '=', rec.phone),
                                              ('international_phone', '=', rec.phone)])
                if similar_leads:
                    rec.is_duplicated = True
                    for lead in similar_leads:
                        lead.update({
                            'is_duplicated': True
                        })
            if rec.secondary_phone:
                if len(rec.secondary_phone) < 11:
                    raise ValidationError(_('Secondary Number must be not less 11 digits'))
                similar_leads = leads.search(['|', '|', ('phone', '=', rec.secondary_phone),
                                              ('secondary_phone', '=', rec.secondary_phone),
                                              ('international_phone', '=', rec.secondary_phone)])
                if similar_leads:
                    rec.is_duplicated = True
                    for lead in similar_leads:
                        lead.update({
                            'is_duplicated': True
                        })
            if rec.international_phone:
                if len(rec.international_phone) < 11:
                    raise ValidationError(_('International Number must be not less 11 digits'))
                similar_leads = leads.search(['|', '|', ('phone', '=', rec.international_phone),
                                              ('secondary_phone', '=', rec.international_phone),
                                              ('international_phone', '=', rec.international_phone)])
                if similar_leads:
                    rec.is_duplicated = True
                    for lead in similar_leads:
                        lead.update({
                            'is_duplicated': True
                        })

    country_id = fields.Many2one(comodel_name="res.country", string="Country")
    country_code = fields.Integer(string="Country Code", related='country_id.phone_code')
    religion = fields.Selection(string="Religion", selection=[('islam', 'Islam'), ('christianity', 'Christianity')])
    organization_id = fields.Many2one(comodel_name="res.organization", string="Organization Name")
    sub_channel_ids = fields.Many2many(comodel_name="utm.channel", relation="sub_channel_lead", string="Sub Channels")
    channel_ids = fields.Many2many(comodel_name="utm.channel", relation="channel_lead", string="Channels")
    # sub_channel_2_id = fields.Many2one(comodel_name="utm.channel", string="Sub Channel 2")
    # channel_2_id = fields.Many2one(comodel_name="utm.channel", string="Channel 2")
    sub_source_ids = fields.Many2many(comodel_name="utm.source", relation="sub_source_lead", string="Sub Sources")
    source_ids = fields.Many2many(comodel_name="utm.source", relation="source_lead", string="Sources")
    # sub_source_2_id = fields.Many2one(comodel_name="utm.source", string="Sub Source 2")
    # source_2_id = fields.Many2one(comodel_name="utm.source", string="Source 2")
    rejection_source = fields.Char(string="Rejection Source")
    rejection_reason = fields.Char(string="Rejection Reason")
    outdoor_location_id = fields.Many2one(comodel_name="outdoor.location", string="Outdoor Location")
    ###############################################
    commission_type_id = fields.Many2one(comodel_name="commission.type", string="Commission Type")
    reassigned_reason_id = fields.Many2one(comodel_name="reassigned.reason", string="Reassigned Reason")
    support_call_id = fields.Many2one(comodel_name="support.call", string="Support Call")
    support_reservation_id = fields.Many2one(comodel_name="support.reservation", string="Support Reservation")
    support_visit_site_id = fields.Many2one(comodel_name="support.visit", string="Support Visit (Site)")
    support_contract_id = fields.Many2one(comodel_name="support.contract", string="Support Contract")
    client_request_type_id = fields.Many2one(comodel_name="client.request.type", string="Client Request Contact Type")

    support_visit_office_id = fields.Many2one(comodel_name="support.visit", string="Support Visit (Office)")
    broker_id = fields.Many2one(comodel_name="res.partner", string="Broker",
                                domain="[('is_broker', '=', True), ('is_company', '=', True)]")
    broker_agent_id = fields.Many2one(comodel_name="res.partner", string="Broker Agent Name",
                                      domain="[('is_broker', '=', True), ('is_company', '=', False)]")
    interested_ids = fields.Many2many(comodel_name="client.interested", string="Client Interested In")
    is_created = fields.Boolean(default=False)

    def check_has_update_group(self):
        if self.env.user.has_group('mabany_crm_customization.edit_lead_group'):
            self.has_update_group = True
            print('update group')
        else:
            self.has_update_group = False
            print('no update group')

    has_update_group = fields.Boolean(compute='check_has_update_group')

    @api.model
    def create(self, vals):
        res = super(CRMLead, self).create(vals)
        res.update({
            'is_created': True
        })
        return res

    @api.depends('broker_agent_id.mobile')
    def _compute_broker_phone(self):
        for lead in self:
            if lead.broker_agent_id.mobile:
                lead.broker_agent_phone = lead.broker_agent_id.mobile

    def _inverse_broker_phone(self):
        for lead in self:
            lead.broker_agent_id.mobile = lead.broker_agent_phone

    broker_agent_phone = fields.Char(string="Broker Agent Phone Number", compute='_compute_broker_phone',
                                     inverse='_inverse_broker_phone')
    ##############################################

    call_status_id = fields.Many2one(comodel_name="call.status", string="Call Status")
    project_id = fields.Many2one(comodel_name="project.project", string="Project")
    request_stage_id = fields.Many2one(comodel_name="request.stage", string="Request Stage")
    unqualified_reason_id = fields.Many2one(comodel_name="unqualified.reason", string="Unqualified Reason")
    transferred_resale_id = fields.Many2one(comodel_name="transferred.resale", string="Transfer/Primary")
    client_request_id = fields.Many2one(comodel_name="client.request", string="Lost Client Request",
                                        domain="[('is_lost', '=', True)]")
    summery = fields.Html(string="Summery")
    next_action = fields.Char(string="Next Action")
    next_action_date = fields.Date(string="Next Action Date")

    ##########################################################################
    unit_category_id = fields.Many2one(comodel_name="product.category", string="Unit Category")
    unit_type_id = fields.Many2one(comodel_name="unit.type", string="Unit Type")
    price_range = fields.Char(string="Price Range")
    preferred_city_id = fields.Many2one('res.country.state', string="Preferred City")
    payment_notes = fields.Html(string="Payment Notes")
    sqm_area = fields.Char(string="Area In SQM")
    unit_view_id = fields.Many2one('unit.view', string="Unit View")
    preferred_district_id = fields.Many2one('preferred.district', string="Preferred District",
                                            domain="[('city_id', '=', preferred_city_id)]")
    payment_method = fields.Char(string="Payment Method")
    reservation_date = fields.Date(string="Reservation Date")
    #########################################################################
    client_request_name = fields.Char(string="Client Request Name")
    original_user = fields.Char(string="Original User")
    original_date = fields.Date(string="Client Request Original Creating Date")
    description_details = fields.Html(string="Description")
