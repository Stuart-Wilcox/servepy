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
        self.assertEqual(router._endware_path_match('/abc/123?val=123', 'GET')[0].query['val'], '123')

    def test_post(self):
        router = Router()

        router.post('/', endware_1)
        router.post('/abc', endware_2)
        router.post('/abc/:val', endware_1)

        self.assertIsNotNone(router._endware_path_match('/', 'POST'))
        self.assertIsNone(router._endware_path_match('/', 'PUT'))
        self.assertIsNone(router._endware_path_match('/', 'GET'))
        self.assertIsNone(router._endware_path_match('/', 'DELETE'))

        self.assertIsNotNone(router._endware_path_match('/abc', 'POST'))
        self.assertIsNotNone(router._endware_path_match('/abc/123', 'POST'))

        self.assertEqual(router._endware_path_match('/', 'POST')[2], endware_1)
        self.assertEqual(router._endware_path_match('/abc', 'POST')[2], endware_2)
        self.assertEqual(router._endware_path_match('/abc/123', 'POST')[2], endware_1)
        self.assertEqual(router._endware_path_match('/abc/123', 'POST')[0].params['val'], '123')
        self.assertEqual(router._endware_path_match('/abc/123?val=123', 'POST')[0].query['val'], '123')

    def test_put(self):
        router = Router()

        router.put('/', endware_1)
        router.put('/abc', endware_2)
        router.put('/abc/:val', endware_1)

        self.assertIsNotNone(router._endware_path_match('/', 'PUT'))
        self.assertIsNone(router._endware_path_match('/', 'POST'))
        self.assertIsNone(router._endware_path_match('/', 'GET'))
        self.assertIsNone(router._endware_path_match('/', 'DELETE'))

        self.assertIsNotNone(router._endware_path_match('/abc', 'PUT'))
        self.assertIsNotNone(router._endware_path_match('/abc/123', 'PUT'))

        self.assertEqual(router._endware_path_match('/', 'PUT')[2], endware_1)
        self.assertEqual(router._endware_path_match('/abc', 'PUT')[2], endware_2)
        self.assertEqual(router._endware_path_match('/abc/123', 'PUT')[2], endware_1)
        self.assertEqual(router._endware_path_match('/abc/123', 'PUT')[0].params['val'], '123')
        self.assertEqual(router._endware_path_match('/abc/123?val=123', 'PUT')[0].query['val'], '123')

    def test_delete(self):
        router = Router()

        router.delete('/', endware_1)
        router.delete('/abc', endware_2)
        router.delete('/abc/:val', endware_1)

        self.assertIsNotNone(router._endware_path_match('/', 'DELETE'))
        self.assertIsNone(router._endware_path_match('/', 'POST'))
        self.assertIsNone(router._endware_path_match('/', 'GET'))
        self.assertIsNone(router._endware_path_match('/', 'PUT'))

        self.assertIsNotNone(router._endware_path_match('/abc', 'DELETE'))
        self.assertIsNotNone(router._endware_path_match('/abc/123', 'DELETE'))

        self.assertEqual(router._endware_path_match('/', 'DELETE')[2], endware_1)
        self.assertEqual(router._endware_path_match('/abc', 'DELETE')[2], endware_2)
        self.assertEqual(router._endware_path_match('/abc/123', 'DELETE')[2], endware_1)
        self.assertEqual(router._endware_path_match('/abc/123', 'DELETE')[0].params['val'], '123')
        self.assertEqual(router._endware_path_match('/abc/123?val=123', 'DELETE')[0].query['val'], '123')

    def test_route(self):
        router = Router()

        router.route('/abc') \
        .get('/', endware_1) \
        .get('/:val', endware_2)

        self.assertIsNotNone(router._endware_path_match('/abc', 'GET'))
        self.assertIsNone(router._endware_path_match('/abc', 'PUT'))
        self.assertIsNone(router._endware_path_match('/abc', 'POST'))
        self.assertIsNone(router._endware_path_match('/abc', 'DELETE'))

        self.assertIsNotNone(router._endware_path_match('/abc/123', 'GET'))

        self.assertEqual(router._endware_path_match('/abc', 'GET')[2], endware_1)
        self.assertEqual(router._endware_path_match('/abc/123', 'GET')[2], endware_2)
        self.assertEqual(router._endware_path_match('/abc/123', 'GET')[0].params['val'], '123')
        self.assertEqual(router._endware_path_match('/abc/123?val=123', 'GET')[0].query['val'], '123')

    def test_use(self):
        router = Router()

        router.use('/abc', middleware_1)
        router.use('/abc/123', middleware_2)

        self.assertIsNotNone(router._middleware_path_match('/abc'))
        self.assertIsNotNone(router._middleware_path_match('/abc/123'))
        self.assertIsNotNone(router._middleware_path_match('/abc/123/def'))

        self.assertEqual(len(router._middleware_path_match('/abc')), 1)
        self.assertEqual(len(router._middleware_path_match('/abc/123')), 2)
        self.assertEqual(len(router._middleware_path_match('/abc/123/def')), 2)

        self.assertEqual(router._middleware_path_match('/abc')[0][1], middleware_1)
        self.assertEqual(router._middleware_path_match('/abc/123')[0][1], middleware_1)
        self.assertEqual(router._middleware_path_match('/abc/123')[1][1], middleware_2)

        self.assertEqual(router._middleware_path_match('/abc?val=123')[0][0].query['val'], '123')


unittest.main()
