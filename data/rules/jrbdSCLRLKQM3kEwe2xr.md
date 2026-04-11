# 模块导入规则

## 导入顺序

- 1级: 必须为 import 类
    - requests
    - re
    - time
- 2级: 必须为项目框架相关如
    - from rest_framework import serializers
    - from rest_framework import serializers
- 3级: 必须为本项目内工具类如
    - from utils.date import DateTimeFormatMixin
    - from utils.openapi.feishu import UserManger
- 4级: 必须为项目 apps 下的模块
    - from apps.SM.models import User
    - from apps.SM.models import Auth
- 5级: 同级模块引入
    - from .models import NodeReview

## 补充规则

- 不同级别导入需分行

## 结果示例

### 正确示例

```
from rest_framework import serializers

from utils.date import DateTimeFormatMixin

from apps.PSC.review_definition.models import ReviewDefinitionVersion
from apps.SM.models import User
from apps.PM.deliverable.instance.models import DeliverableInstance
from apps.PM.nodelist.enums import Choices as choices_node

from ..models import Project_Node
from .models import NodeReview
from .enums import Choices
```

### 错误示例

- 相同级别没有放在同一块
- 不同级别没有分行

```
from utils.date import DateTimeFormatMixin
from .enums import Choices
from apps.PSC.review_definition.models import ReviewDefinitionVersion
from rest_framework import serializers
from apps.SM.models import User
from apps.PM.deliverable.instance.models import DeliverableInstance
from apps.PM.nodelist.enums import Choices as choices_node
from ..models import Project_Node
from .models import NodeReview
```