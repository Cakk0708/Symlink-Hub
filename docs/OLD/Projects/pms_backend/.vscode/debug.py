#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调试脚本执行器

功能：
1. 扫描 scripts 目录下所有 Python 模块供用户选择
2. 用户选择模块后显示所有函数供选择
3. 执行选定的函数
4. 记录最后执行的模块和函数，下次启动时询问是否重复
"""

import os, sys, django, importlib, json, inspect, time
from pathlib import Path
from datetime import datetime

# 路径配置
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_path)

# 初始化Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home.settings')
django.setup()

from apps.SM.models import User


def get_userinfo(instance):
    return {
        'id': instance.id,
        'open_id': instance.user_feishu.open_id,
        'nickname': instance.nickname,
        'avatar': instance.avatar,
        'mobile': instance.mobile,
        'nickname_pinyin': instance.nickname_pinyin,
        'is_in_service': instance.is_in_service,
        'uses': instance.uses,
        'is_superuser': instance.is_superuser,
        'token': ''
    }

class Request:
    user: None
    method: None
    old_user: None

    def __init__(self, user_instance, userinfo):
        self.user = user_instance
        self.old_user = userinfo

class DebugRunner:
    """调试脚本运行器"""

    def __init__(self, scripts_dir: str = None):
        """
        初始化调试运行器

        Args:
            scripts_dir: scripts 目录路径，默认为当前目录
        """
        if scripts_dir is None:
            self.scripts_dir = Path(__file__).parent / "scripts"
        else:
            self.scripts_dir = Path(scripts_dir)

        self.history_file = Path(__file__).parent / ".debug_history.json"
        print(self.history_file)
        self.modules = self._discover_modules()
        self.history = self._load_history()

    def _discover_modules(self) -> dict[str, Path]:
        """
        发现 scripts 目录下所有 Python 模块

        Returns:
            模块名到文件路径的映射
        """
        modules = {}
        for file_path in self.scripts_dir.glob("*.py"):
            # 跳过 __init__.py 和 debug.py 自身
            if file_path.name in ("__init__.py", "debug.py"):
                continue
            module_name = file_path.stem
            modules[module_name] = file_path
        return modules

    def _get_functions_from_module(self, module_name: str) -> dict[str, callable]:
        """
        从模块中获取所有函数

        Args:
            module_name: 模块名

        Returns:
            函数名到函数对象的映射
        """
        functions = {}
        module_path = self.modules[module_name]

        # 动态导入模块
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None or spec.loader is None:
            return functions

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # 获取模块中定义的所有函数
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            # 只包含在当前模块中定义的函数
            if obj.__module__ == module_name:
                functions[name] = obj

        return functions

    def _load_history(self) -> dict:
        """加载执行历史"""
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def _save_history(self, module_name: str, function_name: str):
        """保存执行历史"""
        self.history = {
            "module": module_name,
            "function": function_name,
        }
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except IOError:
            pass

    def _display_menu(self, title: str, items: list, show_index: bool = True) -> int:
        """
        显示菜单并获取用户选择

        Args:
            title: 菜单标题
            items: 选项列表
            show_index: 是否显示序号

        Returns:
            用户选择的索引（0-based），如果输入无效返回 -1
        """
        print(f"\n{'='*50}")
        print(f"  {title}")
        print(f"{'='*50}")

        for i, item in enumerate(items, 1):
            prefix = f"{i}. " if show_index else ""
            print(f"  {prefix}{item}")

        print(f"{'='*50}")

        while True:
            try:
                choice = input("请选择 (输入序号): ").strip()
                if not choice:
                    return -1
                idx = int(choice) - 1
                if 0 <= idx < len(items):
                    return idx
                print(f"请输入 1-{len(items)} 之间的数字")
            except ValueError:
                print("请输入有效的数字")
            except KeyboardInterrupt:
                print("\n操作已取消")
                sys.exit(0)

    def _display_confirm_menu(self, title: str, item: str) -> bool:
        """
        显示确认菜单

        Args:
            title: 确认标题
            item: 要确认的项目

        Returns:
            用户是否确认
        """
        print(f"\n{'='*50}")
        print(f"  {title}")
        print(f"  项目: {item}")
        print(f"{'='*50}")
        print("  1. 确认执行")
        print("  2. 重新选择")
        print(f"{'='*50}")

        while True:
            try:
                choice = input("请选择 (输入序号): ").strip()
                if choice == "1":
                    return True
                elif choice == "2":
                    return False
                print("请输入 1 或 2")
            except KeyboardInterrupt:
                print("\n操作已取消")
                sys.exit(0)

    def save(self, model, data):
        date = '%s-%s-%s'%(
            datetime.now().year,
            str(datetime.now().month).zfill(2),
            str(datetime.now().day).zfill(2)
        )
        path_name = '%s_%s.json'%(
            model,
            str(int(time.time()))
        )

        if not os.path.exists(f'.cache/{date}'):
            os.makedirs(f'.cache/{date}')

        with open(f'.cache/{date}/data_{path_name}', 'w', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False))
        
        print(f"Json Data Path: {os.path.abspath(f'.cache/{date}/data_{path_name}')}")

    def run(self, _type):
        """运行调试器主流程"""
        if not self.modules:
            print("未找到任何可执行的模块")
            return

        # 步骤1: 检查是否有历史记录，询问用户
        repeat_last = _type == '继续执行'

        if repeat_last:
            # 执行上次的函数
            module_name = self.history["module"]
            function_name = self.history["function"]

            if module_name not in self.modules:
                print(f"错误: 上次执行的模块 '{module_name}' 不存在")
                repeat_last = False
            else:
                functions = self._get_functions_from_module(module_name)
                if function_name not in functions:
                    print(f"错误: 函数 '{function_name}' 在模块 '{module_name}' 中不存在")
                    repeat_last = False

        if not repeat_last:
            # 步骤2: 让用户选择模块
            module_list = sorted(list(self.modules.keys()))
            module_idx = self._display_menu("请选择要执行的模块", module_list)

            if module_idx < 0:
                print("未选择模块，退出")
                return

            module_name = module_list[module_idx]

            # 步骤3: 获取模块中的函数
            functions = self._get_functions_from_module(module_name)

            if not functions:
                print(f"模块 '{module_name}' 中没有找到任何函数")
                return

            # 步骤4: 让用户选择函数
            function_list = list(functions.keys())
            function_idx = self._display_menu(
                f"请选择要执行的函数 (模块: {module_name})",
                function_list
            )

            if function_idx < 0:
                print("未选择函数，退出")
                return

            function_name = function_list[function_idx]

        # 获取函数对象
        if not repeat_last:
            functions = self._get_functions_from_module(module_name)
        func = functions[function_name]

        # 执行函数
        print(f"\n{'='*50}")
        print(f"------ 正在执行: {module_name}.{function_name}()")

        try:
            instance = User.objects.get(id=10000)
            userinfo = get_userinfo(instance)

            data = func(
                Request(instance, userinfo),
                userinfo
            )

            self.save('node', data)
            
            print(f"------ 执行完成!")
            print(f"{'='*50}\n")
        except Exception as e:
            print(f"\n{'='*50}")
            print(f"  执行出错!")
            print(f"  错误类型: {type(e).__name__}")
            print(f"  错误信息: {e}")
            print(f"{'='*50}")
            import traceback
            traceback.print_exc()

        # 保存历史
        self._save_history(module_name, function_name)


def main():
    """主入口函数"""
    runner = DebugRunner()
    runner.run(sys.argv[1])

if __name__ == "__main__":
    main()
