from odoo import models, fields, api, _


class HrDocumentBinary(models.Model):
    _name = 'hr.document.binary'

    document = fields.Binary()
    start_date = fields.Date()
    end_date = fields.Date()
    document_id = fields.Many2one('hr.document')
    comment = fields.Char('Comment')
    states = fields.Selection([('recieved','Recieved'),('not_recieved','Not Recieved'),('loaned','Loaned')],string='Status')
    done = fields.Boolean('Done')
