import flask
from flask import jsonify
from flask import request
from . import db_session
from .courses import Courses

blueprint = flask.Blueprint(
    'courses_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/courses')
def get_courses():
    db_sess = db_session.create_session()
    courses = db_sess.query(Courses).all()
    return jsonify(
        {
            'courses':
                [item.to_dict(only=('id', 'user_id',
                                    'type_of_cours',
                                    'about',
                                    'price',
                                    'user.name'))
                 for item in courses]
        }
    )


@blueprint.route('/api/courses/<int:courses_id>', methods=['GET'])
def get_one_courses(courses_id):
    db_sess = db_session.create_session()
    courses = db_sess.query(Courses).get(courses_id)
    if not courses:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'courses': courses.to_dict(only=('id', 'user_id',
                                             'type_of_cours',
                                             'about',
                                             'price',))
        }
    )


'''@blueprint.route('/api/courses', methods=['POST'])
def create_courses():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['type_of_cours', 'about', 'price']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    courses = Courses(
        type_of_cours=request.json['team_leader'],
        about=request.json['about'],
        price=request.json['price'],
    )
    db_sess.add(courses)
    db_sess.commit()
    return jsonify({'success': 'OK'})'''

'''@blueprint.route('/api/courses/<int:courses_id>', methods=['DELETE'])
def delete_courses(courses_id):
    db_sess = db_session.create_session()
    courses = db_sess.query(Courses).get(courses_id)
    if not courses:
        return jsonify({'error': 'Not found'})
    db_sess.delete(courses)
    db_sess.commit()
    return jsonify({'success': 'OK'})'''
