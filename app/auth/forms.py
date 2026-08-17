from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class LoginForm(FlaskForm):
    email = StringField(
        "E-posta",
        validators=[
            DataRequired(message="E-posta adresi zorunludur."),
            Email(message="Geçerli bir e-posta adresi giriniz."),
        ],
    )
    password = PasswordField(
        "Şifre", validators=[DataRequired(message="Şifre zorunludur.")]
    )
    remember_me = BooleanField("Beni hatırla")
    submit = SubmitField("Giriş Yap")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(
        "Mevcut Şifre", validators=[DataRequired(message="Mevcut şifre zorunludur.")]
    )
    new_password = PasswordField(
        "Yeni Şifre",
        validators=[
            DataRequired(message="Yeni şifre zorunludur."),
            Length(min=6, message="Şifre en az 6 karakter olmalıdır."),
        ],
    )
    confirm_password = PasswordField(
        "Yeni Şifre (Tekrar)",
        validators=[
            DataRequired(message="Şifre tekrarı zorunludur."),
            EqualTo("new_password", message="Şifreler eşleşmiyor."),
        ],
    )
    submit = SubmitField("Şifreyi Güncelle")
