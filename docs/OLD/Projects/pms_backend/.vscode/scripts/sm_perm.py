from django.contrib.auth.models import Permission
from django.contrib.auth.management import create_permissions
from django.apps import apps
from django.conf import settings


def execute_cancel(request, userinfo):
    Permission.objects.all().delete()
    print('已清空 auth_permission')


def execute_create(request, userinfo):
    modules = [v['app_label'] for v in settings.SYSTEM_MODULE_CONFIG]
    
    for app_config in apps.get_app_configs():
        if app_config.label in modules:
            app_config.models_module = True

            create_permissions(app_config, verbosity=0)
            app_config.models_module = None

