from flask import Response, abort, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.decorators import it_required
from app.devices import devices_bp
from app.devices.forms import DeviceForm
from app.devices.qr import generate_qr_png
from app.extensions import db
from app.models import Device


def _device_url(device: Device) -> str:
    return url_for("devices.device_detail", device_id=device.id, _external=True)


@devices_bp.route("/")
@login_required
@it_required
def device_list():
    devices = Device.query.order_by(Device.serial_no).all()
    return render_template("devices/device_list.html", devices=devices)


@devices_bp.route("/yeni", methods=["GET", "POST"])
@login_required
@it_required
def new_device():
    form = DeviceForm()
    if form.validate_on_submit():
        serial_no = form.serial_no.data.strip().upper()

        if Device.query.filter_by(serial_no=serial_no).first():
            flash(f"'{serial_no}' seri numaralı bir cihaz zaten kayıtlı.", "danger")
            return render_template("devices/new_device.html", form=form,
                                   units=form.units)

        device = Device(
            name=form.name.data.strip(),
            serial_no=serial_no,
            assigned_to=form.assigned_to.data,
            location=form.location.data,
        )
        db.session.add(device)
        db.session.commit()

        flash(f"'{device.name}' cihazı kaydedildi. QR etiketi hazır.", "success")
        return redirect(url_for("devices.device_detail", device_id=device.id))

    return render_template("devices/new_device.html", form=form, units=form.units)


@devices_bp.route("/<int:device_id>")
@login_required
@it_required
def device_detail(device_id):
    device = db.session.get(Device, device_id)
    if device is None:
        abort(404)

    return render_template("devices/device_detail.html", device=device)


@devices_bp.route("/<int:device_id>/qr.png")
@login_required
@it_required
def device_qr(device_id):
    device = db.session.get(Device, device_id)
    if device is None:
        abort(404)

    box_size = 12 if request.args.get("boyut") == "buyuk" else 6
    png = generate_qr_png(_device_url(device), box_size=box_size)

    response = Response(png, mimetype="image/png")
    if request.args.get("indir"):
        response.headers["Content-Disposition"] = (
            f'attachment; filename="qr-{device.serial_no}.png"'
        )
    return response


@devices_bp.route("/<int:device_id>/etiket")
@login_required
@it_required
def device_label(device_id):
    device = db.session.get(Device, device_id)
    if device is None:
        abort(404)
    return render_template("devices/device_label.html", device=device)
