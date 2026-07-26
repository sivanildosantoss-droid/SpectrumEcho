def init_db():
    conn = sqlite3.connect("spectrumecho.db")
    cursor = conn.cursor()
    
    # Cria a tabela de perfis caso não exista
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL DEFAULT 'legacy',
            name TEXT NOT NULL,
            age INTEGER,
            profile_type TEXT,
            support_level INTEGER
        )
    """)
    
    # Se a tabela já existia sem a coluna user_id, adiciona ela dinamicamente
    try:
        cursor.execute("ALTER TABLE profiles ADD COLUMN user_id TEXT DEFAULT 'legacy'")
    except sqlite3.OperationalError:
        pass  # A coluna já existe

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS echolalia_library (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL DEFAULT 'legacy',
            profile_id INTEGER,
            media_title TEXT,
            phrase TEXT,
            meaning_context TEXT,
            FOREIGN KEY(profile_id) REFERENCES profiles(id)
        )
    """)
    try:
        cursor.execute("ALTER TABLE echolalia_library ADD COLUMN user_id TEXT DEFAULT 'legacy'")
    except sqlite3.OperationalError:
        pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensory_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL DEFAULT 'legacy',
            profile_id INTEGER,
            timestamp DATETIME,
            stress_level INTEGER,
            triggers TEXT,
            notes TEXT,
            FOREIGN KEY(profile_id) REFERENCES profiles(id)
        )
    """)
    try:
        cursor.execute("ALTER TABLE sensory_logs ADD COLUMN user_id TEXT DEFAULT 'legacy'")
    except sqlite3.OperationalError:
        pass
    
    conn.commit()
    conn.close()