from odoo import models, fields, api, _


class ClientSource(models.Model):
    _name = 'client.source'
    _rec_name = 'name'
    _description = 'Client Source'

    name = fields.Char(string='Name', required='True')


class VisitRegistrationCard(models.Model):
    _name = 'visit.registration.card'
    _rec_name = 'sequence'
    _description = 'Visit Registration Card'

    name = fields.Char(string="Visit Card Name")
    sequence = fields.Char(string='Sequence', required=True,
                           readonly=True, default=lambda self: _('New'))
    lead_id = fields.Many2one(comodel_name="crm.lead", string="Lead")
    mobile = fields.Char(string="Mobile", related='partner_id.mobile')
    occupation = fields.Char(string="Occupation")
    notes = fields.Html(string="Notes")
    start_datetime = fields.Datetime(string="Start Date")
    project_interested_in_id = fields.Many2one(comodel_name="project.project", string="Project Interested In")
    broker_id = fields.Many2one(comodel_name="res.partner", string="Broker",
                                domain="[('is_broker', '=', True), ('is_company', '=', True)]")
    next_action_date = fields.Date(string="Next Action Date")
    user_id = fields.Many2one(comodel_name="res.users", string="Assigned To")

    partner_id = fields.Many2one(comodel_name="res.partner", string="Contact Name", required=True)
    email = fields.Char(string="Email", related='partner_id.email')
    project_awareness = fields.Html(string="Project Awareness")
    visit_duration = fields.Char(string="Visit Duration")
    project_id = fields.Many2one(comodel_name="project.project", string="Project Name")
    next_action = fields.Char(string="Next Action")
    campaign_id = fields.Many2one(comodel_name="utm.campaign", string="Campaign Source")
    client_request_id = fields.Many2one(comodel_name="client.request", string="Client Request",
                                        domain="[('is_lost', '=', False)]")

    client_source_id = fields.Many2one(comodel_name="client.source", string="Client Source")
    sub_channel_ids = fields.Many2many(comodel_name="utm.channel", relation="sub_channel_visit", string="Sub Channels")
    channel_ids = fields.Many2many(comodel_name="utm.channel", relation="channel_visit", string="Channels")
    sub_source_ids = fields.Many2many(comodel_name="utm.source", relation="sub_source_visit", string="Sub Sources")
    source_ids = fields.Many2many(comodel_name="utm.source", relation="source_visit", string="Sources")

    @api.model
    def create(self, vals):
        if vals.get('sequence', _('New')) == _('New'):
            vals['sequence'] = self.env['ir.sequence'].next_by_code(
                'visit.registration.card') or _('New')
        res = super(VisitRegistrationCard, self).create(vals)
        return res
