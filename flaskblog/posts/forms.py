from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    service = SelectField(u"Service Type", choices=[], validators=[DataRequired()])
    category = SelectField(u'Category', choices=[], validators=[DataRequired()])
    submit = SubmitField('Post')
