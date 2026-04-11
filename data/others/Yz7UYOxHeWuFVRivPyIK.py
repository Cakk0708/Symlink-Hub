from apps.PM.project.folder.serializers import (
    ProjectFolderListSerializer
)


def get_list(request, userinfo):
    serializer = ProjectFolderListSerializer(
        data={'project_id': 12},
        context={'request': request}
    )

    if not serializer.is_valid():
        return {
            'msg': '参数错误',
            'data': serializer.errors
        }
    
    data = serializer.save()
    
    print('serializer.data ---- ', data)
    
    return {}