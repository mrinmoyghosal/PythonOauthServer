# !/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Mrinmoy Ghosal'

import tornado.web
import tornado.ioloop
import oauth2.tokengenerator
import oauth2.grant
import oauth2.store.redisdb
import oauth2.store.mongodb
import json
import time
import fakeredis
import mongomock
from oauth2 import Provider
from bson.json_util import dumps
from bson.objectid import ObjectId


'''
Mongo Client For Mocking Real Mongo Database ( Used for Testing and Small PoC Only. 
For production scenario this will be replaced with real Pymongo Client)

'''

mongo = mongomock.MongoClient()

# Getting Restaurent
getRes=lambda:mongo['db']['restaurent'].find()

def updateRestaurent(id,name,address,opens,close):
    mongo['db']['restaurent'].find_one_and_update({'_id': ObjectId(id)}, {'$set':{'Name':name,'Address':address,'routine':{'open':opens,'close':close}}}, projection={'_id': False})




# Main OAuth2Handler Performing Token Generation and
class OAuth2Handler(tornado.web.RequestHandler):

    # Generator of tokens (with client authentications)
    def initialize(self, controller):
        self.controller = controller

    def post(self):
        response = self._dispatch_request()

        self._map_response(response)

    def _dispatch_request(self):
        request = self.request
        request.post_param = lambda key: json.loads(request.body.decode())[key]

        return self.controller.dispatch(request, environ={})

    def _map_response(self, response):
        for name, value in list(response.headers.items()):
            self.set_header(name, value)

        self.set_status(response.status_code)
        self.write(response.body)


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self, controller):
        self.controller = controller

    # authenticate tokens
    def prepare(self):
        try:
            token = self.get_argument('access_token', None)
            if not token:
                auth_header = self.request.headers.get('Authorization', None)
                if not auth_header:
                    raise Exception('This resource need a authorization token')
                token = auth_header[7:]

            key = 'oauth2_{}'.format(token)
            access = self.controller.access_token_store.rs.get(key)
            if access:
                access = json.loads(access.decode())
            else:
                raise Exception('Invalid Token')
            if access['expires_at'] <= int(time.time()):
                raise Exception('expired token')
        except Exception as err:

            # Defaulting to Normal User View

            self.set_header('Content-Type', 'application/json')
            self.set_status(200)

            resList=[]
            for res in getRes():
                resList.append({"Name":res['Name'],"Address":res["Address"]})

            self.finish(dumps(resList))


class RestaurentHandler(BaseHandler):

    # Authenticated User's View

    def get(self):
        resList=[]
        for res in getRes():
            print type(res['_id'])
            resList.append(res)
        self.finish(dumps(resList))

class RestaurentUpdateHandler(BaseHandler):

    # Authenticated User's View

    def prepare(self):
        try:
            token = self.get_argument('access_token', None)
            if not token:
                auth_header = self.request.headers.get('Authorization', None)
                if not auth_header:
                    raise Exception('This resource need a authorization token')
                token = auth_header[7:]

            key = 'oauth2_{}'.format(token)
            access = self.controller.access_token_store.rs.get(key)
            if access:
                access = json.loads(access.decode())
            else:
                raise Exception('Invalid Token')
            if access['expires_at'] <= int(time.time()):
                raise Exception('expired token')
        except Exception as err:

            # Defaulting to Normal User View

            self.set_header('Content-Type', 'application/json')
            self.set_status(401)
            self.finish(json.dumps({'error': str(err)}))

    def get(self):


        ids=self.get_argument('id')
        name=self.get_argument('Name')
        address=self.get_argument('Address')
        opens=self.get_argument('open')
        close=self.get_argument('close')

        updateRestaurent(ids,name,address,opens,close)

        self.finish(dumps({"message":"Successful"}))


        


def main():

    # Populate Mongo mock
    
    mongo['db']['oauth_clients'].insert({'identifier': 'admin',
                                         'secret': 'getroot',
                                         'redirect_uris': [],
                                         'authorized_grants': [oauth2.grant.ClientCredentialsGrant.grant_type]})

    # MongoDB for clients store
    client_store = oauth2.store.mongodb.ClientStore(mongo['db']['oauth_clients'])



    for i in range(10):
        mongo['db']['restaurent'].insert({
            "Name":"Restaurent"+str(i),
            "Address":"Address "+str(i),
            "routine":{
                "open":"10 am",
                "close":"5 pm"
            } 
        });


    # Redis for tokens storage using FakeRedis
    token_store = oauth2.store.redisdb.TokenStore(rs=fakeredis.FakeStrictRedis())

    # Generator of tokens
    token_generator = oauth2.tokengenerator.Uuid4()
    token_generator.expires_in[oauth2.grant.ClientCredentialsGrant.grant_type] = 3600
 
    # OAuth2 controller and Provider Setup
    auth_controller = Provider(
        access_token_store=token_store,
        auth_code_store=token_store,
        client_store=client_store,
        token_generator=token_generator
    )

    # Token Generation URI
    auth_controller.token_path = '/oauth/token'


    # Add Client Credentials to OAuth2 controller
    auth_controller.add_grant(oauth2.grant.ClientCredentialsGrant())

    # Create Tornado application
    app = tornado.web.Application([
        (r'/oauth/token', OAuth2Handler, dict(controller=auth_controller)),
        (r'/restaurent', RestaurentHandler, dict(controller=auth_controller)),
        (r'/restaurentUpdate', RestaurentUpdateHandler, dict(controller=auth_controller))
    ])

    # Start Server and Listen for Incoming REST Request
    app.listen(8889)
    print("Server Starting")
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()