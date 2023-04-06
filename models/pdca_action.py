from odoo import models,fields,api

class Action(models.Model):
    _name="pdca.action"
    _description="Action"
    _rec_name="action"
    action = fields.Text(string="Action")
    type_action=fields.Many2one('pdca.type_action',"Type d'action")  
    date_creation = fields.Datetime("Date de creation")
    pilote = fields.Many2one('pdca.affectation_pilote',"Pilote d'action")
    risque= fields.Text(string='Risque')
    type_risque=fields.Many2one('pdca.type_risque',"Type de risque")
    cause=fields.Text(string="Cause")
    oppurtunite=fields.Text(string="Oppurtunite")
    
    constat_id=fields.Many2one('pdca.constat',string="Constat")
    status=fields.Selection([('nonentamne','Non entamne'),
                            ('endefinition',"Definition de l'action"),
                            ('enattentevalidation','En attente de validation'),
                            ('encours','encours'),
                            ('enattenteaproba',"En attente d'approbation"),
                            ('approuve','Approuve'),
                            ('realise','Realise'),
                            ('solde','Solde')],default='endefinition')
    taux_avancement=fields.Integer('Taux d\'avancement',default=0)
    def valider_action(self):
        self.status='encours'
    
    def approuver_action(self):
        self.status= 'approuve'
        if self.type_action.name=='Action corrective':
            self.status='realise'
            self.constat_id.status='traite'
        else:
            self.status='solde'
            self.constat_id.status='solde'
        
    @api.model
    def create(self, values):
        result = super().create(values)
        result.status='enattentevalidation'
        pilote = self.env['pdca.affectation_pilote'].search([('pilote', '=', self.id)], limit=1)
        pilote.action_id=self
        return result

    def write(self, values):
        res = super().write(values)
        
        return res
   
    