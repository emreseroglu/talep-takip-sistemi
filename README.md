# Yapay Zeka Destekli Arıza/Talep Sınıflandırma ve Takip Sistemi

Diyarbakır Tarım ve Orman İl Müdürlüğü – Bilgi İşlem Birimi staj bitirme projesi.

Kurum personelinin donanım, yazılım ve ağ kaynaklı arızalarını bildirdiği;
sistemin bu talepleri makine öğrenmesi ile otomatik kategorize edip öncelik
atadığı; bilgi işlem biriminin talepleri takip edip yönetebildiği web uygulaması.

---

## İçindekiler

- [Özellikler](#özellikler)
- [Kurulum](#kurulum)
- [Örnek Kullanıcılar](#örnek-kullanıcılar)
- [Kullanım Kılavuzu](#kullanım-kılavuzu)
- [Proje Mimarisi](#proje-mimarisi)
- [Yapay Zeka Sınıflandırma Modülü](#yapay-zeka-sınıflandırma-modülü)
- [Veri Modeli](#veri-modeli)
- [Sık Karşılaşılan Sorunlar](#sık-karşılaşılan-sorunlar)

---

## Özellikler

**Personel için**
- Arıza/talep bildirimi (başlık, açıklama, kategori, öncelik)
- Kendi taleplerini listeleme ve durum takibi
- Talep detayında görsel durum çizgisi (Açık → İşlemde → Çözüldü)

**Bilgi işlem için**
- Tüm talepleri görüntüleme; durum, kategori ve önceliğe göre filtreleme
- Durum güncelleme; çözüm süresinin otomatik hesaplanması
- Yapay zeka tahminini personelin seçimiyle karşılaştırmalı görme
- Grafikli yönetim paneli (kategori dağılımı, zaman serisi, arıza türleri,
  ortalama çözüm süresi)

**Cihaz zimmet takibi (QR kod)**
- Cihaz kaydı (birim ve zimmetli kişi bağımlı açılır listelerden seçilir)
- Her cihaz için otomatik QR kod üretimi
- Yazdırılabilir zimmet etiketi (cihaza yapıştırılmak üzere)
- QR okutulduğunda cihazın zimmet bilgisi, açık talepleri ve arıza geçmişi
- Talep formunda isteğe bağlı cihaz seçimi

**SSS chatbotu**
- Sağ alt köşede açılır sohbet balonu (personele gösterilir)
- 22 soru-cevaptan oluşan bilgi tabanı, TF-IDF + kosinüs benzerliğiyle eşleştirme
- En iyi eşleşmenin cevabı gösterilir; diğer eşleşmeler tıklanabilir öneri olur
- Harici yapay zeka servisi gerektirmez; cevap uydurmaz, hazır cevaplardan seçer
- Eşleşme bulunamazsa kullanıcıyı talep oluşturmaya yönlendirir

**Sistem genelinde**
- Rol bazlı yetkilendirme (personel / bilgi işlem)
- Bilgilendirme mesajları kendiliğinden kapanır; hata mesajları ekranda kalır
- Sol yan menülü kurumsal arayüz; dar ekranda açılır panele dönüşür
- Şifrelerin özetlenerek (hash) saklanması
- CSRF koruması, sunucu taraflı form doğrulama
- Türkçe hata mesajları ve hata sayfaları (403 / 404 / 500)

---

## Kurulum

Gereksinim: **Python 3.10 veya üzeri** (geliştirme ortamı: Python 3.13).

```bash
# 1. Depoyu klonla
git clone https://github.com/Ayrton-Senna12/talep-takip-sistemi.git
cd talep-takip-sistemi

# 2. Sanal ortam oluştur ve etkinleştir
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS

# 3. Bağımlılıkları yükle
pip install -r requirements.txt

# 4. Yapay zeka modellerini eğit (models/ klasörüne kaydedilir)
python train_model.py

# 5. Veritabanını oluştur ve örnek kayıtları ekle
python init_db.py

# 6. Uygulamayı başlat
python run.py
```

Uygulama `http://127.0.0.1:5000` adresinde çalışır.

| Komut | İşlevi |
|---|---|
| `python run.py` | Uygulamayı başlatır (yalnızca bu bilgisayardan erişilir) |
| `python run.py --ag` | Yerel ağa açar — **QR kodları telefonla test etmek için gereklidir** |
| `python init_db.py` | Tabloları oluşturur, örnek kayıtları ekler |
| `python init_db.py --reset` | Veritabanını **sıfırlar** ve yeniden kurar |
| `python train_model.py` | Modelleri yeniden eğitir ve başarım raporunu üretir |

> **Sıralama önemlidir:** `train_model.py`, `init_db.py`'den önce çalıştırılmalıdır.
> Aksi hâlde örnek talepler için yapay zeka tahmini üretilemez (uygulama yine de
> çalışır, yalnızca tahmin alanları boş kalır).

### Yapılandırma

Uygulama, hiçbir ayar yapılmadan geliştirme varsayılanlarıyla çalışır.
Ayarları değiştirmek için `.env.example` dosyasını `.env` adıyla kopyalayınız:

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `SECRET_KEY` | geliştirme anahtarı | Oturum çerezlerini imzalar |
| `DATABASE_URL` | `sqlite:///instance/app.db` | Veritabanı bağlantısı |

> ⚠️ **Kurum sunucusuna kurulumda:** `SECRET_KEY` mutlaka değiştirilmeli,
> `init_db.py` içindeki örnek kullanıcılar kaldırılmalı ve uygulama geliştirme
> sunucusu yerine bir WSGI sunucusuyla (Gunicorn, Waitress) çalıştırılmalıdır.

---

## Örnek Kullanıcılar

Tüm hesapların şifresi: `123456`

| Rol | E-posta | Birim |
|-----|---------|-------|
| Bilgi İşlem | `bilgiislem@tarimorman.gov.tr` | Bilgi İşlem Birimi |
| Personel | `ayse.demir@tarimorman.gov.tr` | Bitkisel Üretim ve Bitki Sağlığı |
| Personel | `fatih.kaya@tarimorman.gov.tr` | Hayvan Sağlığı ve Yetiştiriciliği |
| Personel | `zeynep.aslan@tarimorman.gov.tr` | Kırsal Kalkınma ve Örgütlenme |

> Bu hesaplar yalnızca geliştirme ve tanıtım amaçlıdır. Gerçek kurulumda
> `init_db.py` içindeki `DEMO_USERS` listesi kaldırılmalı ve şifreler
> güçlendirilmelidir.

---

## Kullanım Kılavuzu

### Personel akışı

1. Giriş yapılır → doğrudan **Taleplerim** ekranı açılır
2. **Yeni Talep** → başlık ve açıklama yazılır, kategori/öncelik seçilir
3. Talep gönderildiğinde sistem metni analiz eder ve kendi tahminini kaydeder
4. Talep detayından durum takip edilir

### Bilgi işlem akışı

1. Giriş yapılır → **Panel** açılır (sayaçlar, son talepler, grafikler)
2. **Talepler** menüsünden filtreleme yapılır
3. Talep detayında:
   - Bildiren personel ve talep künyesi görülür
   - **Yapay Zeka Sınıflandırması** kartında personelin seçimi ile modelin
     tahmini yan yana gösterilir; farklıysa satır sarıya boyanır
   - Sağdaki butonlarla durum güncellenir

### Adres yapısı

| Adres | Yetki | İşlev |
|---|---|---|
| `/auth/giris` | Herkes | Giriş ekranı |
| `/auth/profil` | Giriş yapmış | Şifre değiştirme |
| `/talepler/` | Personel | Kendi talepleri |
| `/talepler/yeni` | Personel | Yeni talep formu |
| `/talepler/<id>` | Sahibi / Bilgi işlem | Talep detayı |
| `/yonetim/` | Bilgi işlem | Grafikli panel |
| `/yonetim/talepler` | Bilgi işlem | Tüm talepler + filtreler |
| `/yonetim/talepler/<id>` | Bilgi işlem | Detay + durum güncelleme |
| `/cihazlar/` | Bilgi işlem | Zimmetli cihaz listesi |
| `/cihazlar/yeni` | Bilgi işlem | Yeni cihaz kaydı |
| `/cihazlar/<id>` | Bilgi işlem | **QR okutulunca açılan sayfa** |
| `/cihazlar/<id>/qr.png` | Bilgi işlem | QR görseli (`?boyut=buyuk`, `?indir=1`) |
| `/cihazlar/<id>/etiket` | Bilgi işlem | Yazdırılabilir zimmet etiketi |
| `/sss/sor` | Giriş yapmış | Chatbot mesaj uç noktası (POST, JSON) |
| `/sss/sorular` | Giriş yapmış | Sohbete başlarken gösterilen örnek sorular |

---

## Proje Mimarisi

```
talep-takip-sistemi/
├── app/
│   ├── __init__.py           # Uygulama fabrikası (create_app), hata sayfaları
│   ├── extensions.py         # Eklenti nesneleri (db, login_manager, csrf)
│   ├── models.py             # Veritabanı modelleri: User, Ticket, Device
│   ├── decorators.py         # Rol bazlı yetkilendirme (@it_required)
│   ├── auth/                 # Giriş / çıkış / profil
│   │   ├── forms.py
│   │   └── routes.py
│   ├── main/                 # Rol bazlı ana yönlendirme, hakkında sayfası
│   ├── tickets/              # Personelin talep işlemleri
│   │   ├── forms.py
│   │   └── routes.py
│   ├── admin/                # Bilgi işlem paneli
│   │   ├── routes.py
│   │   └── statistics.py     # Dashboard istatistik hesaplamaları
│   ├── devices/              # Cihaz zimmet takibi
│   │   ├── forms.py
│   │   ├── qr.py             # QR kod üretimi
│   │   └── routes.py
│   ├── chatbot/              # SSS chatbot uç noktaları
│   │   └── routes.py
│   ├── ml/                   # Yapay zeka modülü
│   │   ├── preprocessing.py  # Türkçe metin temizleme
│   │   ├── classifier.py     # Model yükleme ve tahmin
│   │   └── faq.py            # SSS eşleştirme (TF-IDF + kosinüs benzerliği)
│   ├── templates/            # Jinja2 şablonları
│   │   ├── base.html         # Ana şablon (üst bant, sol yan menü, footer)
│   │   ├── _flash.html       # Bildirim mesajları
│   │   ├── macros.html       # Form alanı ve hata özeti makroları
│   │   ├── chatbot_widget.html
│   │   ├── devices/
│   │   ├── auth/ tickets/ admin/ main/ errors/
│   └── static/
│       ├── css/style.css     # Kurumsal tema
│       └── img/favicon.svg
├── data/
│   ├── training_data.csv     # 205 satırlık Türkçe eğitim verisi
│   └── faq.json              # 22 soru-cevaplık SSS bilgi tabanı
├── models/                   # Eğitilmiş ML modelleri (train_model.py üretir)
├── reports/                  # Model başarım raporu (train_model.py üretir)
├── instance/                 # SQLite veritabanı (init_db.py üretir)
├── config.py                 # Yapılandırma
├── init_db.py                # Veritabanı kurulum betiği
├── train_model.py            # Model eğitim betiği
├── run.py                    # Çalıştırma noktası
├── .env.example              # Ortam değişkeni örneği
└── requirements.txt
```

> `models/`, `reports/` ve `instance/` klasörleri depoya dâhil değildir; ilk kurulumda
> `train_model.py` ve `init_db.py` tarafından oluşturulurlar.

Uygulama **blueprint** yapısıyla modüllere ayrılmıştır. Her blueprint kendi
rotalarını (`routes.py`) ve gerekiyorsa formlarını (`forms.py`) barındırır.
Eklentiler `extensions.py` içinde uygulamadan bağımsız tanımlanır; bu, dairesel
import sorununu önler.

### Kullanılan Teknolojiler

| Katman | Teknoloji |
|--------|-----------|
| Backend | Python 3.13, Flask 3 |
| Veritabanı | SQLite + SQLAlchemy ORM |
| Kimlik doğrulama | Flask-Login |
| Formlar / doğrulama | Flask-WTF, WTForms |
| Yapay zeka | scikit-learn (TF-IDF + Naive Bayes) |
| Arayüz | Jinja2, Bootstrap 5 |
| Raporlama | Chart.js 4 |

---

## Yapay Zeka Sınıflandırma Modülü

Personel yeni bir talep oluşturduğunda, başlık ve açıklama metni
`app/ml/classifier.py` üzerinden iki ayrı modele verilir:

| Model | Görev | Dosya | Başarım (5-kat CV) |
|---|---|---|---|
| Kategori modeli | donanım / yazılım / ağ / diğer | `models/category_model.joblib` | %78.1 |
| Öncelik modeli | düşük / orta / yüksek | `models/priority_model.joblib` | %70.2 |

**Yöntem:** TF-IDF vektörleştirme (2–5 karakterlik `char_wb` n-gram) +
Multinomial Naive Bayes.

Türkçe eklemeli bir dil olduğu için kelime bazlı yerine **karakter bazlı**
n-gram kullanılmıştır: "yazıcı / yazıcıda / yazıcının" kelime bazlı bir modelde
üç ayrı kelimedir, karakter n-gram'ında ise ortak `yazıc` parçasını paylaşır.
Bu tercih başarımı kategori tarafında %63'ten %78'e yükseltmiştir.

**Şeffaflık ilkesi:** Model tahmini personelin seçimini **değiştirmez**. Her iki
değer de ayrı alanlarda saklanır ve bilgi işlem panelinde karşılaştırmalı
gösterilir. Nihai karar bilgi işlem personeline aittir.

---

## Veri Modeli

```
┌────────────────┐        ┌─────────────────────────┐        ┌──────────────┐
│ User           │        │ Ticket                  │        │ Device       │
├────────────────┤        ├─────────────────────────┤        ├──────────────┤
│ id             │───┐    │ id                      │   ┌────│ id           │
│ full_name      │   └───<│ user_id (FK)            │   │    │ name         │
│ email          │        │ device_id (FK)          │>──┘    │ assigned_to  │
│ department     │        │ title / description     │        │ serial_no    │
│ role           │        │ category / priority     │        │ location     │
│ password_hash  │        │ status                  │        │ registered_at│
│ created_at     │        │ predicted_category      │        └──────────────┘
└────────────────┘        │ predicted_priority      │
                          │ category_confidence     │
                          │ priority_confidence     │
                          │ created_at / updated_at │
                          │ resolved_at             │
                          └─────────────────────────┘
```

| Alan grubu | Değerler |
|---|---|
| `role` | `personel`, `bilgi_islem` |
| `category` | `donanim`, `yazilim`, `ag`, `diger` |
| `priority` | `dusuk`, `orta`, `yuksek` |
| `status` | `acik`, `islemde`, `cozuldu` |

> Sütun adları kod standardı gereği İngilizce; veri değerleri Türkçe'dir.
> Bunun nedeni bu değerlerin aynı zamanda makine öğrenmesi etiketleri olmasıdır.

> `Device.location` alanı cihazın bulunduğu **birimi** tutar ve kullanıcıların
> `department` değerleriyle aynı listeden seçilir. Cihaz formunda önce birim
> seçilir, kişi listesi de o birimde çalışanlarla sınırlanır.

---

## Sık Karşılaşılan Sorunlar

| Sorun | Çözüm |
|---|---|
| `ModuleNotFoundError: No module named 'flask'` | Sanal ortam etkin değil. `venv\Scripts\activate` çalıştırın. |
| Talep oluşturuluyor ama tahmin üretilmiyor | Modeller eğitilmemiş. `python train_model.py` çalıştırın. |
| `no such column: tickets.category_confidence` | Veritabanı eski şemada. `python init_db.py --reset` çalıştırın. |
| Grafikler görünmüyor | Chart.js CDN'den yüklenir; internet bağlantısını kontrol edin. |
| VS Code "paket kurulu değil" uyarısı veriyor | `Ctrl+Shift+P` → *Python: Select Interpreter* → `.\venv\Scripts\python.exe` |
| Port 5000 kullanımda | `run.py` içindeki `app.run(debug=True)` satırını `app.run(debug=True, port=5001)` yapın. |
| QR kod telefonda açılmıyor | Uygulamayı `python run.py --ag` ile başlatın ve telefondan **ekranda yazan ağ adresine** girin. `127.0.0.1` ile açılan sayfada üretilen QR kod telefonda çalışmaz. |
| Telefon ağ adresine bağlanamıyor | Windows Güvenlik Duvarı 5000 portunu engelliyor olabilir; telefon ve bilgisayar aynı Wi-Fi ağında olmalıdır. |

---

## Lisans

MIT — ayrıntılar için [LICENSE](LICENSE) dosyasına bakınız.
