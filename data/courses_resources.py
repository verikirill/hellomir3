from flask_restful import reqparse, abort, Api, Resource
from data import db_session, courses_api
from data.users import User
from data.courses import Courses, CoursesForm
from flask import Flask, render_template, redirect, request, jsonify


def abort_if_courses_not_found(courses_id):
    session = db_session.create_session()
    courses = session.query(Courses).get(courses_id)
    if not courses:
        abort(404, message=f"Course {courses_id} not found")


class CoursesResource(Resource):
    def get(self, courses_id):
        abort_if_courses_not_found(courses_id)
        session = db_session.create_session()
        courses = session.query(Courses).get(courses_id)
        return jsonify({'courses': courses.to_dict(
            only=('type_of_cours', 'about', 'price'))})

    def delete(self, courses_id):
        abort_if_courses_not_found(courses_id)
        session = db_session.create_session()
        courses = session.query(Courses).get(courses_id)
        session.delete(courses)
        session.commit()
        return jsonify({'success': 'OK'})


parser = reqparse.RequestParser()
parser.add_argument('type_of_cours', required=True)
parser.add_argument('about', required=True)
parser.add_argument('price', required=True)


class CoursesListResource(Resource):
    def get(self):
        session = db_session.create_session()
        courses = session.query(Courses).all()
        return jsonify({'courses': [item.to_dict(
            only=('type_of_cours', 'about', 'price')) for item in courses]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        courses = Courses(
            type_of_cours=args['type_of_cours'],
            about=args['about'],
            price=args['price'],
        )
        session.add(courses)
        session.commit()
        return jsonify({'success': 'OK'})
