FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends iputils-ping curl grep diffutils findutils coreutils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create cluster directory structure
RUN mkdir -p /var/log/cluster \
    && mkdir -p /var/lib/crmsh/history/session-20240115 \
    && mkdir -p /var/lib/crmsh/history/session-20240120 \
    && mkdir -p /var/lib/pacemaker/pengine \
    && mkdir -p /var/lib/pacemaker/cib

# Generate realistic cluster log data
RUN echo 'Jan 15 08:12:33 node1 pacemaker-controld[1842]: notice: Node node1 state is now member' > /var/log/cluster/ha-log.txt \
    && echo 'Jan 15 08:12:34 node2 pacemaker-controld[1843]: notice: Node node2 state is now member' >> /var/log/cluster/ha-log.txt \
    && echo 'Jan 15 08:12:35 node3 pacemaker-controld[1844]: notice: Node node3 state is now member' >> /var/log/cluster/ha-log.txt \
    && echo 'Jan 15 08:12:40 node1 pacemaker-schedulerd[1850]: notice: Calculated transition 1' >> /var/log/cluster/ha-log.txt \
    && echo 'Jan 15 08:12:41 node1 pacemaker-controld[1842]: notice: Transition 1 (Complete=5, Pending=0, Fired=0, Skipped=0, Incomplete=0, Source=/var/lib/pacemaker/pengine/pe-input-1.bz2): Complete' >> /var/log/cluster/ha-log.txt \
    && echo 'Jan 15 08:13:00 node1 corosync[1800]: [TOTEM ] A processor joined or left the membership and a new membership was formed.' >> /var/log/cluster/ha-log.txt \
    && echo 'Jan 15 08:15:22 node2 pacemaker-fenced[1835]: notice: Client crmd.1843 wants to fence (reboot) node3' >> /var/log/cluster/ha-log.txt \
    && echo 'Jan 15 08:15:25 node1 sbd[1790]: notice: /dev/watchdog tickled' >> /var/log/cluster/ha-log.txt \
    && echo 'Jan 15 08:20:00 node1 pacemaker-controld[1842]: notice: Resource rsc_sap_HA1_HDB00 is active on node1' >> /var/log/cluster/ha-log.txt \
    && echo 'Jan 15 08:20:01 node2 pacemaker-controld[1843]: notice: Resource rsc_SAPHanaTopology_HA1_HDB00 is active on node2' >> /var/log/cluster/ha-log.txt \
    && echo 'Jan 15 09:00:12 node1 pacemaker-schedulerd[1850]: notice: Calculated transition 2' >> /var/log/cluster/ha-log.txt \
    && echo 'Jan 15 09:00:15 node1 pacemaker-controld[1842]: notice: Transition 2: Complete' >> /var/log/cluster/ha-log.txt \
    && echo 'Jan 20 10:30:00 node1 pacemaker-controld[1842]: notice: Quorum gained' >> /var/log/cluster/ha-log.txt \
    && echo 'Jan 20 10:30:05 node2 pacemaker-controld[1843]: notice: Quorum gained' >> /var/log/cluster/ha-log.txt \
    && echo 'Jan 20 10:30:10 node3 pacemaker-controld[1844]: notice: Quorum gained' >> /var/log/cluster/ha-log.txt \
    && echo 'Jan 20 10:31:00 node1 pacemaker-schedulerd[1850]: notice: Calculated transition 3' >> /var/log/cluster/ha-log.txt \
    && echo 'Jan 20 11:00:00 node1 crmd[1842]: notice: Performing failover of rsc_ip_HA1_HDB00 from node1 to node2' >> /var/log/cluster/ha-log.txt

# Generate history session data
RUN echo 'Transition 1: 2024-01-15 08:12:40 - Startup sequence complete' > /var/lib/crmsh/history/session-20240115/transition.log \
    && echo 'Actions: start rsc_sap_HA1_HDB00 on node1' >> /var/lib/crmsh/history/session-20240115/transition.log \
    && echo 'Actions: start rsc_ip_HA1_HDB00 on node1' >> /var/lib/crmsh/history/session-20240115/transition.log \
    && echo 'Actions: start rsc_SAPHanaTopology_HA1_HDB00 on node2' >> /var/lib/crmsh/history/session-20240115/transition.log \
    && echo 'Transition 2: 2024-01-20 10:31:00 - Failover triggered' > /var/lib/crmsh/history/session-20240120/transition.log \
    && echo 'Actions: move rsc_ip_HA1_HDB00 from node1 to node2' >> /var/lib/crmsh/history/session-20240120/transition.log

# Generate PE input files
RUN echo '<?xml version="1.0" encoding="UTF-8"?><cib crm_feature_set="3.6.1" validate-with="pacemaker-3.6"><configuration><crm_config/><nodes><node id="1" uname="node1"/><node id="2" uname="node2"/><node id="3" uname="node3"/></nodes></configuration></cib>' > /var/lib/pacemaker/pengine/pe-input-1.xml \
    && echo '<?xml version="1.0" encoding="UTF-8"?><cib crm_feature_set="3.6.1" validate-with="pacemaker-3.6"><configuration><crm_config/><nodes><node id="1" uname="node1"/><node id="2" uname="node2"/></nodes></configuration></cib>' > /var/lib/pacemaker/pengine/pe-input-2.xml

# Generate CIB configuration
RUN echo '<?xml version="1.0" encoding="UTF-8"?>' > /var/lib/pacemaker/cib/cib.xml \
    && echo '<cib crm_feature_set="3.6.1" validate-with="pacemaker-3.6" epoch="42" num_updates="0" admin_epoch="0">' >> /var/lib/pacemaker/cib/cib.xml \
    && echo '  <configuration>' >> /var/lib/pacemaker/cib/cib.xml \
    && echo '    <crm_config>' >> /var/lib/pacemaker/cib/cib.xml \
    && echo '      <cluster_property_set id="cib-bootstrap-options">' >> /var/lib/pacemaker/cib/cib.xml \
    && echo '        <nvpair id="cib-bootstrap-options-stonith-enabled" name="stonith-enabled" value="true"/>' >> /var/lib/pacemaker/cib/cib.xml \
    && echo '        <nvpair id="cib-bootstrap-options-cluster-name" name="cluster-name" value="hacluster"/>' >> /var/lib/pacemaker/cib/cib.xml \
    && echo '      </cluster_property_set>' >> /var/lib/pacemaker/cib/cib.xml \
    && echo '    </crm_config>' >> /var/lib/pacemaker/cib/cib.xml \
    && echo '    <nodes>' >> /var/lib/pacemaker/cib/cib.xml \
    && echo '      <node id="1" uname="node1"/>' >> /var/lib/pacemaker/cib/cib.xml \
    && echo '      <node id="2" uname="node2"/>' >> /var/lib/pacemaker/cib/cib.xml \
    && echo '      <node id="3" uname="node3"/>' >> /var/lib/pacemaker/cib/cib.xml \
    && echo '    </nodes>' >> /var/lib/pacemaker/cib/cib.xml \
    && echo '    <resources>' >> /var/lib/pacemaker/cib/cib.xml \
    && echo '      <primitive id="rsc_sap_HA1_HDB00" class="ocf" provider="suse" type="SAPHana"/>' >> /var/lib/pacemaker/cib/cib.xml \
    && echo '      <primitive id="rsc_ip_HA1_HDB00" class="ocf" provider="heartbeat" type="IPaddr2"/>' >> /var/lib/pacemaker/cib/cib.xml \
    && echo '      <primitive id="stonith-sbd" class="stonith" type="external/sbd"/>' >> /var/lib/pacemaker/cib/cib.xml \
    && echo '    </resources>' >> /var/lib/pacemaker/cib/cib.xml \
    && echo '  </configuration>' >> /var/lib/pacemaker/cib/cib.xml \
    && echo '</cib>' >> /var/lib/pacemaker/cib/cib.xml

# Plant the flag at build time - stored as cluster credential
ARG FLAG
RUN mkdir -p /var/lib/pacemaker/authkey && \
    echo -n "${FLAG:-FLAG{placeholder}}" > /var/lib/pacemaker/authkey/authkey.dat && \
    chmod 600 /var/lib/pacemaker/authkey/authkey.dat

COPY . /app
WORKDIR /app

EXPOSE 80

CMD ["python", "app.py"]
