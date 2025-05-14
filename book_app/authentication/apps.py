from django.apps import AppConfig

class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentication'
    label = 'auth_custom'  # This gives our app a unique label different from Django's auth 