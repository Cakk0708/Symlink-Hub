from utils.openapi.feishu.user_manager import FeishuUserManager
from apps.SM.models import User

def call_user(request, userinfo):
    user_instance = User.objects.get(id=10000)
    print('user_instance.user_feishu.open_id ----', );
    print('userinfo ----', userinfo);

    data = FeishuUserManager.get_user_departments(
        user_instance.user_feishu.open_id,
        '%s %s' %(
            user_instance.user_feishu.token_type,
            user_instance.user_feishu.access_token
        )
    )

    print('data ----', data);

    return {}