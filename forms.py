from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[DataRequired()])
    password = PasswordField("Пароль: ", validators=[DataRequired()])
    remember = BooleanField("Запомнить", default=False)
    submit = SubmitField("Войти")

class RegistrationForm(FlaskForm):
    name = StringField("Name: ", validators=[DataRequired()])
    email = StringField("Email: ", validators=[DataRequired()])
    password = PasswordField("Пароль: ", validators=[DataRequired()])
    repeatPassword = PasswordField("Пароль: ", validators=[DataRequired()])
    submit = SubmitField("Зарегестрироваться")

class CreateChatForm(FlaskForm):
    name = StringField("Name: ")
    chooses = SelectField("Chooses")
    submit = SubmitField("Создать")

class SendMessage(FlaskForm):
    text = StringField("Text of message")
    submit = SubmitField("Send")

class UpdateProfile(FlaskForm):
    name = StringField("Name")
    age = StringField("Age")
    aboutUser = StringField("About you")
    submit = SubmitField("Save changes")

class ChangePassword(FlaskForm):
    oldpassword = PasswordField("Old password: ", validators=[DataRequired()])
    newpassword = PasswordField("New password: ", validators=[DataRequired()])
    repeatpassword = PasswordField("Repeat password: ", validators=[DataRequired()])
    submit = SubmitField("Submit")