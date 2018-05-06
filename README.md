# PythonOauthServer
This is a simple implementation of OAuth2 in Python


** Data Storage **

I am using MongoMock inmemory mimic MongoDB database. In Production scenario it can be changed based on the requirement.


Client Step By Step
===========

Get a Token
-------

**Request**
```
curl -i http://localhost:8889/oauth/token -X POST -H 'Content-Type: application/json' -d '{"client_id": "admin", "client_secret": "getroot", "grant_type": "client_credentials", "scope": "restaurent"}'
```

**Response**
```http
HTTP/1.1 200 OK
Content-Length: 100
Content-Type: application/json
Cache-Control: no-store
Pragma: no-cache
Date: Tue, 18 Nov 2014 22:32:18 GMT
Server: TornadoServer/4.0.2
Proxy-Connection: keep-alive
Connection: keep-alive

{"token_type": "Bearer", "expires_in": 3600, "access_token": "7d2adcd2-2756-4531-b7d2-69c19f5b1063"}
```

Consumer Resource with Bearer Token
-------
**Request**

```
curl -i http://localhost:8889/restaurent -H 'Authorization: Bearer c51d4e91-ca89-4bab-a2d1-e68e523b8e59'
```

**Response**
```http
HTTP/1.1 200 OK
Etag: "e8ac30e7653f247f956a04b1f901d893e593cd1b"
Content-Length: 23
Date: Tue, 18 Nov 2014 22:33:15 GMT
Content-Type: text/html; charset=UTF-8
Server: TornadoServer/4.0.2
Proxy-Connection: keep-alive
Connection: keep-alive

[{"_id":{"$oid":"j8ac30e7653h247f956a04b1f901d893e573cd1b"},"Name": "Restaurent 1","Address":"Address 1","routine":{"open":"10 am","close":"5 pm"}},...]

```

Consumer Resource without Bearer Token
-------
**Request**

```
curl http://localhost:8889/restaurent
```

**Response**
```http
HTTP/1.1 200 OK
Etag: "e8ac30e7653f247f956a04b1f901d893e593cd1b"
Content-Length: 23
Date: Tue, 18 Nov 2014 22:33:15 GMT
Content-Type: text/html; charset=UTF-8
Server: TornadoServer/4.0.2
Proxy-Connection: keep-alive
Connection: keep-alive

[{"Name": "Restaurent 1","Address":"Address 1"},...]
```

Consumer Resource Update with Token
-------
**Request**

```
curl -i "http://localhost:8889/restaurentUpdate?id=5aef5a2318d34d27b700b4b3&Name=Test&Address=Test&open=11am&close=7pm" -H 'Authorization: Bearer c51d4e91-ca89-4bab-a2d1-e68e523b8e59'
```

**Response**
```http
HTTP/1.1 200 OK
Etag: "e8ac30e7653f247f956a04b1f901d893e593cd1b"
Content-Length: 23
Date: Tue, 18 Nov 2014 22:33:15 GMT
Content-Type: text/html; charset=UTF-8
Server: TornadoServer/4.0.2
Proxy-Connection: keep-alive
Connection: keep-alive

{"message": "Successful"}
```
