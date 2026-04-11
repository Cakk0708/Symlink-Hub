import os, sys, django, glob, importlib, time, json
from django.conf import settings
from django.db import models
from datetime import datetime

from apps.PM.evaluate.v3.config.utils import get_user_project_roles


def get_detail():
    instance = Project_Node.objects.get(id=917)

    node_serializer = serializerNode(
        instance, 
        context={'request': request, 'userinfo': self.userinfo}
    )

    data = node_serializer.construct_data(instance)

    print(data)