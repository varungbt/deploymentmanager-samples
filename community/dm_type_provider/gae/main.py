from flask import Flask, request, abort
from flask_restplus import Api, Resource, fields
from functools import wraps

import logging
import pprint

app = Flask(__name__)
api = Api(app, version='1.0', title='TodoMVC API', description='A simple TodoMVC API')

ns = api.namespace('todos', description='TODO operations')

todo = api.model(
    'Todo', {
        'id': fields.Integer(readOnly=True, description='The task unique identifier'),
        'task': fields.String(required=True, description='The task details')
    })


class TodoDAO(object):
    def __init__(self):
        self.todos = {}

    def get(self, id):
        if (id in self.todos):
            return self.todos[id]
        api.abort(404, "Todo {} doesn't exist".format(id))

    def create(self, data):
        logging.info("GEPP: In create request")
        logging.debug("GEPP: IN create request")
        id = data['id']
        if (id in self.todos):
            api.abort(409, "Todo {} already exists".format(str(id)))
        self.todos[id] = data
        return data

    def update(self, id, data):
        logging.info("GEPP: In update request")
        logging.debug("GEPP: IN update request")
        if (id in self.todos):
            self.todos[id] = data
            return data
        api.abort(404, "Todo {} doesn't exist".format(id))

    def delete(self, id):
        logging.info("GEPP: Delete record called ...")
        if id in self.todos:
            del self.todos[id]
            return

        api.abort(404, "Todo {} doesn't exist".format(id))


DAO = TodoDAO()


@ns.route('')
class TodoList(Resource):
    @ns.doc('list_todos')
    @ns.marshal_with(todo, envelope='items')
    def get(self):
        '''List all resources'''
        return list(DAO.todos.values())

    @ns.doc('create_todo')
    @ns.expect(todo)
    @ns.marshal_with(todo, code=201)
    def post(self):
        logging.debug("POST request")
        '''Create a given resource'''
        return DAO.create(api.payload), 201


@ns.route('/<int:id>')
class Todo(Resource):
    @ns.doc('get_todo')
    @ns.marshal_with(todo)
    @ns.param('id', 'The task identifier')
    @ns.response(404, 'Todo not found')
    def get(self, id):
        '''Fetch a given resource'''
        return DAO.get(id)

    @ns.doc('delete_todo')
    @ns.response(204, 'Todo deleted')
    @ns.param('id', 'The task identifier')
    def delete(self, id):
        '''Delete a given resource'''
        DAO.delete(id)
        return '', 204

    @ns.expect(todo)
    @ns.response(404, 'Todo not found')
    @ns.param('id', 'The task identifier')
    @ns.marshal_with(todo)
    def put(self, id):
        '''Update a given resource'''
        logging.debug("Inside  put ")
        logging.info(api.payload)

        logging.info("After updating the id ")
        api.payload["id"] = id

        logging.info(api.payload)

        return DAO.update(id, api.payload)