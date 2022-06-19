import json

import requests

from odoo import api, fields, models
from odoo.exceptions import AccessDenied, UserError
from odoo.addons.auth_signup.models.res_users import SignupError

from odoo.addons import base
base.models.res_users.USER_PRIVATE_FIELDS.append('oauth_access_token')


class InheritAuth(models.Model):
	_inherit = 'auth.oauth.provider'

	client_secret = fields.Char(string='Client Secret Key') 



class InheritUsers(models.Model):
	_inherit = 'res.users'


	@api.model
	def _generate_signup_values_azure(self, provider, validation, params):
		oauth_uid = validation['id']
		email = validation.get('userPrincipalName', 'provider_%s_user_%s' % (provider, oauth_uid))
		name = validation.get('name', email)
		return {
			'name': name,
			'login': email,
			'email': email,
			'oauth_provider_id': provider,
			'oauth_uid': oauth_uid,
			'oauth_access_token': params['access_token'],
			'active': True,
		}


	@api.model
	def _auth_oauth_validate_azure(self, provider, access_token):
		""" return the validation data corresponding to the access token """
		oauth_provider = self.env['auth.oauth.provider'].browse(provider)
		get_param = self.env['ir.config_parameter'].sudo().get_param
		base_url = get_param('web.base.url', default='http://www.odoo.com?NoBaseUrl')
		client_id = oauth_provider.client_id
		scope = oauth_provider.scope
		client_secret = oauth_provider.client_secret
		headers = {"content-type": "application/x-www-form-urlencoded"}
		data = {
			'code': access_token,
			'client_id': client_id,
			'client_secret': client_secret,
			'scope': scope,
			'grant_type':'authorization_code',
			'redirect_uri': base_url + '/microsoft_sso_integration/microsoft'
		}
		
		token = requests.post(oauth_provider.validation_endpoint,headers=headers,data=data).json()
		validation ={}
		headers['Authorization'] = 'Bearer'+' '+token.get('access_token')
		abc = requests.get('https://graph.microsoft.com/v1.0/users', headers = headers).json()
		validation.update(abc.get('value')[0])
		validation['access_token'] = token.get('access_token')
		return validation


	@api.model
	def _auth_oauth_signin_azure(self, provider, validation, params):
		""" retrieve and sign in the user corresponding to provider and validated access token
			:param provider: oauth provider id (int)
			:param validation: result of validation of access token (dict)
			:param params: oauth parameters (dict)
			:return: user login (str)
			:raise: AccessDenied if signin failed

			This method can be overridden to add alternative signin methods.
		"""
		oauth_uid = validation['user_id']
		try:
			oauth_user = self.search([("oauth_uid", "=", oauth_uid), ('oauth_provider_id', '=', provider)])
			if not oauth_user:
				raise AccessDenied()
			assert len(oauth_user) == 1
			oauth_user.write({'oauth_access_token': params['access_token']})
			return oauth_user.login
		except AccessDenied as access_denied_exception:
			if self.env.context.get('no_user_creation'):
				return None
			state = json.loads(params['state'])
			token = state.get('t')
			values = self._generate_signup_values_azure(provider, validation, params)
			try:
				_, login, _ = self.signup(values, token)
				return login
			except (SignupError, UserError):
				raise access_denied_exception



	@api.model
	def auth_oauth_microsoft(self, provider, params):
		# Advice by Google (to avoid Confused Deputy Problem)
		# if validation.audience != OUR_CLIENT_ID:
		#   abort()
		# else:
		#   continue with the process
		validation = self._auth_oauth_validate_azure(provider, params['code'])
		params['access_token'] = validation.get('access_token')
		access_token = validation.get('access_token')
		# required check
		if not validation.get('user_id'):
			# Workaround: facebook does not send 'user_id' in Open Graph Api
			if validation.get('id'):
				validation['user_id'] = validation['id']
			else:
				raise AccessDenied()

		# retrieve and sign in user
		login = self._auth_oauth_signin_azure(provider, validation, params)
		if not login:
			raise AccessDenied()
		# return user credentials
		return (self.env.cr.dbname, login, access_token)



	def _check_credentials(self, password, env):
		try:
			return super(InheritUsers, self)._check_credentials(password, env)
		except AccessDenied:
			passwd_allowed = env['interactive'] or not self.env.user._rpc_api_keys_only()
			if passwd_allowed and self.env.user.active:
				res = self.sudo().search([('id', '=', self.env.uid), ('oauth_access_token', '=', password)])
				if res:
					return
			raise

	def _get_session_token_fields(self):
		return super(InheritUsers, self)._get_session_token_fields() | {'oauth_access_token'}

