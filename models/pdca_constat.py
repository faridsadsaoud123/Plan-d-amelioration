from odoo import fields, models,api

import logging



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
    
    def creer_constat_url(self):
        
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        constat_form_url = '/web#id=%d&action=139&model=pdca.constat&view_type=form&cids=&menu_id=109' % self.id
        
        return base_url + constat_form_url
    
    def pass_dir_pilote_emails(self):
        dir_pilote_ids=self.direction_pilote.ids
        dir_pilote_records=self.env['pdca.direction'].search([('id','in',dir_pilote_ids)])
        personnes_concernes=''
        for dir_pilote in dir_pilote_records:
            if dir_pilote.directeur.email not in personnes_concernes:
                personnes_concernes+=dir_pilote.directeur.email+','
        personnes = personnes_concernes.rstrip(",")
        return personnes

    def send_mail_notif(self):

        template_id = self.env.ref('Plan-d-Amelioration-main.creation_constat_template')

        for rec in self:
            self.creer_constat_url()
            template_id.send_mail(rec.id, force_send=True)
        return
    
    @api.model
    def create(self, vals):
        record = super(Constat, self).create(vals)
        record.send_mail_notif()
        return record
    
    @api.depends('action_ids.status')
    def _changer_status(self):
        for record in self :
            actions_states=record.action_ids.mapped('status')
            verify=True
            for state in actions_states:
                if state != 'solde':
                    verify=False
                    break
                else: continue
            if verify : 
                record.status='solde'
