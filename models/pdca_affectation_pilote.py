from odoo import fields,models,api

class AffectationPilote(models.Model):
    _name = "pdca.affectation_pilote"
    _rec_name='pilote'
    constat_id=fields.Many2one('pdca.constat','Constat')
    pilote = fields.Many2one('res.users',"Pilote d'action")
    action_id=fields.Many2one('pdca.action','Action',
    domain=[('constat_id','=',constat_id)]
    )
    def ajouter_action(self): 
        self.constat_id.status='encours'
        return {
            'res_model': 'pdca.action',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('Plan-d-Amelioration-main.pdca_action_view_form').id,
            'context': {'default_pilote': self.id,'default_constat_id':self.constat_id.id},
        }
    
    def update_action(self):
      
        action = self.env['pdca.action'].search([('pilote', '=', self.id)], limit=1)
        
        if action:
            if action.taux_avancement==100:
                action.status='enattenteaproba'
                print('c bon tekfa laction')
            else:
                action.taux_avancement=action.taux_avancement+10
