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

    if bool(args.account_id) != bool(args.agent_id):
        errors.append("--account-id and --agent-id must be provided together")
    elif args.account_id and args.agent_id:
        validate_account(feishu_config, args.account_id, errors)
        validate_agent_and_binding(config, args.account_id, args.agent_id, errors)

    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1

    print("VALID")
    print("- access baseline: pairing DM, open groups, direct mention required")
    if args.account_id and args.agent_id:
        print("- account, agent, and binding: consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
