import importlib
import unittest
import serve

def callback(req, res, next):
    pass

class TestRouter(unittest.TestCase):
    def test_creation(self):
        router = serve.Router()
        self.assertFalse(router is None)
        self.assertTrue(len(router.paths) is 0)
        self.assertTrue(len(router.pathTable) is 0)
        self.assertTrue(len(router.subRouters) is 0)

    def test_get(self):
        router = serve.Router()
        try:
            router.get('', callback)
            self.assertTrue(False)
        except serve.Router.PathNameError:
            self.assertTrue(True)

        try:
            router.get('/', callback)
            self.assertTrue('/' in router.paths)
            self.assertTrue( ('/', 'GET', callback)  in router.pathTable)
        except serve.Router.PathNameError:
            self.assertTrue(False)

        try:
            router.get('/abc/', callback)
            self.assertTrue('/abc/' in router.paths)
            self.assertTrue( ('/abc/', 'GET', callback) in router.pathTable)
        except serve.Router.PathNameError:
            self.assertTrue(False)

    def test_post(self):
        router = serve.Router()
        try:
            router.post('', callback)
            self.assertTrue(False)
        except serve.Router.PathNameError:
            self.assertTrue(True)
        try:
            router.post('/', callback)
            self.assertTrue('/' in router.paths)
            self.assertTrue( ('/', 'POST', callback)  in router.pathTable)
        except serve.Router.PathNameError:
            self.assertTrue(False)
        try:
            router.post('/abc/', callback)
            self.assertTrue('/abc/' in router.paths)
            self.assertTrue( ('/abc/', 'POST', callback) in router.pathTable)
        except serve.Router.PathNameError:
            self.assertTrue(False)

    def test_put(self):
        router = serve.Router()
        try:
            router.put('', callback)
            self.assertTrue(False)
        except serve.Router.PathNameError:
            self.assertTrue(True)

        try:
            router.put('/', callback)
            self.assertTrue('/' in router.paths)
            self.assertTrue( ('/', 'PUT', callback)  in router.pathTable)
        except serve.Router.PathNameError:
            self.assertTrue(False)

        try:
            router.put('/abc/', callback)
            self.assertTrue('/abc/' in router.paths)
            self.assertTrue( ('/abc/', 'PUT', callback) in router.pathTable)
        except serve.Router.PathNameError:
            self.assertTrue(False)

    def test_delete(self):
        router = serve.Router()
        try:
            router.delete('', callback)
            self.assertTrue(False)
        except serve.Router.PathNameError:
            self.assertTrue(True)

        try:
            router.delete('/', callback)
            self.assertTrue('/' in router.paths)
            self.assertTrue( ('/', 'DELETE', callback)  in router.pathTable)
        except serve.Router.PathNameError:
            self.assertTrue(False)

        try:
            router.delete('/abc/', callback)
            self.assertTrue('/abc/' in router.paths)
            self.assertTrue( ('/abc/', 'DELETE', callback) in router.pathTable)
        except serve.Router.PathNameError:
            self.assertTrue(False)

    def test_all(self):
        router = serve.Router()
        try:
            router.all('', callback)
            self.assertTrue(False)
        except serve.Router.PathNameError:
            self.assertTrue(True)

        try:
            router.all('/', callback)
            self.assertTrue('/' in router.paths)
            self.assertTrue( ('/', 'GET', callback)  in router.pathTable)
            self.assertTrue( ('/', 'POST', callback)  in router.pathTable)
            self.assertTrue( ('/', 'PUT', callback)  in router.pathTable)
            self.assertTrue( ('/', 'DELETE', callback)  in router.pathTable)
        except serve.Router.PathNameError:
            self.assertTrue(False)

        try:
            router.all('/abc/', callback)
            self.assertTrue('/abc/' in router.paths)
            self.assertTrue( ('/abc/', 'GET', callback) in router.pathTable)
            self.assertTrue( ('/abc/', 'POST', callback) in router.pathTable)
            self.assertTrue( ('/abc/', 'PUT', callback) in router.pathTable)
            self.assertTrue( ('/abc/', 'DELETE', callback) in router.pathTable)
        except serve.Router.PathNameError:
            self.assertTrue(False)

    def test_use(self):
        router = serve.Router()

        try:
            router.use('/', callback)
            self.assertTrue('/' in router.middlewarePaths)
            self.assertTrue( ('/',callback)  in router.middlewarePathTable)
        except serve.Router.PathNameError:
            self.assertTrue(False)

        try:
            router.use('/abc/', callback)
            self.assertTrue('/abc/' in router.middlewarePaths)
            self.assertTrue( ('/abc/', callback) in router.middlewarePathTable)
        except serve.Router.PathNameError:
            self.assertTrue(False)

    def test_route(self):
        router = serve.Router()
        try:
            router.route('')
            self.assertTrue(False)
        except serve.Router.PathNameError:
            self.assertTrue(True)

        try:
            subRouter = router.route('/')
            self.assertTrue(subRouter is not None)
            self.assertTrue(subRouter.pathPrefix is '/')
            self.assertTrue(len(subRouter.paths) is 0)
            self.assertTrue(len(subRouter.pathTable) is 0)
        except serve.Router.PathNameError:
            self.assertTrue(True)

        try:
            subRouter = router.route('/abc/')
            self.assertTrue(subRouter is not None)
            self.assertTrue(subRouter.pathPrefix is '/abc/')
            self.assertTrue(len(subRouter.paths) is 0)
            self.assertTrue(len(subRouter.pathTable) is 0)
        except serve.Router.PathNameError:
            self.assertTrue(True)

    def test__getPaths(self):
        router = serve.Router()

        self.assertTrue(len(router._getPaths()) is 0)

        router.get('/', callback)
        self.assertTrue(len(router._getPaths()) is 1)
        self.assertTrue('/' in router._getPaths())

        router.get('/abc/', callback)
        self.assertTrue(len(router._getPaths()) is 2)
        self.assertTrue('/abc/' in router._getPaths())

        subRouter = router.route('/def/')
        self.assertTrue(len(subRouter._getPaths()) is 0)

        subRouter.get('/', callback)
        self.assertTrue(len(subRouter._getPaths()) is 1)
        self.assertTrue('/' in subRouter._getPaths())

        subRouter.get('/abc/', callback)
        self.assertTrue(len(subRouter._getPaths()) is 2)
        self.assertTrue('/abc/' in subRouter._getPaths())

        self.assertTrue(len(router._getPaths()) is 4)
        self.assertTrue('/def/' in router._getPaths())
        self.assertTrue('/def/abc/' in router._getPaths())

        subRouter.route('/ghi/').get('/abc/', callback).get('/def/', callback)
        self.assertTrue('/def/ghi/abc/' in router._getPaths())
        self.assertTrue('/def/ghi/def/' in router._getPaths())

    def test__pathMatch(self):
        router = serve.Router()

        router.route('/abc/').get('/def/', callback).post('/DEF/', callback)

        self.assertTrue(len(router._pathMatch('/'))==0)

        self.assertTrue(len(router._pathMatch('/abc/def/'))==1)
        self.assertTrue(len(router._pathMatch('/abc/DEF/'))==1)

        self.assertTrue(len(router._pathMatch('/abc/')) == 0)

        self.assertTrue(len(router._pathMatch('/abc/de')) == 0)

        self.assertFalse(len(router._pathMatch('/abc/def?var=value')) == 0)





class TestRequest(unittest.TestCase):
    def test_creation(self):
        app = serve.App()
        req = serve.Request(app, 'http://localhost:8080/abc/123/', 'HTTP/1.1', 'GET')
        self.assertFalse(req is None)
        self.assertFalse(req.app is None)
        self.assertFalse(req.originalUrl is None)
        self.assertTrue(req.originalUrl == '/abc/123/')
        self.assertTrue(req.method == 'GET')
        self.assertTrue(req.body is None)
        self.assertTrue(req.headers == {})
        self.assertTrue(req.protocol == 'HTTP/1.1')

        body = '''
        <!DOCTYPE html>
        <html>
        <head>
        <title>Foo Bar</title>
        </head>
        <body>
        <p>Hello World!</p>
        </body>
        </html>
        '''
        headers = {'Content-Type': 'text/html', 'Content-Length':len(body), 'Cache-Control':'No-Cache'}
        cookies = {'token':'1q2w3e4r5t6y7u8i9o0p!A@S#D$F%G^H&J*K(L):', 'user':'Foo Bar'}
        req = serve.Request(app, 'http://localhost:8080/abc/123?foo=bar&baz=', 'HTTP/1.1', 'POST', headers=headers, body=body, cookies=cookies)

        self.assertFalse(req is None)
        self.assertTrue(req.app is app)
        self.assertTrue(req.originalUrl == '/abc/123?foo=bar&baz=')
        self.assertTrue(req.body == body)
        for item in [req.headers[key] is None for key in headers]:
            self.assertFalse(item)
        self.assertTrue(req.cookies == cookies)
        self.assertTrue(req.stale)
        self.assertFalse(req.fresh)

    def test_accepts(self):
        pass
    def test_isType(self):
        pass
    def test_param(self):
        pass
    def test_range(self):
        pass

class TestResponse(unittest.TestCase):
    def test_creation(self):
        pass
    def test_append(self):
        pass
    def test_attachment(self):
        pass
    def test_cookie(self):
        pass
    def test_clearCookie(self):
        pass
    def test_download(self):
        pass
    def test_end(self):
        pass
    def test_format(self):
        pass
    def test_json(self):
        pass
    def test_jsonp(self):
        pass
    def test_links(self):
        pass
    def test_location(self):
        pass
    def test_redirect(self):
        pass
    def test_render(self):
        pass
    def test_send(self):
        pass
    def test_sendFile(self):
        pass
    def tet_sendStatus(self):
        pass
    def test_status(self):
        pass

class TestApp(unittest.TestCase):
    def test_all(self):
        pass
    def test_delete(self):
        pass
    def test_get(self):
        pass
    def test_listen(self):
        pass
    def test_param(self):
        pass
    def test_path(self):
        pass
    def test_post(self):
        pass
    def test_put(self):
        pass
    def test_route(self):
        pass
    def test_use(self):
        pass
    def test__routePath(self):
        app = serve.App()
        router = serve.Router()
        router.get('/abc/', callback)
        app.use(router, path='/')
        app._routePath('/abc/', 'GET')

class TestPath(unittest.TestCase):
    def test_creation(self):
        path_str = ['/abc/123/', '/abc/123/', '/abc/:num/', '/abc/234/', '/def/123/']
        paths = [serve.Path(p) for p in path_str]

    def test_matching(self):
        path_str = ['/abc/123/', '/abc/123/', '/abc/:num/', '/abc/234/', '/def/123/', '/abc/']
        paths = [serve.Path(p) for p in path_str]

        self.assertTrue(paths[0].match(paths[1]))
        self.assertFalse(paths[0].match(paths[3]))

        self.assertTrue(paths[2].match(paths[0]))
        self.assertTrue(paths[2].params['num']=='123')

        self.assertFalse(paths[0].match(paths[3]))
        self.assertFalse(paths[0].match(paths[4]))

        self.assertTrue(paths[5].match(paths[0], middleware=True))
        self.assertFalse(paths[5].match(paths[4], middleware=True))


if __name__ == '__main__':
    unittest.main()
