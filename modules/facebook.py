#! /usr/bin/env python
#
# pyfacebook - Python bindings for the Facebook API
#
# Copyright (c) 2008, Samuel Cormier-Iijima
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY <copyright holder> ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <copyright holder> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# slightly modified by Massimo Di Pierro
# facebook connect patch by Jon Vlachoyiannis (jon@emotionull.com)

"""
Python bindings for the Facebook API (pyfacebook - http://code.google.com/p/pyfacebook)

PyFacebook is a client library that wraps the Facebook API.

For more information, see

Home Page: http://code.google.com/p/pyfacebook
Developer Wiki: http://wiki.developers.facebook.com/index.php/Python
Facebook IRC Channel: #facebook on irc.freenode.net

PyFacebook can use simplejson if it is installed, which
is much faster than XML and also uses less bandwith. Go to
http://undefined.org/python/#simplejson to download it, or do
apt-get install python-simplejson on a Debian-like system.
"""

import md5
import sys
import time
import urllib
import urllib2
import httplib
import mimetypes

# try to use simplejson first, otherwise fallback to XML
import gluon.contrib.simplejson as simplejson
RESPONSE_FORMAT = 'JSON'

#__all__ = ['add_facebook_instance','require_facebook_login','require_facebook_add','get_facebook_user']

PYFACEBOOK_VERSION = '0.1'

# REST URLs
# Change these to /bestserver.php to use the bestserver.
FACEBOOK_URL = 'http://api.facebook.com/restserver.php'
FACEBOOK_SECURE_URL = 'https://api.facebook.com/restserver.php'

# class json(object): pass

# simple IDL for the Facebook API
FACEBOOK_METHODS = {
    # feed methods
    'feed': {
        'publishStoryToUser': [
            ('title', str, []),
            ('body', str, ['optional']),
            ('image_1', str, ['optional']),
            ('image_1_link', str, ['optional']),
            ('image_2', str, ['optional']),
            ('image_2_link', str, ['optional']),
            ('image_3', str, ['optional']),
            ('image_3_link', str, ['optional']),
            ('image_4', str, ['optional']),
            ('image_4_link', str, ['optional']),
            ('priority', int, ['optional']),
        ],

        'publishActionOfUser': [
            ('title', str, []),
            ('body', str, ['optional']),
            ('image_1', str, ['optional']),
            ('image_1_link', str, ['optional']),
            ('image_2', str, ['optional']),
            ('image_2_link', str, ['optional']),
            ('image_3', str, ['optional']),
            ('image_3_link', str, ['optional']),
            ('image_4', str, ['optional']),
            ('image_4_link', str, ['optional']),
            ('priority', int, ['optional']),
        ],

        'publishTemplatizedAction': [
            # facebook expects title_data and body_data to be JSON
            # simplejson.dumps({'place':'Florida'}) would do fine
            # actor_id is now deprecated, use page_actor_id instead
            ('actor_id', int, []),
            ('page_actor_id', int, []),
            ('title_template', str, []),
            ('title_data', str, ['optional']),
            ('body_template', str, ['optional']),
            ('body_data', str, ['optional']),
            ('body_general', str, ['optional']),
            ('image_1', str, ['optional']),
            ('image_1_link', str, ['optional']),
            ('image_2', str, ['optional']),
            ('image_2_link', str, ['optional']),
            ('image_3', str, ['optional']),
            ('image_3_link', str, ['optional']),
            ('image_4', str, ['optional']),
            ('image_4_link', str, ['optional']),
            ('target_ids', list, ['optional']),
        ],
    },

    # fql methods
    'fql': {
        'query': [
            ('query', str, []),
        ],
    },

    # friends methods
    'friends': {
        'areFriends': [
            ('uids1', list, []),
            ('uids2', list, []),
        ],

        'get': [],

        'getAppUsers': [],
    },

    # notifications methods
    'notifications': {
        'get': [],

        'send': [
            ('to_ids', list, []),
            ('notification', str, []),
            ('email', str, ['optional']),
        ],

        'sendRequest': [
            ('to_ids', list, []),
            ('type', str, []),
            ('content', str, []),
            ('image', str, []),
            ('invite', bool, []),
        ],

        'sendEmail': [
            ('recipients', list, []),
            ('subject', str, []),
            ('text', str, ['optional']),
            ('fbml', str, ['optional']),
        ]
    },

    # profile methods
    'profile': {
        'setFBML': [
            ('markup', str, ['optional']),
            ('uid', int, ['optional']),
            ('profile', str, ['optional']),
            ('profile_action', str, ['optional']),
            ('mobile_fbml', str, ['optional']),
        ],

        'getFBML': [
            ('uid', int, ['optional']),
        ],
    },

    # users methods
    'users': {
        'getInfo': [
            ('uids', list, []),
            ('fields', list, [('default', ['name'])]),
        ],

        'getLoggedInUser': [],

        'isAppAdded': [],

        'hasAppPermission': [
            ('ext_perm', str, []),
        ],

        'setStatus': [
            ('status', str, []),
            ('clear', bool, []),
        ],
    },

    # events methods
    'events': {
        'get': [
            ('uid', int, ['optional']),
            ('eids', list, ['optional']),
            ('start_time', int, ['optional']),
            ('end_time', int, ['optional']),
            ('rsvp_status', str, ['optional']),
        ],

        'getMembers': [
            ('eid', int, []),
        ],
    },

    # update methods
    'update': {
        'decodeIDs': [
            ('ids', list, []),
        ],
    },

    # groups methods
    'groups': {
        'get': [
            ('uid', int, ['optional']),
            ('gids', list, ['optional']),
        ],

        'getMembers': [
            ('gid', int, []),
        ],
    },

    # marketplace methods
    'marketplace': {
        'createListing': [
            ('listing_id', int, []),
            ('show_on_profile', bool, []),
            ('listing_attrs', str, []),
        ],

        'getCategories': [],

        'getListings': [
            ('listing_ids', list, []),
            ('uids', list, []),
        ],

        'getSubCategories': [
            ('category', str, []),
        ],

        'removeListing': [
            ('listing_id', int, []),
            ('status', str, []),
        ],

        'search': [
            ('category', str, ['optional']),
            ('subcategory', str, ['optional']),
            ('query', str, ['optional']),
        ],
    },

    # pages methods
    'pages': {
        'getInfo': [
            ('page_ids', list, ['optional']),
            ('uid', int, ['optional']),
        ],

        'isAdmin': [
            ('page_id', int, []),
        ],

        'isAppAdded': [
            ('page_id', int, []),
        ],

        'isFan': [
            ('page_id', int, []),
            ('uid', int, []),
        ],
    },

    # photos methods
    'photos': {
        'addTag': [
            ('pid', int, []),
            ('tag_uid', int, [('default', 0)]),
            ('tag_text', str, [('default', '')]),
            ('x', float, [('default', 50)]),
            ('y', float, [('default', 50)]),
            ('tags', str, ['optional']),
        ],

        'createAlbum': [
            ('name', str, []),
            ('location', str, ['optional']),
            ('description', str, ['optional']),
        ],

        'get': [
            ('subj_id', int, ['optional']),
            ('aid', int, ['optional']),
            ('pids', list, ['optional']),
        ],

        'getAlbums': [
            ('uid', int, ['optional']),
            ('aids', list, ['optional']),
        ],

        'getTags': [
            ('pids', list, []),
        ],
    },

    # fbml methods
    'fbml': {
        'refreshImgSrc': [
            ('url', str, []),
        ],

        'refreshRefUrl': [
            ('url', str, []),
        ],

        'setRefHandle': [
            ('handle', str, []),
            ('fbml', str, []),
        ],
    },

    'data': {
        'getCookies': [
            ('uid', int, []),
            ('string', str, []),
        ],

        'setCookie': [
            ('uid', int, []),
            ('name', str, []),
            ('value', str, []),
            ('expires', int, ['optional']),
            ('path', str, ['optional']),
        ],
    },
}


class Proxy(object):
    """Represents a "namespace" of Facebook API calls."""

    def __init__(self, client, name):
        self._client = client
        self._name = name

    def __call__(self, method, args=None, add_session_args=True):
        if add_session_args:
            self._client._add_session_args(args)

        return self._client('%s.%s' % (self._name, method), args)


# generate the Facebook proxies
def __generate_proxies():
    for namespace in FACEBOOK_METHODS:
        methods = {}

        for method in FACEBOOK_METHODS[namespace]:
            params = ['self']
            body = ['args = {}']

            for param_name, param_type, param_options in FACEBOOK_METHODS[namespace][method]:
                param = param_name

                for option in param_options:
                    if isinstance(option, tuple) and option[0] == 'default':
                        if param_type == list:
                            param = '%s=None' % param_name
                            body.append('if %s is None: %s = %s' % (param_name, param_name, repr(option[1])))
                        else:
                            param = '%s=%s' % (param_name, repr(option[1]))

                if 'optional' in param_options:
                    param = '%s=None' % param_name
                    body.append('if %s is not None: args[\'%s\'] = %s' % (param_name, param_name, param_name))
                else:
                    body.append('args[\'%s\'] = %s' % (param_name, param_name))

                params.append(param)

            # simple docstring to refer them to Facebook API docs
            body.insert(0, '"""Facebook API call. See http://developers.facebook.com/documentation.php?v=1.0&method=%s.%s"""' % (namespace, method))

            body.insert(0, 'def %s(%s):' % (method, ', '.join(params)))

            body.append('return self(\'%s\', args)' % method)

            exec('\n    '.join(body))

            methods[method] = eval(method)

        proxy = type('%sProxy' % namespace.title(), (Proxy, ), methods)

        globals()[proxy.__name__] = proxy


__generate_proxies()


class FacebookError(Exception):
    """Exception class for errors received from Facebook."""

    def __init__(self, code, msg, args=None):
        self.code = code
        self.msg = msg
        self.args = args

    def __str__(self):
        return 'Error %s: %s' % (self.code, self.msg)


class AuthProxy(Proxy):
    """Special proxy for facebook.auth."""

    def getSession(self):
        """Facebook API call. See http://developers.facebook.com/documentation.php?v=1.0&method=auth.getSession"""
        args = {}
        try:
            args['auth_token'] = self._client.auth_token
        except AttributeError:
            raise RuntimeError('Client does not have auth_token set.')
        result = self._client('%s.getSession' % self._name, args)
        self._client.session_key = result['session_key']
        self._client.uid = result['uid']
        self._client.secret = result.get('secret')
        self._client.session_key_expires = result['expires']
        return result

    def createToken(self):
        """Facebook API call. See http://developers.facebook.com/documentation.php?v=1.0&method=auth.createToken"""
        token = self._client('%s.createToken' % self._name)
        self._client.auth_token = token
        return token


class FriendsProxy(FriendsProxy):
    """Special proxy for facebook.friends."""

    def get(self):
        """Facebook API call. See http://developers.facebook.com/documentation.php?v=1.0&method=friends.get"""
        if self._client._friends:
            return self._client._friends
        return super(FriendsProxy, self).get()


class PhotosProxy(PhotosProxy):
    """Special proxy for facebook.photos."""

    def upload(self, image, aid=None, caption=None, size=(604, 1024)):
        """Facebook API call. See http://developers.facebook.com/documentation.php?v=1.0&method=photos.upload

        size -- an optional size (width, height) to resize the image to before uploading. Resizes by default
                to Facebook's maximum display width of 604.
        """
        args = {}

        if aid is not None:
            args['aid'] = aid

        if caption is not None:
            args['caption'] = caption

        args = self._client._build_post_args('facebook.photos.upload', self._client._add_session_args(args))

        try:
            import cStringIO as StringIO
        except ImportError:
            import StringIO

        try:
            import Image
        except ImportError:
            data = StringIO.StringIO(open(image, 'rb').read())
        else:
            img = Image.open(image)
            if size:
                img.thumbnail(size, Image.ANTIALIAS)
            data = StringIO.StringIO()
            img.save(data, img.format)

        content_type, body = self.__encode_multipart_formdata(list(args.iteritems()), [(image, data)])
        h = httplib.HTTP('api.facebook.com')
        h.putrequest('POST', '/restserver.php')
        h.putheader('Content-Type', content_type)
        h.putheader('Content-Length', str(len(body)))
        h.putheader('MIME-Version', '1.0')
        h.putheader('User-Agent', 'PyFacebook Client Library')
        h.endheaders()
        h.send(body)

        reply = h.getreply()

        if reply[0] != 200:
            raise Exception('Error uploading photo: Facebook returned HTTP %s (%s)' % (reply[0], reply[1]))

        response = h.file.read()

        return self._client._parse_response(response, 'facebook.photos.upload')


    def __encode_multipart_formdata(self, fields, files):
        """Encodes a multipart/form-data message to upload an image."""
        boundary = '-------tHISiStheMulTIFoRMbOUNDaRY'
        crlf = '\r\n'
        l = []

        for (key, value) in fields:
            l.append('--' + boundary)
            l.append('Content-Disposition: form-data; name="%s"' % str(key))
            l.append('')
            l.append(str(value))
        for (filename, value) in files:
            l.append('--' + boundary)
            l.append('Content-Disposition: form-data; filename="%s"' % (str(filename), ))
            l.append('Content-Type: %s' % self.__get_content_type(filename))
            l.append('')
            l.append(value.getvalue())
        l.append('--' + boundary + '--')
        l.append('')
        body = crlf.join(l)
        content_type = 'multipart/form-data; boundary=%s' % boundary
        return content_type, body


    def __get_content_type(self, filename):
        """Returns a guess at the MIME type of the file from the filename."""
        return str(mimetypes.guess_type(filename)[0]) or 'application/octet-stream'


class Facebook(object):
    """
    Provides access to the Facebook API.

    Instance Variables:

    added
        True if the user has added this application.

    api_key
        Your API key, as set in the constructor.

    app_name
        Your application's name, i.e. the APP_NAME in http://apps.facebook.com/APP_NAME/ if
        this is for an internal web application. Optional, but useful for automatic redirects
        to canvas pages.

    auth_token
        The auth token that Facebook gives you, either with facebook.auth.createToken,
        or through a GET parameter.

    callback_path
        The path of the callback set in the Facebook app settings. If your callback is set
        to http://www.example.com/facebook/callback/, this should be '/facebook/callback/'.
        Optional, but useful for automatic redirects back to the same page after login.

    desktop
        True if this is a desktop app, False otherwise. Used for determining how to
        authenticate.

    in_canvas
        True if the current request is for a canvas page.

    internal
        True if this Facebook object is for an internal application (one that can be added on Facebook)

    page_id
        Set to the page_id of the current page (if any)

    secret
        Secret that is used after getSession for desktop apps.

    secret_key
        Your application's secret key, as set in the constructor.

    session_key
        The current session key. Set automatically by auth.getSession, but can be set
        manually for doing infinite sessions.

    session_key_expires
        The UNIX time of when this session key expires, or 0 if it never expires.

    uid
        After a session is created, you can get the user's UID with this variable. Set
        automatically by auth.getSession.

    ----------------------------------------------------------------------

    """

    def __init__(self, api_key, secret_key, auth_token=None, app_name=None, callback_path=None, internal=None):
        """
        Initializes a new Facebook object which provides wrappers for the Facebook API.

        If this is a desktop application, the next couple of steps you might want to take are:

        facebook.auth.createToken() # create an auth token
        facebook.login()            # show a browser window
        wait_login()                # somehow wait for the user to log in
        facebook.auth.getSession()  # get a session key

        For web apps, if you are passed an auth_token from Facebook, pass that in as a named parameter.
        Then call:

        facebook.auth.getSession()

        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.session_key = None
        self.session_key_expires = None
        self.auth_token = auth_token
        self.secret = None
        self.uid = None
        self.page_id = None
        self.in_canvas = False
        self.added = False
        self.app_name = app_name
        self.callback_path = callback_path
        self.internal = internal
        self._friends = None

        for namespace in FACEBOOK_METHODS:
            self.__dict__[namespace] = eval('%sProxy(self, \'%s\')' % (namespace.title(), 'facebook.%s' % namespace))

        self.auth = AuthProxy(self, 'facebook.auth')


    def _hash_args(self, args, secret=None):
        """Hashes arguments by joining key=value pairs, appending a secret, and then taking the MD5 hex digest."""
        hasher = md5.new(''.join(['%s=%s' % (x, args[x]) for x in sorted(args.keys())]))
        if secret:
            hasher.update(secret)
        elif self.secret:
            hasher.update(self.secret)
        else:
            hasher.update(self.secret_key)
        return hasher.hexdigest()


    def _parse_response_item(self, node):
        """Parses an XML response node from Facebook."""
        if node.nodeType == node.DOCUMENT_NODE and \
            node.childNodes[0].hasAttributes() and \
            node.childNodes[0].hasAttribute('list') and \
            node.childNodes[0].getAttribute('list') == "true":
            return {node.childNodes[0].nodeName: self._parse_response_list(node.childNodes[0])}
        elif node.nodeType == node.ELEMENT_NODE and \
            node.hasAttributes() and \
            node.hasAttribute('list') and \
            node.getAttribute('list')=="true":
            return self._parse_response_list(node)
        elif len(filter(lambda x: x.nodeType == x.ELEMENT_NODE, node.childNodes)) > 0:
            return self._parse_response_dict(node)
        else:
            return ''.join(node.data for node in node.childNodes if node.nodeType == node.TEXT_NODE)


    def _parse_response_dict(self, node):
        """Parses an XML dictionary response node from Facebook."""
        result = {}
        for item in filter(lambda x: x.nodeType == x.ELEMENT_NODE, node.childNodes):
            result[item.nodeName] = self._parse_response_item(item)
        if node.nodeType == node.ELEMENT_NODE and node.hasAttributes():
            if node.hasAttribute('id'):
                result['id'] = node.getAttribute('id')
        return result


    def _parse_response_list(self, node):
        """Parses an XML list response node from Facebook."""
        result = []
        for item in filter(lambda x: x.nodeType == x.ELEMENT_NODE, node.childNodes):
            result.append(self._parse_response_item(item))
        return result


    def _check_error(self, response):
        """Checks if the given Facebook response is an error, and then raises the appropriate exception."""
        if type(response) is dict and response.has_key('error_code'):
            raise FacebookError(response['error_code'], response['error_msg'], response['request_args'])


    def _build_post_args(self, method, args=None):
        """Adds to args parameters that are necessary for every call to the API."""
        if args is None:
            args = {}

        for arg in args.items():
            if type(arg[1]) == list:
                args[arg[0]] = ','.join(str(a) for a in arg[1])
            elif type(arg[1]) == unicode:
                args[arg[0]] = arg[1].encode("UTF-8")

        args['method'] = method
        args['api_key'] = self.api_key
        args['v'] = '1.0'
        args['format'] = RESPONSE_FORMAT
        args['sig'] = self._hash_args(args)

        return args


    def _add_session_args(self, args=None):
        """Adds 'session_key' and 'call_id' to args, which are used for API calls that need sessions."""
        if args is None:
            args = {}

        if not self.session_key:
            raise RuntimeError('Session key not set. Make sure auth.getSession has been called.')

        args['session_key'] = self.session_key
        args['call_id'] = str(int(time.time() * 1000))

        return args


    def _parse_response(self, response, method, format=None):
        """Parses the response according to the given (optional) format, which should be either 'JSON' or 'XML'."""
        if not format:
            format = RESPONSE_FORMAT

        if format == 'JSON':
            result = simplejson.loads(response)

            self._check_error(result)
        elif format == 'XML':
            dom = minidom.parseString(response)
            result = self._parse_response_item(dom)
            dom.unlink()

            if 'error_response' in result:
                self._check_error(result['error_response'])

            result = result[method[9:].replace('.', '_') + '_response']
        else:
            raise RuntimeError('Invalid format specified.')

        return result


    def __call__(self, method, args=None, secure=False):
        """Make a call to Facebook's REST server."""
        post_data = urllib.urlencode(self._build_post_args(method, args))

        if secure:
            response = urllib2.urlopen(FACEBOOK_SECURE_URL, post_data).read()
        else:
            response = urllib2.urlopen(FACEBOOK_URL, post_data).read()

        return self._parse_response(response, method)


    # URL helpers
    def get_url(self, page, **args):
        """
        Returns one of the Facebook URLs (www.facebook.com/SOMEPAGE.php).
        Named arguments are passed as GET query string parameters.

        """
        return 'http://www.facebook.com/%s.php?%s' % (page, urllib.urlencode(args))


    def get_app_url(self, path=''):
        """
        Returns the URL for this app's canvas page, according to app_name.
        
        """
        return 'http://apps.facebook.com/%s/%s' % (self.app_name, path)


    def get_add_url(self, next=None):
        """
        Returns the URL that the user should be redirected to in order to add the application.

        """
        args = {'api_key': self.api_key, 'v': '1.0'}

        if next is not None:
            args['next'] = next

        return self.get_url('install', **args)


    def get_authorize_url(self, next=None, next_cancel=None):
        """
        Returns the URL that the user should be redirected to in order to authorize certain actions for application.

        """
        args = {'api_key': self.api_key, 'v': '1.0'}

        if next is not None:
            args['next'] = next

        if next_cancel is not None:
            args['next_cancel'] = next_cancel

        return self.get_url('authorize', **args)


    def get_login_url(self, next=None, popup=False, canvas=True):
        """
        Returns the URL that the user should be redirected to in order to login.

        next -- the URL that Facebook should redirect to after login

        """
        args = {'api_key': self.api_key, 'v': '1.0'}

        if next is not None:
            args['next'] = next
			
        if canvas is True:
            args['canvas'] = 1

        if popup is True:
            args['popup'] = 1

        if self.auth_token is not None:
            args['auth_token'] = self.auth_token

        return self.get_url('login', **args)


    def login(self, popup=False):
        """Open a web browser telling the user to login to Facebook."""
        import webbrowser
        webbrowser.open(self.get_login_url(popup=popup))


    def check_session(self, request):
        """
        Checks the given web2py HttpRequest for Facebook parameters such as
        POST variables or an auth token. If the session is valid, returns True
        and this object can now be used to access the Facebook API. Otherwise,
        it returns False, and the application should take the appropriate action
        (either log the user in or have him add the application).

        """
        self.in_canvas = (request.post_vars.fb_sig_in_canvas=='1')

        if self.session_key and (self.uid or self.page_id):
            return True

        if request.post_vars:
            params = self.validate_signature(request.post_vars)
        else:
            if 'installed' in request.get_vars:
                self.added = True

            if 'fb_page_id' in request.get_vars:
                self.page_id = request.get_vars.fb_page_id

            if 'auth_token' in request.get_vars:
                self.auth_token = request.get_vars.auth_token

                try:
                    self.auth.getSession()
                except FacebookError, e:
                    self.auth_token = None
                    return False

                return True

            params = self.validate_signature(request.get_vars)

        if not params:
            return False

        if params.get('in_canvas') == '1':
            self.in_canvas = True

        if params.get('added') == '1':
            self.added = True

        if params.get('expires'):
            self.session_key_expires = int(params['expires'])

        if 'friends' in params:
            if params['friends']:
                self._friends = params['friends'].split(',')
            else:
                self._friends = []

        if 'session_key' in params:
            self.session_key = params['session_key']
            if 'user' in params:
                self.uid = params['user']
            elif 'page_id' in params:
                self.page_id = params['page_id']
            else:
                return False
        else:
            return False

        return True


    def validate_signature(self, post, prefix='fb_sig', timeout=None):
        """
        Validate parameters passed to an internal Facebook app from Facebook.

        """
        args = post.copy()

        if prefix not in args:
            return None

        del args[prefix]

        if timeout and '%s_time' % prefix in post and time.time() - float(post['%s_time' % prefix]) > timeout:
            return None

        args = dict([(key[len(prefix + '_'):], value) for key, value in args.items() if key.startswith(prefix)])

        hash = self._hash_args(args)

        if hash == post[prefix]:
            return args
        else:
            return None

###### added by Massimo Di Pierro ########

def add_facebook_instance(request,settings):
    '''
    Intended to create an instances of facebook.Facebook to
    use to interact with the API for this specific session.
    '''

    # if already has a facebook instance, immediately return
    if request.facebook: return request

    # auth_token is other important possible param
    api_key = settings.FACEBOOK_API_KEY
    secret_key = settings.FACEBOOK_SECRET_KEY
    app_name = settings.FACEBOOK_APP_NAME
    callback_path = settings.FACEBOOK_CALLBACK_PATH
    internal = settings.FACEBOOK_INTERNAL or True
    request.facebook = Facebook(
        api_key=api_key,
        secret_key=secret_key,
        app_name=app_name,
        callback_path=callback_path,
        internal=internal
        )

def require_facebook_login(request, settings,next=None):
    """
    Used for redirecting the user to the Facebook
    login page if not already logged in.

    Usage:
      require_facebook_login(request,settings)
    """
    if not request.facebook: add_facebook_instance(request,settings)
    fb = request.facebook
    if not fb.check_session(request):
        redirect(fb.get_login_url(next=next))
    return fb

def require_facebook_add(request, settings, next=None):
    """
    Used for redirecting the user to the Facebook
    add-app page.

    Usage:
      require_facebook_add(request,settings)
    """
    if not request.facebook: add_facebook_instance(request,settings)
    fb = request.facebook
    if not fb.check_session(request):
        redirect(fb.get_login_url(next=next))
    if not fb.added:
        redirect(fb.get_add_url(next=next)) 
    return fb

def get_facebook_user(facebook):
    """
    Return the fb.models.User model instance associated with
    the @facebook parameter.

    Usage:
      user = get_facebook_user(some_facebook_instance)
    """
    query = "SELECT uid, first_name, last_name FROM user WHERE uid=%s" % facebook.uid
    # FQL results a list of dicts, retrieve the first (and only) one
    results = facebook.fql.query(query)[0]
    return "%s %s" % (results[u'first_name'], results[u'last_name'])


def facebook_connect(request, settings, infinite_session=None):
	"""
    Facebook connect using a user's session key or an infinite session

    Usage:
	connected = facebook_connect(request, facebook_settings)
	if connected:
		user = get_facebook_user(request.facebook)
	"""

	if not request.facebook: add_facebook_instance(request,settings)
	fb = request.facebook
	
	if request.vars.session != None:
		if infinite_session == None:
			fb.session_key = request.vars.session.split('{"session_key":"')[1].split('","uid":')[0]
			fb.expires = 0
		else:
			fb.session_key = infinite_session

		fb.uid = request.vars.session.split('"uid":')[1].split(',"expires":')[0]
		fb.auth.createToken()
	return True if fb.session_key != None else False



if __name__ == '__main__':
    # sample desktop application

    api_key = ''
    secret_key = ''

    facebook = Facebook(api_key, secret_key)

    facebook.auth.createToken()

    # Show login window
    # Set popup=True if you want login without navigational elements
    facebook.login()

    # Login to the window, then press enter
    print 'After logging in, press enter...'
    raw_input()

    facebook.auth.getSession()
    print 'Session Key:   ', facebook.session_key
    print 'Your UID:      ', facebook.uid

    info = facebook.users.getInfo([facebook.uid], ['name', 'birthday', 'affiliations', 'sex'])[0]

    print 'Your Name:     ', info['name']
    print 'Your Birthday: ', info['birthday']
    print 'Your Gender:   ', info['sex']

    friends = facebook.friends.get()
    friends = facebook.users.getInfo(friends[0:5], ['name', 'birthday', 'relationship_status'])

    for friend in friends:
        print friend['name'], 'has a birthday on', friend['birthday'], 'and is', friend['relationship_status']

    arefriends = facebook.friends.areFriends([friends[0]['uid']], [friends[1]['uid']])

    photos = facebook.photos.getAlbums(facebook.uid)

from gluon.storage import Storage
facebook_settings=Storage()

