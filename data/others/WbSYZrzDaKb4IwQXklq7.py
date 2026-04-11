from apps.API.views import (
    check_feishu_temp_folder
)


def get_views_func(request, userinfo):
    check_feishu_temp_folder()
    
    return {}
