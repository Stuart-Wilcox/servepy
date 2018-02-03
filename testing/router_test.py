import unittest
from src.serve import Router

print('\n***ROUTER TEST***\n')

def middleware_1(req, res, next):
    pass

def middleware_2(req, res, next):
    next()

def endware_1(req, res):
    pass

def endware_2(req, res):
    pass

class TestRouter(unittest.TestCase):
    def test_init(self):
        router = Router()

        self.assertIsNotNone(router)

    def test_all(self):
        router = Router()

        router.all('/', endware_1)
        router.all('/', endware_2)

        self.assertIsNotNone(router._endware_path_match('/', 'GET'))
        self.assertIsNotNone(router._endware_path_match('/', 'PUT'))
        self.assertIsNotNone(router._endware_path_match('/', 'POST'))
        self.assertIsNotNone(router._endware_path_match('/', 'DELETE'))

        self.assertIsNone(router._endware_path_match('/abc', 'GET'))

        self.assertEqual(router._endware_path_match('/', 'GET')[2], endware_1) # endware_1 matches method in tuple in endware

    def test_get(self):
        router = Router()

        router.get('/', endware_1)
        router.get('/abc', endware_2)
        router.get('/abc/:val', endware_1)

        self.assertIsNotNone(router._endware_path_match('/', 'GET'))
        self.assertIsNone(router._endware_path_match('/', 'PUT'))
        self.assertIsNone(router._endware_path_match('/', 'POST'))
        self.assertIsNone(router._endware_path_match('/', 'DELETE'))

        self.assertIsNotNone(router._endware_path_match('/abc', 'GET'))
        self.assertIsNotNone(router._endware_path_match('/abc/123', 'GET'))

        self.assertEqual(router._endware_path_match('/', 'GET')[2], endware_1)
        self.assertEqual(router._endware_path_match('/abc', 'GET')[2], endware_2)
        self.assertEqual(router._endware_path_match('/abc/123', 'GET')[2], endware_1)
        self.assertEqual(router._endware_path_match('/abc/123', 'GET')[0].params['val'], '123')
        # self.assertEqual(router._endware_path_match('/abc/123?val=123', 'GET')[0].query['val'], '123')
        print(router._endware_path_match('/abc/123?val=123', 'GET')[0].query)


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

unittest.main()
