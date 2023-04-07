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
    
    
    
    def approuver_action(self):
        self.status= 'approuve'
        if self.type_action.name=='Action corrective':
            self.status='realise'
            self.constat_id.status='traite'
        else:
            self.status='solde'
            """ verify=True
            actions_records=self.env['pdca.action'].search([('constat_id','in',self.constat_id)])
            for action in actions_records:
                if action:
                    if action.status!='solde':
                       verify=False 
                    else: continue
            if verify:
                self.constat_id.status='solde' """
                        

    def creer_action_definie_url(self):
        
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        constat_form_url = '/web#id=%d&action=142&model=pdca.action&view_type=form&cids=1&menu_id=109' % self.id
        
        return base_url + constat_form_url
    def send_mail_notif(self):

        template_id = self.env.ref('Plan-d-Amelioration-main.action_definie_template')

        for rec in self:
            self.creer_action_definie_url()
            template_id.send_mail(rec.id, force_send=True,email_values={
                'email_to':self.constat_id.create_uid.email
            })
        return
    def send_mail_redefinion(self):
        template_id = self.env.ref('Plan-d-Amelioration-main.action_redefinie_template')

        for rec in self:
            self.creer_action_definie_url()
            template_id.send_mail(rec.id, force_send=True,email_values={
                'email_to':self.pilote.pilote.email,
            })
        return
    def send_mail_validation(self):
        template_id = self.env.ref('Plan-d-Amelioration-main.validation_template')

        for rec in self:
            self.creer_action_definie_url()
            template_id.send_mail(rec.id, force_send=True,email_values={
                'email_to':self.pilote.pilote.email,
            })
        return
    def redefinir_action(self):
        self.send_mail_redefinion()
    def valider_action(self):
        self.send_mail_validation();
        self.status='encours'
    @api.model
    def create(self, values):
        result = super().create(values)
        result.status='enattentevalidation'
        pilote = self.env['pdca.affectation_pilote'].search([('pilote', '=', self.id)], limit=1)
        pilote.action_id=self
        if result.constat_id and result.id not in result.constat_id.action_ids.ids:
            result.constat_id.write({'action_ids':[(4,result.id)]})
        result.send_mail_notif()
        return result
    def write(self, values):
        res = super().write(values)
        self.send_mail_notif()
        return res
   
    
    