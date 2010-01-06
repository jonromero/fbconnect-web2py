# coding: utf8
from applications.fbconnect.modules.facebook import *

facebook_settings.FACEBOOK_API_KEY = 'xxx'
facebook_settings.FACEBOOK_SECRET_KEY = 'xxx'
facebook_settings.FACEBOOK_APP_NAME = "fbconnect-web2py"
facebook_settings.FACEBOOK_INTERNAL = True
facebook_settings.FACEBOOK_CALLBACK_PATH = "/fbconnect/default/test"

def index():
	connected = facebook_connect(request, facebook_settings)
	if connected:
		user = get_facebook_user(request.facebook)
		response.flash = "Hello ", user
		
	return dict(api_key=facebook_settings.FACEBOOK_API_KEY)


def user():
    """
    exposes:
    http://..../[app]/default/user/login 
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()
