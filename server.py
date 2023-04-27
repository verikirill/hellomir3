import os

from flask import Flask, render_template, redirect, request, abort, jsonify
from data import db_session
from data.loginfrom import LoginForm
from data.users import User
from data.courses import Courses, CoursesForm
from flask_login import LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField
from wtforms.validators import DataRequired
from flask_login import login_user
from data.users import RegisterForm
import requests
from flask_restful import reqparse, abort, Api, Resource
from data import db_session, courses_api
from flask import make_response
from data import courses_resources
from flask import url_for
from werkzeug.utils import secure_filename
from PIL import Image
import random
import smtplib

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    courses = db_sess.query(Courses)
    if current_user.is_authenticated:
        courses = db_sess.query(Courses).filter(
            (Courses.user == current_user))
    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/buy-courses")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/login")


@app.route('/test')
def test():
    return render_template('obzor-cursa.html')


@app.route('/cours', methods=['GET', 'POST'])
@login_required
def add_cours():
    db_sess = db_session.create_session()
    form = CoursesForm()
    user = db_sess.query(User)
    user_status = user.filter((User.email == current_user.email)).first()
    user_status = user_status.role
    if user_status == 'user':
        return render_template('youareuser.html')
    else:
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            courses = Courses()
            courses.price = form.price.data
            courses.about = form.about.data
            courses.type_of_cours = form.type_of_cours.data
            courses.url_on_files = form.url_on_files.data
            current_user.courses.append(courses)
            db_sess.merge(current_user)
            db_sess.commit()
            if request.method == 'POST':
                file = request.files['file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    db_sess = db_session.create_session()
                    items = db_sess.query(Courses).all()[-1]
                    file.save(os.path.join(UPLOAD_FOLDER, str(items.id) + '.jpg'))
                else:
                    e = random.randint(1, 2)
                    if e == 2:
                        print(1)
                        im1 = Image.open('static/img/investor.jpg')
                    else:
                        print(2)
                        im1 = Image.open('static/img/invest2.jpg')
                    db_sess = db_session.create_session()
                    items = db_sess.query(Courses).all()[-1]
                    im1.save(f'static/uploads/{items.id}.jpg')
            return redirect('/buy-courses')
        return render_template('courses.html', title='Добавление курса', form=form)


@app.route('/courses/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_cours(id):
    form = CoursesForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        cours = db_sess.query(Courses).filter(Courses.id == id,
                                              Courses.user_id == current_user.id
                                              ).first()
        if cours and cours is not None:
            form.type_of_cours.data = cours.type_of_cours
            form.about.data = cours.about
            form.price.data = cours.price
            form.url_on_files.data = cours.url_on_files
        else:
            return redirect('/takogo-cursa-net')
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        cours = db_sess.query(Courses).filter(Courses.id == id,
                                              Courses.user_id == current_user.id
                                              ).first()
        if cours and cours is not None:
            print(form.type_of_cours.data)
            cours.type_of_cours = form.type_of_cours.data
            cours.about = form.about.data
            cours.price = form.price.data
            cours.url_on_files = form.url_on_files.data
            db_sess.commit()
            if request.method == 'POST':
                file = request.files['file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(UPLOAD_FOLDER, str(cours.id) + '.jpg'))
            return redirect('/buy-courses')
        else:
            return redirect('/takogo-cursa-net')
    return render_template('courses.html',
                           title='Редактирование курса',
                           form=form
                           )


@app.route('/cours_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def cours_delete(id):
    print(current_user)
    db_sess = db_session.create_session()
    courses = db_sess.query(Courses).filter(Courses.id == id,
                                            Courses.user_id == current_user.id
                                            ).first()
    if courses:
        db_sess.delete(courses)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/buy-courses')


@app.route('/buy-courses', methods=['GET'])
@login_required
def buy_courses():
    db_sess = db_session.create_session()
    user = db_sess.query(User)
    items = db_sess.query(Courses).order_by(Courses.price).all()
    if current_user.is_authenticated:
        return render_template('buy_courses.html', data=items)
    else:
        return render_template('zaregaysya_brat.html')


@app.route('/contacts', methods=['GET'])
@login_required
def contacts():
    db_sess = db_session.create_session()
    user = db_sess.query(User)
    return render_template('contacts.html')


@app.route('/obzorcursa/<int:id>', methods=['GET', 'POST'])
@login_required
def obozor_courses(id):
    id_int = id
    db_sess = db_session.create_session()
    user = db_sess.query(Courses).filter(Courses.id == id)
    a = db_sess.query(Courses).all()
    max_id = int(a[-1].id)
    min_id = int(a[0].id)
    id_next = max_id
    id_prev = min_id
    for i in range(len(a)):
        if a[i].id == id:
            if int(a[i - 1].id) > int(min_id) and i != 0:
                id_prev = int(a[i - 1].id)
            else:
                id_prev = min_id
            if i != len(a) - 1:
                if int(a[i + 1].id) < int(max_id) and i < len(a) - 1:
                    id_next = int(a[i + 1].id)
            else:
                id_next = max_id
            break
    us_id = current_user.id
    user = user.first()
    delete_id = f'/cours_delete/{id_int}'
    izmen_id = f'/courses/{id_int}'
    id = f'uploads/{id}.jpg'
    return render_template('curs.html', id=id, data=user, id_prev=id_prev, id_next=id_next, id_int=id_int,
                           max_id=max_id, min_id=min_id, us_id=us_id, data_us_id=user.user_id, delete_id=delete_id,
                           izmen_id=izmen_id)


@app.errorhandler(404)
def not_found(error):
    # return make_response(jsonify({'error': 'Not found'}), 404)
    nomer = random.randint(1, 3)
    return render_template('4041.html', nomer=nomer)


# @app.errorhandler(500)
# def oshibka(error):
#     return redirect('/buy-courses')


@app.errorhandler(400)
def bad_request(_):
    return render_template('badrequetsik.html')


@app.route('/send-cours/<int:id>', methods=['GET', 'POST'])
@login_required
def send_cours(id):
    db_sess = db_session.create_session()
    cours = db_sess.query(Courses).filter(Courses.id == id,).first()
    users = db_sess.query(User).filter(User.id == current_user.id).first()
    if (cours and cours is not None) and (users and users is not None):
        users.owned_courses = users.owned_courses + ', ' + str(id)
        db_sess.commit()
    return redirect('/buy-courses')


@app.route('/profile', methods=['GET'])
@login_required
def profile():
    db_sess = db_session.create_session()
    users = db_sess.query(User).filter(User.id == current_user.id).first().owned_courses
    if users == '':
        users = 'У вас нет, приобретённых курсов'
        return render_template('profile1.html', owned_courses=users)
    else:
        owned_courses = users.split(', ')
        print(owned_courses)
        courses = db_sess.query(Courses).all()
        owned_courses.pop(0)
        print(owned_courses)
        for i in range(len(owned_courses)):
            owned_courses[i] = int(owned_courses[i])

    return render_template('profile2.html', owned_courses=owned_courses, courses=courses)


if __name__ == '__main__':
    db_session.global_init("db/courses.db")
    app.register_blueprint(courses_api.blueprint)
    # api.add_resource(jobs_resources.JobsListResource, '/api/v2/jobs')
    # api.add_resource(jobs_resources.JobsResource, '/api/v2/jobs/<int:jobs_id>')
    app.run(port=8082, host='127.0.0.1')
