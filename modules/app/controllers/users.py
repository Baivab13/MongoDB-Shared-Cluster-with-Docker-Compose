""" controller and routes for users """
import os
from flask import request, jsonify, render_template, redirect
from app import app, mongo
import logger
from bson.objectid import ObjectId
import sys

ROOT_PATH = os.environ.get('ROOT_PATH')
LOG = logger.get_root_logger(
    __name__, filename=os.path.join(ROOT_PATH, 'output.log'))


@app.route('/user/create', methods=['GET'])
def create_user():
    return render_template('user/create.html')


@app.route('/user/<id>/edit', methods=['GET'])
def edit_user(id):
    data = mongo.db.users.find_one({"_id": ObjectId(id)})

    return render_template('user/edit.html', user=data)


@app.route('/user-update', methods=['POST'])
def update_user():
    mongo.db.users.update_one(
        {"_id": ObjectId(request.form.get('id'))},
        {'$set': {'name': request.form.get('name'), 'email': request.form.get('email')}})
    return redirect('/user', 200)


@app.route('/user/<id>/delete', methods=['GET'])
def delete_user(id):
    db_response = mongo.db.users.delete_one({"_id": ObjectId(id)})
    if db_response.deleted_count == 1:
        return redirect('/user', 200)
    else:
        return jsonify({'ok': True, 'message': 'no record found'}), 200


@app.route('/user', methods=['GET', 'POST'])
def user():
    if request.method == 'GET':
        # Calculate number of documents to skip
        page_num = request.args.get('page', default=1, type=int)
        page_size = 5
        skips = page_size * (page_num - 1)

        # Skip and limit
        data = mongo.db.users.find().skip(skips).limit(page_size)

        return render_template('user/index.html', users=[i for i in data])

    data = request.form
    if request.method == 'POST':

        if data.get('name', None) is not None and data.get('email', None) is not None:
            mongo.db.users.insert_one({'name': data.get('name'), 'email': data.get('email')})
            return redirect('/user', 200)
        else:
            return jsonify({'ok': False, 'message': 'Bad request parameters!'}), 400
