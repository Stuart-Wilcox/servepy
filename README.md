# Serverpy

Servepy is an HTTP server framework modelled after the Express.js library for Node.js

## Contents
[Usage](#usage)
- [Simple Usage](#simple-usage)
- [More Advanced Usage](#more-advanced-usage)

[Documentation](#documentation)
- [App](#app)
- [Router](#router)
- [Request](#request)
- [Response](#response)

## Usage
### Simple Usage
This is a demo for a very simple usage to demonstrate the core concepts.

In a new terminal, navigate to the project directory and make two files, server.py and handlers.py, just like below.
```[python]
# server.py
import servepy
import handlers

app = servepy.App()
router = serverpy.Router()

router.get(handlers.getRoot, '/')

app.use(router)

app.listen(port=8080, hostname='localhost')
```
```[python]
# handlers.py

def getRoot(req, res):
  req.append('Content-Type', 'text/plain')
  req.status(200)
  req.send('Hello world!')
```
Use the command $python server.py (Windows) or $python3 server.py (Linux) to start the server.

In your web browser (or if you prefer, a rest client), naviagate to http://localhost:8080/ to see the message 'Hello World'

### More advanced usage
```[python]
# server.py
import servepy
import handlers

app = servepy.App()
router = servepy.Router()

sub_router = router.route('/songs/')

sub_router.get(handler.getSongs, '/')
sub_router.post(handler.addSong, '/')
sub_router.delete(handler.deleteSong, '/')
sub_router.get(handler.getSongsByTitle, '/:title/')

def log(req, res, next):
  print('[%s] %s' % (req.method, req.originalUrl))

app.use(log, '/')
app.use(router)

app.listen(port=8080, hostname='localhost')
```
```[python]
# handlers.py
import sqlite3
import models

conn = sqlite3.connect('example.db')
c = conn.cursor()

def addSong(req, res):
  if req.body.title and req.body.artist and req.body.album:
    c.execute('INSERT INTO Song VALUES (?,?,?)', (req.body.title, req.body.artist, req.body.album))
    conn.commit()
    res.status(200).json({'success':True, 'message':'Successfully added song'})
  else:
    res.status(400).json({'success':False, 'message':'Invalid request parameters in body'})

def getSongs(req, res):
  songs = c.execute('SELECT * FROM Song ORDER BY title ASC, artist ASC')
  if len(songs) != 0:
    res.status(200).json({'success':True, 'message':songs})
  else:
    res.status(304).json()

def deleteSong(req, res):
  if req.title and req.artist:
    c.execute('DELETE FROM Song WHERE title=? AND artist=?', (req.query.title, req.query.artist))
    conn.commit()
    res.status(200).json({'success':True, 'message':'Successfully removed song'})
  else:
    res.status(400).json({'success':False, 'message':'Invalid request parameters in body'})

def getSongsByTitle(req, res):
  if req.title:
    songs = c.execute('SELECT * FROM Song WHERE title=? ORDER BY artist ASC', req.params.title)
    res.status(200).json({'success':True, 'message':songs})
  else:
    res.status(400).json({'success':False, 'message':'Invalid request parameters in body'})
```
```[python]
import sqlite3

conn = sqlite3.connect('example.db')
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS Song(title TEXT, artist TEXT, album TEXT)')
```

## Documentation

### App
#### Properties
###### locals
The app.locals object has properties that are local variables within the application. Once set, the value of app.locals properties persits throughout the life of the application.
###### mountpath
The app.mountpath property contains one or more path patterns on which the sub-app was mounted.
###### routers
The app.routers property is a collection of routers or other middleware that the app is using. Theses are updated through app.use(...)
#### Methods
###### all(path, callback, [,callback ...])
This method is like using app.METHOD(...) but for all HTTP verbs
###### delete(path, callback [, callback...])
Routes HTTP DELETE requests to the specified path with the specified callback function(s)
###### get(path, callback [,callback ...])
Routes HTTP GET requests to the specified path with the specified callback function(s)
###### listen([path], [callback], [port], [hostname])
Starts a socket and listens for connections on the given path.
###### post(path, callback [,callback ...])
Routes HTTP POST requests to the specified path with the specified callback(s)
###### route(path)
Returns an instance of a single route which can be used like a router
###### use(callback [, path] [, callbacks ...])
Mount the specified middleware function(s) or router(s) at the specified path

### Router
#### Methods
###### all(path, [, callback, ...] callback)
This method is just like the ```router.METHOD()``` methods, except that it matches all HTTP methods (verbs).

This method is extremely useful for mapping “global” logic for specific path prefixes or arbitrary matches.
###### METHOD(path, [, callback, ...] callback)
The ```router.METHOD()``` methods provide the routing functionality, where ```METHOD``` is one of the HTTP methods, such as ```GET```,  ```PUT```, ```POST```, and so on, in lowercase. Thus, the actual methods are ```router.get()```, ```router.post()```, ```router.put()```, and so on.
###### param(name, callback)
Adds callback triggers to route parameters, where name is the ```name``` of the parameter and ```callback``` is the callback function.
###### route(path)
Returns an instance of a single route which you can then use to handle HTTP verbs with optional middleware. Use ```router.route()``` to avoid duplicate route naming and thus typing errors.
###### use([path], [function, ...] function)
Uses the specified middleware ```function``` or functions, with optional mount path ```path```, that defaults to “/”.

This method is similar to ```app.use()```. A simple example and use case is described below. See ```app.use()``` for more information.

### Request
#### Properties
###### app
This property holds a reference to the instance of the Express application that is using the middleware.
###### baseUrl
The URL path on which a router instance was mounted. This property is similar to the ```mountpath``` property of the app object, except ```app.moutpath``` returns the matched path pattern(s).
###### body
Contains an object representing the data submitted in the request body(if there is one). By default, it is ```None``` and will be automatically populated if a body is present on a request.
###### cookies
Contains the cookies send by the request. If there are no cookies, it defaults to ```None```.
###### fresh
Indicates whether the request is 'fresh'. It is the opposite of ```req.stale```. It is true if the ```cache-control``` request header doesn't have a ```no-cache``` directive and any of the following are true:
  - The ```if-modified-since``` request header is specified and ```last-modified``` request header is equal to or earlier than the modified response header
  - The ```if-none-match``` request header is *
  - The ```if-none-match``` request header, after being parsed into its directives, does not match the ```etage``` response header.

###### hostname
Contains the hostname derived from the ```Host``` HTTP header. When the trust proxy setting does not evaluate to false, this property will instead have the value of the ```X-Forwarded-Host``` header field. This header can be set by the client or by the proxy.
###### ip
Contains the remove IP address of the request. When the trust proxy setting does not evaluate to false, tye vakue of this property is derived from the left-most entry in the ```X-Forwarded-For``` header. This header can be set by the client or by the proxy.
###### ips
When the trust proxy setting does not evaluate to false, this property contains an array of IP addresses specified in the ```X-Forwarded-For``` request header. Otherwise, it contains an empty array. This header can be set by the client or by the proxy.
###### method
Contains a string corresponding to the HTTP method if the request: ```GET, POST, PUT, DELETE, ...etc.```
###### originalUrl
This property is much like ```req.url```; however, it retains the original request URL, allowing you to rewrite it freely for internal routing purposes. For example, the "mounting" feature of ```app.use()``` will rewrite ```req.url``` to strip the mount point
###### params
This property is an object containing the properties mapped ti the names route "parameters". For example, if you have the route ```/user/:name```, then "name" property is availabke as ```req.params.name```. This object defaults to ```None```.
###### path
Contains the path part of the request URL.
###### protocol
Contains the request protocol string: either ```http``` or ```https```. When the trust proxy setting does not evaluate to false, this property will use the value of the ```X-Forwarded-To``` header field if present. This header can be set by the client or by the proxy.
###### query
This property is an object containing a property for each query string parameter in the route. If there is no query string, it is ```None```.
###### route
Contains the urrently-matched route, a string.
###### secure
A Boolean property that is true if a TLS connection is estnblished. Equivalent to: ```req.protocol=='https'```
###### stale
Indicates whether the request is "stale", and it is the opposite of fresh. (See req.fresh)
###### subdomains
An array of subdomains in the domain name of the requests.
###### xhr
A Boolean property that is ```True``` if the request's ```X-Requested-With``` header is "XMLHttpRequest", indicating that the request was issued by a client library such as JQuery.
#### Methods
###### accepts(types)
Checks if the specified content types are acceptable, based on the request’s ```Accept``` HTTP header field. The method returns the best match, or if none of the specified content types is acceptable, returns ```False``` (in which case, the application should respond with 406 "Not Acceptable").
###### get(field)
Returns the specified HTTP request header field (case-insensitive match). The Referrer and Referer fields are interchangeable.
###### is(type)
Returns the matching content type if the incoming request’s ```Content-Type``` HTTP header field matches the MIME type specified by the type parameter. Returns ```False``` otherwise.
###### param(name [, defaultValue])
Deprecated. Use either req.params, req.body or req.query, as applicable.
###### range(size [,options])
Range header parser. The ```size``` parameter is the maximum size of the resource. The ```options``` parameter is an object that can have a combine property to specify overlapping & adjacent ranges should be combined. Defaults to ```False```.


### Response
#### Properties
###### app
This property holds a reference to the instance of the Express application that is using the middleware.
It is identical to the ```req.app``` property in the request object.
###### headerSent
Boolean property that indicates if the app sent HTTP headers for the response.
###### locals
An object that contains response local variables scoped to the request, and therefore available only to the view(s) rendered during that request / response cycle (if any). Otherwise, this property is identical to app.locals.

This property is useful for exposing request-level information such as the request path name, authenticated user, user settings, and so on.
#### Methods
###### append(field [, value])
Appends the specified value to the HTTP response header field. If the header is not already set, it creates the header with the specified value. The value parameter can be a string or an array. If the header is already set, the value given as a parameter will be ignored and the value in place will remain.

Note: calling ```res.set()``` after ```res.append()``` will reset the previously-set header value.
###### attachment([filename])
Sets the HTTP response ```Content-Disposition``` header field to “attachment”. If a filename is given, then it sets the ```Content-Type``` based on the extension name, and sets the ```Content-Disposition``` “filename=” parameter.
###### cookie(name, value [, options])
Sets cookie name to value. The value parameter may be a string or object.

The options parameter is an object that can have the following properties.
###### clearCookie(name [, options])
Clears the cookie specified by name. For details about the options object, see ```res.cookie()```.
###### download(path [, filename] [, options] [, fn])
Transfers the file at path as an “attachment”. Typically, browsers will prompt the user for download. By default, the ```Content-Disposition``` header “filename=” parameter is path (this typically appears in the browser dialog). Override this default with the filename parameter.

When an error occurs or transfer is complete, the method calls the optional callback function ```fn```. This method uses ```res.sendFile()``` to transfer the file.

The optional options argument passes through to the underlying ```res.sendFile()``` call, and takes the exact same parameters.
###### end([data] [, encoding])
Ends the response process. Use to quickly end the response without any data. If you need to respond with data, instead use methods such as ```res.send()``` and ```res.json()```.
###### format(object)
Performs content-negotiation on the ```Accept``` HTTP header on the request object, when present. It uses ```req.accepts()``` to select a handler for the request, based on the acceptable types ordered by their quality values. If the header is not specified, the first callback is invoked. When no match is found, the server responds with 406 “Not Acceptable”, or invokes the default callback.

The ```Content-Type``` response header is set when a callback is selected. However, you may alter this within the callback using methods such as ```res.set()``` or ```res.type()```.
###### get(field)
Returns the HTTP response header specified by field. The match is case-insensitive.
###### json([body])
Sends a JSON response. This method sends a response (with the correct content-type) that is the parameter converted to a JSON string.

The parameter can be any JSON type, meaning the built in types (```boolean, int, float, complex, list, tuple, dict, str, bytes, ... etc.```), and you can also use it to convert other values to JSON, such as ```None```(although this is technically not valid JSON).
###### jsonp([body])
Sends a JSON response with JSONP support. This method is identical to ```res.json()```, except that it opts-in to JSONP callback support.
###### links(links)
Joins the links provided as properties of the parameter to populate the response’s ```Link``` HTTP header field.
###### location(path)
Sets the response ```Location``` HTTP header to the specified path parameter.
###### redirect([status,] path)
Redirects to the URL derived from the specified path, with specified status, a positive integer that corresponds to an HTTP status code . If not specified, status defaults to “302 “Found”.
###### render(view [, locals] [, callback])
Renders a view and sends the rendered HTML string to the client. Optional parameters:
  - ```locals```, an object whose properties define local variables for the view.
  - ```callback```, a callback function. If provided, the method returns both the possible error and rendered string, but does not perform an automated response. When an error occurs, the method invokes ```next(err)``` internally.
The ```view``` argument is a string that is the file path of the view file to render. This can be an absolute path, or a path relative to the views setting. If the path does not contain a file extension, then the view engine setting determines the file extension. If the path does contain a file extension then the module will be loaded for the specified template engine and render it using the loaded module’s function.
###### send([body])
Sends the HTTP response.

The body parameter can be a ```str```, ```object```, ```tuple```, ```dict``` or a ```list```.
###### sendFile(path [, options] [, fn])
Transfers the file at the given path. Sets the ```Content-Type``` response HTTP header field based on the filename’s extension. Unless the root option is set in the options object, ```path``` must be an absolute path to the file.
###### sendStatus(statusCode)
Sets the response HTTP status code to ```statusCode``` and send its string representation as the response body.
###### set(field [, value])
Sets the response’s HTTP header ```field``` to ```value```. To set multiple fields at once, pass an object as the parameter.
###### status(code)
Sets the HTTP status for the response.
###### type(type)
Sets the ```Content-Type``` HTTP header to the MIME type as determined by the specified type. If type contains the “/” character, then it sets the ```Content-Type``` to type.
###### vary(field)
Adds the field to the ```Vary``` response header, if it is not there already.
