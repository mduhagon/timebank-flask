from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, HiddenField, BooleanField, SelectField
from wtforms.validators import DataRequired
from flaskblog.models import TypeOfService

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    lat = HiddenField("lat", validators=[DataRequired()], default="52.5200")
    lng = HiddenField("lng", validators=[DataRequired()], default="13.4050")
    service = SelectField(u'Type of Service', choices=TypeOfService.choices(), coerce=TypeOfService.coerce, validators=[DataRequired()])
    category = SelectField(u'Category', choices=[(1, 'Home Reparations'), (2, 'Gardening'), (3, 'Tutoring'), (4, 'Car/Bike/Boat Reparations'), (5, 'Handcrafts'), (6, 'Pets'), (7, 'Accounting'), (8, 'Fashion & Beauty'), (9, 'Electronic'), (10, 'Music & Movies & Books'), (11, 'Transportation'), (12, 'Foods & Drinks'), (13, 'Photography'), (14, 'Tickets'), (15, 'Other')], validators=[DataRequired()])
    submit = SubmitField('Post')
