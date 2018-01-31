import serve

def root(req, res):
    res.status(200).send("Hello world!")

def print_path_val(req, res):
    res.status(200).send("Hello %s!" % req.params['name'])

def print_query_val(req, res):
    res.status(200).send("Hello %s" % req.query['name'])

app = serve.App()

router = serve.Router()

router.route('/').get('/', root).get('/abc/:name', print_path_val).get('/abc', print_query_val)

router.route('/def').get('/', root)


app.use(router)

app.listen(port=8080)
