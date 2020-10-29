# servepy 1.0.3

servepy is a web server framework inspired by Express.js

For more info, installation and usage visit [servepy's official site](https://stuart-wilcox.github.io/servepy-site/main)

## Contents
[Installation](#installation)
- [Pip](#pip)

[Usage](#usage)
- [Simple Usage](#simple-usage)
- [Sample](#sample)

[Documentation](#documentation)
- [App](#app)
- [Router](#router)
- [Request](#request)
- [Response](#response)

## Installation
The fastest and easiest way to install servepy is using [pip](https://pip.pypa.io/en/stable/). If you don't have pip, you can get it [here](https://pip.pypa.io/en/stable/installing/), but if you installed python properly you should alread have it. Before continuing, make sure to update pip by running ```pip install --upgrade pip``` for Windows and ```sudo pip3 install --upgrade pip``` for Linux.

### Pip
This is the recommended way to get servepy.

Windows ```pip install servepy```
Linux ```sudo -H pip3 install servepy```

It's that easy, and now you can simply use ```import servepy```.

*NOTE: If you get warnings about failing to build the wheel file, just ignore them it should still work.*


## Usage
### Simple Usage
This is a demo for a very simple usage to demonstrate the core concepts.

In a new terminal, navigate to your project directory and make two files, server.py and handlers.py, just like below.
```[python]
# server.py
import servepy
import handlers

app = servepy.App()
router = servepy.Router()

# this specifies that a GET request to url path '/' will execute the function handlers.getRoot
router.get('/', handlers.getRoot)

# mount the router on the app
app.use(router)

# start the server
app.listen(port=8080, hostname='localhost')
```
```[python]
# handlers.py

def getRoot(req, res):
  req.set('Content-Type', 'text/plain') # set the Content-Type header to text/plain
  req.status(200) # set the HTTP status to 200 OK
  req.send('Hello world!') # send the string as the response body
```
Execute your server in a terminal (command prompt)

In your web browser (or if you prefer, a REST API client like Postman or Insomnia), navigate to http://localhost:8080/ to see the message 'Hello World'. To stop the server, issue a keyboard interrupt with CTRL+C.

### Sample

To see a working example, look at what is in the [sample directory](./sample). In here, there are two files: ```home.html``` and ```server.py```. The latter is the server code and the former is a very simple html file to render in a browser.

To run the sample, in a temrinal (command prompt) navigate to the root of the servepy directory and simply execute sample. Windows: ```sample.bat``` <br/>
Linux: ```sample.sh```

*NOTE: Linux users will most likely need to give execution permission to ```sample.sh```. To do so, in the project directory use the command ```$ sudo chmod +x sample.sh```.*

## Documentation

### App
#### Properties
###### locals
The app.locals object has properties that are local variables within the application. Once set, the value of app.locals properties persits throughout the life of the application.
###### mountpath
The app.mountpath property contains one or more path patterns on which the sub-app was mounted.

#### Methods
###### all(path, callback)
This method is like using app.METHOD(...) but for all HTTP verbs
###### delete(path, callback)
Routes HTTP DELETE requests to the specified path with the specified callback function(s)
###### get(path, callback)
Routes HTTP GET requests to the specified path with the specified callback function(s)
###### listen([path], [callback], [port], [hostname])
Starts a socket and listens for connections on the given path.
###### post(path, callback)
Routes HTTP POST requests to the specified path with the specified callback(s)
###### route(path)
Returns an instance of a single route which can be used like a router
###### use(callback [, path])
Mount the specified middleware function(s) or router(s) at the specified path. If no path is provided, '/' is used.

### Router
#### Methods
###### all(path, callback)
This method is just like the ```router.METHOD()``` methods, except that it matches all HTTP methods (verbs).

This method is extremely useful for mapping “global” logic for specific path prefixes or arbitrary matches.
###### METHOD(path, callback)
The ```router.METHOD()``` methods provide the routing functionality, where ```METHOD``` is one of the HTTP methods, such as ```GET```,  ```PUT```, ```POST```, and ```DELETE```, in lowercase. Thus, the actual methods are ```router.get()```, ```router.post()```, ```router.put()```, and ```router.delete()```.
###### param(name, callback)
Adds callback triggers to route parameters, where name is the ```name``` of the parameter and ```callback``` is the callback function.
###### route(path)
Returns an instance of a single route which you can then use to handle HTTP verbs with optional middleware. Use ```router.route()``` to avoid duplicate route naming and thus typing errors.
###### use(function [,path])
Uses the specified middleware ```function```, with optional mount path ```path```, that defaults to '/'.

This method is similar to ```app.use()```. A simple example and use case is described below. See ```app.use()``` for more information.

### Request
#### Properties
###### app
This property holds a reference to the instance of the Express application that is using the middleware.
###### body
Contains an object representing the data submitted in the request body (if there is one). By default, it is ```None``` and will be automatically populated if a body is not present on a request.
**NOTE: Support only exists for parsing bodies of the following Content-Type: text/plain, application/json, application/x-www-form-urlencoded**
###### cookies
**NOTE: Not implemented yet**<br/>
Contains the cookies sent by the request. If there are no cookies, it defaults to ```None```.
###### fresh
Indicates whether the request is 'fresh'. It is the opposite of ```req.stale```. It is true if the ```cache-control``` request header doesn't have a ```no-cache``` directive and any of the following are true:
  - The ```if-modified-since``` request header is specified and ```last-modified``` request header is equal to or earlier than the modified response header
  - The ```if-none-match``` request header is *
  - The ```if-none-match``` request header, after being parsed into its directives, does not match the ```stage``` response header.

###### hostname
Contains the hostname derived from the ```Host``` HTTP header. When the trust proxy setting does not evaluate to false, this property will instead have the value of the ```X-Forwarded-Host``` header field. This header can be set by the client or by the proxy.
###### method
Contains a string corresponding to the HTTP method if the request: ```GET, POST, PUT, DELETE, ...etc.```
<br/>**NOTE: Support only exists for GET, POST, PUT & DELETE. Other methods such as HEAD, OPTIONS, etc. are not yet supported**
###### originalUrl
This property is much like ```req.url```; however, it retains the original request URL, allowing you to rewrite it freely for internal routing purposes. For example, the "mounting" feature of ```app.use()``` will rewrite ```req.url``` to strip the mount point
###### params
This property is a ```dict``` containing the properties mapped to the names path parameters. For example, if you have the route ```/user/:name```, then "name" property is available as ```req.params['name']```. The dictionary defaults to ```{}``` if no path parameters are used.
###### path
Contains the path part of the request URL.
###### protocol
Contains the request protocol string, ex: ```HTTP/1.1```
###### query
This property is a ```dict``` containing a property for each query string parameter in the route. If there is no query string, it is ```{}```; an empty dictionary
###### route
Contains the currently-matched route, a string
###### stale
Indicates whether the request is "stale", and it is the opposite of fresh. (See req.fresh)
###### xhr
A Boolean property that is ```True``` if the request's ```X-Requested-With``` header is "XMLHttpRequest", indicating that the request was issued by a client library such as JQuery
#### Methods
###### accepts(types)
Checks if the specified content types are acceptable, based on the request’s ```Accept``` HTTP header field. The method returns the best match, or if none of the specified content types is acceptable, returns ```False``` (in which case, the application should respond with 406 "Not Acceptable")
###### get(field)
Returns the specified HTTP request header field (case-insensitive match). The Referrer and Referer fields are interchangeable
###### is_type(type)
Returns the matching content type if the incoming request’s ```Content-Type``` HTTP header field matches the MIME type specified by the type parameter. Returns ```False``` otherwise


### Response
#### Properties
###### app
This property holds a reference to the instance of the Express application that is using the middleware.
It is identical to the ```req.app``` property in the request object.
###### header_sent
Boolean property that indicates if the app sent HTTP headers for the response.

#### Methods
###### append(field [, value])
Appends the specified value to the HTTP response header field. If the header is not already set, it creates the header with the specified value. The value parameter can be a string or an array. If the header is already set, the value given as a parameter will be ignored and the value in place will remain.

Note: calling ```res.set()``` after ```res.append()``` will reset the previously-set header value.
###### attachment([filename])
Sets the HTTP response ```Content-Disposition``` header field to “attachment”. If a filename is given, then it sets the ```Content-Type``` based on the extension name, and sets the ```Content-Disposition``` “filename=” parameter.
###### cookie(name, value [, options])
**NOTE: Not implemented yet**<br/>
Sets cookie name to value. The value parameter may be a string or object.

The options parameter is an object that can have the following properties.
###### clearCookie(name [, options])
**NOTE: Not implemented yet**<br/>
Clears the cookie specified by name. For details about the options object, see ```res.cookie()```.

###### get(field)
Returns the HTTP response header specified by field. The match is case-insensitive.
###### json([body])
Sends a JSON response. This method sends a response (with the correct content-type) that is the parameter converted to a JSON string.

The parameter can be any JSON type, meaning the built in types (```boolean, int, float, complex, list, tuple, dict, str, bytes, ... etc.```), and you can also use it to convert other values to JSON, such as ```None```(although this is technically not valid JSON).

###### send([body])
Sends the HTTP response.

The body parameter can be a ```str```, ```object```, ```tuple```, ```dict``` or a ```list```.

###### set(field [, value])
Sets the response’s HTTP header ```field``` to ```value```. To set multiple fields at once, pass an object as the parameter.
###### status(code)
Sets the HTTP status for the response.
###### type(type)
Sets the ```Content-Type``` HTTP header to the MIME type as determined by the specified type.
