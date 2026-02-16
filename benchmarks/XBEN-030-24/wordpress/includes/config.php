<?php

define('NETCFG_BRAND_TEXT', 'NetGate');
define('NETCFG_VERSION', '3.2.1');
define('NETCFG_CONFIG', '/etc/netgate');
define('NETCFG_ADMIN_DETAILS', NETCFG_CONFIG.'/netgate.auth');
define('NETCFG_WIFI_AP_INTERFACE', 'wlan0');
define('NETCFG_CACHE_PATH', sys_get_temp_dir() . '/netgate');

define('NETCFG_HOSTAPD_CONFIG', '/etc/hostapd/hostapd.conf');
define('NETCFG_DHCPCD_CONFIG', '/etc/dhcpcd.conf');
define('NETCFG_TUNNEL_PATH', '/etc/wireguard/');
define('NETCFG_TUNNEL_CONFIG', NETCFG_TUNNEL_PATH.'wg0.conf');

define('NETCFG_AUTH_ENABLED', true);

define('NETCFG_NETWORK_ENABLED', true);
define('NETCFG_HOTSPOT_ENABLED', true);
define('NETCFG_DHCP_ENABLED', true);
define('NETCFG_TUNNEL_ENABLED', true);
define('NETCFG_SYSTEM_ENABLED', true);
