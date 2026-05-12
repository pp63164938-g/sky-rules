# -*- coding: utf-8 -*-
"""
Sky Rules 全量同步脚本
同步 workflows / rules 到 Windsurf、Antigravity/Gemini、Codex/Agents。

用法:
  python sync-workflows.py          # git 提交并同步全部
  python sync-workflows.py --no-git # 跳过 git，仅同步全部
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parent
HOME = Path.home()

SRC_WORKFLOWS = ROOT / "workflows"
SRC_RULES = ROOT / "rules"
SRC_SKILLS = ROOT / "skills"

CODEX_AGENTS_FILE = HOME / ".codex" / "AGENTS.md"
AGENTS_SKILLS_DIR = HOME / ".agents" / "skills"

SYNC_MAP = [
    {
        "name": "Windsurf 工作流",
        "src": SRC_WORKFLOWS,
        "dst": HOME / ".codeium" / "windsurf" / "global_workflows",
        "mode": "mirror",
        "pattern": "*.md",
    },
    {
        "name": "Antigravity 工作流",
        "src": SRC_WORKFLOWS,
        "dst": HOME / ".gemini" / "antigravity" / "global_workflows",
        "mode": "mirror",
        "pattern": "*.md",
    },
    {
        "name": "Antigravity 规则",
        "src": SRC_RULES / "global-rules.md",
        "dst": HOME / ".gemini" / "GEMINI.md",
        "mode": "file",
    },
    {
        "name": "Windsurf 全局规则",
        "src": SRC_RULES / "global-rules.md",
        "dst": HOME / ".codeium" / "windsurf" / "memories" / "global_rules.md",
        "mode": "file",
    },
    {
        "name": "Codex 全局规则",
        "src": SRC_RULES / "global-rules.md",
        "dst": CODEX_AGENTS_FILE,
        "mode": "codex_rules",
    },
    {
        "name": "Agents/Codex Skills",
        "src": SRC_WORKFLOWS,
        "dst": AGENTS_SKILLS_DIR,
        "mode": "agents_skills",
        "pattern": "*.md",
    },
]


def git_commit_and_push() -> None:
    """自动提交并推送 sky-rules 仓库变更。"""
    print("[1/2] Git 提交变更...")
    os.chdir(ROOT)

    subprocess.run(["git", "add", "-A"], check=True, capture_output=True)

    result = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
    if result.returncode != 0:
        subprocess.run(
            ["git", "commit", "-m", "update: sync workflows and rules"],
            check=True,
            capture_output=True,
        )
        push_result = subprocess.run(["git", "push"], capture_output=True, text=True)
        if push_result.returncode == 0:
            print("    OK: 已提交并推送")
        else:
            print("    WARN: 已提交，推送失败（可能无远程或网络问题）")
    else:
        print("    无变更需要提交")
    print()


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text

    metadata: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"').strip("'")
    return metadata, parts[2].lstrip()


def slugify(value: str) -> str:
    value = value.lower().replace(".", "-").replace("_", "-")
    value = re.sub(r"[^a-z0-9-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value[:63] or "sky-workflow"


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def sync_mirror(name: str, src: Path, dst: Path, pattern: str) -> None:
    """镜像同步：将源目录中匹配的文件完整同步到目标目录。"""
    if not src.exists():
        print(f"  SKIP {name}: 源目录不存在 ({src})")
        return

    dst.mkdir(parents=True, exist_ok=True)
    src_files = {f.name: f for f in src.glob(pattern)}

    copied, skipped = 0, 0
    for name_f, src_file in src_files.items():
        dst_file = dst / name_f
        if dst_file.exists() and dst_file.stat().st_mtime >= src_file.stat().st_mtime:
            skipped += 1
            continue
        shutil.copy2(src_file, dst_file)
        copied += 1

    removed = 0
    for dst_file in dst.glob(pattern):
        if dst_file.name not in src_files:
            dst_file.unlink()
            removed += 1

    print(f"  OK {name}: 复制 {copied}, 跳过 {skipped}, 删除 {removed}")


def sync_file(name: str, src: Path, dst: Path) -> None:
    """单文件同步。"""
    if not src.exists():
        print(f"  SKIP {name}: 源文件不存在 ({src})")
        return

    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
        print(f"  SKIP {name}: 无变更")
        return

    shutil.copy2(src, dst)
    print(f"  OK {name}: 已同步")


def sync_codex_rules(name: str, src: Path, dst: Path) -> None:
    """同步全局规则到 Codex 的用户级 AGENTS.md。"""
    if not src.exists():
        print(f"  SKIP {name}: 源文件不存在 ({src})")
        return

    text = src.read_text(encoding="utf-8")
    _, body = split_frontmatter(text)
    content = (
        "<!-- Generated from D:\\self\\Ai\\sky-rules\\rules\\global-rules.md. "
        "Edit the source file, then sync again. -->\n\n"
        f"{body.lstrip()}"
    )
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(content, encoding="utf-8", newline="\n")
    print(f"  OK {name}: 已同步")


def sync_agents_skills(name: str, src: Path, dst: Path, pattern: str) -> None:
    """将 workflows/*.md 转换为 Agents/Codex 可识别的 skill 目录。"""
    if not src.exists():
        print(f"  SKIP {name}: 源目录不存在 ({src})")
        return

    dst.mkdir(parents=True, exist_ok=True)
    source_names: set[str] = set()
    copied = 0

    for src_file in sorted(src.glob(pattern)):
        skill_name = slugify(src_file.stem)
        source_names.add(skill_name)

        text = src_file.read_text(encoding="utf-8")
        metadata, body = split_frontmatter(text)
        description = metadata.get("description") or src_file.stem
        description = f"Use when the user wants this Sky workflow: {description}"

        skill_dir = dst / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(
            "---\n"
            f"name: {skill_name}\n"
            f"description: {yaml_quote(description)}\n"
            "---\n\n"
            f"<!-- Generated from {src_file}. Edit the source workflow, then sync again. -->\n\n"
            f"{body.rstrip()}\n",
            encoding="utf-8",
            newline="\n",
        )
        copied += 1

    removed = 0
    for skill_dir in dst.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue
        try:
            first_chunk = skill_file.read_text(encoding="utf-8")[:300]
        except UnicodeDecodeError:
            continue
        generated = "Generated from D:\\self\\Ai\\sky-rules\\workflows" in first_chunk
        if generated and skill_dir.name not in source_names:
            shutil.rmtree(skill_dir)
            removed += 1

    print(f"  OK {name}: 生成 {copied}, 删除过期 {removed}")


def sync_all() -> None:
    """执行全部同步任务。"""
    print("[2/2] 同步文件到各编辑器...")

    for item in SYNC_MAP:
        mode = item["mode"]
        if mode == "mirror":
            sync_mirror(item["name"], item["src"], item["dst"], item["pattern"])
        elif mode == "file":
            sync_file(item["name"], item["src"], item["dst"])
        elif mode == "codex_rules":
            sync_codex_rules(item["name"], item["src"], item["dst"])
        elif mode == "agents_skills":
            sync_agents_skills(item["name"], item["src"], item["dst"], item["pattern"])


def main() -> None:
    no_git = "--no-git" in sys.argv

    print("=" * 45)
    print("Sky Rules - 全量同步 (workflows + rules + skills)")
    print("=" * 45)
    print()

    if not no_git:
        git_commit_and_push()

    sync_all()

    print()
    print("=" * 45)
    print("同步完成！重启编辑器/插件即可生效。")
    print("=" * 45)


if __name__ == "__main__":
    main()
