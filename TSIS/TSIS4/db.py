import psycopg2

_CFG = dict(host="localhost", dbname="postgres",
            user="postgres", password="postgres", port=5432)

def _conn():
    return psycopg2.connect(**_CFG)

def init_db():
    with _conn() as c:
        with c.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS snake_players (
                    id         SERIAL PRIMARY KEY,
                    username   VARCHAR(50) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS snake_sessions (
                    id        SERIAL PRIMARY KEY,
                    player_id INTEGER REFERENCES snake_players(id) ON DELETE CASCADE,
                    score     INTEGER NOT NULL,
                    level     INTEGER NOT NULL,
                    played_at TIMESTAMP DEFAULT NOW()
                )
            """)

def get_or_create_player(username: str) -> int:
    with _conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT id FROM snake_players WHERE username=%s", (username,))
            row = cur.fetchone()
            if row:
                return row[0]
            cur.execute(
                "INSERT INTO snake_players(username) VALUES(%s) RETURNING id",
                (username,)
            )
            return cur.fetchone()[0]

def save_session(player_id: int, score: int, level: int):
    with _conn() as c:
        with c.cursor() as cur:
            cur.execute(
                "INSERT INTO snake_sessions(player_id,score,level) VALUES(%s,%s,%s)",
                (player_id, score, level)
            )

def get_top10() -> list:
    try:
        with _conn() as c:
            with c.cursor() as cur:
                cur.execute("""
                    SELECT p.username, s.score, s.level,
                           TO_CHAR(s.played_at, 'YYYY-MM-DD') AS dt
                    FROM snake_sessions s
                    JOIN snake_players p ON p.id = s.player_id
                    ORDER BY s.score DESC
                    LIMIT 10
                """)
                return cur.fetchall()
    except Exception:
        return []
