import socket
import sys

from app import create_app

app = create_app()


def local_ip() -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except OSError:
            return "127.0.0.1"


if __name__ == "__main__":
    if "--ag" in sys.argv:
        adres = local_ip()
        print("=" * 58)
        print("  Uygulama yerel ağa açıldı.")
        print(f"  Bu bilgisayardan : http://127.0.0.1:5000")
        print(f"  Telefon/tabletten: http://{adres}:5000")
        print()
        print("  QR kodların telefonda çalışması için uygulamaya")
        print(f"  http://{adres}:5000 adresinden giriniz.")
        print("=" * 58)
        app.run(debug=True, host="0.0.0.0", port=5000)
    else:
        app.run(debug=True)
