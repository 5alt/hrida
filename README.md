# Hrida
Hrida is a http interface for frida. The idea is inspired by [Brida](https://github.com/federicodotta/Brida/).

Write a frida script that exports [rpc](https://www.frida.re/docs/javascript-api/#rpc) funtions. You can use http requests to pass arguments and retrieve the return value.


## Dependencies
* [frida](https://www.frida.re/)
* [flask](http://flask.pocoo.org/docs/)

## Ussage
```
Usage: hrida.py [options] frida_script

Options:
  -h HOST            Listen address.
  -p PORT            Listen port.
  -a APPLICATION_ID  Application that frida will attach to.
```

### call
```
URL: http://<host>:<port>/call
Method: POST
Params: method, args
```

method: method name that is exported by frida_script

args: arguments for the method as a json array (`json.dumps([arg1, arg2])`)

Example:

method=init&args=["md5", "salt"]

### reload frida script
```
URL: http://<host>:<port>/reload
Method: GET
```

reload the frida script

### attach to the application
```
URL: http://<host>:<port>/spawn?app=<application_id>
Method: GET
```

application_id: the target application's package name

## Contact

http://5alt.me

md5_salt [AT] qq.com