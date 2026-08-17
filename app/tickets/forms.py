from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

from app.models import CATEGORIES, CATEGORY_LABELS, Device, PRIORITIES, PRIORITY_LABELS

CATEGORY_CHOICES = [(c, CATEGORY_LABELS[c]) for c in CATEGORIES]
PRIORITY_CHOICES = [(p, PRIORITY_LABELS[p]) for p in PRIORITIES]


class TicketForm(FlaskForm):
    title = StringField(
        "Başlık",
        validators=[
            DataRequired(message="Başlık alanı zorunludur."),
            Length(min=5, max=150, message="Başlık 5-150 karakter arasında olmalıdır."),
        ],
    )
    description = TextAreaField(
        "Açıklama",
        validators=[
            DataRequired(message="Açıklama alanı zorunludur."),
            Length(min=15, message="Lütfen sorunu en az 15 karakterle açıklayınız."),
        ],
        description=(
            "Sorunu olabildiğince ayrıntılı yazınız. "
            "Sistem, yazdığınız açıklamayı analiz ederek kategoriyi otomatik belirler."
        ),
    )
    category = SelectField(
        "Kategori", choices=CATEGORY_CHOICES, default="diger",
        description="Emin değilseniz 'Diğer' olarak bırakabilirsiniz.",
    )
    priority = SelectField(
        "Öncelik", choices=PRIORITY_CHOICES, default="orta",
        description="İşinizi ne kadar aksattığını belirtiniz.",
    )
    device_id = SelectField(
        "İlgili Cihaz",
        choices=[],
        default="0",
        description=(
            "Arıza belirli bir cihazla ilgiliyse seçiniz. "
            "Cihazın üzerindeki QR etiketini okutarak da bu sayfaya gelebilirsiniz."
        ),
    )
    submit = SubmitField("Talebi Gönder")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        devices = Device.query.order_by(Device.serial_no).all()
        self.device_id.choices = [("0", "— Cihaz seçilmedi —")] + [
            (str(d.id), d.label) for d in devices
        ]
