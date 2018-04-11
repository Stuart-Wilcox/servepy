from src.serve import App, Router
import os

names = []

def names_to_html():
    names_str = ''
    for name in names:
        names_str += '\n<li>'

        name = name.replace('<', '&lt;')
        name = name.replace('>', '&gt;')

        names_str += name
        names_str += '</li>'
    return names_str + '\n'

if __name__ == '__main__':

    def listening():
        print("App is listening at localhost on port 8080")

    def log_incoming_request(req, res, next):
        print('[%s] %s' % (req.method, req.originalUrl) ) # print the request type and path
        next() # make sure the endware is reached

    def serve_homepage(req, res):
        homepage = open(os.path.join(os.path.dirname(__file__), 'home.html'), 'r').read() # read the file as a string
        homepage = homepage.replace('{{names}}', names_to_html()) # replace {{names}} with a list

        res.status(200).set('Content-Type', 'text/html').send( homepage ) # send it back as html

    def post_name(req, res):
        names.append(req.body['name']) # add the name to the list
        serve_homepage(req, res) # serve the homepage the same

    app = App()
    router = Router()

    # mount the endware
    router.get('/', serve_homepage)
    router.post('/', post_name)

    # mount the middleware
    app.use(router)
    app.use(log_incoming_request)

    # start the server
    app.listen(port=8080, callback=listening)
