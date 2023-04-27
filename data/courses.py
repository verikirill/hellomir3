import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class Courses(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'courses'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("users.id"))
    type_of_cours = sqlalchemy.Column(sqlalchemy.Text)
    about = sqlalchemy.Column(sqlalchemy.Text)
    price = sqlalchemy.Column(sqlalchemy.Float)
    url_on_files = sqlalchemy.Column(sqlalchemy.Text)
    user = orm.relationship('User')

    def __repr__(self):
        return self.type_of_cours

class CoursesForm(FlaskForm):
    type_of_cours = StringField('Название курса', validators=[DataRequired()])
    about = TextAreaField('Описание курса:', validators=[DataRequired()])
    price = StringField('Цена курса', validators=[DataRequired()])
    url_on_files = StringField('Ссылка на файлы курса', validators=[DataRequired()])
    submit = SubmitField('Применить')
