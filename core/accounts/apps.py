from django.apps import AppConfig

class AccountsConfig(AppConfig):
    name = 'accounts'  # or whatever your app name is

    def ready(self):
        import accounts.signals  # ✅ this ensures signals get registered
