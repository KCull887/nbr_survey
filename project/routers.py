patient_data_apps = ["main_repo"]


class CustomDatabaseRouter:

    def db_for_read(self, model, **hints):
        """
        Attempts to read auth models go to auth_db.
        """
        if model._meta.app_label in patient_data_apps:
            return 'patient_data'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth models go to auth_db.
        """
        if model._meta.app_label in patient_data_apps:
            return 'patient_data'
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        If not set, migrations will create duplicate tables in all databases.
        """
        if app_label in patient_data_apps:
            return db == 'patient_data'
        return db == 'default'