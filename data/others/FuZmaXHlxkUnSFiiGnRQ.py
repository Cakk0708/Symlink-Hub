from apps.SM.system.utils import (
    get_version_from_pms_admin
)

def get_pms_admin_version(request, userinfo):
    data = get_version_from_pms_admin()

    print(data)
    
    return data
