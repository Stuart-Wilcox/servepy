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

unittest.main()
