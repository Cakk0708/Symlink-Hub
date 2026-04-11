from apps.PM.evaluation.v3.config.utils import (
    get_user_project_roles,
    get_user_evaluable_roles
)
from apps.PM.projects.models import Project_List


def get_utils_user_project_roles(request, userinfo):
    instance = Project_List.objects.get(id=28)
    data = get_user_project_roles(instance, request.user)
    print(data)

def get_utils_user_evaluable_roles(request, userinfo):
    instance = Project_List.objects.all().last()
    data = get_user_evaluable_roles(instance, request.user)
    print(data)
