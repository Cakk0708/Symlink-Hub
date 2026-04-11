from apps.PM.authority.utils import AuthorityVerifier
from apps.SM.user.models import User

def verify(request, userinfo):
    user_instance = User.objects.get(id=10285)
    pm_permission = AuthorityVerifier(49, user_instance, 'project_node')
    print('pm_permission.verify() ----', pm_permission.verify(2200));

    return {}