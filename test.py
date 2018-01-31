import importlib
import unittest
from serve import App, Router, Request, Response

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

class TestRouter(unittest.TestCase):
    def test_init(self):
        router = Router()

        self.assertIsNotNone(router)

    def test_all(self):
        pass
    def test_get(self):
        pass
    def test_post(self):
        pass
    def test_put(self):
        pass
    def test_delete(self):
        pass
    def test_route(self):
        pass
    def test_use(self):
        pass

if __name__ == '__main__':
    unittest.main()
