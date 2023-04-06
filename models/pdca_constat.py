from odoo import fields, models,api

class Constat(models.Model):
    _name = "pdca.constat"
    _description = "Constats"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    document = fields.Binary('Document:')
    name = fields.Text('Constat:')
    type_constat = fields.Many2one('pdca.type_constat',string="Type Constat")
    direction_concerne = fields.Many2one('pdca.direction', string="Direction Concernees")
    origine= fields.Many2one('pdca.origine',string="Origine")
    activite = fields.Many2one('pdca.unite',string="Activite",domain="[('direction','=',direction_pilote)]")
    processus = fields.Many2one('pdca.processus',string='Processus',domain="[('unite','=',activite)]")
    direction_pilote = fields.Many2many('pdca.direction',string="Direction Pilote")
    status = fields.Selection([('ouvert','Ouvert'),
                               ('encours','En cours'),
                               ('traite','Traite'),
                               ('solde','Solde'),
                               ('annule','Annule')],default="ouvert")
    
    action_ids=fields.One2many('pdca.action','constat_id','Actions')
 
    def affecter_pilote(self):
        return {
            'res_model': 'pdca.affectation_pilote',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('Plan-d-Amelioration-main.affectation_pilote_view_form').id,
            'context': {'default_constat_id': self.id},
        }
    

    def annuler_constat(self):
        self.status='annule'
    