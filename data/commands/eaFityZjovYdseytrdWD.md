---
name: data-migrate
---

由于本版本我们对于项目实现了大量的重构工作，现在我们将要在`scripts/v.1.3.6`设计一个用于读取`prod`数据库迁移至`dev`数据库脚本

- 数据库：
1. 来源库：`PMS_prod`
2. 目标库：`PMS_dev`
阅读`home/settings/dev_fkq.py`的`DATABASES`可理解数据库端口、账号、密码、

- 操作表：
1. 来源表：PMS_prod.tool_project_customerModel
2. 目标表：PMS_dev.BDM_customer_model

- 注意点：
1. 你需要完整阅读目标表的模块文档后开始设计迁移脚本
2. 本次迁移工作只针对数据库迁移
3. 无需阅读过往迁移记录（按照新数据实现）
4. 不存在旧模型结构参考
5. 如存在差异较大不能确定处理方案的字段需询问用户解决方案
6. 需阅读`/Users/ly/Code/pms_backend/scripts/v1.3.6/migration_record.md`了解迁移历史
7. 完成脚本设计后务必自行执行验证可靠性
8. 迁移数据时只能使用sql与法不能使用ORM模型与法
   
- 迁移脚本希望实现的内容：
1. 清空目标表数据与下标
2. 阅读来源表字段与目标字段
3. 定制转移目标字段
4. 在`scripts/v1.3.6`下创建迁移脚本

- 输出要求：
1. 输出文件脚本名`data_migration_{app_name}_{model_name}`
2. 需在`scripts/v1.3.6`构造迁移记录md文件注明已迁移的表、时间等信息
3. `remark`字段注明：`从 xxx 迁移 | 原id=x`
4. 迁移过程中如有字段依赖其他表需在迁移记录做注明待办任务供后续完善
5. 如需要created_at、updated_at相关字段时默认使用`用户: 1`