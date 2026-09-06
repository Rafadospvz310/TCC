from django.apps import AppConfig

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        from django.db.backends.mysql import base
        from django.db.backends.mysql import features
        
        # Desativa a verificação de versão do MariaDB/MySQL
        base.DatabaseWrapper.check_database_version_supported = lambda self: None
        
        # Desativa o uso de RETURNING em comandos INSERT no MariaDB 10.4
        features.DatabaseFeatures.can_return_columns_from_insert = False