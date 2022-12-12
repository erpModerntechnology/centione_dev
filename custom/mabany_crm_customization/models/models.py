# -*- coding: utf-8 -*-

from odoo import models, fields, api

#############################################


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
    
    
class UnitCategory(models.Model):
    _name = 'unit.category'
    _rec_name = 'name'
    _description = 'Unit Category'

    name = fields.Char(string='Name', required='True')


class UnitType(models.Model):
    _name = 'unit.type'
    _rec_name = 'name'
    _description = 'Unit Type'

    name = fields.Char(string='Name', required='True')


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    def create_visit(self):
        self.ensure_one()
        visit_id = self.env['visit.registration.card'].create({
            'lead_id': self.id,
            'partner_id': self.partner_id.id,
            'campaign_id': self.campaign_id.id,
            'channel_id': self.channel_id.id,
            'sub_channel_id': self.sub_channel_id.id,
            'source_id': self.source_id.id,
            'sub_source_id': self.sub_source_id.id,

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

    mobile_no = fields.Char(string="Mobile No.", related='partner_id.mobile')
    secondary_phone = fields.Char(string="Secondary Phone")
    international_phone = fields.Char(string="International Phone")
    country_id = fields.Many2one(comodel_name="res.country", string="Country")
    country_code = fields.Integer(string="Country Code", related='country_id.phone_code')
    religion = fields.Selection(string="Religion", selection=[('islam', 'Islam'), ('christianity', 'Christianity')])
    organization_id = fields.Many2one(comodel_name="res.organization", string="Organization Name")
    sub_channel_id = fields.Many2one(comodel_name="utm.channel", string="Sub Channel")
    channel_id = fields.Many2one(comodel_name="utm.channel", string="Channel")
    sub_channel_2_id = fields.Many2one(comodel_name="utm.channel", string="Sub Channel 2")
    channel_2_id = fields.Many2one(comodel_name="utm.channel", string="Channel 2")
    sub_source_id = fields.Many2one(comodel_name="utm.source", string="Sub Source")
    sub_source_2_id = fields.Many2one(comodel_name="utm.source", string="Sub Source 2")
    source_2_id = fields.Many2one(comodel_name="utm.source", string="Source 2")
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
                                domain="[('is_broker', '=', True)]")
    broker_agent_id = fields.Many2one(comodel_name="res.partner", string="Broker Agent Name",
                                      domain="[('is_broker', '=', True)]")
    interested_ids = fields.Many2many(comodel_name="client.interested", string="Client Interested In")
    broker_agent_phone = fields.Char(string="Broker Agent Phone Number")
    ##############################################

    call_status_id = fields.Many2one(comodel_name="call.status", string="Call Status")
    project_id = fields.Many2one(comodel_name="project.project", string="Project")
    request_stage_id = fields.Many2one(comodel_name="request.stage", string="Request Stage")
    unqualified_reason_id = fields.Many2one(comodel_name="unqualified.reason", string="Unqualified Reason")
    transferred_resale_id = fields.Many2one(comodel_name="transferred.resale", string="Transferred to Resale")
    client_request_id = fields.Many2one(comodel_name="client.request", string="Lost Client Request",
                                        domain="[('is_lost', '=', True)]")
    summery = fields.Html(string="Summery")
    next_action = fields.Char(string="Next Action")
    next_action_date = fields.Date(string="Next Action Date")

    ##########################################################################
    unit_category_id = fields.Many2one(comodel_name="unit.category", string="Unit Category")
    unit_type_id = fields.Many2one(comodel_name="unit.type", string="Unit Type")
    price_range = fields.Char(string="Price Range")
    preferred_city = fields.Char(string="Preferred City")
    payment_notes = fields.Html(string="Payment Notes")
    sqm_area = fields.Char(string="Area In SQM")
    unit_view = fields.Char(string="Unit View")
    preferred_district = fields.Char(string="Preferred District")
    payment_method = fields.Char(string="Payment Method")
    reservation_date = fields.Date(string="Reservation Date")
    #########################################################################
    client_request_name = fields.Char(string="Client Request Name")
    original_user = fields.Char(string="Original User")
    original_date = fields.Date(string="Client Request Original Creating Date")
    description_details = fields.Html(string="Description")
