import json
import re

from flask import Flask, render_template, redirect, url_for, request, session, jsonify, Response
from sqlalchemy import text

from app import app
from app.db import db
from app.models import User, Device, Port, Ipv4Address, AlertRule, EventLog


@app.after_request
def apply_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers.pop('Server', None)
    return response


def require_auth(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


@app.route('/', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    if session.get('user_id'):
        return redirect(url_for('overview'))
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('overview'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html', error=error)


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/overview')
@require_auth
def overview():
    user = User.query.get(session['user_id'])
    devices = Device.query.all()
    up_count = sum(1 for d in devices if d.status == 1)
    down_count = sum(1 for d in devices if d.status == 0)
    events = EventLog.query.order_by(EventLog.event_id.desc()).limit(10).all()
    return render_template('overview.html', user=user, devices=devices,
                           up_count=up_count, down_count=down_count, events=events)


@app.route('/devices')
@require_auth
def devices():
    user = User.query.get(session['user_id'])
    all_devices = Device.query.all()
    return render_template('devices.html', user=user, devices=all_devices)


@app.route('/device/<int:device_id>')
@require_auth
def device_detail(device_id):
    user = User.query.get(session['user_id'])
    device = Device.query.get_or_404(device_id)
    ports = Port.query.filter_by(device_id=device_id).all()
    events = EventLog.query.filter_by(device_id=device_id).order_by(
        EventLog.event_id.desc()).limit(20).all()
    return render_template('device_detail.html', user=user, device=device,
                           ports=ports, events=events)


@app.route('/ports')
@require_auth
def ports():
    user = User.query.get(session['user_id'])
    all_ports = db.session.query(Port, Device).join(Device, Port.device_id == Device.device_id).all()
    return render_template('ports.html', user=user, port_data=all_ports)


@app.route('/alerts')
@require_auth
def alerts():
    user = User.query.get(session['user_id'])
    rules = AlertRule.query.all()
    return render_template('alerts.html', user=user, rules=rules)


@app.route('/eventlog')
@require_auth
def eventlog():
    user = User.query.get(session['user_id'])
    events = EventLog.query.order_by(EventLog.event_id.desc()).all()
    return render_template('eventlog.html', user=user, events=events)


@app.route('/search/inventory')
@require_auth
def search_inventory():
    user = User.query.get(session['user_id'])
    return render_template('search_inventory.html', user=user)


@app.route('/api/data/inventory-lookup', methods=['POST'])
@require_auth
def inventory_lookup():
    search_type = request.form.get('search_type', '')
    address = request.form.get('address', '').strip()
    device_id = request.form.get('device_id', '')
    interface = request.form.get('interface', '')

    current = int(request.form.get('current', 1))
    row_count = int(request.form.get('rowCount', 50))

    params = {}

    if search_type == 'ipv4':
        sql = ("SELECT P.port_id, P.if_descr, P.if_alias, P.hw_address, P.if_speed, "
               "P.if_oper_status, P.in_errors, P.out_errors, D.hostname, D.device_id, "
               "A.ipv4_address, A.ipv4_prefixlen "
               "FROM port P "
               "JOIN device D ON P.device_id = D.device_id "
               "JOIN ipv4_address A ON P.port_id = A.port_id "
               "WHERE 1=1 ")
        if address:
            sql += "AND A.ipv4_address LIKE :addr "
            params['addr'] = '%' + address + '%'

    elif search_type == 'hardware':
        # Normalize MAC address input by stripping common separators
        cleaned = re.sub(r'[: \-\.\s]', '', address).replace('0x', '')
        sql = ("SELECT P.port_id, P.if_descr, P.if_alias, P.hw_address, P.if_speed, "
               "P.if_oper_status, P.in_errors, P.out_errors, D.hostname, D.device_id "
               "FROM port P "
               "JOIN device D ON P.device_id = D.device_id "
               "WHERE P.hw_address LIKE '%" + cleaned + "%' ")

    else:
        return jsonify({'current': current, 'rowCount': row_count, 'rows': [], 'total': 0})

    if device_id and device_id.isdigit():
        sql += "AND P.device_id = :dev_id "
        params['dev_id'] = int(device_id)

    if interface:
        sql += "AND P.if_descr LIKE :iface "
        params['iface'] = interface

    try:
        sql += "ORDER BY D.hostname ASC "

        result = db.session.execute(text(sql), params)
        rows = []
        for row in result:
            row_dict = row._asdict()
            entry = {
                'hostname': row_dict.get('hostname', ''),
                'interface': row_dict.get('if_descr', ''),
                'description': row_dict.get('if_alias', ''),
            }
            if search_type == 'ipv4':
                addr_str = row_dict.get('ipv4_address', '')
                prefix = row_dict.get('ipv4_prefixlen', '')
                entry['address'] = f"{addr_str}/{prefix}" if prefix else addr_str
            elif search_type == 'hardware':
                raw = row_dict.get('hw_address', '')
                if raw and len(raw) == 12:
                    entry['address'] = ':'.join(raw[i:i+2] for i in range(0, 12, 2))
                else:
                    entry['address'] = raw
            rows.append(entry)

        total = len(rows)
        return jsonify({
            'current': current,
            'rowCount': row_count,
            'rows': rows,
            'total': total
        })

    except Exception:
        db.session.rollback()
        return jsonify({
            'current': current,
            'rowCount': row_count,
            'rows': [],
            'total': 0,
            'error': 'Search query failed'
        }), 500


@app.route('/ping')
def health_ping():
    return 'OK', 200
