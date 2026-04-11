from apps.BDM.department.serializers import (
    DeptListSerializer
)
from apps.BDM.department.utils import get_list_queryset


def get_list(request, userinfo):
    queryset = get_list_queryset()
    
    res = DeptListSerializer(queryset, many=True)

    print('success:', res.data)
