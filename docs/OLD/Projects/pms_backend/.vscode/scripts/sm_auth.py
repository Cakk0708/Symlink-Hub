from apps.SM.auth.serializers import (
    LoginSerializer
)


def execute_login(request, userinfo):
    # data = {
    #     "provider": "OTHER",
    #     "login_type": "PASSWORD",
    #     "username": "Cakk",
    #     "password": "MOM888",
    # }
    data = {
        "provider": "FEISHU",
        "loginType": "REQUESTACCESS",
        "code": "eLYiz94BH454AKybaxABb04AAa6axA3d",
    }
    res = LoginSerializer(data=data)

    if not res.is_valid():
        print("err: ", res.errors)
        exit()

    print('success:', res.data)
