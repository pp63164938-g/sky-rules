#!/usr/bin/env python3
"""Validate the Feishu/OpenClaw baseline without printing secrets."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    """Parse the configuration and optional route identifiers."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path, help="Path to openclaw.json")
    parser.add_argument("--account-id", help="Feishu account ID to validate")
    parser.add_argument("--agent-id", help="OpenClaw agent ID to validate")
    parser.add_argument(
        "--check-workspace",
        action="store_true",
        help="Require the selected agent workspace and its baseline files",
    )
    parser.add_argument(
        "--business-skill",
        action="append",
        default=[],
        help="Required workspace skill directory; may be repeated",
    )
    parser.add_argument(
        "--require-tool",
        action="append",
        default=[],
        help="Required per-agent tools.allow entry; may be repeated",
    )
    parser.add_argument(
        "--forbid-tool",
        action="append",
        default=[],
        help="Forbidden per-agent tools.allow entry; may be repeated",
    )
    parser.add_argument(
        "--agent-skill",
        action="append",
        default=[],
        help=(
            "Expected per-agent skills allowlist entry; may be repeated. "
            "When supplied, the allowlist must match exactly"
        ),
    )
    return parser.parse_args()


def load_config(config_path: Path) -> dict[str, Any]:
    """Load an OpenClaw JSON configuration."""
    with config_path.open("r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    if not isinstance(config, dict):
        raise ValueError("configuration root must be an object")

    return config


def get_object(value: Any) -> dict[str, Any]:
    """Return a dictionary for object-like values."""
    return value if isinstance(value, dict) else {}


def get_list(value: Any) -> list[Any]:
    """Return a list for array-like values."""
    return value if isinstance(value, list) else []


def validate_access_policy(feishu_config: dict[str, Any], errors: list[str]) -> None:
    """Validate the shared Feishu access baseline."""
    if feishu_config.get("dmPolicy") != "pairing":
        errors.append("channels.feishu.dmPolicy must be 'pairing'")

    if feishu_config.get("groupPolicy") != "open":
        errors.append("channels.feishu.groupPolicy must be 'open'")

    if feishu_config.get("requireMention") is not True:
        errors.append("channels.feishu.requireMention must be true")

    if feishu_config.get("typingIndicator") is not True:
        errors.append("channels.feishu.typingIndicator must be explicitly true")

    group_allow_from = feishu_config.get("groupAllowFrom")
    if group_allow_from not in (None, []):
        errors.append(
            "channels.feishu.groupAllowFrom must be absent under the open-group baseline"
        )

    for entry in get_list(group_allow_from):
        if not isinstance(entry, str) or not entry.startswith("oc_"):
            errors.append(
                "channels.feishu.groupAllowFrom entries must start with 'oc_', never 'ou_'"
            )
            break

    for entry in get_list(feishu_config.get("allowFrom")):
        if not isinstance(entry, str) or (entry != "*" and not entry.startswith("ou_")):
            errors.append("channels.feishu.allowFrom entries must be '*' or start with 'ou_'")
            break


def validate_unique_account_app_ids(
    feishu_config: dict[str, Any], errors: list[str]
) -> None:
    """Reject duplicate App IDs that make account routing ambiguous."""
    accounts = get_object(feishu_config.get("accounts"))
    account_ids_by_app_id: dict[str, list[str]] = {}
    for account_id, account_value in accounts.items():
        account = get_object(account_value)
        app_id = account.get("appId")
        if not isinstance(app_id, str) or not app_id:
            continue
        account_ids_by_app_id.setdefault(app_id, []).append(str(account_id))

    for account_ids in account_ids_by_app_id.values():
        if len(account_ids) > 1:
            errors.append(
                "Feishu appId must belong to exactly one account; duplicate accounts: "
                + ", ".join(sorted(account_ids))
            )


def validate_account(
    feishu_config: dict[str, Any], account_id: str, errors: list[str]
) -> None:
    """Validate one Feishu account without exposing its secret."""
    accounts = get_object(feishu_config.get("accounts"))
    account = get_object(accounts.get(account_id))

    if not account:
        errors.append(f"Feishu account '{account_id}' is missing")
        return

    if account.get("enabled") is not True:
        errors.append(f"Feishu account '{account_id}' must be enabled")

    app_id = account.get("appId")
    if not isinstance(app_id, str) or not app_id.startswith("cli_"):
        errors.append(f"Feishu account '{account_id}' has an invalid appId")

    if not account.get("appSecret"):
        errors.append(f"Feishu account '{account_id}' is missing appSecret")


def validate_agent_and_binding(
    config: dict[str, Any], account_id: str, agent_id: str, errors: list[str]
) -> None:
    """Validate the selected agent and its Feishu route."""
    agents_config = get_object(config.get("agents"))
    agent_list = get_list(agents_config.get("list"))
    matching_agents = [
        agent
        for agent in agent_list
        if isinstance(agent, dict) and agent.get("id") == agent_id
    ]

    if len(matching_agents) != 1:
        errors.append(
            f"Agent '{agent_id}' must exist exactly once; found {len(matching_agents)}"
        )
    else:
        agent = matching_agents[0]
        if not agent.get("workspace"):
            errors.append(f"Agent '{agent_id}' is missing workspace")
        if not agent.get("agentDir"):
            errors.append(f"Agent '{agent_id}' is missing agentDir")

    bindings = get_list(config.get("bindings"))
    matching_bindings = []
    for binding in bindings:
        if not isinstance(binding, dict):
            continue
        match = get_object(binding.get("match"))
        if match.get("channel") == "feishu" and match.get("accountId") == account_id:
            matching_bindings.append(binding)

    if len(matching_bindings) != 1:
        errors.append(
            f"Feishu account '{account_id}' must have exactly one route binding; "
            f"found {len(matching_bindings)}"
        )
    elif matching_bindings[0].get("agentId") != agent_id:
        errors.append(f"Feishu account '{account_id}' routes to a different agent")


def validate_workspace(
    config: dict[str, Any], agent_id: str, business_skills: list[str], errors: list[str]
) -> None:
    """Validate baseline workspace files and explicitly required business skills."""
    agents_config = get_object(config.get("agents"))
    agent_list = get_list(agents_config.get("list"))
    agent = next(
        (
            agent_value
            for agent_value in agent_list
            if isinstance(agent_value, dict) and agent_value.get("id") == agent_id
        ),
        None,
    )
    if not isinstance(agent, dict):
        return

    workspace_value = agent.get("workspace")
    if not isinstance(workspace_value, str) or not workspace_value.strip():
        return

    workspace_path = Path(workspace_value).expanduser()
    if not workspace_path.is_dir():
        errors.append(f"Agent '{agent_id}' workspace directory is missing")
        return

    for filename in ("AGENTS.md", "SOUL.md"):
        if not (workspace_path / filename).is_file():
            errors.append(f"Agent '{agent_id}' workspace is missing {filename}")

    for skill_name in business_skills:
        if not skill_name or "/" in skill_name or "\\" in skill_name:
            errors.append(f"Invalid business skill directory name: {skill_name!r}")
            continue
        skill_path = workspace_path / "skills" / skill_name / "SKILL.md"
        if not skill_path.is_file():
            errors.append(
                f"Agent '{agent_id}' workspace is missing business skill '{skill_name}'"
            )


def validate_agent_tools(
    config: dict[str, Any],
    agent_id: str,
    required_tools: list[str],
    forbidden_tools: list[str],
    errors: list[str],
) -> None:
    """Validate an explicit per-agent tool allowlist when a policy is requested."""
    if not required_tools and not forbidden_tools:
        return

    agents_config = get_object(config.get("agents"))
    agent_list = get_list(agents_config.get("list"))
    agent = next(
        (
            agent_value
            for agent_value in agent_list
            if isinstance(agent_value, dict) and agent_value.get("id") == agent_id
        ),
        None,
    )
    if not isinstance(agent, dict):
        return

    tools_config = get_object(agent.get("tools"))
    allow_values = tools_config.get("allow")
    if not isinstance(allow_values, list) or not all(
        isinstance(tool_value, str) for tool_value in allow_values
    ):
        errors.append(f"Agent '{agent_id}' must define an explicit tools.allow list")
        return

    allowed_tools = set(allow_values)
    for tool_name in required_tools:
        if tool_name not in allowed_tools:
            errors.append(f"Agent '{agent_id}' tools.allow is missing '{tool_name}'")
    for tool_name in forbidden_tools:
        if tool_name in allowed_tools:
            errors.append(f"Agent '{agent_id}' tools.allow must not include '{tool_name}'")


def validate_agent_skills(
    config: dict[str, Any],
    agent_id: str,
    expected_skills: list[str],
    errors: list[str],
) -> None:
    """Validate an exact per-agent skill allowlist when one is requested."""
    if not expected_skills:
        return

    agents_config = get_object(config.get("agents"))
    agent_list = get_list(agents_config.get("list"))
    agent = next(
        (
            agent_value
            for agent_value in agent_list
            if isinstance(agent_value, dict) and agent_value.get("id") == agent_id
        ),
        None,
    )
    if not isinstance(agent, dict):
        return

    skill_values = agent.get("skills")
    if not isinstance(skill_values, list) or not all(
        isinstance(skill_value, str) for skill_value in skill_values
    ):
        errors.append(f"Agent '{agent_id}' must define an explicit skills allowlist")
        return

    actual_skills = set(skill_values)
    requested_skills = set(expected_skills)
    if len(actual_skills) != len(skill_values):
        errors.append(f"Agent '{agent_id}' skills must not contain duplicates")
    for skill_name in sorted(requested_skills - actual_skills):
        errors.append(f"Agent '{agent_id}' skills is missing '{skill_name}'")
    for skill_name in sorted(actual_skills - requested_skills):
        errors.append(f"Agent '{agent_id}' skills has unexpected '{skill_name}'")


def main() -> int:
    """Run validation and return a process-friendly status code."""
    args = parse_args()
    errors: list[str] = []

    try:
        config = load_config(args.config)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"INVALID: unable to read configuration: {error}", file=sys.stderr)
        return 2

    channels = get_object(config.get("channels"))
    feishu_config = get_object(channels.get("feishu"))
    if not feishu_config:
        errors.append("channels.feishu is missing")
    else:
        validate_access_policy(feishu_config, errors)
        validate_unique_account_app_ids(feishu_config, errors)

    if bool(args.account_id) != bool(args.agent_id):
        errors.append("--account-id and --agent-id must be provided together")
    elif args.account_id and args.agent_id:
        validate_account(feishu_config, args.account_id, errors)
        validate_agent_and_binding(config, args.account_id, args.agent_id, errors)
        if args.check_workspace:
            validate_workspace(config, args.agent_id, args.business_skill, errors)
        validate_agent_tools(
            config,
            args.agent_id,
            args.require_tool,
            args.forbid_tool,
            errors,
        )
        validate_agent_skills(config, args.agent_id, args.agent_skill, errors)
    elif (
        args.check_workspace
        or args.business_skill
        or args.require_tool
        or args.forbid_tool
        or args.agent_skill
    ):
        errors.append(
            "workspace, business skill, tool, and agent skill validation require "
            "--account-id and --agent-id"
        )

    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1

    print("VALID")
    print(
        "- access baseline: pairing DM, open groups, direct mention required, "
        "typing indicator explicit"
    )
    if args.account_id and args.agent_id:
        print("- account, agent, and binding: consistent")
        if args.check_workspace:
            print("- workspace baseline and required business skills: present")
        if args.require_tool or args.forbid_tool:
            print("- per-agent tool allowlist: matches the requested capability boundary")
        if args.agent_skill:
            print("- per-agent skill allowlist: exactly matches the requested business scope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
