#!/usr/bin/env python3
"""
Claude 配置软连接管理脚本
用于同步 Claude 工作区配置到实际项目目录

Author: Claude
Date: 2026-03-13
"""

import os
import sys
import shutil
from pathlib import Path

# ==================== 配置区域 ====================

# 用户配置
USERNAME = "ly"
CLOUD_CLAUDE_PATH = (
    f"/Users/{USERNAME}/Library/Mobile Documents/com~apple~CloudDocs/Claude"
)
PROJECT_BASE_PATH = f"/Users/{USERNAME}/Code"  # 可根据实际修改

# 项目配置字典
PROJECTS = {
    "1": {
        "name": "pms_backend",
        "type": "backend",
        "target_path": f"{PROJECT_BASE_PATH}/PMS/backend",
        "source_path": f"{CLOUD_CLAUDE_PATH}/Projects/pms_backend",
    },
    "2": {
        "name": "pms_frontend",
        "type": "frontend",
        "target_path": f"{PROJECT_BASE_PATH}/PMS/frontend-h5",
        "source_path": f"{CLOUD_CLAUDE_PATH}/Projects/pms_frontend",
    },
    "3": {
        "name": "pms_frontend-admin",
        "type": "frontend",
        "target_path": f"{PROJECT_BASE_PATH}/PMS/frontend-admin",
        "source_path": f"{CLOUD_CLAUDE_PATH}/Projects/pms-admin_frontend",
    },
    "4": {
        "name": "mom_backend",
        "type": "backend",
        "target_path": f"{PROJECT_BASE_PATH}/mom_backend",
        "source_path": f"{CLOUD_CLAUDE_PATH}/Projects/mom_backend",
    },
}

# 全局配置路径
GLOBAL_FEATURES_PATH = f"{CLOUD_CLAUDE_PATH}/Features/global"
GLOBAL_RULES_SOURCE = f"{GLOBAL_FEATURES_PATH}/rules"
GLOBAL_SKILLS_SOURCE = f"{GLOBAL_FEATURES_PATH}/skill"

# 项目类型特性路径
BACKEND_FEATURES_PATH = f"{CLOUD_CLAUDE_PATH}/Features/project_backend"
FRONTEND_FEATURES_PATH = f"{CLOUD_CLAUDE_PATH}/Features/project_frontend"


# ==================== 核心函数 ====================


def is_symlink(path: Path) -> bool:
    """检查路径是否为软连接"""
    return path.is_symlink()


def safe_remove(path: Path) -> bool:
    """
    安全删除路径

    Args:
        path: 要删除的路径

    Returns:
        bool: 是否成功删除
    """
    # 检查是否为软连接（包括损坏的软连接）
    if is_symlink(path):
        path.unlink()
        print(f"  ✓ 已删除软连接: {path}")
        return True

    # 路径不存在且不是软连接，无需处理
    if not path.exists():
        return True

    # 实体文件或目录，需要用户确认
    response = input(f"  ⚠️  发现实体文件/目录: {path}\n     是否删除? (y/n): ")
    if response.lower() == "y":
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
        print(f"  ✓ 已删除: {path}")
        return True
    else:
        print(f"  ✗ 跳过删除: {path}")
        return False


def create_symlink(source: Path, target: Path) -> bool:
    """
    创建软连接

    如果目标已存在，先删除（软连接直接删，实体文件确认后删），再创建新连接

    Args:
        source: 源路径（绝对路径）
        target: 目标路径（绝对路径）

    Returns:
        bool: 是否成功创建
    """
    if not source.exists():
        print(f"  ✗ 源路径不存在: {source}")
        return False

    # 如果目标已存在，先删除
    if target.exists() or target.is_symlink():
        print(f"  ℹ️  目标已存在，准备删除: {target}")
        if not safe_remove(target):
            print(f"  ✗ 删除失败，无法创建软连接")
            return False

    # 确保目标父目录存在
    target.parent.mkdir(parents=True, exist_ok=True)

    # 创建软连接
    os.symlink(source, target)
    print(f"  ✓ 创建软连接: {target} -> {source}")
    return True


def merge_symlink_children(source_dir: Path, target_dir: Path) -> bool:
    """
    将源目录下的子项合并到目标目录中

    为 source_dir 下的每个直接子项在 target_dir 下创建同名软连接，
    保留目标目录中未冲突的原有内容。

    Args:
        source_dir: 源目录
        target_dir: 目标目录

    Returns:
        bool: 是否成功
    """
    if not source_dir.exists() or not source_dir.is_dir():
        print(f"  ⚠️  源目录不存在或不是目录: {source_dir}")
        return True

    children = list(source_dir.iterdir())
    if not children:
        print(f"  ⚠️  源目录为空，跳过合并: {source_dir}")
        return True

    target_dir.mkdir(parents=True, exist_ok=True)

    for child in children:
        target_child = target_dir / child.name
        if not create_symlink(child, target_child):
            return False

    return True


def update_global_links() -> bool:
    """
    更新全局根目录软连接

    检查 ~/.claude/ 根目录，删除旧的 rules 和 skills 软连接，
    从 Features/global 创建新的软连接

    Returns:
        bool: 是否成功
    """
    print("\n[1] 检查并更新全局根目录软连接")
    print("-" * 50)

    home_claude = Path.home() / ".claude"

    # 检查并删除旧的 rules 软连接
    rules_target = home_claude / "rules"
    if rules_target.exists() or rules_target.is_symlink():
        print(f"  检测到已存在的 rules: {rules_target}")
        if not safe_remove(rules_target):
            return False

    # 检查并删除旧的 skills 软连接
    skills_target = home_claude / "skills"
    if skills_target.exists() or skills_target.is_symlink():
        print(f"  检测到已存在的 skills: {skills_target}")
        if not safe_remove(skills_target):
            return False

    # 创建新的软连接
    global_rules_source = Path(GLOBAL_RULES_SOURCE)
    global_skills_source = Path(GLOBAL_SKILLS_SOURCE)

    if not create_symlink(global_rules_source, rules_target):
        return False

    if not create_symlink(global_skills_source, skills_target):
        return False

    print("  ✓ 全局根目录软连接更新完成")
    return True


def update_project_links(project: dict) -> bool:
    """
    更新项目目录软连接

    检查项目目录中是否存在 .claude、.vscode、.mcp.json，
    如存在则删除，然后重新创建软连接

    Args:
        project: 项目配置字典

    Returns:
        bool: 是否成功
    """
    print(f"\n[2] 更新项目软连接: {project['name']}")
    print("-" * 50)

    target_path = Path(project["target_path"])
    source_path = Path(project["source_path"])

    # 检查目标项目目录是否存在
    if not target_path.exists():
        print(f"  ⚠️  目标项目目录不存在: {target_path}")
        response = input("     是否创建目录? (y/n): ")
        if response.lower() == "y":
            target_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ 已创建目录: {target_path}")
        else:
            return False

    # 检查源目录是否存在
    if not source_path.exists():
        print(f"  ✗ 源配置目录不存在: {source_path}")
        return False

    # 定义需要创建的软连接
    links_to_create = [
        ("CLAUDE.md", "CLAUDE.md"),
        (".claude", ".claude"),
        (".vscode", ".vscode"),
    ]

    # 如果项目有 .mcp.json，也创建软连接
    mcp_json_source = source_path / ".mcp.json"
    if mcp_json_source.exists():
        links_to_create.append((".mcp.json", ".mcp.json"))

    # 删除旧连接并创建新连接
    for source_name, target_name in links_to_create:
        source_file = source_path / source_name
        target_file = target_path / target_name

        if (target_file.exists() or target_file.is_symlink()) and source_file.exists():
            if not safe_remove(target_file):
                continue

        if source_file.exists():
            create_symlink(source_file, target_file)

    print("  ✓ 项目软连接更新完成")
    return True


def update_project_features(project: dict) -> bool:
    """
    更新项目 Features 软连接

    根据项目类型（backend/frontend）从 Features/ 提取相关子文件夹，
    在项目的 .claude/ 目录内创建软连接。

    通用规则：
    1. 先由 update_global_links() 更新全局 ~/.claude 下的 Features/global
    2. 再按项目类型补充项目级 Features，例如 frontend -> Features/project_frontend

    Args:
        project: 项目配置字典

    Returns:
        bool: 是否成功
    """
    print(f"\n[3] 更新项目 Features: {project['name']}")
    print("-" * 50)

    target_path = Path(project["target_path"])
    project_type = project["type"]
    claude_dir = target_path / ".claude"

    # 确保 .claude 目录存在
    if not claude_dir.exists():
        print(f"  ✗ .claude 目录不存在: {claude_dir}")
        return False

    feature_paths = {
        "backend": Path(BACKEND_FEATURES_PATH),
        "frontend": Path(FRONTEND_FEATURES_PATH),
    }
    features_base = feature_paths.get(project_type)
    if features_base is None:
        print(f"  ⚠️  未知项目类型，跳过 Features 处理: {project_type}")
        return True

    if not features_base.exists() or not list(features_base.iterdir()):
        print(f"  ⚠️  项目特性源目录不存在或为空: {features_base}")
        return True

    rules_source = features_base / "rules"
    if rules_source.exists() and list(rules_source.iterdir()):
        rules_target = claude_dir / "rules"
        if not create_symlink(rules_source, rules_target):
            return False

    skills_source = features_base / "skills"
    if skills_source.exists() and list(skills_source.iterdir()):
        skills_target = claude_dir / "skills"
        if not merge_symlink_children(skills_source, skills_target):
            return False

    # 清理旧版本遗留的分类型 skills 目录，避免与合并后的 .claude/skills 并存
    for legacy_name in ("skills_backend", "skills_frontend"):
        legacy_target = claude_dir / legacy_name
        if legacy_target.exists() or legacy_target.is_symlink():
            print(f"  ℹ️  清理旧的分类型 skills 目录: {legacy_target}")
            if not safe_remove(legacy_target):
                return False

    print("  ✓ 项目 Features 更新完成")
    return True


def show_menu():
    """显示交互式菜单"""
    print("=" * 50)
    print("Claude 配置软连接管理工具")
    print("=" * 50)
    print("请选择要更新的项目:")
    for key, project in PROJECTS.items():
        type_mark = "🔧" if project["type"] == "backend" else "🎨"
        print(f"  {key}. {type_mark} {project['name']}")
    print("  0. 退出")
    print("-" * 50)


def main():
    """主函数"""
    try:
        while True:
            show_menu()
            choice = input("请输入选项: ").strip()

            if choice == "0":
                print("👋 再见!")
                break

            if choice not in PROJECTS:
                print("✗ 无效选项，请重新输入\n")
                continue

            project = PROJECTS[choice]
            print(f"\n开始处理项目: {project['name']}")
            print("=" * 50)

            # 1. 更新全局根目录软连接
            if not update_global_links():
                print("\n✗ 全局软连接更新失败，已终止")
                continue

            # 2. 更新项目目录软连接
            if not update_project_links(project):
                print("\n✗ 项目软连接更新失败，已终止")
                continue

            # 3. 更新项目 Features
            if not update_project_features(project):
                print("\n✗ 项目 Features 更新失败，已终止")
                continue

            print("\n" + "=" * 50)
            print(f"✅ 项目 {project['name']} 配置同步完成!")
            print("=" * 50 + "\n")

    except KeyboardInterrupt:
        print("\n\n👋 用户中断，再见!")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


# ==================== 入口 ====================

if __name__ == "__main__":
    main()
