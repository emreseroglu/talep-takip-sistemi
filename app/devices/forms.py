from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

from app.extensions import db
from app.models import User

SHARED_ASSIGNEE = "Ortak Kullanım"


def unit_choices():
    rows = (db.session.query(User.department)
            .distinct().order_by(User.department).all())
    return [(row[0], row[0]) for row in rows]


def people_by_unit() -> dict:
    mapping = {}
    for user in User.query.order_by(User.full_name).all():
        mapping.setdefault(user.department, []).append(user.full_name)

    for unit in mapping:
        mapping[unit].append(SHARED_ASSIGNEE)
    return mapping


class DeviceForm(FlaskForm):
    name = StringField(
        "Cihaz Adı",
        validators=[
            DataRequired(message="Cihaz adı zorunludur."),
            Length(min=3, max=120, message="Cihaz adı 3-120 karakter olmalıdır."),
        ],
        description="Marka ve model bilgisiyle yazınız.",
    )
    serial_no = StringField(
        "Seri No / Demirbaş No",
        validators=[
            DataRequired(message="Seri no zorunludur."),
            Length(min=3, max=80, message="Seri no 3-80 karakter olmalıdır."),
        ],
        description="Sistemde benzersiz olmalıdır; QR etiketinde de yazar.",
    )
    location = SelectField(
        "Birim / Konum",
        validators=[DataRequired(message="Birim seçiniz.")],
        description="Cihazın bulunduğu birimi seçiniz.",
    )
    assigned_to = SelectField(
        "Zimmetli Kişi",
        validators=[DataRequired(message="Zimmetli kişi seçiniz.")],
        description="Listede yalnızca seçtiğiniz birimde çalışanlar görünür.",
    )
    submit = SubmitField("Kaydet")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.units = people_by_unit()
        self.location.choices = [("", "— Birim seçiniz —")] + unit_choices()

        everyone = sorted({name for names in self.units.values() for name in names})
        self.assigned_to.choices = [("", "— Kişi seçiniz —")] + [
            (name, name) for name in everyone
        ]

    def validate_assigned_to(self, field):
        if field.data == SHARED_ASSIGNEE:
            return

        if field.data not in self.units.get(self.location.data, []):
            raise ValidationError("Seçilen kişi bu birimde görünmüyor.")
