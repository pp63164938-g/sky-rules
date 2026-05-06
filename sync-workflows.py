# -*- coding: utf-8 -*-
"""
Sky Rules 全量同步脚本
同步 workflows / rules / skills 到 Windsurf 和 Antigravity

用法:
  python sync-workflows.py          # 同步全部
  python sync-workflows.py --no-git # 跳过 git 提交
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# ========== 路径配置 ==========
ROOT = Path(__file__).parent
HOME = Path.home()

# 源目录
SRC_WORKFLOWS = ROOT / "workflows"
SRC_RULES = ROOT / "rules"
SRC_SKILLS = ROOT / "skills"  # 预留，目录不存在时自动跳过

# 同步映射表：(源, 目标, 模式)
# 模式: "mirror" = 镜像同步整个目录(删除目标多余文件), "file" = 单文件复制
SYNC_MAP = [
    # --- Workflows ---
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
    # --- Rules ---
    # 源文件统一叫 global-rules.md，同步时映射为各编辑器要求的文件名
    {
        "name": "Antigravity 规则",
        "src": SRC_RULES / "global-rules.md",
        "dst": HOME / ".gemini" / "GEMINI.md",
        "mode": "file",
    },
    # Windsurf 全局规则由 Windsurf 自身管理(memories/global_rules.md)
    # 如需从 sky-rules 管理，取消以下注释并在 rules/ 下创建 global_rules.md
    # {
    #     "name": "Windsurf 全局规则",
    #     "src": SRC_RULES / "global_rules.md",
    #     "dst": HOME / ".codeium" / "windsurf" / "memories" / "global_rules.md",
    #     "mode": "file",
    # },
    # --- Skills (预留) ---
    # {
    #     "name": "Windsurf Skills",
    #     "src": SRC_SKILLS,
    #     "dst": HOME / ".codeium" / "windsurf" / "skills",
    #     "mode": "mirror",
    #     "pattern": "*.md",
    # },
]


def git_commit_and_push():
    """自动提交并推送 sky-rules 仓库变更"""
    print("[1/2] Git 提交变更...")
    os.chdir(ROOT)

    subprocess.run(["git", "add", "-A"], check=True, capture_output=True)

    # 检查是否有暂存变更
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
    if result.returncode != 0:
        subprocess.run(
            ["git", "commit", "-m", "update: sync workflows and rules"],
            check=True, capture_output=True
        )
        push_result = subprocess.run(
            ["git", "push"], capture_output=True, text=True
        )
        if push_result.returncode == 0:
            print("    ✅ 已提交并推送")
        else:
            print("    ⚠️  已提交，推送失败（可能无远程或网络问题）")
    else:
        print("    无变更需要提交")
    print()


def sync_mirror(name: str, src: Path, dst: Path, pattern: str):
    """镜像同步：将源目录中匹配的文件完整同步到目标目录"""
    if not src.exists():
        print(f"  ⏭️  {name}: 源目录不存在，跳过 ({src})")
        return

    dst.mkdir(parents=True, exist_ok=True)
    src_files = {f.name: f for f in src.glob(pattern)}

    # 复制/更新文件
    copied, skipped = 0, 0
    for name_f, src_file in src_files.items():
        dst_file = dst / name_f
        # 检查是否需要更新（比较修改时间）
        if dst_file.exists() and dst_file.stat().st_mtime >= src_file.stat().st_mtime:
            skipped += 1
            continue
        shutil.copy2(src_file, dst_file)
        copied += 1

    # 删除目标中多余的文件（镜像模式）
    removed = 0
    for dst_file in dst.glob(pattern):
        if dst_file.name not in src_files:
            dst_file.unlink()
            removed += 1

    print(f"  ✅ {name}: 复制 {copied}, 跳过 {skipped}, 删除 {removed}")


def sync_file(name: str, src: Path, dst: Path):
    """单文件同步"""
    if not src.exists():
        print(f"  ⏭️  {name}: 源文件不存在，跳过 ({src})")
        return

    dst.parent.mkdir(parents=True, exist_ok=True)

    # 检查是否需要更新
    if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
        print(f"  ⏭️  {name}: 无变更，跳过")
        return

    shutil.copy2(src, dst)
    print(f"  ✅ {name}: 已同步")


def sync_all():
    """执行全部同步任务"""
    print("[2/2] 同步文件到各编辑器...")

    for item in SYNC_MAP:
        if item["mode"] == "mirror":
            sync_mirror(item["name"], item["src"], item["dst"], item["pattern"])
        elif item["mode"] == "file":
            sync_file(item["name"], item["src"], item["dst"])


def main():
    no_git = "--no-git" in sys.argv

    print("=" * 45)
    print("Sky Rules - 全量同步 (workflows + rules)")
    print("=" * 45)
    print()

    if not no_git:
        git_commit_and_push()

    sync_all()

    print()
    print("=" * 45)
    print("同步完成！重启编辑器即可生效。")
    print("=" * 45)


if __name__ == "__main__":
    main()
