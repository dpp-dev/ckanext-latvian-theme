import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class Latvian_ThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'latvian_theme')


def auth_user_list(context, data_dict):
    user = context["model"].User.get(context.get('user'))
    #ignore_auth is used in email sending code
    if context.get('ignore_auth') is True:
        return {'success': True}
    #sysadmin can see anything
    elif getattr(user, 'sysadmin', False):
        return {'success': True}
    #all else fails
    else:
        return {'success': False}
    
@toolkit.auth_allow_anonymous_access
def auth_user_show(context, data_dict):
    if not context.get("for_view", False) and not context.get("api_version", False):
        #Not in a view and not through the API, likely to be internal code
        return {"success":True}
    #Either view or API request
    user = context.get('user', '')
    viewed_user = getattr(context.get("user_obj"), "name", None)
    if user == viewed_user:
        return {'success': True}
    else:
        return auth_user_list(context, data_dict)

class Latvian_AuthPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IAuthFunctions)
    #IAuthFunctions
    def get_auth_functions(self):
        return {"user_list": auth_user_list,
                "user_show": auth_user_show
               }
