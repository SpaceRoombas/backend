from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo

class PasswordResetForm(FlaskForm):
    password = PasswordField('Password:', validators=[DataRequired()])
    confirmPassword = PasswordField('Confirm Password:', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('SUBMIT')
    
