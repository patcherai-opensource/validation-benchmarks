import random
import datetime

random.seed(42)
nodes = ['node1', 'node2', 'node3']
resources = ['ip-192.168.1.100', 'apache', 'mysql-primary', 'drbd0', 'fence-node1', 'fence-node2']
actions = ['start', 'stop', 'monitor', 'promote', 'demote', 'migrate_to', 'migrate_from']
severities = ['info', 'notice', 'warning', 'info', 'info', 'info', 'notice']
components = ['pengine', 'crmd', 'lrmd', 'stonith-ng', 'cib', 'attrd', 'pacemakerd']

base = datetime.datetime(2024, 1, 15, 8, 0, 0)
lines = []
for i in range(500):
    dt = base + datetime.timedelta(seconds=random.randint(0, 36000))
    node = random.choice(nodes)
    sev = random.choice(severities)
    comp = random.choice(components)
    rsc = random.choice(resources)
    action = random.choice(actions)

    templates = [
        '{dt} {node} {comp}[{pid}]:  {sev}: Initiating {action} operation {rsc}_{action}_0 on {node}',
        '{dt} {node} {comp}[{pid}]:  {sev}: Operation {rsc}_{action}_0 returned: ok (rc=0)',
        '{dt} {node} {comp}[{pid}]:  {sev}: Resource {rsc} is running on {node}',
        '{dt} {node} {comp}[{pid}]:  notice: Calculated transition {trans}: {rsc}',
        '{dt} {node} {comp}[{pid}]:  {sev}: Node {node} state is member',
        '{dt} {node} {comp}[{pid}]:  info: Performing quorum update',
        '{dt} {node} {comp}[{pid}]:  {sev}: High availability heartbeat from {node}',
    ]

    line = random.choice(templates).format(
        dt=dt.strftime('%b %d %H:%M:%S'),
        node=node,
        comp=comp,
        pid=random.randint(1000, 9999),
        sev=sev,
        rsc=rsc,
        action=action,
        trans=random.randint(40, 200)
    )
    lines.append((dt, line))

lines.sort(key=lambda x: x[0])
with open('/var/log/cluster/ha-log.txt', 'w') as f:
    for _, line in lines:
        f.write(line + '\n')
