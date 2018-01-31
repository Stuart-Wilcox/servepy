# python lib emulating Expressjs lib
import os
import socketserver
import traceback
import threading

class express():
    def __init__(self):
        pass
    def json(self, options=None):
        # options:{
        #  inflate: Boolean=true,
        #  limit: Mixed='100kb',
        #  reviver: Function=None,
        #  strict: Boolean=true,
        #  type: Mixed='application/json',
        #  verify: Function=None
        # }
        pass
    def static(self, root, options=None):
        # options:{
        #  dotfiles: String='ignore',
        #  etag: Boolean=true,
        #  extensions: Mized=false
        #  fallthrough: Boolean=true,
        #  immutable: Boolean=false
        #  index: Mized="index.html"
        #  lastModified: Boolean=true
        #  maxAge: Number=0
        #  redirect: Boolean=true,
        #  setHeaders: Function=None
        # }
        pass
    def Router(self, options=None):
        # options:{
        #  caseSensitive: Boolean=false,
        #  mergeParams: Boolean=false
        #  strict: Boolean=false
        # }
        pass
    def urlencoded(self, options=None):
        # options:{
        #  extended: Boolean=true,
        #  inflate: Boolean=true,
        #  limit: Mixed='100kb'
        #  parameterLimit: Number=1000
        #  type: Mized='application/x-www-form-urlencoded',
        #  verify: Function=None
        # }
        pass

class App():

    # class used by the socket server to handle incoming requests
    class RequestHandler(socketserver.ThreadingMixIn, socketserver.BaseRequestHandler):

        # constructor
        def __init__(self, request, client_address, server):
            # call super class constructor
            super().__init__(request, client_address, server)

        # method invoked on incoming request
        def handle(self):
            # self.request is populated by the constructor on instantiation

            # receive the request (a socket.socket object) and decode it using UTF-8
            self.data = self.request.recv(1024).decode('utf-8')

            # wrap all logic in a try - except so that if things go wrong, it sends a default HTTP 500 message
            try:
                # get the request as a request object (see below) and the path as a string
                request, path = self.__parseHttp__(self.data)

                # object to hold the response that will be sent to the client
                response = Response(None)

                # execute the registered middleware and handler callbacks
                self.exec_callbacks(path, request.method, request, response)

                # use the socket to send the response back to the client
                self.request.send(
                    bytes(response.__str__(),'utf-8')
                )
            except Exception:
                # if something goes wrong, the default behaviour is below (send a HTTP 500)
                traceback.print_exc() # print the stack trace for debugging

                # use the socket to send the error response
                self.request.send(bytes("HTTP/1.1 500 Internal Server Error\nContent-Type:text/plain\n\nServer encountered an error. Please check logs", 'utf-8'))

        def __parseHttp__(self, rawRequest):
            # get protocol, method, and path
            httpLine = rawRequest.replace('\r', '').split('\n')[0].split(' ')
            method, path, protocol = httpLine
            completeUrl = protocol.split('/')[0].lower() + '://' + self.server.app._getHostname() + ':' + str(self.server.app._getPort()) + path

            rawRequest = rawRequest.replace('\r', '').split('\n')[1:] # format line endings then split by them. Remove the http header line

            headers = dict()
            section = 0
            body = None

            # iterate through lines of the request
            for index, line in enumerate(rawRequest):

                if section == 0:
                    # headers
                    line = line.split(':', 1) # split the header line by name:value pairs
                    if line[0] is None or line[0]=='':
                        # the is a newline after the headers but before the body, so change sections from headers to body
                        section += 1
                        continue
                    headers[line[0]] = line[1] # add the entry to the headers dictionary
                else:
                    #body
                    body = '\n'.join(rawRequest[index:]) # add the entire body in one chunk, after putting the lines together
                    break

            return Request(self.server.app, completeUrl, protocol, method, headers, body=body, params=dict(), cookies=None, baseUrl=None), path

        def exec_callbacks(self, path, method, request, response):
            # get the callbacks in order
            middleware, endware = self.server.app._routePath(path, method)

            # middleware (Path, function)
            # endware (Path, method, callback)

            class Next:
                def __init__(self, next=False):
                    self.n = next
                def false(self):
                    self.n = False
                def toggle(self):
                    if self.n:
                        self.n = False
                    else:
                        self.n = True
                def next(self):
                    self.n = True

            # execute middleware first

            if len(middleware) != 0: # if there is any middleware then execute it

                next = Next(True) #instantiate the next tracker

                for path, function in middleware: # iterate over the middleware [ (Path, function) ]

                    next.toggle()# toggle the next to get it ready for usage

                    # set req.query and req.params
                    request.query.update(path.query)
                    request.params.update(path.params)

                    function(request, response, next.next)

                    if response._sent:
                        # the middleware called send on the response so we are done in exec_callbacks
                        return
                    if not next.n:
                        # next() was never called so we can just kill this thread since it will hang forever
                        # TODO test this
                        threading.current_thread()._is_running = False

            if len(endware) is 0:
                # there is nothing to do so give the 404 error message
                response.status(404).send("Cannot %s %s" % (method, path.path))
                return
            else:
                path, method, callback = endware

                callback(request, response)

                if not response._sent:
                    # the object was never sent so we can just kill this thread
                    # TODO test this
                    threading.current_thread()._is_running = False


    class Server(socketserver.TCPServer):
        """
        The implementation of the underlying socket server. This class is used to wrap the attribute of app (the parent/owner app)
        """
        def __init__(self, server_address, RequestHandlerClass, app, bind_and_activate=True):
            # call super class constructor
            super().__init__(server_address, RequestHandlerClass, bind_and_activate)
            # this is the key, getting a reference to the parent application which owns this
            self.app = app

    def __init__(self):
        self.locals = None  # local properties to application
        self.mountpath = None  # patterns on which a sub app mounted

        self.__listening = False # if the app object is listening (called .listen() )
        self.routers = [Router()] # list of routers on this app. The first one is for general usage
        self.__hostname = None # optionally used when listening

    def on(self, event, callback):
        pass

    def all(self, path, callback, *args, **kwargs):
        # like app.METHOD() but matches all HTTP verbs
        self.routers[0].all(path=path, callback=callback)
        return

    def delete(self, path, callback, *args, **kwargs):
        # routes HTTP DELETE requests to the specified path and callback(s)
        self.routers[0].delete(path, callback)
        return self

    def disable(self, name):
        # set name to false
        pass

    def disabled(self, name):
        # true if setting name is disabled
        pass

    def enable(self, name):
        # set name to true
        pass

    def enabled(self, name):
        # true if setting name is enabled
        pass

    def engine(self, ext, callback):
        # register the given template engine
        pass

    def get(self, path, callback, *args, **kwargs):
        # routes HTTP GET requests to the specified path and callback(s)
        self.routers[0].get(path, callback)
        return self

    def listen(self, path=None, callback=None, port=8080, hostname='localhost', backlog=None):
        # starts a UNIX socket and listens for connections on the given path

        # check the quick way if the server is already listening
        if self.__listening:
            raise Exception('Already listening')
        else:

            self.__listening = True # toggle listening
            self.__path = path
            self.__port = port
            self.__hostname = hostname
            self.__backlog = backlog

            self.__socketserver = self.Server((self.__hostname, self.__port), self.RequestHandler, self, False) # instantiate the socket server
            # this allows for graceful shutdown
            self.__socketserver.allow_reuse_address = True
            self.__socketserver.server_bind()
            self.__socketserver.server_activate()
            try:
                # start the underlying server
                self.__socketserver.serve_forever()
            except KeyboardInterrupt:
                # gracefully handle shutdown
                self.__socketserver.shutdown()
                self.__socketserver.server_close()

    def param(self, callback, name=None):
        # add callback to route parameters
        pass

    def path(self):
        # canonical path of the app
        return self.__path

    def post(self, path, callback, *args, **kwargs):
        # routes HTTP POST requests to the specified path and callback(s)
        self.routers[0].post(path, callback)
        return self

    def put(self, path, callback, *args, **kwargs):
        # routes HTTP PUT requests to the specified path and callback(s)
        self.routers[0].put(path, callback)
        return self

    def render(self, view, callback, locals=None):
        # returns rendered HTML view via the callback function
        pass

    def route(self, path):
        # returns an instance of a single route which can be used like a Router
        router = Router()
        self.routers.append(router)
        return router

    def set(self, name, value):
        # assigns setting name to value
        pass

    def use(self, callback, path='/', *args, **kwargs):
        # mounts the specified middleware function(s) at the specified path

        if type(callback) is Router: # the callback is a router
            self.routers.append(callback)
        else: # the callback is a function
            self.routers[0].use(path, callback)

    def _getHostname(self):
        return self.__hostname

    def _getPort(self):
        return self.__port

    def _getIp(self):
        return '127.0.0.1' # TODO

    def _routePath(self, path, method):
        """Given the path and http method, this function will attempt to find a single endware and any middleware prepared to handle it"""

        endware = None # hold the endware that will be given to the handler
        middleware = [] # the middleware that will be given to the handler

        for router in self.routers: # iterate through the app's known routers

            endware_path_match = router._endware_path_match(path, method) # get the endware that matches a path (Path, method, callback)
            middleware_path_matches = router._middleware_path_match(path) # get the list of middlewares that match the path (Path, function)

            middleware.extend(middleware_path_matches) # append all matching middleware

            if endware is None:
                endware = endware_path_match
        return (middleware, endware)


class Router():

    class PathNameError(Exception):
        pass

    def __init__(self):
        self.sub_routers = [] # list of sub_routers of the form (Router, path)

        self.path_prefix = '' # indicates the path that this router is mounted on relative to parent routers
                              # when a parent mounts a new router it must manually set this attribute

        self.endware_paths = set() # all endware paths under this router for fast lookup in path matching
        self.middleware_paths = set() # all middleware paths under this router for fast lookup in path matching

        self.endware_path_table = list() # list of tuples of the form (path, method, callback) where path is an array of the canonical path split by '/' and callback is an ENDWARE function
        self.middleware_path_table = list() # list of tuples of the form (path, callback) where path is an array of the canonical path split by '/' and callback is a MIDDLEWARE function

    def all(self, path, callback):
        # add endware under each of the available methods
        self.__add_endware(path, 'GET', callback)
        self.__add_endware(path, 'POST', callback)
        self.__add_endware(path, 'PUT', callback)
        return self.__add_endware(path, 'DELETE', callback)

    def get(self, path, callback):
        return self.__add_endware(path, 'GET', callback)
        return self

    def post(self, path, callback):
        return self.__add_endware(path, 'POST', callback)

    def put(self, path, callback):
        return self.__add_endware(path, 'PUT', callback)

    def delete(self, path, callback):
        return self.__add_endware(path, 'DELETE', callback)

    def __add_endware(self, path, method, callback):
        path = self.__validate_path(path) # format the path

        path = Path(path) # make the path string into a Path object

        self.endware_paths.add(path) # add the path to the endware path set
        self.endware_path_table.append( (path, method, callback) ) # add the (path,method,callback) tuple

        return self

    def param(self, name, callback):
        pass

    def route(self, path):
        path = self.__validate_path(path) # format the path

        path = Path(path)

        sub_router = Router() # instantiate new child router
        sub_router.path_prefix = path # indicate the child router is mounted under path

        self.sub_routers.append( (sub_router, path) ) # mount the child router

        return sub_router

    def use(self, path, function, *args, **kwargs):
        path = self.__validate_path(path) # format the path

        path = Path(path)

        self.middleware_paths.add(path) # add the path to middleware path set
        self.middleware_path_table.append(  (path,function) ) # add the (path,function) tuple

    def __validate_path(self, path):
        # paths must begin with a slash (this is enforced)
        if not path.startswith('/'):
            raise self.PathNameError("Path must start with character '/'")

        # paths must end with a slash (for compatability with older code)
        # but to allow users to omit the slash, just add one as needed
        if not path.endswith('/'):
            return path + '/'

        return path

    def __get_endware_paths(self):
        # method to get the endware paths on this router and all child routers recursively

        if len(self.sub_routers) is 0:
            # there are no children (leaf) so just return the local endware paths
            return self.endware_paths

        else:
            # this router does have children so we must add all of their endware paths and append all of those to this router's endware paths

            endware_paths = [] # hold the endware paths here

            for sub_router in self.sub_routers: # iterate over children
                # sub_router is a tuple of (Router, mount_path)
                sub_router_mount_path = sub_router[1]

                for endware_path in sub_router[0].__get_endware_paths(): # iterate over the child's paths (calling it's get_endware_paths() function in a recursive manner)
                    # endware_path is a Path

                    # add the sub router mount path to the start and remove the '/' in the beginning (so there isn't a '//'')
                    endware_path.path = sub_router_mount_path + endware_path.path[1:]

                    # append the path to the paths that get returned
                    endware_paths.append(endware_path)

            # after getting all the child endware_paths to paths, add this router's endware_paths
            endware_paths.extend(self.endware_paths)

            return endware_paths

    def __get_middleware_paths(self):
        # method to get the middleware paths on this router and all child routers recursively

        if len(self.sub_routers) is 0:
            # there are no children (leaf) so just return the local middleware paths
            return self.middleware_paths

        else:
            # this router does have children so we must add all of their middleware paths and append all of those to this router's middleware paths

            middleware_paths = [] # hold the middleware paths here

            for sub_router in self.sub_routers: # iterate over children
                #sub_router is a tuple of (Router, mount_path)
                sub_router_mount_path = sub_router[1]

                for middleware_path in sub_router[0].__get_middleware_paths(): # iterate over middleware paths in the sub router (recursively)
                    # middleare_path is a Path

                    # remove the '/' in the beginning (so there isn't a '//'')
                    middleware_path.path = sub_router_mount_path + middleware_path.path[1:]

                    # append the path to the paths that get returned
                    middleware_paths.append(middleware_path)

            middleware_paths.extend(self.middleware_paths) # add the current router's middleware paths

            return middleware_paths

    def _get_endware_path_table(self):
        # method to get the endware path table recursively

        if len(self.sub_routers) is 0:
            # this router has no children (leaf) so just return the path table
            return self.endware_path_table

        else:
            # this router does have children so we must add all the endware path table entries to this router's entries

            endware_path_tables = [] # hold the endware path table entries

            for sub_router in self.sub_routers: # iterate over sub routers
                #sub_router is a tuple of (Router, mount_path)
                sub_router_mount_path = sub_router[1].path_str()

                for endware_path_table in sub_router[0]._get_endware_path_table():
                    # endware_path_table is a tuple (path, method, callback)

                    endware_path = endware_path_table[0]
                    endware_method = endware_path_table[1]
                    endware_callback = endware_path_table[2]

                    endware_path.path = sub_router_mount_path + endware_path.path_str(remove_leading_slash=True) # put the sub router mount path in front of the path and remove the extra '/'

                    endware_path_tables.append( (endware_path, endware_method, endware_callback) ) # add the child path table entries to the tables

            endware_path_tables.extend(self.endware_path_table) # add this router's path tables to the tables

        return endware_path_tables

    def _get_middleware_path_table(self):
        # method to get the middleware path table recursively

        if len(self.sub_routers) is 0:
            # this router has no children (leaf) so just return the path table
            return self.middleware_path_table

        else:
            # this router does have children so we must add all the middleware path table entries to this router's entries

            middleware_path_tables = [] # hold the middleware path endware_path_tables

            for sub_router in self.sub_routers: # iterate over sub routers
                #sub_router is a tuple of (Router, mount_path)
                sub_router_mount_path = sub_router[1]

                for middleware_path_table in sub_router[0]._get_middleware_path_table():
                    # middleware_path_table is a tuple (path, callback)

                    middleware_path = middleware_path_table[0]
                    middleware_callback = middleware_path_table[1]

                    middleware_path.path = sub_router_mount_path + middleware_path.path_str(remove_leading_slash=True) # put the sub router path in the start and remove the extra '/'

                    middleware_path_tables.append( (middleware_path, middleware_callback) ) # add the child path table entries to the tables

            middleware_path_tables.extend(self.middleware_path_table) # add this router's path tables to the tables

        return middleware_path_tables

    def _endware_path_match(self, path, method):
        candidate = None # only one possible candidate

        # TODO: make sure the path matches look for a literal match before a path param match

        for endware_path_table_entry in self._get_endware_path_table(): # iterate over endware path table
            endware_path = endware_path_table_entry[0]
            endware_method = endware_path_table_entry[1]
            endware_callback = endware_path_table_entry[2]

            if endware_path.match(Path(path)) and endware_method == method: # use Path.match() to test for matching
                candidate = (endware_path, endware_method, endware_callback) # set the candidate
                break # exit from the loop once we get one
        return candidate

    def _middleware_path_match(self, path):
        candidates = [] # list of possible candidates

        for middleware_path, middleware_function in self._get_middleware_path_table(): # get the endware paths from the recursive method

            if middleware_path.match(Path(path), middleware=True): # use Path.macth() with the middleware flag to test for matching
                candidates.append( (middleware_path, middleware_function) ) # append to the candidates

        return candidates


class Path():
    class PathNameError(Exception):
        pass

    def __init__(self, path):
        # check for the empty string
        if len(path) == 0:
            raise self.PathNameError('Path name cannot be blank')


        if not path.startswith('/'):
            raise PathNameError('Invalid pathname, must start with \'/''')
        if not path.endswith('/') and path != '/':
            path = path + '/'

        self.params = dict()
        self.query = dict() # make a dictionary for the query string

        if '?' in path:
            query_string = path.split('?')[1] # split by the question mark and take the second half

            for q in query_string.split('&'):
                # iterate through the query parameters and populate the dictionary, delimeted by '&'
                q = q.split('=') # split the query by name and value pairs, delimeted by '='
                self.query[q[0]]=q[1] # fill the dictionary

        self.path = path.split('/')[1:-1] # split the path by slashes and get rid of the first and last since they are always blank

    def path_str(self, remove_leading_slash=False):
        if remove_leading_slash:
            return '/'.join(self.path)[1:]
        else:
            return '/'.join(self.path)

    def match(self, path, middleware=False):
        # path can be a string or a Path object
        if type(path) is str:
            actual = path
        else:
            actual = path.path
        expected = self.path

        # unless middleware, the paths must have the same length to match
        if not middleware:
            if len(expected) != len(actual):
                return False]

        for index, e in enumerate(expected):
            # iterate over pieces of url. if they match, continue, if there is a path param deal with it. otherwise they dont match
            if middleware and index >= len(actual):
                return False
            a = actual[index]
            if a == e:
                continue
            elif e.startswith(':'):
                # deal with path param
                self.params[e.split(':')[1]] = a
            else:
                return False
        return True

    def __eq__(self, other):
        if type(other) is Path:
            return self.path == other.path
        else:
            return False

    def __hash__(self):
        return hash('/'.join(self.path))

    def __str__(self):
        return '/'.join(self.path)


class Request():
    def __init__(self, app, completeUrl, protocol, method, headers=dict(), body=None, params={}, cookies={}, baseUrl=None, path=None):
        self.app = app
        self.baseUrl = baseUrl
        self.body = body
        self.cookies = cookies
        self.fresh = None
        self.hostname = app._getHostname()
        self.headers = headers
        self.ip = app._getIp()
        self.ips = []
        self.method = method
        self.originalUrl = ('/' + '/'.join(completeUrl.split('/')[3:])).replace('//', '/')
        self.params = params
        self.path = path
        self.protocol = protocol

        if len(completeUrl.split('?', 1)) > 1:
            queryString = completeUrl.split('?', 1)[1]
            self.query = {}
            for pair in queryString.split('&'):
                pair = pair.split('=')
                self.query[pair[0]]=pair[1]
        else:
            self.query = {}

        self.route = None
        self.secure = None
        self.signedCookies = None
        if 'Cache-Control' in headers:
            self.stale = headers['Cache-Control']=='No-Cache'
            self.fresh = not self.stale
        else:
            self.stale = False
            self.fresh = True
        self.subdomains = None
        self.xhr = None

    def accepts(self, types):
        if 'Accept' not in self.headers:
            return False
        return types in self.headers['Accept'].split(',')

    def acceptsLanguages(self, lang, *args, **kwargs):
        pass

    def get(self, field):
        return self.getattr(field)

    def isType(self, type):
        pass

    def param(self, name, defaultValue=None):
        raise Error('Deprecated. Use attribute params instead.')

    def range(self, size, options=None):
        pass

    def __str__(self):
        headerString = ''
        for headerName in self.headers:
            headerString+='%s:%s\n'%(headerName, self.headers[headerName])
        return "%s %s %s\n%s\n\n%s" % (self.method, self.originalUrl, self.protocol, headerString, self.body)


class Response():
    def __init__(self, app):
        self.app = app
        self.headersSent = None
        self.locals = None

        self.__headers = {'Content-Type'.upper():'text/plain'}
        self.__body = ''
        self.__status = 200
        self._sent = False

    def append(self, field, value=None):
        field = field.upper()

        try:
            self.__headers[field]
        except KeyError:
            self.__headers[field] = value

        return self

    def attachment(self, filename=None):
        self.set('Content-Disposition', 'attachment')
        if filename is not None:
            extension = filename.split('.')[-1:]
            supportedExtensions = {
                'html':'text/html',
                'css':'text/css',
                'js':'text/javascript',
                'pdf':'application/pdf',
                'json':'application/json',
                'xml':'application/xml',
                'txt':'text/plain',
                'bmp':'image/bmp',
                'gif':'image/gif',
                'jpeg':'image/jpeg',
                'png':'image/png',
                'mpeg':'audio/mpeg',
                'ogg':'audio/ogg',
                'wav':'audio/wav',
                'mp4':'video/mp4',
            }
            try:
                self.set('Content-Type', supportedExtensions[extension])
            except KeyError:
                raise Error('Unsupported file type: %s'%filename)
            self.set('Content-Disposition', 'attachment; filename=%s'%filename)
        return self


    def cookie(self, name, value, options=None):
        pass

    def clearCookie(self, name, options=None):
        pass

    def download(self, path, filename=None, options=None, fn=None):
        pass

    def end(self, data=None, encoding=None):
        pass

    def format(self, object):
        pass

    def get(self, field):
        field = field.upper()
        try:
            return self.__headers[field]
        except KeyError:
            return None

    def json(self, body=None):
        self.headers['Content-Type'] = 'application/json'.upper()
        if body is not None:
            #convert body to json
            jsonBody = body
            self.send(jsonBody)
        else:
            self.send('{}')

    def jsonp(self, body=None):
        pass

    def links(self, links):
        pass

    def location(self, path):
        pass

    def redirect(self, path, status=None):
        pass

    def render(self, view, locals=None, callback=None):
        pass

    def send(self, body=None):
        self._body = body
        self.append('Content-Length'.upper(), len(bytes(body, 'utf-8')))
        self.append('Connection'.upper(), 'close')
        self._sent = True

    def sendFile(self, path, options=None, fn=None):
        pass

    def sendStatus(self, statusCode):
        pass

    def set(self, field, value=None):
        pass

    def status(self, code=None):
        if code is not None:
            if code < 100 or code > 600:
                raise Error('Invalid http code supplied')
            self.__status = code
            return self
        else:
            return self.__status

    def type(self, type):
        pass

    def vary(self, field):
        pass

    def __str__(self):
        headerString = ''
        for headerName in self.__headers:
            headerString+='%s:%s\n'%(headerName, self.__headers[headerName])
        statusString = {
            200:'OK',
            201:'Created',
            204:'No Content',
            301:'Moved Permanently',
            304:'Not Modified',
            307:'Temporary Redirect',
            308:'Permanent Redirect',
            400:'Bad Request',
            401:'Unauthorized',
            403:'Forbidden',
            404:'Not Found',
            405:'Method Not Allowed',
            415:'Unsupported Media Type',
            500:'Internal Server Error',
            501:'Not Implemented',
            503:'Service Unavailable'
        }


        return 'HTTP/1.1 %s %s\n%s\n%s' % (self.__status, statusString[self.__status], headerString, self._body)





if __name__=='__main__':

    def middleware_func_1(req, res, next):
        print("[%s] %s" % (req.method, req.originalUrl) )
        next()

    def dummy_func_1(req, res):
        res.append('Content-Type', 'text/plain').send("Hello World")

    def dummy_func_2(req, res):
        res.append('Content-Type', 'application/json').status(200).send('{"success":"true"}')

    app = App()
    router = Router()
    router.use('/', middleware_func_1)
    router.get('/', dummy_func_1).get('/working', dummy_func_2)
    app.use(router)
    app.listen(port=8080, hostname='localhost')
