import ckan.logic as logic
import ckan.model as model
from functools import wraps
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.plugins as plugins
from ckan.common import _, c, request
import ckan.plugins.toolkit as toolkit

from ckan.controllers.revision import RevisionController

class Latvian_ThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'latvian_theme')


#Replacement RevisionController

class CustomRevisionController(RevisionController):
    
    def __before__(self, action, **env):
        RevisionController.__before__(self, action, **env)
        context = {'model': model, 'user': c.user,
                   'auth_user_obj': c.userobj}
        if not getattr(c.userobj, 'sysadmin', False):
            base.abort(404)

    def list(self, *args, **kwargs):
        return RevisionController.list(self)
             
    def diff(self, *args, **kwargs):
        return RevisionController.diff(self)
             
    def edit(self, *args, **kwargs):
        return RevisionController.edit(self)
             
    def index(self, *args, **kwargs):
        return RevisionController.index(self)
             
    def read(self, *args, **kwargs):
        return RevisionController.read(self)
             

#Authentification functions

#Auth function chaining is not yet supported
#def auth_datastore_search(context, data_dict):
#    print(data_dict)
#    return {'success': True}

@toolkit.auth_allow_anonymous_access
def auth_group_show(context, data_dict):
    if not context.get("for_view", False) and not context.get("api_version", False):
        #Not in a view and not through the API, likely to be internal code
        return {"success":True}
    user = context.get("auth_user_obj", {})
    user_uuid = getattr(user, 'id', '')
    group_id = data_dict["id"]
    member_data = toolkit.get_action('member_list')(
        data_dict={'id': group_id, 'object_type': 'user'})
    member_uuids = [data[0] for data in member_data]
    if not getattr(user, 'sysadmin', False) and not user_uuid in member_uuids:
        #Modifying data_dict, which is passed by reference, so the modification is propagated further
        data_dict["include_users"] = False
    return {'success': True}

@toolkit.auth_allow_anonymous_access
def auth_user_list(context, data_dict):
    if not context.get("for_view", False) and not context.get("api_version", False):
        #Not in a view and not through the API, likely to be internal code
        return {"success":True}
    #Either view or API request
    user = context["model"].User.get(context.get('user'))
    #This one may be redundant with the view&API check
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
    user = context.get('user', '')
    viewed_user = getattr(context.get("user_obj"), "name", None)
    if user == viewed_user:
        return {'success': True}
    else:
        return auth_user_list(context, data_dict)

#Overridden actions

#CKAN install I'm working on is too old to have action chaining available
#@toolkit.chained_action
#@logic.side_effect_free
#def safe_datastore_search(datastore_search, context, data_dict):
#    print(data_dict)
#    return datastore_search(context, data_dict)

class Latvian_AuthPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IRoutes, inherit=True)
    #plugins.implements(plugins.IActions)

    #IActions
    #def get_actions(self):
    #    print("action added")
    #    return {"datastore_search":safe_datastore_search}
    
    def before_map(self, map):
        rev_c = 'ckanext.latvian_theme.plugin:CustomRevisionController'
        map.connect('/revision', controller=rev_c, action='index')
        map.connect('/revision/list', controller=rev_c, action='list')
        map.connect('/revision/{id}', controller=rev_c, action='read')
        map.connect('/revision/edit/{id}', controller=rev_c, action='edit')
        map.connect('/revision/diff/{id}', controller=rev_c, action='diff')
        return map

    #IAuthFunctions
    def get_auth_functions(self):
        return {"user_list": auth_user_list,
                "group_show": auth_group_show,
                #"datastore_search": auth_datastore_search,
                "organization_show": auth_group_show,
                "user_show": auth_user_show
               }
