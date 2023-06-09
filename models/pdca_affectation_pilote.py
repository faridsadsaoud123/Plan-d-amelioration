from odoo import fields,models,api

class AffectationPilote(models.Model):
    _name = "pdca.affectation_pilote"
    _rec_name='pilote'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    constat_id=fields.Many2one('pdca.constat','Constat')
    pilote = fields.Many2one('pdca.employe',"Pilote d'action")
    action_id=fields.Many2one('pdca.action','Action',
    domain=[('constat_id','=',constat_id)]
    )
    # definir une nouvelle action par le pilote 
    # en redirigant vers le formulaire de definition d'une action
    def ajouter_action(self): 
        self.constat_id.status='encours'
        return {
            'res_model': 'pdca.action',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('Plan-d-Amelioration-main.pdca_action_view_form').id,
            'context': {'default_pilote': self.id,'default_constat_id':self.constat_id.id},
        }
    
    #creation d'un url vers une action en cliquant sur le button dans le mail

    def creer_taux_avancement_constat_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        action_form_url = '/web#id=%d&action=142&model=pdca.action&view_type=form&cids=1&menu_id=109' % self.action_id.id
        
        return base_url + action_form_url
    
    #infromer le createur de constat que le taux d'avancement est a 100%

    def send_taux_avancement_notification(self):
        template_id = self.env.ref('Plan-d-Amelioration-main.taux_avancement_template')

        for rec in self:
            self.creer_taux_avancement_constat_url()
            template_id.send_mail(rec.id, force_send=True,email_values={
                'email_to':self.constat_id.create_uid.email
            })
        return
    
    #renseigner le taux d'avancement a chaque fois par le pilote

    def update_action(self):
      
        action = self.env['pdca.action'].search([('pilote', '=', self.id)], limit=1)
        
        if action:
            if action.taux_avancement==100:
                action.status='enattenteaproba'
                self.send_taux_avancement_notification()     
            else:
                action.taux_avancement=action.taux_avancement+10


    def creer_affectation_pilote_url(self):
        
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        pilote_form_url = '/web#id=%d&action=145&model=pdca.affectation_pilote&view_type=form&cids=&menu_id=109' % self.id
        
        return base_url + pilote_form_url
    
    # notifier le pilote sur le onstat qu'il va traiter

    def send_mail_notif(self):

        template_id = self.env.ref('Plan-d-Amelioration-main.affectation_pilote_template')

        for rec in self:
            self.creer_affectation_pilote_url()
            template_id.send_mail(rec.id, force_send=True)
        return
    
    #override la fonction create

    @api.model
    def create(self, vals):
        record = super(AffectationPilote, self).create(vals)
        record.send_mail_notif()
        return record