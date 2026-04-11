from apps.PM.nodelist.models import Project_Node
from apps.PM.nodelist.serializers import (
    ReadSerializer, ReadSerializer,
    PatchCompleteSerializer
)

from utils.user import UserHelper


def get_detail(request, userinfo):
    instance = Project_Node.objects.get(id=45)
    serializer = ReadSerializer(
        instance,
        context={'request': request, 'userinfo': userinfo}
    )
    
    print('serializer.data ---- ', serializer.data)
    
    return serializer.data

def call_signal_func(request, userinfo):
    from apps.PM.nodelist.signals import (
        _get_next_milestone_nodes,
        _check_and_activate_next_milestone
    )

    instance = Project_Node.objects.get(id=98681)
    data = _get_next_milestone_nodes(instance.list, instance)

    # data = _check_and_activate_next_milestone(instance)

    print('data ---- ', data)

    return {}

def get_detail(request, userinfo):
    instance = Project_Node.objects.get(id=285)

    node_serializer = ReadSerializer(
        instance, 
        context={'request': request, 'userinfo': userinfo}
    )

    data = node_serializer.data

    print('data ---- ', data)

    return data

def call_complete(request, userinfo):
    instance = Project_Node.objects.get(id=4007)
    
    res = PatchCompleteSerializer(instance, context={'request': request})

    print('res ---- ', res)

    return {}
