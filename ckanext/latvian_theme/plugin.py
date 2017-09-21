import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class Latvian_ThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'latvian_theme')


class Latvian_AuthPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IAuthFunctions)
    
    def auth_user_list(self, context, data_dict):
        user = context["model"].User.get(context.get('user'))
        #ignore_auth is used in email sending code
        if context.get('ignore_auth') is True:
            return {'success': True}
        #sysadmin can see anything
        elif user.sysadmin:
            return {'success': True}
        #all else fails
        else:
            return {'success': False}

    #IAuthFunctions
    def get_auth_functions(self):
        return {"user_list": self.auth_user_list}
