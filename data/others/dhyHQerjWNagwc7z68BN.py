from apps.PM.change.utils import (
    construct_project_change_scopes,
    init_project_change
)
from apps.PM.change.signals import _create_approval_flow
from apps.PM.models import Project_List, Project_change


def call_utils_construct_project_change_scopes(request, userinfo):
    instance = Project_List.objects.get(id=33)

    data = construct_project_change_scopes(instance)
    
    print('serializer.data ---- ', data)
    
    return {}

def call_signal(request, userinfo):
    instance = Project_change.objects.get(
        project_id=30
    )

    data = _create_approval_flow(instance)
    
    print('serializer.data ---- ', data)
    
    return {}


def call_utils_init_project_change(request, userinfo):
    change_instance = Project_change.objects.get(id=893)

    init_project_change(change_instance)

    return {}
