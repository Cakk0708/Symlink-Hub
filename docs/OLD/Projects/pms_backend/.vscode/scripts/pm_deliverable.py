from apps.PM.deliverable.instance.models import DeliverableInstance


def call_folder_task(request, userinfo):
    from apps.PM.deliverable.folder.tasks import (
        async_ensure_folder_exists,
    )

    res = async_ensure_folder_exists(21)

    print('res ---- ', res)

    return {}

def call_move_file_to_folder(request, userinfo):
    from apps.PM.deliverable.tasks import async_move_temp_file_to_folder_task

    async_move_temp_file_to_folder_task(36)

    return {}

def call_task(request, userinfo):
    from apps.PM.deliverable.tasks import async_reclaim_node_deliverable_permissions

    async_reclaim_node_deliverable_permissions(259)

    return {}

def call_detail(request, userinfo):
    from apps.PM.deliverable.instance.serializers import ResolveDeliverableSerializer

    instance = DeliverableInstance.objects.get(id=63)
    res = ResolveDeliverableSerializer(instance, context={'request': request}).data
    
    return res

