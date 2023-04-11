from odoo import models,fields,api

class Employe(models.Model):
    _name='pdca.employe'
    _description='Action'
    _inherits = {'res.users': 'user_id'}
    
    user_id=fields.Many2one('res.users','Employe',ondelete='cascade',delegate=True,required=True)
    direction_id=fields.Many2one('pdca.direction','Direction')
    matricule_cnas=fields.Integer('Matricule CNAS')
    