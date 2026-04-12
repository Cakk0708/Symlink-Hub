#!/usr/bin/env python3
"""从目标项目导入已有的 AI 配置文件到 data 目录。

初始化项目时，扫描目标项目中已有的 skills、rules、agents 等文件，
复制到 data/ 目录并自动创建 config.json 和 tags.json 条目。
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
import string
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 常量（与 update_link.py 保持一致）
# ---------------------------------------------------------------------------

SCHEME_MEMORY_FILENAME = {
    "claude": "CLAUDE.md",
    "codex": "AGENTS.md",
}

SCHEME_WORKSPACE_DIR = {
    "claude": ".claude",
    "codex": ".codex",
}

DIR_TO_RESOURCE_TYPE = {
    "skills": "skills",
    "rules": "rules",
    "agents": "agents",
    "commands": "commands",
    "docs": "docs",
}

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------


def generate_id(length: int = 20) -> str:
    """生成随机短 ID（与现有 config 风格一致）。"""
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


def load_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict | list) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=4) + "\n",
        encoding="utf-8",
    )


def get_existing_names_by_type(config: dict) -> dict[str, set[str]]:
    """从 config 中提取每个资源类型下已有的 name 集合。"""
    result: dict[str, set[str]] = {}
    for resource_type, raw_value in config.items():
        names: set[str] = set()
        if isinstance(raw_value, list):
            for block in raw_value:
                if isinstance(block, dict):
                    for meta in block.values():
                        if isinstance(meta, dict) and "name" in meta:
                            names.add(meta["name"])
        elif isinstance(raw_value, dict):
            for meta in raw_value.values():
                if isinstance(meta, dict) and "name" in meta:
                    names.add(meta["name"])
        if names:
            result[resource_type] = names
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="从目标项目导入 AI 配置文件到 data 目录",
    )
    parser.add_argument(
        "--project",
        required=True,
        help="项目 key（对应 project.json 中的键名）",
    )
    parser.add_argument(
        "--scheme",
        choices=tuple(SCHEME_MEMORY_FILENAME),
        help="方案（claude/codex），不传时交互询问",
    )
    return parser.parse_args()


def prompt_scheme() -> str:
    options = list(SCHEME_MEMORY_FILENAME)
    while True:
        answer = input("请选择方案 [claude/codex]: ").strip().lower()
        if answer in options:
            return answer
        print("输入无效，请输入 claude 或 codex。")


def prompt_tags(available_tags: list[str]) -> list[str]:
    """交互式选择标签。"""
    print("\n可用标签:")
    for i, tag in enumerate(available_tags, 1):
        print(f"  {i}. {tag}")
    print("  0. 输入自定义标签")

    while True:
        raw = input("选择标签（编号或标签名，逗号分隔）: ").strip()
        if not raw:
            continue

        selected: list[str] = []
        invalid = False
        for part in raw.split(","):
            part = part.strip()
            if not part:
                continue
            try:
                num = int(part)
                if num == 0:
                    custom = input("输入自定义标签（逗号分隔）: ").strip()
                    selected.extend(
                        t.strip() for t in custom.split(",") if t.strip()
                    )
                elif 1 <= num <= len(available_tags):
                    selected.append(available_tags[num - 1])
                else:
                    print(f"  无效编号: {num}")
                    invalid = True
                    break
            except ValueError:
                if part in available_tags:
                    selected.append(part)
                else:
                    print(f"  无效标签: {part}")
                    invalid = True
                    break

        if not invalid and selected:
            return selected
        if not invalid:
            print("请至少选择一个标签。")


# ---------------------------------------------------------------------------
# 扫描
# ---------------------------------------------------------------------------


def scan_project(project_path: Path, scheme: str) -> list[dict]:
    """扫描项目目录，返回发现的资源列表。"""
    workspace_dir = project_path / SCHEME_WORKSPACE_DIR[scheme]
    resources: list[dict] = []

    # 扫描工作目录下的各类资源
    if workspace_dir.exists():
        for dir_name, resource_type in DIR_TO_RESOURCE_TYPE.items():
            type_dir = workspace_dir / dir_name
            if not type_dir.exists():
                continue
            if resource_type == "skills":
                resources.extend(_scan_skills(type_dir))
            else:
                resources.extend(_scan_flat_resources(type_dir, resource_type))

    # 根目录 memory 文件
    memory_file = project_path / SCHEME_MEMORY_FILENAME[scheme]
    if memory_file.exists():
        resources.append({
            "resource_type": "memory",
            "source_path": memory_file,
            "name": SCHEME_MEMORY_FILENAME[scheme],
            "structure": [],
            "references": [],
        })

    # 根目录 mcp 文件
    mcp_file = project_path / ".mcp.json"
    if mcp_file.exists():
        resources.append({
            "resource_type": "mcp",
            "source_path": mcp_file,
            "name": ".mcp.json",
            "structure": [],
            "references": [],
        })

    return resources


def _scan_skills(skills_dir: Path) -> list[dict]:
    """扫描 skills 目录，处理 SKILL.md + references/ 结构。"""
    resources: list[dict] = []
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue

        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        references: list[dict] = []
        refs_dir = skill_dir / "references"
        if refs_dir.exists():
            for ref_file in sorted(refs_dir.iterdir()):
                if ref_file.is_file():
                    references.append({
                        "source_path": ref_file,
                        "name": ref_file.stem,
                    })

        resources.append({
            "resource_type": "skills",
            "source_path": skill_md,
            "name": skill_dir.name,
            "structure": [],
            "references": references,
        })

    return resources


def _scan_flat_resources(type_dir: Path, resource_type: str) -> list[dict]:
    """扫描 rules/agents/commands/docs 等平面资源目录。"""
    resources: list[dict] = []
    for md_file in sorted(type_dir.rglob("*.md")):
        rel = md_file.relative_to(type_dir)
        parts = list(rel.parts)
        structure = parts[:-1]
        name = parts[-1].removesuffix(".md")

        resources.append({
            "resource_type": resource_type,
            "source_path": md_file,
            "name": name,
            "structure": structure,
            "references": [],
        })

    return resources


# ---------------------------------------------------------------------------
# 导入
# ---------------------------------------------------------------------------


def resource_exists(
    name: str,
    resource_type: str,
    existing_names: dict[str, set[str]],
) -> bool:
    return name in existing_names.get(resource_type, set())


def copy_to_data(resource: dict, resource_id: str) -> None:
    """将资源文件复制到 data 目录。"""
    resource_type = resource["resource_type"]
    source = resource["source_path"]

    if resource_type == "mcp":
        target = DATA_DIR / "mcp" / f"{resource_id}.json"
    elif resource_type in {"references", "others"}:
        target = DATA_DIR / resource_type / f"{resource_id}{source.suffix}"
    else:
        target = DATA_DIR / resource_type / f"{resource_id}.md"

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def add_to_config(
    config: dict,
    resource_type: str,
    resource_id: str,
    entry: dict,
) -> None:
    """向 config 添加一条资源记录。"""
    if resource_type not in config:
        config[resource_type] = []

    items = config[resource_type]
    if isinstance(items, list):
        items.append({resource_id: entry})
    elif isinstance(items, dict):
        items[resource_id] = entry


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------


def main() -> int:
    args = parse_args()
    scheme = args.scheme or prompt_scheme()

    try:
        projects_data = load_json(DATA_DIR / "project.json")
        config = load_json(DATA_DIR / "config.json")
        tag_catalog = load_json(DATA_DIR / "tags.json")

        # ---- 校验项目 ----
        if args.project not in projects_data:
            print(f"未找到项目: {args.project}")
            return 1

        project_meta = projects_data[args.project]
        project_path = Path(project_meta["path"]).expanduser()

        if not project_path.exists():
            print(f"项目路径不存在: {project_path}")
            return 1

        existing_names = get_existing_names_by_type(config)
        available_tags = (
            list(tag_catalog)
            if isinstance(tag_catalog, list)
            else list(tag_catalog.keys())
        )

        # ---- 扫描 ----
        print(f"\n扫描项目: {args.project} ({project_path})")
        print(f"方案: {scheme}\n")

        discovered = scan_project(project_path, scheme)

        if not discovered:
            print("未发现可导入的资源。")
            return 0

        # 区分新资源与已有资源
        new_resources: list[dict] = []
        skipped_names: list[str] = []
        for res in discovered:
            if resource_exists(res["name"], res["resource_type"], existing_names):
                skipped_names.append(
                    f"  [{res['resource_type']}] {res['name']}"
                )
            else:
                new_resources.append(res)

        if skipped_names:
            print(f"跳过 {len(skipped_names)} 个已存在的资源:")
            for s in skipped_names:
                print(s)
            print()

        if not new_resources:
            print("所有资源已存在，无需导入。")
            return 0

        print(f"待导入 {len(new_resources)} 个新资源:")
        for i, res in enumerate(new_resources, 1):
            ref_count = len(res.get("references", []))
            ref_info = f" + {ref_count} refs" if ref_count else ""
            struct = "/".join(res["structure"])
            struct_info = f" [{struct}]" if struct else ""
            print(f"  {i}. [{res['resource_type']}] {res['name']}{struct_info}{ref_info}")

        # ---- 确认 ----
        confirm = input(f"\n是否开始导入？[Y/n] ").strip().lower()
        if confirm in ("n", "no"):
            print("已取消。")
            return 0

        # ---- 逐个导入 ----
        imported = 0
        new_tags: set[str] = set()

        for resource in new_resources:
            resource_type = resource["resource_type"]

            # 交互式选择标签
            print(f"\n--- [{resource_type}]: {resource['name']} ---")
            tags = prompt_tags(available_tags)
            new_tags.update(tags)

            # 先导入 references（仅 skills 有）
            ref_ids: list[str] = []
            for ref in resource.get("references", []):
                ref_id = generate_id()
                ref_resource = {
                    "resource_type": "references",
                    "source_path": ref["source_path"],
                    "name": ref["name"],
                    "structure": [],
                }
                copy_to_data(ref_resource, ref_id)
                ref_entry: dict = {"name": ref["name"], "tags": tags}
                add_to_config(config, "references", ref_id, ref_entry)
                ref_ids.append(ref_id)
                print(f"  引用: {ref['name']} -> {ref_id}")

            # 导入主资源
            resource_id = generate_id()
            copy_to_data(resource, resource_id)

            entry: dict = {"name": resource["name"], "tags": tags}
            if resource.get("structure"):
                entry["structure"] = resource["structure"]
            if ref_ids:
                entry["reference"] = ref_ids

            add_to_config(config, resource_type, resource_id, entry)
            print(f"  已导入: {resource['name']} -> {resource_id}")
            imported += 1

        # ---- 更新 tags.json ----
        if isinstance(tag_catalog, list):
            current_tags = set(tag_catalog)
            added = sorted(new_tags - current_tags)
            if added:
                tag_catalog.extend(added)
                print(f"\n新增标签: {', '.join(added)}")

        # ---- 保存 ----
        save_json(DATA_DIR / "config.json", config)
        save_json(DATA_DIR / "tags.json", tag_catalog)

        print(f"\n导入完成: {imported} 个资源")
        return 0

    except KeyboardInterrupt:
        print("\n用户取消执行。", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"执行失败: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
