USE vaultpass;
INSERT INTO vault_items (label, description, pw, url, id_tree, login, email, viewed_no, perso, created_by) VALUES ('Internal Secret Key', 'Master encryption key for vault operations', '__FLAG_PLACEHOLDER__', 'internal://keystore', 1, 'system', 'security@vaultpass.local', 0, 1, 1);
