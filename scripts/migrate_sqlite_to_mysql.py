"""One-off script to migrate data from SQLite to MySQL.

Usage (from project root, with docker compose running):
  docker compose run --rm -v ./data:/app/data bot python scripts/migrate_sqlite_to_mysql.py
"""

import os
import sqlite3
import pymysql

SQLITE_PATH = "data/dog_walker.db"

# Parse DATABASE_URL: mysql+aiomysql://user:pass@host:port/db or mysql+pymysql://...
db_url = os.environ["DATABASE_URL"]
# Strip scheme
parts = db_url.split("://", 1)[1]  # user:pass@host:port/db
userpass, hostrest = parts.rsplit("@", 1)
user, password = userpass.split(":", 1)
hostport, database = hostrest.split("/", 1)
if ":" in hostport:
    host, port = hostport.split(":", 1)
    port = int(port)
else:
    host, port = hostport, 3306

print(f"SQLite: {SQLITE_PATH}")
print(f"MySQL:  {user}@{host}:{port}/{database}")

# Read from SQLite
sqlite_conn = sqlite3.connect(SQLITE_PATH)
sqlite_conn.row_factory = sqlite3.Row
cur = sqlite_conn.cursor()

users = [dict(r) for r in cur.execute("SELECT * FROM users").fetchall()]
walks = [dict(r) for r in cur.execute("SELECT * FROM walks").fetchall()]
sqlite_conn.close()

print(f"\nFound {len(users)} users and {len(walks)} walks in SQLite")

# Write to MySQL
mysql_conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
mysql_cur = mysql_conn.cursor()

# Insert users
inserted_users = 0
for u in users:
    try:
        mysql_cur.execute(
            "INSERT INTO users (id, telegram_id, username, language, is_active, created_at, display_name) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (u["id"], u["telegram_id"], u["username"], u["language"],
             u["is_active"], u["created_at"], u["display_name"]),
        )
        inserted_users += 1
    except pymysql.err.IntegrityError:
        print(f"  Skipping user {u['id']} (already exists)")

# Insert walks
inserted_walks = 0
for w in walks:
    try:
        mysql_cur.execute(
            "INSERT INTO walks (id, user_id, walked_at, didnt_poop, long_walk, is_finalized) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (w["id"], w["user_id"], w["walked_at"], w["didnt_poop"],
             w["long_walk"], w["is_finalized"]),
        )
        inserted_walks += 1
    except pymysql.err.IntegrityError:
        print(f"  Skipping walk {w['id']} (already exists)")

mysql_conn.commit()
mysql_conn.close()

print(f"\nMigrated {inserted_users} users and {inserted_walks} walks to MySQL")
print("Done!")
