from src.serve import App, Router
import os

if __name__ == '__main__':

    def serve_homepage(req, res):
        homepage = open(os.path.join(os.path.dirname(__file__), 'home.html'), 'r').read()

        res.status(200).set('Content-Type', 'text/html').send( homepage )

    def log_incoming_request(req, res, next):
        print('[%s] %s' % (req.method, req.originalUrl) )
        next()

    app = App()
    router = Router()

    router.get('/', serve_homepage)

    app.use(router)
    app.use(log_incoming_request)

    app.listen(port=8080)
