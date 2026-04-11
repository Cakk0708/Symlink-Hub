from apps.SM.user.serializers import (
    ListSerializer
)
from apps.SM.models import User


def get_list(request, userinfo):
    users_qs = User.objects.filter(
        in_service=True
    ).order_by('-uses')
    
    res = ListSerializer(users_qs, many=True)

    print('success:', res.data)
