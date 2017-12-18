# python lib emulating Expressjs lib
import os
import socketserver
import traceback

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

    class RequestHandler(socketserver.ThreadingMixIn, socketserver.BaseRequestHandler):

        def __init__(self, request, client_address, server):
            super().__init__(request, client_address, server)

        def handle(self):
            self.data = self.request.recv(1024).decode('utf-8')

            # wrap all logic in a try - except so that if things go wrong, it sends a default HTTP 500 message
            try:
                request, path = self.__parseHttp__(self.data)
                response = Response(None)
                self.exec_callbacks(path, request.method, request, response)

                self.request.send(
                    bytes(response.__str__(),'utf-8')
                )

            except Exception:
                traceback.print_exc()
                self.request.send(bytes("HTTP/1.1 500 Internal Server Error\nContent-Type:text/plain\n\nServer encountered an error. Please check logs", 'utf-8'))

        def __parseHttp__(self, rawRequest):
            # get protocol, method, and path
            httpLine = rawRequest.replace('\r', '').split('\n')[0].split(' ')
            method, path, protocol = httpLine

            rawRequest = rawRequest.replace('\r', '').split('\n')[1:]

            headers = dict()
            section = 0
            body = None
            for index, line in enumerate(rawRequest):

                if section == 0:
                    # headers
                    line = line.split(':', 1)
                    if line[0] is None or line[0]=='':
                        section += 1
                        continue
                    headers[line[0]] = line[1]
                else:
                    #body
                    body = '\n'.join(rawRequest[index:])
                    break

            return Request(self.server.app, path, protocol, method, headers, body=body, params=None, cookies=None, baseUrl=None), path

        def exec_callbacks(self, path, method, request, response):
            callbacks = [c for p,m,c in self.server.app._routePath(path, method)]
            if len(callbacks) == 0:
                response.status(404).send("")
                return
            for c in callbacks:
                c(request, response, None)

    class Server(socketserver.TCPServer):
        def __init__(self, server_address, RequestHandlerClass, app, bind_and_activate=True):
            super().__init__(server_address, RequestHandlerClass, bind_and_activate)
            self.app = app

    def __init__(self):
        self.locals = None  # local properties to application
        self.mountpath = None  # patterns on which a sub app mounted

        self.__listening = False
        self.routers = [Router()]
        self.__hostname = None

    def on(self, event, callback):
        pass

    def all(self, path, callback, *args, **kwargs):
        # like app.METHOD() but matches all HTTP verbs
        self.routers[0].all(path=path, callback=callback)
        return

    def delete(self, path, callback, *args, **kwargs):
        # routes HTTP DELETE requests to the specified path and callback(s)
        self.routers[0].delete(path, callback)
        return

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
        self.routers.get(path, callback)
        return

    def listen(self, path=None, callback=None, port=8080, hostname='localhost', backlog=None):
        # starts a UNIX socket and listens for connections on the given path
        if self.__listening:
            raise Exception('Already listening')
        else:
            self.__listening = True
            self.__path = path
            self.__port = port
            self.__hostname = hostname
            self.__backlog = backlog
            self.__socketserver = self.Server((self.__hostname, self.__port), self.RequestHandler, self, False)
            self.__socketserver.allow_reuse_address = True
            self.__socketserver.server_bind()
            self.__socketserver.server_activate()
            try:
                self.__socketserver.serve_forever()
            except KeyboardInterrupt:
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
        return

    def put(self, path, callback, *args, **kwargs):
        # routes HTTP PUT requests to the specified path and callback(s)
        self.router[0].put(path, callback)
        return

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

    def _getIp(self):
        return '127.0.0.1' # TODO

    def _routePath(self, path, method):
        entries = []
        for router in self.routers:
            matches = router._pathMatch(path)
            if matches is None or len(matches) == 0:
                continue
            entries.extend(matches)
        return entries


class Router():

    class PathNameError(Exception):
        pass

    def __init__(self):
        self.subRouters = [] # list of subrouters of the form (Router, path)
        self.pathPrefix = ''
        self.paths = set() # all paths under this router for qucker lookup
        self.pathTable = list() # list of tuples of the form (path, method, callback)

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
        self.paths.add(path)
        self.all(path, function)

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

    def _getPathTable(self):
        if len(self.subRouters) is 0:
            return self.pathTable
        else:
            pathTable = []
            for subRouterEntry in self.subRouters:
                for pathTableEntry in subRouterEntry[0]._getPathTable():
                    pathTable.append((pathTableEntry[0], pathTableEntry[1], pathTableEntry[2]))

            pathTable.extend(self.pathTable)
        return pathTable

    def _pathMatch(self, path):
        path = path.split('?')[0]+'/'
        path = path.replace('//', '/')
        path = path.split('/')[1:-1]
        paths = self._getPaths()
        candidate_paths = []

        for p in paths:
            p = p.split('/')[1:-1]
            p_str = '/'.join(p)
            p_str = '/'+p_str+'/'
            p_str = p_str.replace('//', '/')

            if p == path:
                for entry in self._getPathTable():
                    if entry[0] == p_str:
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

    def acceptsCharset(self, charset, *args, **kwargs):
        pass

    def acceptsEncodings(self, encoding, *args, **kwargs):
        pass

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

        self.headers = dict()
        self._body = ''
        self._status = 200

    def append(self, field, value=None):
        self.headers[field]=value
        return self

    def attachment(self, filename=None):
        pass

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
        pass

    def json(self, body=None):
        pass

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
        self.append('Content-Length', len(bytes(body, 'utf-8')))
        self.append('Connection', 'close')

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
            self._status = code
            return self
        else:
            return self._status


    def type(self, type):
        pass

    def vary(self, field):
        pass

    def __str__(self):
        headerString = ''
        for headerName in self.headers:
            headerString+='%s:%s\n'%(headerName, self.headers[headerName])
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


        return 'HTTP/1.1 %s %s\n%s\n%s' % (self._status, statusString[self._status],headerString, self._body)

if __name__=='__main__':

    def dummy_func_1(req, res, next):
        res.append('Content-Type', 'text/plain').send("Hello World")

    def dummy_func_2(req, res, next):
        res.append('Content-Type', 'application/json').status(200).send('{"success":"true"}')

    app = App()

    router = Router()
    router.route('/').get('/', dummy_func_1).get('/working/', dummy_func_2)
    app.use(router)
    app.listen(port=8080, hostname='localhost')
