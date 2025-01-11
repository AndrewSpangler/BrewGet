from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email
from flask_wtf import FlaskForm

from .models import PermissionsLevel, PermissionsMap

PERM_FORM_OPTIONS = PermissionsMap.copy()
PERM_FORM_OPTIONS.pop(PermissionsLevel.OWNER)
class PermissionForm(FlaskForm):
    permission = SelectField('Set Permission Level', choices=[(key, value) for key, value in PERM_FORM_OPTIONS.items()])
    submit = SubmitField("Submit Changes")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=4, max=80)])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=4, max=80)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")
    
class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Change Password')

class GenerateUserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Generate User')