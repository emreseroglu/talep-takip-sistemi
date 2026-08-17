import sys
from datetime import datetime, timedelta

from app import create_app
from app.extensions import db
from app.ml.classifier import classify, is_ready
from app.models import Device, ROLE_IT, ROLE_STAFF, Ticket, User

DEMO_USERS = [
    {
        "full_name": "Mehmet Yılmaz",
        "email": "bilgiislem@tarimorman.gov.tr",
        "department": "Bilgi İşlem Birimi",
        "role": ROLE_IT,
        "password": "123456",
    },
    {
        "full_name": "Ayşe Demir",
        "email": "ayse.demir@tarimorman.gov.tr",
        "department": "Bitkisel Üretim ve Bitki Sağlığı Şube Müdürlüğü",
        "role": ROLE_STAFF,
        "password": "123456",
    },
    {
        "full_name": "Fatih Kaya",
        "email": "fatih.kaya@tarimorman.gov.tr",
        "department": "Hayvan Sağlığı ve Yetiştiriciliği Şube Müdürlüğü",
        "role": ROLE_STAFF,
        "password": "123456",
    },
    {
        "full_name": "Zeynep Aslan",
        "email": "zeynep.aslan@tarimorman.gov.tr",
        "department": "Kırsal Kalkınma ve Örgütlenme Şube Müdürlüğü",
        "role": ROLE_STAFF,
        "password": "123456",
    },
]

DEMO_DEVICES = [
    {
        "name": "HP ProDesk 400 G7 Masaüstü",
        "assigned_to": "Ayşe Demir",
        "serial_no": "TRM-PC-001",
        "location": "Bitkisel Üretim ve Bitki Sağlığı Şube Müdürlüğü",
    },
    {
        "name": "Canon i-SENSYS MF443dw Yazıcı",
        "assigned_to": "Ortak Kullanım",
        "serial_no": "TRM-PRN-002",
        "location": "Bitkisel Üretim ve Bitki Sağlığı Şube Müdürlüğü",
    },
    {
        "name": "Lenovo ThinkPad E15 Dizüstü",
        "assigned_to": "Fatih Kaya",
        "serial_no": "TRM-NB-003",
        "location": "Hayvan Sağlığı ve Yetiştiriciliği Şube Müdürlüğü",
    },
    {
        "name": "Epson EB-X49 Projeksiyon Cihazı",
        "assigned_to": "Ortak Kullanım",
        "serial_no": "TRM-PRJ-004",
        "location": "Kırsal Kalkınma ve Örgütlenme Şube Müdürlüğü",
    },
]


DEMO_TICKETS = [
    (18, 6, "ayse.demir@tarimorman.gov.tr",
     "Yazıcıda kağıt sıkışması",
     "İkinci kattaki ortak yazıcıya çıktı gönderdiğimde kağıt sıkışıyor ve "
     "ekranda kırmızı uyarı ışığı yanıyor. Sıkışan kağıdı çıkardım ama sorun devam ediyor.",
     "donanim", "orta", "cozuldu"),

    (15, 2, "fatih.kaya@tarimorman.gov.tr",
     "Excel dosyası açılmıyor",
     "Hayvan kayıt listesini tuttuğumuz Excel dosyasını açmak istediğimde "
     "'dosya bozuk' hatası veriyor ve program kapanıyor.",
     "yazilim", "yuksek", "cozuldu"),

    (12, 24, "zeynep.aslan@tarimorman.gov.tr",
     "İnternet bağlantısı kopuyor",
     "Odamdaki bilgisayarda internet sürekli kesiliyor. Ağ kablosunu değiştirdim "
     "ancak sorun düzelmedi. Kablosuz ağa da bağlanamıyorum.",
     "ag", "yuksek", "cozuldu"),

    (9, 4, "ayse.demir@tarimorman.gov.tr",
     "Bilgisayar çok yavaş açılıyor",
     "Bilgisayarım açılırken yaklaşık on dakika sürüyor. Açıldıktan sonra da "
     "programlar geç tepki veriyor.",
     "donanim", "dusuk", "cozuldu"),

    (7, None, "fatih.kaya@tarimorman.gov.tr",
     "EBYS sistemine giriş yapamıyorum",
     "Elektronik Belge Yönetim Sistemine kullanıcı adı ve şifremle giriş yapmaya "
     "çalışıyorum ancak 'yetkisiz kullanıcı' uyarısı alıyorum.",
     "yazilim", "yuksek", "islemde"),

    (6, None, "zeynep.aslan@tarimorman.gov.tr",
     "Klavyede bazı tuşlar çalışmıyor",
     "Klavyemde Q, W ve E tuşları basmama rağmen yazmıyor. Başka bir klavye "
     "denediğimde sorun yaşanmıyor.",
     "donanim", "dusuk", "islemde"),

    (5, 3, "ayse.demir@tarimorman.gov.tr",
     "Yazıcı ağda görünmüyor",
     "Bilgisayarımdan yazıcıyı bulamıyorum. Yazıcı listesinde görünmüyor, "
     "elle eklemeye çalıştığımda da bağlanamıyor.",
     "ag", "orta", "cozuldu"),

    (4, None, "fatih.kaya@tarimorman.gov.tr",
     "Monitör görüntü vermiyor",
     "Bilgisayarı açtığımda kasa çalışıyor ancak ekran siyah kalıyor. "
     "Kabloları kontrol ettim, takılı görünüyor.",
     "donanim", "yuksek", "acik"),

    (3, None, "zeynep.aslan@tarimorman.gov.tr",
     "Ofis programı lisans uyarısı veriyor",
     "Word ve Excel açıldığında lisans süresinin dolduğuna dair uyarı çıkıyor "
     "ve dosyaları kaydetmeme izin vermiyor.",
     "yazilim", "orta", "acik"),

    (2, None, "ayse.demir@tarimorman.gov.tr",
     "Yeni personel için kullanıcı hesabı talebi",
     "Birimimize yeni katılan personel için sisteme kullanıcı hesabı "
     "açılmasını ve bilgisayar kurulumunun yapılmasını rica ederim.",
     "diger", "dusuk", "acik"),

    (1, None, "fatih.kaya@tarimorman.gov.tr",
     "Kablosuz ağa bağlanamıyorum",
     "Dizüstü bilgisayarım kurum kablosuz ağını görüyor ancak şifreyi girdiğimde "
     "bağlanamıyor, sürekli kimlik doğrulama hatası veriyor.",
     "ag", "orta", "acik"),

    (0, None, "zeynep.aslan@tarimorman.gov.tr",
     "Tarayıcıdan belge taranamıyor",
     "Çok fonksiyonlu yazıcının tarama özelliğini kullanamıyorum. "
     "Tara tuşuna bastığımda 'bağlantı yok' hatası alıyorum.",
     "donanim", "orta", "acik"),
]


def guess_device_id(title, email):
    text = title.lower()
    if "yazıcı" in text or "tarayıcı" in text:
        serial_no = "TRM-PRN-002"
    elif email.startswith("ayse"):
        serial_no = "TRM-PC-001"
    elif email.startswith("fatih"):
        serial_no = "TRM-NB-003"
    else:
        return None

    device = Device.query.filter_by(serial_no=serial_no).first()
    return device.id if device else None


def seed_tickets():
    if Ticket.query.count() > 0:
        return 0

    now = datetime.now()
    added = 0
    for (days_ago, solve_hours, email, title, description,
         category, priority, status) in DEMO_TICKETS:
        user = User.query.filter_by(email=email).first()
        if user is None:
            continue

        created = now - timedelta(days=days_ago, hours=2)
        resolved = created + timedelta(hours=solve_hours) if solve_hours else None

        prediction = classify(title, description)

        db.session.add(Ticket(
            user_id=user.id,
            device_id=guess_device_id(title, email),
            title=title,
            description=description,
            category=category,
            priority=priority,
            status=status,
            created_at=created,
            updated_at=resolved or created,
            resolved_at=resolved,
            predicted_category=prediction["category"],
            predicted_priority=prediction["priority"],
            category_confidence=prediction["category_confidence"],
            priority_confidence=prediction["priority_confidence"],
        ))
        added += 1
    return added


def seed_users():
    added = 0
    for item in DEMO_USERS:
        if User.query.filter_by(email=item["email"]).first():
            continue
        user = User(
            full_name=item["full_name"],
            email=item["email"],
            department=item["department"],
            role=item["role"],
        )
        user.set_password(item["password"])
        db.session.add(user)
        added += 1
    return added


def seed_devices():
    added = 0
    for item in DEMO_DEVICES:
        if Device.query.filter_by(serial_no=item["serial_no"]).first():
            continue
        db.session.add(Device(**item))
        added += 1
    return added


def main():
    reset = "--reset" in sys.argv
    app = create_app()

    with app.app_context():
        if reset:
            db.drop_all()
            print("[!] Mevcut tablolar silindi.")

        db.create_all()
        print("[+] Tablolar oluşturuldu: users, tickets, devices")

        if not is_ready():
            print("[!] Uyarı: Eğitilmiş model bulunamadı. Örnek talepler için "
                  "yapay zeka tahmini üretilmeyecek.")
            print("    Modelleri eğitmek için: python train_model.py")

        user_count = seed_users()
        device_count = seed_devices()
        db.session.commit()

        ticket_count = seed_tickets()
        db.session.commit()

        print(f"[+] {user_count} örnek kullanıcı eklendi.")
        print(f"[+] {device_count} örnek cihaz eklendi.")
        print(f"[+] {ticket_count} örnek talep eklendi.")
        print("\nGiriş bilgileri (tüm hesapların şifresi: 123456)")
        print("-" * 55)
        for item in DEMO_USERS:
            rol = "Bilgi İşlem" if item["role"] == ROLE_IT else "Personel"
            print(f"  {rol:<12} | {item['email']}")
        print("-" * 55)
        print("\nUygulamayı başlatmak için: python run.py")


if __name__ == "__main__":
    main()
