import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Device, Port, Ipv4Address, AlertRule, EventLog, SystemConfig

app = Flask(__name__)

app.secret_key = 'k8s-nw-prod-9f3a2b7c'

db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_pass = os.environ.get('DB_PASSWORD', 'netwatch_monitoring')
db_name = os.environ.get('DB_NAME', 'netwatch')
db_port = os.environ.get('DB_PORT', '3306')

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.app_context().push()
db.create_all()

existing = User.query.filter_by(username='operator').first()
if not existing:
    # Default monitoring operator account
    operator = User(
        id=1001,
        username='operator',
        password='operator',
        first_name='Network',
        last_name='Operator',
        email='operator@netwatch.local',
        role='viewer',
    )
    db.session.add(operator)

    admin_user = User(
        id=1002,
        username='admin',
        password='Adm!nN3tW@tch#2024',
        first_name='System',
        last_name='Administrator',
        email='admin@netwatch.local',
        role='admin',
    )
    db.session.add(admin_user)
    db.session.commit()

    # Populate devices
    devices_data = [
        Device(device_id=1, hostname='core-rtr-01.dc1.netwatch.local', sys_name='core-rtr-01',
               os='ios-xe', status=1, uptime=8640000, location='DC1-ROW-A'),
        Device(device_id=2, hostname='dist-sw-01.dc1.netwatch.local', sys_name='dist-sw-01',
               os='nxos', status=1, uptime=4320000, location='DC1-ROW-B'),
        Device(device_id=3, hostname='access-sw-01.dc1.netwatch.local', sys_name='access-sw-01',
               os='ios', status=1, uptime=2160000, location='DC1-ROW-C'),
        Device(device_id=4, hostname='fw-edge-01.dc1.netwatch.local', sys_name='fw-edge-01',
               os='panos', status=1, uptime=7200000, location='DC1-DMZ'),
        Device(device_id=5, hostname='wlc-01.dc1.netwatch.local', sys_name='wlc-01',
               os='aireos', status=0, uptime=0, location='DC1-ROW-A'),
        Device(device_id=6, hostname='core-rtr-02.dc2.netwatch.local', sys_name='core-rtr-02',
               os='junos', status=1, uptime=6048000, location='DC2-ROW-A'),
        Device(device_id=7, hostname='mgmt-sw-01.dc1.netwatch.local', sys_name='mgmt-sw-01',
               os='ios', status=1, uptime=1728000, location='DC1-MGMT'),
    ]
    for d in devices_data:
        db.session.add(d)
    db.session.commit()

    # Populate ports with realistic data
    ports_data = [
        # core-rtr-01
        Port(port_id=101, device_id=1, if_descr='GigabitEthernet0/0/0', if_alias='Uplink to ISP-A',
             if_type='ethernetCsmacd', if_speed=1000000000, hw_address='00a1b2c3d401',
             if_oper_status='up', if_admin_status='up', in_octets=982345678, out_octets=876543210,
             in_errors=0, out_errors=0),
        Port(port_id=102, device_id=1, if_descr='GigabitEthernet0/0/1', if_alias='Uplink to ISP-B',
             if_type='ethernetCsmacd', if_speed=1000000000, hw_address='00a1b2c3d402',
             if_oper_status='up', if_admin_status='up', in_octets=567890123, out_octets=432109876,
             in_errors=2, out_errors=0),
        Port(port_id=103, device_id=1, if_descr='TenGigabitEthernet0/1/0', if_alias='Core to dist-sw-01',
             if_type='ethernetCsmacd', if_speed=10000000000, hw_address='00a1b2c3d403',
             if_oper_status='up', if_admin_status='up', in_octets=1234567890, out_octets=987654321,
             in_errors=0, out_errors=0),
        Port(port_id=104, device_id=1, if_descr='Loopback0', if_alias='Management Loopback',
             if_type='softwareLoopback', if_speed=0, hw_address='',
             if_oper_status='up', if_admin_status='up', in_octets=0, out_octets=0,
             in_errors=0, out_errors=0),

        # dist-sw-01
        Port(port_id=201, device_id=2, if_descr='Ethernet1/1', if_alias='Uplink to core-rtr-01',
             if_type='ethernetCsmacd', if_speed=10000000000, hw_address='0050ab12cd01',
             if_oper_status='up', if_admin_status='up', in_octets=876543210, out_octets=765432109,
             in_errors=0, out_errors=0),
        Port(port_id=202, device_id=2, if_descr='Ethernet1/2', if_alias='To access-sw-01',
             if_type='ethernetCsmacd', if_speed=1000000000, hw_address='0050ab12cd02',
             if_oper_status='up', if_admin_status='up', in_octets=345678901, out_octets=234567890,
             in_errors=1, out_errors=0),
        Port(port_id=203, device_id=2, if_descr='Ethernet1/3', if_alias='To access-sw-02',
             if_type='ethernetCsmacd', if_speed=1000000000, hw_address='0050ab12cd03',
             if_oper_status='down', if_admin_status='up', in_octets=0, out_octets=0,
             in_errors=15, out_errors=3),
        Port(port_id=204, device_id=2, if_descr='Vlan100', if_alias='Server VLAN',
             if_type='l3ipvlan', if_speed=0, hw_address='0050ab12cd04',
             if_oper_status='up', if_admin_status='up', in_octets=123456789, out_octets=98765432,
             in_errors=0, out_errors=0),

        # access-sw-01
        Port(port_id=301, device_id=3, if_descr='FastEthernet0/1', if_alias='Workstation-A',
             if_type='ethernetCsmacd', if_speed=100000000, hw_address='aabb11223301',
             if_oper_status='up', if_admin_status='up', in_octets=56789012, out_octets=45678901,
             in_errors=0, out_errors=0),
        Port(port_id=302, device_id=3, if_descr='FastEthernet0/2', if_alias='Workstation-B',
             if_type='ethernetCsmacd', if_speed=100000000, hw_address='aabb11223302',
             if_oper_status='up', if_admin_status='up', in_octets=34567890, out_octets=23456789,
             in_errors=0, out_errors=0),
        Port(port_id=303, device_id=3, if_descr='FastEthernet0/3', if_alias='Printer-Floor2',
             if_type='ethernetCsmacd', if_speed=100000000, hw_address='aabb11223303',
             if_oper_status='up', if_admin_status='up', in_octets=12345678, out_octets=9876543,
             in_errors=0, out_errors=0),
        Port(port_id=304, device_id=3, if_descr='GigabitEthernet0/1', if_alias='Uplink to dist-sw-01',
             if_type='ethernetCsmacd', if_speed=1000000000, hw_address='aabb11223304',
             if_oper_status='up', if_admin_status='up', in_octets=456789012, out_octets=345678901,
             in_errors=0, out_errors=0),

        # fw-edge-01
        Port(port_id=401, device_id=4, if_descr='ethernet1/1', if_alias='Outside Interface',
             if_type='ethernetCsmacd', if_speed=1000000000, hw_address='cc0011ddeef1',
             if_oper_status='up', if_admin_status='up', in_octets=1567890123, out_octets=1234567890,
             in_errors=0, out_errors=0),
        Port(port_id=402, device_id=4, if_descr='ethernet1/2', if_alias='Inside Interface',
             if_type='ethernetCsmacd', if_speed=1000000000, hw_address='cc0011ddeef2',
             if_oper_status='up', if_admin_status='up', in_octets=1098765432, out_octets=987654321,
             in_errors=0, out_errors=0),
        Port(port_id=403, device_id=4, if_descr='ethernet1/3', if_alias='DMZ Interface',
             if_type='ethernetCsmacd', if_speed=1000000000, hw_address='cc0011ddeef3',
             if_oper_status='up', if_admin_status='up', in_octets=234567890, out_octets=123456789,
             in_errors=0, out_errors=0),

        # wlc-01
        Port(port_id=501, device_id=5, if_descr='management', if_alias='WLC Mgmt',
             if_type='ethernetCsmacd', if_speed=1000000000, hw_address='dd22ee33ff01',
             if_oper_status='down', if_admin_status='up', in_octets=0, out_octets=0,
             in_errors=0, out_errors=0),

        # core-rtr-02
        Port(port_id=601, device_id=6, if_descr='ge-0/0/0', if_alias='Uplink to transit-peer',
             if_type='ethernetCsmacd', if_speed=10000000000, hw_address='1122aabb0601',
             if_oper_status='up', if_admin_status='up', in_octets=2345678901, out_octets=1987654321,
             in_errors=0, out_errors=0),
        Port(port_id=602, device_id=6, if_descr='ge-0/0/1', if_alias='Cross-connect to DC1',
             if_type='ethernetCsmacd', if_speed=10000000000, hw_address='1122aabb0602',
             if_oper_status='up', if_admin_status='up', in_octets=876543210, out_octets=765432109,
             in_errors=0, out_errors=0),

        # mgmt-sw-01
        Port(port_id=701, device_id=7, if_descr='GigabitEthernet0/1', if_alias='IPMI-Server01',
             if_type='ethernetCsmacd', if_speed=1000000000, hw_address='eeff00112201',
             if_oper_status='up', if_admin_status='up', in_octets=12345678, out_octets=9876543,
             in_errors=0, out_errors=0),
        Port(port_id=702, device_id=7, if_descr='GigabitEthernet0/2', if_alias='IPMI-Server02',
             if_type='ethernetCsmacd', if_speed=1000000000, hw_address='eeff00112202',
             if_oper_status='up', if_admin_status='up', in_octets=23456789, out_octets=12345678,
             in_errors=0, out_errors=0),
        Port(port_id=703, device_id=7, if_descr='GigabitEthernet0/3', if_alias='Console-Server',
             if_type='ethernetCsmacd', if_speed=1000000000, hw_address='eeff00112203',
             if_oper_status='up', if_admin_status='up', in_octets=3456789, out_octets=2345678,
             in_errors=0, out_errors=0),
    ]
    for p in ports_data:
        db.session.add(p)
    db.session.commit()

    # Populate IPv4 addresses
    ipv4_data = [
        Ipv4Address(ipv4_address_id=1, port_id=101, ipv4_address='203.0.113.1', ipv4_prefixlen=30),
        Ipv4Address(ipv4_address_id=2, port_id=102, ipv4_address='198.51.100.1', ipv4_prefixlen=30),
        Ipv4Address(ipv4_address_id=3, port_id=103, ipv4_address='10.1.0.1', ipv4_prefixlen=30),
        Ipv4Address(ipv4_address_id=4, port_id=104, ipv4_address='10.255.0.1', ipv4_prefixlen=32),
        Ipv4Address(ipv4_address_id=5, port_id=201, ipv4_address='10.1.0.2', ipv4_prefixlen=30),
        Ipv4Address(ipv4_address_id=6, port_id=204, ipv4_address='10.100.0.1', ipv4_prefixlen=24),
        Ipv4Address(ipv4_address_id=7, port_id=301, ipv4_address='10.100.0.101', ipv4_prefixlen=24),
        Ipv4Address(ipv4_address_id=8, port_id=401, ipv4_address='203.0.113.5', ipv4_prefixlen=30),
        Ipv4Address(ipv4_address_id=9, port_id=402, ipv4_address='10.1.0.5', ipv4_prefixlen=30),
        Ipv4Address(ipv4_address_id=10, port_id=403, ipv4_address='10.200.0.1', ipv4_prefixlen=24),
        Ipv4Address(ipv4_address_id=11, port_id=501, ipv4_address='10.1.10.1', ipv4_prefixlen=24),
        Ipv4Address(ipv4_address_id=12, port_id=601, ipv4_address='198.51.100.5', ipv4_prefixlen=30),
        Ipv4Address(ipv4_address_id=13, port_id=602, ipv4_address='10.2.0.1', ipv4_prefixlen=30),
        Ipv4Address(ipv4_address_id=14, port_id=701, ipv4_address='10.250.0.1', ipv4_prefixlen=24),
    ]
    for ip in ipv4_data:
        db.session.add(ip)
    db.session.commit()

    # Populate alert rules
    alerts_data = [
        AlertRule(id=1, rule_name='Device Down', severity='critical', expression='devices.status != 1',
                  enabled=1),
        AlertRule(id=2, rule_name='Port Errors Threshold', severity='warning',
                  expression='ports.in_errors > 10 OR ports.out_errors > 10', enabled=1),
        AlertRule(id=3, rule_name='High CPU Usage', severity='warning',
                  expression='processors.usage > 90', enabled=1),
        AlertRule(id=4, rule_name='Interface Down', severity='critical',
                  expression='ports.if_oper_status = down AND ports.if_admin_status = up', enabled=1),
    ]
    for a in alerts_data:
        db.session.add(a)
    db.session.commit()

    # Populate event log
    events_data = [
        EventLog(event_id=1, device_id=5, message='Device wlc-01 went down', severity='critical',
                 timestamp='2024-10-28 14:23:01'),
        EventLog(event_id=2, device_id=2, message='Port Ethernet1/3 link down on dist-sw-01',
                 severity='warning', timestamp='2024-10-28 13:15:42'),
        EventLog(event_id=3, device_id=1, message='BGP peer 203.0.113.2 established',
                 severity='info', timestamp='2024-10-28 12:00:05'),
        EventLog(event_id=4, device_id=4, message='Firewall policy update applied',
                 severity='info', timestamp='2024-10-28 11:45:30'),
        EventLog(event_id=5, device_id=3, message='Port FastEthernet0/3 errors above threshold',
                 severity='warning', timestamp='2024-10-27 22:10:15'),
        EventLog(event_id=6, device_id=6, message='OSPF adjacency change on ge-0/0/1',
                 severity='info', timestamp='2024-10-27 18:33:22'),
        EventLog(event_id=7, device_id=7, message='New device mgmt-sw-01 discovered',
                 severity='info', timestamp='2024-10-26 09:12:00'),
    ]
    for e in events_data:
        db.session.add(e)
    db.session.commit()

    # Store sensitive configuration data
    with open('/flag') as f:
        flag_content = f.read()

    config_data = [
        SystemConfig(config_id=1, config_group='snmp', config_name='community_ro',
                     config_value='public'),
        SystemConfig(config_id=2, config_group='snmp', config_name='community_rw',
                     config_value='priv4t3-rw'),
        SystemConfig(config_id=3, config_group='auth', config_name='ldap_bind_dn',
                     config_value='cn=svc-netwatch,ou=services,dc=corp,dc=local'),
        SystemConfig(config_id=4, config_group='auth', config_name='ldap_bind_password',
                     config_value='LdapB1nd!Secure'),
        SystemConfig(config_id=5, config_group='system', config_name='license_key',
                     config_value=flag_content),
        SystemConfig(config_id=6, config_group='alerting', config_name='smtp_server',
                     config_value='smtp.netwatch.local'),
        SystemConfig(config_id=7, config_group='alerting', config_name='smtp_port',
                     config_value='587'),
        SystemConfig(config_id=8, config_group='poller', config_name='interval',
                     config_value='300'),
        SystemConfig(config_id=9, config_group='poller', config_name='threads',
                     config_value='16'),
    ]
    for c in config_data:
        db.session.add(c)
    db.session.commit()

from app import routes
