from apps.PM.project.serializers import ProjectListParamsSerializer

def call_serializer(request, userinfo):
    data = {
        "type": 'CHGS',
        'sort': 'CCT:ASC'
    }
    serializer = ProjectListParamsSerializer(data=data)

    if not serializer.is_valid():
        return {
            'msg': '参数错误',
            'data': serializer.errors
        }

    print('serializer.data ----', serializer.build_project_list(serializer.data));

    return {}
