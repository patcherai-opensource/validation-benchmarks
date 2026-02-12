<?php header('Content-Type: text/xml; charset=utf-8'); echo '<?xml version="1.0" encoding="UTF-8"?>'; ?>

<configuration-registry xmlns="http://internal.apache.org/config">
    <registry-info>
        <name>Internal Configuration Service</name>
        <version>2.1.4</version>
        <status>active</status>
    </registry-info>
    <service-entries>
        <entry key="axis.deployment.token"><FLAG></entry>
        <entry key="axis.cluster.name">prod-cluster-01</entry>
        <entry key="axis.service.registry">internal-service:80</entry>
        <entry key="axis.admin.enabled">true</entry>
    </service-entries>
</configuration-registry>
