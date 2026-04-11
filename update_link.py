#!/usr/bin/env python3
"""根据 data 配置生成项目软连接目录。"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


RESOURCE_TYPES = (
    "skills",
    "rules",
    "agents",
    "commands",
    "docs",
    "memory",
    "mcp",
    "others",
)

CONFIG_TYPES = ("references", *RESOURCE_TYPES)

SCHEME_MEMORY_FILENAME = {
    "claude": "CLAUDE.md",
    "codex": "AGENTS.md",
}

SCHEME_WORKSPACE_DIR = {
    "claude": ".claude",
    "codex": ".codex",
}

SCHEME_STALE_ITEMS = {
    "claude": (".codex", "AGENTS.md"),
    "codex": (".claude", "CLAUDE.md"),
}

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
LINKS_DIR = ROOT / ".links"


@dataclass(frozen=True)
class Project:
    """项目配置。"""

    key: str
    tags: tuple[str, ...]
    path: Path


@dataclass(frozen=True)
class Resource:
    """资源配置。"""

    resource_type: str
    resource_id: str
    meta: dict

    @property
    def name(self) -> str:
        """返回配置中的资源名。"""
        return self.meta.get("name", self.resource_id)

    @property
    def tags(self) -> tuple[str, ...]:
        """返回资源标签。"""
        return tuple(self.meta.get("tags", []))

    @property
    def structure(self) -> tuple[str, ...]:
        """返回配置中的目录结构。"""
        return tuple(self.meta.get("structure", []))

    @property
    def references(self) -> tuple[str, ...]:
        """返回 skill 的引用资源。"""
        return tuple(self.meta.get("reference", []))


def load_json(path: Path) -> dict | list:
    """读取 JSON 文件。"""
    return json.loads(path.read_text(encoding="utf-8"))


def flatten_config_items(raw_value: object) -> dict[str, dict]:
    """将 config 内的 list[dict] 拉平成单层映射。"""
    if isinstance(raw_value, dict):
        return raw_value

    if not isinstance(raw_value, list):
        raise TypeError(f"不支持的配置结构: {type(raw_value)!r}")

    merged: dict[str, dict] = {}
    for block in raw_value:
        if not isinstance(block, dict):
            raise TypeError(f"配置块必须为 dict，收到: {type(block)!r}")
        for key, value in block.items():
            if key in merged:
                raise ValueError(f"发现重复资源 ID: {key}")
            merged[key] = value
    return merged


def load_projects(path: Path) -> list[Project]:
    """读取项目配置。"""
    raw_projects = load_json(path)
    if not isinstance(raw_projects, dict):
        raise TypeError("project.json 顶层必须为对象")

    projects: list[Project] = []
    for key, meta in raw_projects.items():
        projects.append(
            Project(
                key=key,
                tags=tuple(meta.get("tags", [])),
                path=Path(meta["path"]).expanduser(),
            )
        )
    return projects


def load_config(path: Path) -> dict[str, dict[str, Resource]]:
    """读取并标准化资源配置。"""
    raw_config = load_json(path)
    if not isinstance(raw_config, dict):
        raise TypeError("config.json 顶层必须为对象")

    resources: dict[str, dict[str, Resource]] = {}
    for resource_type in CONFIG_TYPES:
        merged = flatten_config_items(raw_config.get(resource_type, []))
        resources[resource_type] = {
            resource_id: Resource(resource_type, resource_id, meta)
            for resource_id, meta in merged.items()
        }
    return resources


def load_tag_catalog(path: Path) -> set[str]:
    """读取 tags.json。"""
    raw_tags = load_json(path)
    if not isinstance(raw_tags, list):
        raise TypeError("tags.json 顶层必须为数组")
    return {tag for tag in raw_tags if isinstance(tag, str)}


def prompt_scheme() -> str:
    """交互式选择 memory 输出方案。"""
    options = list(SCHEME_MEMORY_FILENAME)

    try:
        result = subprocess.run(
            [
                "osascript",
                "-e",
                (
                    'choose from list {"claude", "codex"} '
                    'with prompt "请选择 memory 方案" '
                    'default items {"claude"}'
                ),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        answer = result.stdout.strip()
        if answer in options:
            return answer
    except Exception:  # noqa: BLE001
        pass

    while True:
        answer = input("请选择 memory 方案 [claude/codex]: ").strip().lower()
        if answer in SCHEME_MEMORY_FILENAME:
            return answer
        print("输入无效，请输入 claude 或 codex。")


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description="生成 .links 项目软连接")
    parser.add_argument(
        "--scheme",
        choices=tuple(SCHEME_MEMORY_FILENAME),
        help="memory 输出方案，不传时交互询问",
    )
    parser.add_argument(
        "--project",
        action="append",
        dest="projects",
        help="仅生成指定项目，可多次传入",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    return parser.parse_args()


def match_resources(
    project_tags: Iterable[str],
    resources: dict[str, Resource],
) -> list[Resource]:
    """返回项目命中的资源。"""
    project_tag_set = set(project_tags)
    return [
        resource
        for resource in resources.values()
        if project_tag_set.intersection(resource.tags)
    ]


def source_path_for(resource_type: str, resource_id: str) -> Path:
    """推导资源源文件路径。"""
    base_dir = DATA_DIR / resource_type

    if resource_type == "mcp":
        return base_dir / f"{resource_id}.json"

    if resource_type in {"others", "references"}:
        matches = sorted(base_dir.glob(f"{resource_id}.*"))
        if len(matches) != 1:
            raise FileNotFoundError(
                f"{resource_type} 资源 {resource_id} 无法唯一定位源文件: "
                f"{matches}"
            )
        return matches[0]

    return base_dir / f"{resource_id}.md"


def remove_path(path: Path) -> None:
    """删除已有目录或文件。"""
    if not path.exists() and not path.is_symlink():
        return

    if path.is_symlink() or path.is_file():
        path.unlink()
        return

    shutil.rmtree(path)


def ensure_symlink(source: Path, target: Path) -> None:
    """创建软连接。"""
    if not source.exists():
        raise FileNotFoundError(f"源文件不存在: {source}")

    if target.exists() or target.is_symlink():
        if target.is_symlink() and target.resolve() == source.resolve():
            return
        if target.is_dir() and not target.is_symlink():
            shutil.rmtree(target)
        else:
            target.unlink()

    target.parent.mkdir(parents=True, exist_ok=True)
    os.symlink(source, target)


def build_filename(resource: Resource, source: Path) -> str:
    """构造目标文件名。"""
    suffix = source.suffix

    if resource.resource_type == "mcp":
        return ".mcp.json"

    if resource.resource_type == "others":
        return (
            resource.name
            if resource.name.endswith(suffix)
            else f"{resource.name}{suffix}"
        )

    if resource.resource_type in {
        "rules",
        "agents",
        "commands",
        "docs",
    }:
        return resource.name if resource.name.endswith(suffix) else (
            f"{resource.name}{suffix}"
        )

    raise ValueError(f"不支持为 {resource.resource_type} 构造文件名")


def workspace_dirname(scheme: str) -> str:
    """返回当前方案对应的工作目录名称。"""
    return SCHEME_WORKSPACE_DIR[scheme]


def path_parts_for_resource_with_scheme(
    resource: Resource,
    source: Path,
    scheme: str,
) -> tuple[str, ...]:
    """构造相对路径片段。"""
    workspace_dir = workspace_dirname(scheme)

    if resource.resource_type == "rules":
        return (
            workspace_dir,
            "rules",
            *resource.structure,
            build_filename(resource, source),
        )

    if resource.resource_type == "agents":
        return (
            workspace_dir,
            "agents",
            *resource.structure,
            build_filename(resource, source),
        )

    if resource.resource_type == "commands":
        return (
            workspace_dir,
            "commands",
            *resource.structure,
            build_filename(resource, source),
        )

    if resource.resource_type == "docs":
        return (
            workspace_dir,
            "docs",
            *resource.structure,
            build_filename(resource, source),
        )

    if resource.resource_type == "others":
        return (*resource.structure, build_filename(resource, source))

    raise ValueError(f"不支持的资源类型: {resource.resource_type}")


def validate_tag_usage(
    projects: list[Project],
    resources_by_type: dict[str, dict[str, Resource]],
    tag_catalog: set[str],
) -> None:
    """校验项目和资源标签。"""
    unknown_tags: set[str] = set()

    for project in projects:
        unknown_tags.update(set(project.tags) - tag_catalog)

    for resource_group in resources_by_type.values():
        for resource in resource_group.values():
            unknown_tags.update(set(resource.tags) - tag_catalog)

    if unknown_tags:
        raise ValueError(
            "以下标签未在 data/tags.json 中声明: "
            + ", ".join(sorted(unknown_tags))
        )


def assert_no_duplicate_targets(
    project: Project,
    root: Path,
    resources: Iterable[Resource],
    scheme: str,
) -> None:
    """校验单项目下不会生成重复目标。"""
    used_targets: dict[Path, Resource] = {}

    for resource in resources:
        source = source_path_for(resource.resource_type, resource.resource_id)

        if resource.resource_type == "skills":
            target = (
                root
                / workspace_dirname(scheme)
                / "skills"
                / resource.name
                / "SKILL.md"
            )
        elif resource.resource_type == "memory":
            continue
        elif resource.resource_type == "mcp":
            target = root / ".mcp.json"
        else:
            target = root.joinpath(
                *path_parts_for_resource_with_scheme(resource, source, scheme)
            )

        previous = used_targets.get(target)
        if previous is None:
            used_targets[target] = resource
            continue

        raise ValueError(
            f"项目 {project.key} 存在目标路径冲突: {target}\n"
            f"- {previous.resource_type}:{previous.resource_id} ({previous.name})\n"
            f"- {resource.resource_type}:{resource.resource_id} ({resource.name})"
        )


def link_skill(
    project_root: Path,
    resource: Resource,
    references: dict[str, Resource],
    scheme: str,
) -> None:
    """生成单个 skill。"""
    skill_dir = project_root / workspace_dirname(scheme) / "skills" / resource.name
    skill_source = source_path_for("skills", resource.resource_id)
    ensure_symlink(skill_source, skill_dir / "SKILL.md")

    for reference_id in resource.references:
        reference = references.get(reference_id)
        if reference is None:
            raise KeyError(
                f"skill {resource.resource_id} 引用了不存在的 reference: "
                f"{reference_id}"
            )

        reference_source = source_path_for("references", reference_id)
        ensure_symlink(
            reference_source,
            skill_dir / "references" / reference.name,
        )


def link_memory(
    project: Project,
    project_root: Path,
    resources: list[Resource],
    scheme: str,
) -> None:
    """生成 memory。"""
    if not resources:
        return

    if len(resources) > 1:
        resource_list = ", ".join(resource.resource_id for resource in resources)
        raise ValueError(
            f"项目 {project.key} 命中了多个 memory，无法合并到单文件: "
            f"{resource_list}"
        )

    memory = resources[0]
    source = source_path_for("memory", memory.resource_id)
    target = project_root / SCHEME_MEMORY_FILENAME[scheme]
    ensure_symlink(source, target)


def link_mcp(project_root: Path, resources: list[Resource]) -> None:
    """生成 mcp。"""
    if not resources:
        return

    if len(resources) > 1:
        resource_list = ", ".join(resource.resource_id for resource in resources)
        raise ValueError(f"mcp 仅支持单个文件，当前命中: {resource_list}")

    resource = resources[0]
    source = source_path_for("mcp", resource.resource_id)
    ensure_symlink(source, project_root / ".mcp.json")


def link_flat_resources_with_scheme(
    project_root: Path,
    resources: list[Resource],
    scheme: str,
) -> None:
    """生成 rules、agents、commands、docs、others。"""
    for resource in resources:
        source = source_path_for(resource.resource_type, resource.resource_id)
        target = project_root.joinpath(
            *path_parts_for_resource_with_scheme(resource, source, scheme)
        )
        ensure_symlink(source, target)


def sync_template_to_project(
    template_root: Path,
    target_root: Path,
    scheme: str,
) -> None:
    """将模板目录的顶层项同步到真实项目目录。"""
    target_root.mkdir(parents=True, exist_ok=True)

    for stale_name in SCHEME_STALE_ITEMS[scheme]:
        stale_path = target_root / stale_name
        if stale_path.exists() or stale_path.is_symlink():
            remove_path(stale_path)

    for item in sorted(template_root.iterdir()):
        target = target_root / item.name
        if target.exists() or target.is_symlink():
            remove_path(target)
        ensure_symlink(item, target)


def build_project_links(
    project: Project,
    resources_by_type: dict[str, dict[str, Resource]],
    scheme: str,
) -> None:
    """构造单个项目的 .links 目录。"""
    project_root = LINKS_DIR / project.key

    if project_root.exists() or project_root.is_symlink():
        remove_path(project_root)
    project_root.mkdir(parents=True, exist_ok=True)

    matched_resources = {
        resource_type: match_resources(project.tags, resources_by_type[resource_type])
        for resource_type in RESOURCE_TYPES
    }

    conflict_resources = []
    for resource_type in (
        "skills",
        "rules",
        "agents",
        "commands",
        "docs",
        "mcp",
        "others",
    ):
        conflict_resources.extend(matched_resources[resource_type])
    assert_no_duplicate_targets(project, project_root, conflict_resources, scheme)

    for skill in matched_resources["skills"]:
        link_skill(project_root, skill, resources_by_type["references"], scheme)

    link_flat_resources_with_scheme(project_root, matched_resources["rules"], scheme)
    link_flat_resources_with_scheme(project_root, matched_resources["agents"], scheme)
    link_flat_resources_with_scheme(
        project_root,
        matched_resources["commands"],
        scheme,
    )
    link_flat_resources_with_scheme(project_root, matched_resources["docs"], scheme)
    link_flat_resources_with_scheme(project_root, matched_resources["others"], scheme)
    link_memory(project, project_root, matched_resources["memory"], scheme)
    link_mcp(project_root, matched_resources["mcp"])
    sync_template_to_project(project_root, project.path, scheme)


def filter_projects(
    projects: list[Project],
    selected_keys: list[str] | None,
) -> list[Project]:
    """按参数筛选项目。"""
    if not selected_keys:
        return projects

    selected = set(selected_keys)
    filtered = [project for project in projects if project.key in selected]
    missing = sorted(selected - {project.key for project in filtered})
    if missing:
        raise KeyError(f"未找到项目: {', '.join(missing)}")
    return filtered


def print_summary(projects: list[Project], scheme: str) -> None:
    """打印执行摘要。"""
    print(f"memory 方案: {scheme} -> {SCHEME_MEMORY_FILENAME[scheme]}")
    for project in projects:
        print(f"已生成: {LINKS_DIR / project.key}")


def main() -> int:
    """脚本入口。"""
    args = parse_args()
    scheme = args.scheme or prompt_scheme()

    try:
        projects = load_projects(DATA_DIR / "project.json")
        projects = filter_projects(projects, args.projects)
        resources_by_type = load_config(DATA_DIR / "config.json")
        tag_catalog = load_tag_catalog(DATA_DIR / "tags.json")
        validate_tag_usage(projects, resources_by_type, tag_catalog)

        LINKS_DIR.mkdir(parents=True, exist_ok=True)

        for project in projects:
            build_project_links(
                project,
                resources_by_type,
                scheme,
            )

        print_summary(projects, scheme)
        return 0
    except KeyboardInterrupt:
        print("\n用户取消执行。", file=sys.stderr)
        return 130
    except Exception as exc:  # noqa: BLE001
        print(f"执行失败: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
