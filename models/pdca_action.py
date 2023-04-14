from odoo import models,fields,api,_

class Action(models.Model):
    _name="pdca.action"
    _description="Action"
    _rec_name="action"
    action = fields.Text(string="Action")
    type_action=fields.Many2one('pdca.type_action',"Type d'action")  
    date_creation = fields.Datetime(string="Date de creation")
    pilote = fields.Many2one('pdca.affectation_pilote',"Pilote d'action")
    risque= fields.Text(string='Risque')
    type_risque=fields.Many2one('pdca.type_risque',"Type de risque")
    cause=fields.Text(string="Cause")
    oppurtunite=fields.Text(string="Oppurtunite")
    date_creation= fields.Datetime(string="Date de craetion ",default=fields.Datetime.now())
    date_fin_previsionnelle=fields.Date(string="Date de fin previsionnelle")
    constat_id=fields.Many2one('pdca.constat',string="Constat")
    status=fields.Selection([('nonentamne','Non entamne'),
                            ('endefinition',"Definition de l'action"),
                            ('enattentevalidation','En attente de validation'),
                            ('encours','encours'),
                            ('enattenteaproba',"En attente d'approbation"),
                            ('approuve','Approuve'),
                            ('realise','Realise'),
                            ('solde','Solde'),
                            ('abondonne','Abondonne')],default='endefinition',statusbar={'abondonne':{'invisible':1}})
    taux_avancement=fields.Integer('Taux d\'avancement',default=0)
    motif_rejet=fields.Text("Motif de rejet")
    disable_notification = fields.Boolean(default=False)
    
    # creer un url vers la page de l'action concernee 
    # en cliquant sur le button qui se trouve dans le mail

    def creer_action_definie_url(self):
        
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        action_form_url = '/web#id=%d&action=142&model=pdca.action&view_type=form&cids=1&menu_id=109' % self.id
        
        return base_url + action_form_url
    
    #helper function
    def pass_dir_pilote_emails(self):
        personne=''
        #avoir les emails du directeur et de referent 
        personne=personne+self.pilote.pilote.direction_id.directeur.user_id.email+','+self.pilote.pilote.user_id.email
        if self.status=='abondonne':
            personne=personne+','+self.constat_id.create_uid.email
            # si l'action est abondonne on ajoute l'email de createur de constat
        return personne.rstrip(",")

    # envoyer une notification par email pour les personnes concernees 
    # elle accepte template et email comme arguments
    # template : car on va l'utiliser dans plusieur fonctionalite donc le contenu differe 

    def send_mail_notifiction(self,template,email):
        template_id = self.env.ref(template)
        for rec in self:
            self.creer_action_definie_url()
            template_id.send_mail(rec.id, force_send=True,email_values={
                'email_to':email
            })
        return
    
    #notifier le pilote pour redifinir l'action en cliquant sur le button redefinir

    def redefinir_action(self):
        self.send_mail_notifiction('Plan-d-Amelioration-main.action_redefinie_template',self.pilote.pilote.user_id.email)
    
    # valider l'action et notifier le pilote 

    def valider_action(self):
        self.status='encours'
        self.send_mail_notifiction('Plan-d-Amelioration-main.validation_template',self.pilote.pilote.user_id.email)
        
    #approuver une action

    def approuver_action(self):
        if self.taux_avancement==100:    
            self.status= 'approuve'
            if self.type_action.name=='Action corrective':
                self.status='realise'
                self.constat_id.status='traite'
                self.send_mail_notifiction('Plan-d-Amelioration-main.approuvation_template',self.pass_dir_pilote_emails())
            else:
                self.status='solde'
                self.send_mail_notifiction('Plan-d-Amelioration-main.approuvation_template',self.pass_dir_pilote_emails())
                
                verify=True
                actions_records=self.env['pdca.action'].search([('constat_id','=',self.constat_id.id)])
                for action in actions_records:
                    if action.status!='solde':
                        verify=False 
                        break
                    else: continue
                if verify:
                    self.constat_id.status='solde'

    #desapprouver une action

    def desapprouver_action(self):
        if self.taux_avancement==100:
            self.status='encours'
            self.taux_avancement=self.taux_avancement-10
            self.send_mail_notifiction('Plan-d-Amelioration-main.desapprouvation_template',self.pilote.pilote.user_id.email)
    
    # abandonner une action et notifier la direction pilote 
    # puis une redirection vers une page ou il y a l'action concernee

    def abandonner_action(self):
            self.status='abondonne'
            self.disable_notification=True
            self.send_mail_notifiction('Plan-d-Amelioration-main.abandonnation_template',self.pass_dir_pilote_emails())
            
            return {
                'name':_('Action abondonne'),
                'res_model': 'pdca.action',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'view_type': 'form',
                'view_id': False,
                'domain': [('id','=',self.id)],
                'context':{
                    'create':False,
                    'editable':False,
                }
            }

    #override les fonctions create() et write() 

    @api.model
    def create(self, values):
        result = super().create(values)
        result.status='enattentevalidation'
        # pilote = self.env['pdca.affectation_pilote'].search([('pilote', '=', self.id)], limit=1)
        # pilote.action_id=self
        if result.pilote and not result.pilote.action_id:
            result.pilote.write({'action_id':[(4,result.id)]})
        if result.constat_id and result.id not in result.constat_id.action_ids.ids:
            result.constat_id.write({'action_ids':[(4,result.id)]})
        result.send_mail_notifiction('Plan-d-Amelioration-main.action_definie_template',self.constat_id.create_uid.email)
        return result
    def write(self, values):
        res = super().write(values)
        if self.disable_notification:
            return res
        else:
            self.send_mail_notifiction('Plan-d-Amelioration-main.action_definie_template',self.constat_id.create_uid.email)
            return res
