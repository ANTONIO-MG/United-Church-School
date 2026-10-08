class PrimaryReplicaRouter:
    """
    Database router for the United Church School LMS project.

    Topology:
        - ``default`` -> PostgreSQL  (PRIMARY: all reads and writes)
        - ``backup``  -> MySQL       (BACKUP / DR server)

    All ORM reads and writes go to the PostgreSQL ``default`` connection.
    The MySQL ``backup`` connection is kept schema-compatible (run
    ``python manage.py migrate --database=backup``) so it can serve as a
    disaster-recovery target / reporting replica.  Application code never
    talks to it implicitly; use ``.using('backup')`` explicitly if needed.
    """

    primary_db = "default"
    backup_db = "backup"

    def db_for_read(self, model, **hints):
        return self.primary_db

    def db_for_write(self, model, **hints):
        return self.primary_db

    def allow_relation(self, obj1, obj2, **hints):
        # Both connections hold the same schema, so relations are fine.
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Migrations run on the primary by default and on the backup when
        # explicitly targeted with ``migrate --database=backup``.
        return db in (self.primary_db, self.backup_db)
