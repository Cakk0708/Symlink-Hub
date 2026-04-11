# 代码注释规范

全局生效，适用于项目所有 Python 文件。

---

## 三级注释体系

### 一级注释 — 模块 / 核心逻辑块

用于模块入口、复杂业务流程、重要算法、关键架构逻辑。

```python
"""
=============
说明内容（可多行）
=============
"""
```

规则：
- 必须使用三引号块
- 上下必须有 `=============` 分隔线，长度保持一致
- 内容可多行

### 二级注释 — 类 / 函数 / 方法

用于所有 class、def 定义。

```python
class OrderService:
    """订单服务，负责订单创建与状态管理"""

def create_order(user_id: int):
    """创建订单"""
```

规则：
- 单行三引号，紧跟定义行下方
- 内容简洁，不写冗余描述
- 不加分隔线

### 三级注释 — 局部逻辑说明

用于复杂判断、特殊逻辑、临时 workaround、关键变量说明。

```python
# 库存不足直接终止，防止超卖
if stock < quantity:
    raise OutOfStockError()
```

规则：
- 使用 `#`，放在代码**上方**，不写行尾注释
- 说明**为什么（Why）**，不重复代码含义

---

## 禁止行为

```python
# ❌ 无意义注释
# 设置变量
a = 1

# ❌ 重复代码含义
# 遍历列表
for item in items: ...

# ❌ 大段复杂逻辑缺少一级注释块
```

---

## 完整结构示例

```python
"""
=============
订单库存校验逻辑

该逻辑用于防止超卖，所有订单创建前必须执行。
=============
"""

class InventoryService:
    """库存服务"""

    def check_stock(self, product_id: int, quantity: int):
        """检查库存是否充足"""

        stock = self.get_stock(product_id)

        # 库存不足时抛出异常，由上层统一处理响应
        if stock < quantity:
            raise OutOfStockError()
```


## 模块顶部注释

每个模块文件顶部必须有一级注释说明模块用途：
```python
"""
=============
Module: user_api.py
Description: 用户接口相关逻辑
Author: Cakk
=============
"""
```
