from sqlalchemy import Engine, inspect, text


def migrate_schedule_time_column(engine: Engine) -> None:
    inspector = inspect(engine)
    if "schedules" not in inspector.get_table_names():
        return

    columns = {column["name"]: column for column in inspector.get_columns("schedules")}
    if columns["time"]["nullable"]:
        return

    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE schedules_migrated (
                id INTEGER NOT NULL PRIMARY KEY,
                date DATE NOT NULL,
                time TIME,
                title VARCHAR(200) NOT NULL,
                alert_enabled BOOLEAN NOT NULL DEFAULT 0,
                notified_at DATETIME,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))
        connection.execute(text("""
            INSERT INTO schedules_migrated
                (id, date, time, title, alert_enabled, notified_at, created_at, updated_at)
            SELECT id, date, time, title, alert_enabled, notified_at, created_at, updated_at
            FROM schedules
        """))
        connection.execute(text("DROP TABLE schedules"))
        connection.execute(text("ALTER TABLE schedules_migrated RENAME TO schedules"))
