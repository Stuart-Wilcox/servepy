# python lib mimicking Express.js
import os, sys
import socketserver
import traceback
import threading


class App():

    # class used by the socket server to handle incoming requests
    class __RequestHandler(socketserver.ThreadingMixIn, socketserver.BaseRequestHandler):

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

        # TODO move this to its own class
        def __parseHttp__(self, rawRequest):
            # get protocol, method, and path
            httpLine = rawRequest.replace('\r', '').split('\n')[0].split(' ')
            method, path, protocol = httpLine
            completeUrl = protocol.split('/')[0].lower() + '://' + self.server.app._get_hostname() + ':' + str(self.server.app._get_port()) + path

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
            middleware, endware = self.server.app._route_path(path, method)

            # middleware (Path, function)
            # endware (Path, method, callback)

            class __Next:
                def __init__(self):
                    self.n = threading.Event()

                def next(self):
                    self.n.set()

                def wait(self):
                    try:
                        val = self.n.wait()
                    except Exception:
                        print('EXEC')
                    self.n.clear()
                    return val

            class __TimeoutException(Exception):
                pass

            # execute middleware first

            if len(middleware) != 0: # if there is any middleware then execute it

                next = __Next() #instantiate the next tracker

                for path, function in middleware: # iterate over the middleware [ (Path, function) ]

                    # set req.query and req.params
                    request.query.update(path.query)
                    request.params.update(path.params)

                    request.route = path.path_str()

                    try:
                        function(request, response, next.next)
                    except TypeError:
                        function(request, response)

                    next.wait()

                    if response._sent:
                        return

            if endware is None:
                # there is nothing to do so give the 404 error message
                response.status(404).send("Cannot %s %s" % (method, path))
                return
            else:
                path, method, callback = endware

                # set req.query and req.params
                request.query.update(path.query)
                request.params.update(path.params)

                request.route = path.path_str()

                callback(request, response)

                if not response._sent:
                    # the object was never sent so we can just kill this thread
                    # TODO test this
                    threading.current_thread()._is_running = False

    class __Server(socketserver.TCPServer):
        """
        The implementation of the underlying socket server. This class is used to wrap the attribute of app (the parent/owner app)
        """
        def __init__(self, server_address, RequestHandlerClass, app, bind_and_activate=True):
            # call super class constructor
            super().__init__(server_address, RequestHandlerClass, bind_and_activate)
            # this is the key, getting a reference to the parent application which owns this
            self.app = app

    def __init__(self):
        self.locals = dict()  # local properties to application
        self.mountpath = ''  # patterns on which a sub app mounted

        self.__listening = False # if the app object is listening (called .listen() )
        self.__routers = [Router()] # list of routers on this app. The first one is for general usage
        self.__hostname = None # optionally used when listening

    def all(self, path, callback):
        # like app.METHOD() but matches all HTTP verbs
        self.__routers[0].all(path=path, callback=callback)
        return self

    def delete(self, path, callback):
        # routes HTTP DELETE requests to the specified path and callback(s)
        self.__routers[0].delete(path, callback)
        return self

    def get(self, path, callback):
        # routes HTTP GET requests to the specified path and callback(s)
        self.__routers[0].get(path, callback)
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

            self.__socketserver = self.__Server((self.__hostname, self.__port), self.__RequestHandler, self, False) # instantiate the socket server
            # this allows for graceful shutdown
            self.__socketserver.allow_reuse_address = True
            self.__socketserver.server_bind()
            self.__socketserver.server_activate()
            try:
                # start the underlying server
                if callback is not None:
                    callback()
                self.__socketserver.serve_forever()
            except KeyboardInterrupt:
                # gracefully handle shutdown
                self.__socketserver.shutdown()
                self.__socketserver.server_close()

    def path(self):
        # canonical path of the app
        return self.__path

    def post(self, path, callback):
        # routes HTTP POST requests to the specified path and callback(s)
        self.__routers[0].post(path, callback)
        return self

    def put(self, path, callback):
        # routes HTTP PUT requests to the specified path and callback(s)
        self.__routers[0].put(path, callback)
        return self

    def route(self, path):
        # returns an instance of a single route which can be used like a Router
        router = Router()
        router.path_prefix = path
        self.__routers.append(router)
        return router

    def set(self, name, value):
        # assigns setting name to value
        self.locals[name] = value
        return self

    def use(self, callback, path='/'):
        # mounts the specified middleware function(s) at the specified path

        if type(callback) is Router: # the callback is a router
            self.__routers.append(callback)
        else: # the callback is a function
            self.__routers[0].use(path, callback)

    def _get_hostname(self):
        return self.__hostname

    def _get_port(self):
        return self.__port

    def _get_ip(self):
        return '127.0.0.1' # TODO

    def _route_path(self, path, method):
        """Given the path and http method, this function will attempt to find a single endware and any middleware prepared to handle it"""

        endware = None # hold the endware that will be given to the handler
        middleware = [] # the middleware that will be given to the handler

        for router in self.__routers: # iterate through the app's known routers

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
        self.__sub_routers = [] # list of sub_routers of the form (Router, path)

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

    def post(self, path, callback):
        return self.__add_endware(path, 'POST', callback)

    def put(self, path, callback):
        return self.__add_endware(path, 'PUT', callback)

    def delete(self, path, callback):
        return self.__add_endware(path, 'DELETE', callback)

    def __add_endware(self, path, method, callback):
        path = self.__validate_path(path) # format the path

        path = _Path(path) # make the path string into a Path object

        self.endware_paths.add(path) # add the path to the endware path set
        self.endware_path_table.append( (path, method, callback) ) # add the (path,method,callback) tuple

        return self

    def route(self, path):
        path = self.__validate_path(path) # format the path

        if path != '/':
            path = _Path(path)

            sub_router = Router() # instantiate new child router
            sub_router.path_prefix = path # indicate the child router is mounted under path

            self.__sub_routers.append( (sub_router, path) ) # mount the child router

            return sub_router
        else:
            return self

    def use(self, path, function):
        path = self.__validate_path(path) # format the path

        path = _Path(path)

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

    def __get_endware_path_table(self):
        # method to get the endware path table recursively

        if len(self.__sub_routers) is 0:
            # this router has no children (leaf) so just return the path table
            return self.endware_path_table

        else:
            # this router does have children so we must add all the endware path table entries to this router's entries

            endware_path_tables = [] # hold the endware path table entries

            for sub_router in self.__sub_routers: # iterate over sub routers
                #sub_router is a tuple of (Router, mount_path)
                sub_router_mount_path = sub_router[1]
                #print(sub_router_mount_path)

                for endware_path_table in sub_router[0].__get_endware_path_table():
                    # endware_path_table is a tuple (path, method, callback)

                    endware_path = endware_path_table[0]
                    endware_method = endware_path_table[1]
                    endware_callback = endware_path_table[2]

                    # this line is resetting the enware_path value
                    #endware_path.path = sub_router_mount_path.path + endware_path.path

                    sub_router_endware_path = _Path('/')
                    sub_router_endware_path.path = sub_router_mount_path.path + endware_path.path

                    endware_path_tables.append( (sub_router_endware_path, endware_method, endware_callback) ) # add the child path table entries to the tables

            endware_path_tables.extend(self.endware_path_table) # add this router's path tables to the tables

        return endware_path_tables

    def __get_middleware_path_table(self):
        # method to get the middleware path table recursively

        if len(self.__sub_routers) is 0:
            # this router has no children (leaf) so just return the path table
            return self.middleware_path_table

        else:
            # this router does have children so we must add all the middleware path table entries to this router's entries

            middleware_path_tables = [] # hold the middleware path endware_path_tables

            for sub_router in self.__sub_routers: # iterate over sub routers
                #sub_router is a tuple of (Router, mount_path)
                sub_router_mount_path = sub_router[1]

                for middleware_path_table in sub_router[0].__get_middleware_path_table():
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

        for endware_path_table_entry in self.__get_endware_path_table(): # iterate over endware path table
            endware_path = endware_path_table_entry[0]
            endware_method = endware_path_table_entry[1]
            endware_callback = endware_path_table_entry[2]

            if endware_path.match(_Path(path)) and endware_method == method: # use Path.match() to test for matching
                candidate = (endware_path, endware_method, endware_callback) # set the candidate
                break # exit from the loop once we get one
        return candidate

    def _middleware_path_match(self, path):
        candidates = [] # list of possible candidates

        for middleware_path, middleware_function in self.__get_middleware_path_table(): # get the endware paths from the recursive method

            if middleware_path.match(_Path(path), middleware=True): # use Path.macth() with the middleware flag to test for matching
                candidates.append( (middleware_path, middleware_function) ) # append to the candidates

        return candidates


class _Path():
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
            path = path.split('?')[0] + '/' # split by the question mark and set the path to the first half and making ure to append a trailing slash

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
                return False

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
        if type(other) is _Path:
            return self.path == other.path
        else:
            return False

    def __hash__(self):
        return hash('/'.join(self.path))

    def __str__(self):
        return '/'.join(self.path)


class Request():
    def __init__(self, app, completeUrl, protocol, method, headers=dict(), body=None, params={}, cookies={}, path=None, baseUrl=None, route=None):
        self.app = app
        self.body = body
        self.cookies = cookies
        self.fresh = None
        self.hostname = app._get_hostname()
        self.headers = headers
        self.ip = app._get_ip()
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

        self.route = route

        if 'Cache-Control' in headers:
            self.stale = headers['Cache-Control']=='No-Cache'
            self.fresh = not self.stale
        else:
            self.stale = False
            self.fresh = True
        self.subdomains = None
        try:
            self.xhr = self.headers['X-Requested-With'.upper()] == 'XMLHttpRequest'
        except KeyError:
            self.xhr = False

    def accepts(self, types):
        if 'Accept' not in self.headers:
            return False
        return types in self.headers['Accept'].split(',')

    def get(self, field):
        try:
            return self.headers[field.upper()]
        except KeyError:
            return None

    def is_type(self, type):
        pass

    def param(self, name, defaultValue=None):
        raise Error('Deprecated. Use attribute params instead.')

    def __str__(self):
        headerString = ''
        for headerName in self.headers:
            headerString+='%s:%s\n'%(headerName, self.headers[headerName])
        return "%s %s %s\n%s\n\n%s" % (self.method, self.originalUrl, self.protocol, headerString, self.body)


class Response():
    def __init__(self, app=None):
        self.app = app
        self.headers_sent = None

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


    def get(self, field):
        field = field.upper()
        try:
            return self.__headers[field]
        except KeyError:
            return None

    def json(self, body=None):
        self.headers['Content-Type'] = 'application/json'.upper()
        self.headers_sent = True
        if body is not None:
            #convert body to json
            jsonBody = body
            self.send(jsonBody)
        else:
            self.send('{}')

    def send(self, body=None):
        self._body = body
        self.set('Content-Length'.upper(), len(bytes(body, 'utf-8')))
        self.set('Connection'.upper(), 'close')
        self.headers_sent = True
        self._sent = True


    def set(self, field, value=None):
        self.__headers[field.upper()] = value

        return self

    def status(self, code=None):
        if code is not None:
            if code < 100 or code > 600:
                raise Error('Invalid http code supplied')
            self.__status = code
            return self
        else:
            return self.__status

    def type(self, type):
        if '/' in type:
            self.headers['Content-Type'.upper()] = type
        return self



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
