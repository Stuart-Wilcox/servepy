import unittest
from src.serve import App, Router

print('\n***APP TEST***\n')

def middleware_1(req, res, next):
    pass

def middleware_2(req, res, next):
    next()

def endware_1(req, res):
    pass

def endware_2(req, res):
    pass

class TestApp(unittest.TestCase):
    def test_init(self):
        app = App()

        self.assertIsNotNone(app, msg='App non properly instantiated')
        self.assertIs(type(app.locals), dict, msg='App.locals should be {} on instantiation')
        self.assertIs(app.mountpath, '', msg='App.mountpath should be \'\' on instantiation')

    def test_all(self):
        app = App()

        app.all('/', endware_1)
        result = app.all('/abc', endware_2)

        self.assertIs(result, app) # make sure it returns the App again

        # make sure all the methods are in there
        self.assertIsNotNone(app._route_path('/', 'GET')[1])
        self.assertIsNotNone(app._route_path('/', 'PUT')[1])
        self.assertIsNotNone(app._route_path('/', 'POST')[1])
        self.assertIsNotNone(app._route_path('/', 'DELETE')[1])

        # make sure the methods are all the same correct one
        self.assertIs(app._route_path('/', 'GET')[1][2], endware_1)
        self.assertIs(app._route_path('/', 'PUT')[1][2], endware_1)
        self.assertIs(app._route_path('/', 'POST')[1][2], endware_1)
        self.assertIs(app._route_path('/', 'DELETE')[1][2], endware_1)

    def test_delete(self):
        app = App()

        app.delete('/', endware_1)
        result = app.delete('/abc', endware_2)

        # make sure only the delete method is in there
        self.assertIsNone(app._route_path('/', 'GET')[1])
        self.assertIsNone(app._route_path('/', 'PUT')[1])
        self.assertIsNone(app._route_path('/', 'POST')[1])
        self.assertIsNotNone(app._route_path('/', 'DELETE')[1])

        # make sure the methods is correct one
        self.assertIs(app._route_path('/', 'DELETE')[1][2], endware_1)

    def test_get(self):
        app = App()

        app.get('/', endware_1)
        result = app.get('/abc', endware_2)

        # make sure only the delete method is in there
        self.assertIsNotNone(app._route_path('/', 'GET')[1])
        self.assertIsNone(app._route_path('/', 'PUT')[1])
        self.assertIsNone(app._route_path('/', 'POST')[1])
        self.assertIsNone(app._route_path('/', 'DELETE')[1])

        # make sure the methods is correct one
        self.assertIs(app._route_path('/', 'GET')[1][2], endware_1)

    def test_post(self):
        app = App()

        app.post('/', endware_1)
        result = app.post('/abc', endware_2)

        # make sure only the delete method is in there
        self.assertIsNone(app._route_path('/', 'GET')[1])
        self.assertIsNone(app._route_path('/', 'PUT')[1])
        self.assertIsNotNone(app._route_path('/', 'POST')[1])
        self.assertIsNone(app._route_path('/', 'DELETE')[1])

        # make sure the methods is correct one
        self.assertIs(app._route_path('/', 'POST')[1][2], endware_1)

    def test_put(self):
        app = App()

        app.put('/', endware_1)
        result = app.put('/abc', endware_2)

        # make sure only the delete method is in there
        self.assertIsNone(app._route_path('/', 'GET')[1])
        self.assertIsNotNone(app._route_path('/', 'PUT')[1])
        self.assertIsNone(app._route_path('/', 'POST')[1])
        self.assertIsNone(app._route_path('/', 'DELETE')[1])

        # make sure the methods is correct one
        self.assertIs(app._route_path('/', 'PUT')[1][2], endware_1)

    def test_route(self):
        app = App()

        result = app.route('/')

        self.assertIsNotNone(result)
        self.assertIs(type(result), Router)

    def test_use(self):
        app = App()

        app.use(middleware_1, path='/')

        router = Router()

        router.use('/', middleware_2)

        app.use(router, path='/abc')

        self.assertIsNotNone(app._route_path('/', 'GET')[0])

        self.assertEqual(len(app._route_path('/', 'GET')[0]), 2) # two elements in the middleware
        self.assertIsNone(app._route_path('/', 'GET')[1]) # no items in the endware

        self.assertTrue(middleware_1 in app._route_path('/', 'GET')[0][0]) # middleware_1 in the first tuple in middleware

        self.assertTrue(middleware_2 in app._route_path('/', 'GET')[0][1]) # middleware_2 in the second tuple in middleware

unittest.main()
