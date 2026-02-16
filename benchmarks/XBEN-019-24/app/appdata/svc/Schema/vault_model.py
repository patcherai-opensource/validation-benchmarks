"""
VaultKeeper - Vault Item Model
Database operations for vault items (passwords, notes, etc.)
"""

class VaultItemModel:
    def __init__(self, db):
        self.db = db

    def get_items_by_folder(self, folder_id, user_id):
        """Get all items in a folder accessible by user"""
        query = """
            SELECT i.id, i.label, i.description, i.url, i.folder_id,
                   i.created_at, i.updated_at
            FROM items i
            JOIN folder_access fa ON i.folder_id = fa.folder_id
            WHERE i.folder_id = %s AND fa.user_id = %s
        """
        return self.db.select(query, (folder_id, user_id))

    def get_item_password(self, item_id, user_id):
        """Retrieve encrypted password for an item"""
        query = """
            SELECT i.encrypted_password, i.encryption_type
            FROM items i
            JOIN folder_access fa ON i.folder_id = fa.folder_id
            WHERE i.id = %s AND fa.user_id = %s
        """
        result = self.db.select(query, (item_id, user_id))
        return result[0] if result else None

    def create_item(self, data):
        """Insert a new vault item"""
        query = """
            INSERT INTO items (label, login, encrypted_password, url,
                             description, folder_id, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        self.db.execute(query, (
            data['label'], data['login'], data['encrypted_password'],
            data.get('url', ''), data.get('description', ''),
            data['folder_id'], data['created_by']
        ))
