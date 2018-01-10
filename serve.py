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

            return Request(self.server.app, completeUrl, protocol, method, headers, body=body, params=None, cookies=None, baseUrl=None), path

        def exec_callbacks(self, path, method, request, response):
            # get the callbacks in order
            endware, middleware = self.server.app._routePath(path, method)

            callbacks = [c for p,m,c in endware]
            middleware_callbacks = [c for p, c in middleware]

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

            if len(middleware_callbacks) != 0:
                next = Next(True)
                for index, callback in enumerate(middleware_callbacks):
                    next.toggle()

                    callback(request, response, next.next)
                    if response._sent:
                        return
                    if not next.n:
                        raise Exception('Must use next()')

            if len(callbacks) == 0:
                # there is nothing to do
                response.status(404).send("Cannot %s %s" % (method, path))
                return

            # execute callbacks in order
            for index, callback in enumerate(callbacks):
                n = False
                def next():
                    n = True
                try:
                    callback(request, response)
                except TypeError:
                    callback(request, response, next)


    # the implementation of the underlying socket server
    class Server(socketserver.TCPServer):
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
        pass

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
        self.routers.append(callback)

    def _getHostname(self):
        return self.__hostname

    def _getPort(self):
        return self.__port

    def _getIp(self):
        return '127.0.0.1' # TODO

    def _routePath(self, path, method):
        entries = []
        middlewareEntries = []
        for router in self.routers:
            matches = router._pathMatch(path)
            middlewareMatches = router._middlewarePathMatch(path)
            if middlewareMatches is not None and len(middlewareMatches) != 0:
                middlewareEntries.extend(middlewareMatches)
            if matches is None or len(matches) == 0:
                continue
            entries.extend(matches)
        return (entries, middlewareEntries)


class Router():

    class PathNameError(Exception):
        pass

    def __init__(self):
        self.subRouters = [] # list of subrouters of the form (Router, path)
        self.pathPrefix = ''
        self.paths = set() # all paths under this router for qucker lookup
        self.middlewarePaths = set()
        self.pathTable = list() # list of tuples of the form (path, method, callback) where callback is an ENDWARE function
        self.middlewarePathTable = list() # list of tuples of the form (path, callback) where callback is a MIDDLEWARE function

    def all(self, path, callback, *args, **kwargs):
        self._validatePath(path)
        self.get(path, callback, args, kwargs)
        self.post(path, callback, args, kwargs)
        self.put(path, callback, args, kwargs)
        self.delete(path, callback, args, kwargs)
        return self

    def get(self, path, callback, *args, **kwargs):
        self._validatePath(path)
        self.paths.add(path)
        self.pathTable.append((self._buildpath(path), 'GET', callback))
        return self

    def post(self, path, callback, *args, **kwargs):
        self._validatePath(path)
        self.paths.add(path)
        self.pathTable.append((self._buildpath(path), 'POST', callback))
        return self

    def put(self, path, callback, *args, **kwargs):
        self._validatePath(path)
        self.paths.add(path)
        self.pathTable.append((self._buildpath(path), 'PUT', callback))
        return self

    def delete(self, path, callback, *args, **kwargs):
        self._validatePath(path)
        self.paths.add(path)
        self.pathTable.append((self._buildpath(path), 'DELETE', callback))
        return self

    def param(self, name, callback):
        pass

    def route(self, path):
        self._validatePath(path)
        subRouter = Router()
        subRouter.pathPrefix = path
        self.subRouters.append( (subRouter, path) )

        return subRouter

    def use(self, path, function, *args, **kwargs):
        if path is None:
            path = '/'
        self._validatePath(path)
        self.middlewarePaths.add(path)
        self.middlewarePathTable.append( (self._buildpath(path), function) )

    def _validatePath(self, path):
        if not path.startswith('/'):
            raise self.PathNameError("Path must start with character '/'")
        if not path.endswith('/'):
            raise self.PathNameError("Path must end with character '/'")

    def _buildpath(self, path):
        # append the path prefix to the given path, remove slash in between
        return self.pathPrefix[:-1] + path

    def _getPaths(self):
        if len(self.subRouters) is 0:
            # this is a leaf
            return self.paths
        else:
            # this is the root router
            paths = []
            for subRouterEntry in self.subRouters:
                for path in subRouterEntry[0]._getPaths(): # subRouterEntry[0] is the router, [1] is the path
                    paths.append(subRouterEntry[1]+path[1:])
            paths.extend(self.paths)
            return paths

    def _getMiddlewarePaths(self):
        if len(self.subRouters) is 0:
            # this is a leaf
            return self.middlewarePaths
        else:
            # this is the root router
            paths = []
            for subRouterEntry in self.subRouters:
                for path in subRouterEntry[0]._getMiddlewarePaths(): # subRouterEntry[0] is the router, [1] is the path
                    paths.append(subRouterEntry[1]+path[1:])
            paths.extend(self.middlewarePaths)
            return paths

    def _getPathTable(self):
        if len(self.subRouters) is 0:
            return self.pathTable
        else:
            pathTable = []
            for subRouterEntry in self.subRouters:
                for pathTableEntry in subRouterEntry[0]._getPathTable():
                    pathTable.append( (pathTableEntry[0], pathTableEntry[1], pathTableEntry[2]) )

            pathTable.extend(self.pathTable)
        return pathTable

    def _getMiddlewarePathTable(self):
        if len(self.subRouters) is 0:
            return self.middlewarePathTable
        else:
            middlewarePathTable = []
            for subRouterEntry in self.subRouters:
                for middlewarePathTableEntry in subRouterEntry[0]._getMiddlewarePathTable():
                    middlewarePathTable.append( (middlewarePathTableEntry[0], middlewarePathTableEntry[1]) )
            middlewarePathTable.extend(self.middlewarePathTable)
        return middlewarePathTable

    def _pathMatch(self, path):
        path = path.split('?')[0]+'/' # get rid of query params
        path = path.replace('//', '/') # remove any errors in previous step
        path = path.split('/')[1:-1] # get rid of 'http:/' and the trailing '/'
        paths = self._getPaths() # get paths in a recursive manner
        candidate_paths = [] # holder for the candidates

        for p in paths:
            # remove everything before first '/' and after last '/'
            p = p.split('/')[1:-1]
            p_str = '/'.join(p)
            p_str = '/'+p_str+'/'
            p_str = p_str.replace('//', '/')

            if p == path:
                for entry in self._getPathTable():
                    if entry[0] == p_str:
                        candidate_paths.append(entry)

        return candidate_paths

    def _middlewarePathMatch(self, path):
        path = path.split('?')[0]+'/' # get rid of query params
        path = path.replace('//', '/') # remove any errors in previous step
        path = path.split('/')[1:-1] # get rid of 'http:/' and the trailing '/'
        paths = self._getMiddlewarePaths() # get paths in a recursive manner
        candidate_paths = [] # holder for the candidates

        for p in paths:
            # remove everything before first '/' and after last '/'
            p = p.split('/')[1:-1]
            p_str = '/'.join(p)
            p_str = '/'+p_str+'/'
            p_str = p_str.replace('//', '/')

            pathSubset = True

            if len(p) <= len(path):
                for index, section in enumerate(p):
                    if section != path[index]:
                        pathSubset = False

            if pathSubset:
                for entry in self._getMiddlewarePathTable():
                    availPathSet = entry[0]
                    pathSet = p_str

                    if availPathSet <= pathSet:
                        candidate_paths.append(entry)

        return candidate_paths


class Request():
    def __init__(self, app, completeUrl, protocol, method, headers=dict(), body=None, params=None, cookies={}, baseUrl=None, path=None):
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
    router.route('/').get('/', dummy_func_1).get('/working/', dummy_func_2)
    app.use(router)
    app.listen(port=8080, hostname='localhost')
