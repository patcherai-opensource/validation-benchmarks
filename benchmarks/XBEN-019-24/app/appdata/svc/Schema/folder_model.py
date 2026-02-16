"""
VaultKeeper - Folder Model
Database operations for folder management
"""

class FolderModel:
    def __init__(self, db):
        self.db = db

    def get_folders_for_user(self, user_id):
        """Get all folders accessible by user"""
        query = """
            SELECT f.id, f.title, f.parent_id, f.created_at,
                   fa.access_level
            FROM folders f
            JOIN folder_access fa ON f.id = fa.folder_id
            WHERE fa.user_id = %s
            ORDER BY f.parent_id, f.title
        """
        return self.db.select(query, (user_id,))

    def create_folder(self, title, parent_id, created_by):
        """Create a new folder"""
        query = """
            INSERT INTO folders (title, parent_id, created_by, created_at)
            VALUES (%s, %s, %s, NOW())
        """
        self.db.execute(query, (title, parent_id, created_by))
