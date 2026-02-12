<?php
// TeamPass LDAP Connector Plugin

class LdapConnector
{
    private $server;
    private $baseDn;
    private $adminDn;
    private $adminPassword;

    public function __construct($config)
    {
        $this->server = $config['ldap_server'];
        $this->baseDn = $config['ldap_base_dn'];
    }

    public function authenticate($username, $password)
    {
        $conn = ldap_connect($this->server);
        if (!$conn) return false;

        ldap_set_option($conn, LDAP_OPT_PROTOCOL_VERSION, 3);
        $dn = "uid={$username},{$this->baseDn}";
        
        return @ldap_bind($conn, $dn, $password);
    }
}
