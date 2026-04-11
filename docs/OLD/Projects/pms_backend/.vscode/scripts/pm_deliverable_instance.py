from apps.PM.deliverable.instance.serializers import ResolveDeliverableSerializer
from apps.PM.deliverable.instance.models import DeliverableInstance


def call_resolve(request, userinfo):
    serializer = ResolveDeliverableSerializer(
        data={
            'id': 20
        }, context={'request': request})

    if not serializer.is_valid():
        print(serializer.errors)
        exit()

    print('serializer.data ----', serializer.data);

    return {}

