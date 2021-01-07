from flask_wtf import FlaskForm
from wtforms.validators import Email, DataRequired, EqualTo
from wtforms import StringField, SubmitField, PasswordField
from flask import request

class ProfileForm(FlaskForm):
    first_name = StringField()
    last_name = StringField()
    username = StringField()
    email = StringField(validators=[Email()])
    password = PasswordField()
    confirm_password = PasswordField(validators=[EqualTo('password')])
    submit = SubmitField('Update Profile')

class EditBlogPostForm(FlaskForm):
    body = StringField()
    submit = SubmitField('Edit Post')

class SearchForm(FlaskForm):
    q = StringField(('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)










