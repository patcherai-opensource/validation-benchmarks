# Application constants for OpenRefine extensions
# Extension configuration

GDATA_EXTENSION = {
    "name": "Google Data Extension",
    "version": "1.3.0",
    "description": "Import and export data from Google Sheets, Fusion Tables, and other Google services.",
    "oauth_scopes": [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/fusiontables"
    ]
}

DATABASE_EXTENSION = {
    "name": "Database Extension",
    "version": "1.2.1",
    "description": "Connect to relational databases for import and export.",
    "supported_databases": ["MySQL", "PostgreSQL", "SQLite", "MariaDB"]
}

WIKIDATA_EXTENSION = {
    "name": "Wikidata Extension",
    "version": "1.1.0",
    "description": "Upload edits directly to Wikidata from OpenRefine."
}
