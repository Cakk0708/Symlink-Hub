---
name: vocabulary-flatten-serializer
description: 当用户提到"扁平化列表"、"扁平化序列化器"、"ListSerializer"、"模块首页列表"、"GET List接口"或要求处理"index序号"、"默认排序规则"、"字段合并性"、"字段跳转链接"时，必须调用此技能以获取正确的物理路径和功能定义。
---

# 术语：扁平化序列化器 (Flat Serializer)

## 触发关键词
- 扁平化列表、扁平化序列化器、ListSerializer
- 模块首页列表、列表页接口、GET List接口
- index序号、序号问题、分页序号
- 默认排序规则、字段合并性、字段跳转链接、字段固定列

## 定义
在本项目中，“扁平化列表”、“扁平化序列化器”特指每个模块 `serializers/` 目录下名为 `ListSerializer` 的类。

多个命名指向
1. 扁平化列表
2. 扁平化序列化器
3. 模块首页列表

## 术语定义
当你遇到以下术语时，请按此逻辑理解：
  - **物理指向**：指对应模块 `serializers/` 文件夹下的 `ListSerializer` 类。
  - **功能逻辑**：专门负责 `GET` List 接口的扁平化数据输出，不处理嵌套写入。

## 核心职责
1. **输出限定**：仅用于 `GET` List 接口的数据展示。
2. **结构要求**：禁止使用 `depth > 0` 的嵌套，所有外键必须通过 `SlugRelatedField` 或 `SerializerMethodField` 转换为一级键值对。
3. **排序规则**：在模块 utils.py 中定义默认排序规则，默认 ID 逆序排序，如排序模块含有 status 审批状态则 stauts=`PENDING`优先级最高。

## 关联物理路径
- 路径模板：`/apps/{模块名}/serializers/`
- 文件名关键词：`ListSerializer`

## 交互示例
1. 如果用户要求“修改 BDM 的扁平化序列化器”，你应该定位到 `/apps/BDM/serializers/` 并查找 `ListSerializer` 类。
2. 如果用户说“修改 MAT 模块的扁平化序列化器”：
   - 第一步：查 CSV 找到 bom 路径 `/apps/BDM/material/`。
   - 第二步：定位到 `/apps/BDM/material/serializers/`。
   - 第三步：寻找名为 `ListSerializer` 的类进行操作。

## 数据实例
```python
class ListSerializer(serializers.ModelSerializer):
    # 一定存在
    index = serializers.IntegerField(label="序号")
    # 一定存在
    primaryId = serializers.IntegerField(source='primary_id', label="单据ID")
    # 一定存在
    code = serializers.CharField(source='conv.code', label="单位编码")
    # 一定存在
    status = serializers.ChoiceField(
        choices=Choices.status, source='conv.status', label="数据状态"
    )
    createTime = serializers.CharField(source='conv.create_time', label="创建时间")
    disableFlag = serializers.BooleanField(source='conv.disable_flag', label="禁用状态")
    materialCode = serializers.CharField(source='material.code', label="物料编码")
    materialName = serializers.CharField(source='material.name', label="物料名称")
    # 有子项的单据才存在
    secondaryId = serializers.IntegerField(label="次级ID")
    category = serializers.ChoiceField(choices=Choices.category, label="单位类型")
    unitName = serializers.CharField(source='unit.name', label="单位名称")
    unitGroupName = serializers.CharField(
        source='unit.group.name',
        label="单位分组",
        allow_null=True,
    )
    numerator = serializers.DecimalField(max_digits=20, decimal_places=10, label="换算分子")
    denominator = serializers.IntegerField(label="换算分母")
    
    
    class Meta:
        model = Conv
        fields = [
            'index',
            'primaryId',
            'code',
            'status',
            'createTime',
            'disableFlag',
            'materialCode',
            'materialName',
            'secondaryId',
            'category',
            'unitName',
            'numerator',
            'denominator',
            'unitGroupName',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 设置字段可见性 & 可过滤性
        for field in ['index', 'primaryId']:
            self.fields[field].visible = False
            self.fields[field].filterable = False

        # 设置字段可合并性
        for field in [
                'code', 'status', 'createTime', 'disableFlag',
                'materialCode', 'materialName'
            ]:
            self.fields[field].mergeable = True

        # 定义 code 的跳转链接
        self.fields['code'].link = {
            'pkField': 'primaryId',
            'path': route_link_helper.generate_module_route_link(
                ContentType.objects.get_for_model(self.Meta.model)
            )
        }
        
        # 设置字段固定标识
        self.fields['code'].is_fixed_column = True

        # 定义 foreign 关联关系
        for field, model, pk_field in [
            ('unitGroupName', UnitGroup, 'name'),
            ('materialCode', model_matm, 'code'),
            ('materialName', model_matm, 'name'),
            ('unitName', model_uom, 'name'),
        ]:
            self.fields[field].foreign = {
                'appLabel': ContentType.objects.get_for_model(model).app_label,
                'model': ContentType.objects.get_for_model(model).model,
                'pkField': pk_field
            }
```