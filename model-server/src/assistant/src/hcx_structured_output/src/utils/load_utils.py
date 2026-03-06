# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

# src/utils/load_utils.py
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import yaml


def load_prompt_yaml(
    path: Union[str, Path], prompt_key: Optional[str] = None
) -> Tuple[str, List[Dict[str, Any]]]:
    p = Path(path)
    cfg = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    if prompt_key is None:
        # Generic structure: system_rules and fewshots at top level
        return cfg.get("system_rules", ""), cfg.get("fewshots", [])
    else:
        # Edu structure: specific section with system_rules and fewshots
        if prompt_key not in cfg:
            raise ValueError(f"Prompt key '{prompt_key}' not found in {path}")

        prompt_section = cfg[prompt_key]
        system_rules = prompt_section.get("system_rules", "")
        fewshots = prompt_section.get("fewshots", [])

        return system_rules, fewshots


def load_yaml(path: str, encoding: str = "utf-8") -> dict:
    pattern = re.compile(r"\$\{(\w+)(?::-(.*))?\}")

    with open(path, "r", encoding=encoding) as f:
        content = f.read()

    def replace_env(match):
        env_var = match.group(1)
        default_val = match.group(2)
        return os.getenv(env_var, default_val)

    substituted_content = pattern.sub(replace_env, content)
    return yaml.safe_load(substituted_content)


def load_api_config() -> Dict[str, Any]:
    """API 설정을 assistant/api_info.yaml에서 로드"""
    current_dir = Path(__file__).parent
    possible_paths = [
        current_dir / "../../../../api_info.yaml",  #  src/assistant/
        current_dir / "../../src/assistant/api_info.yaml",  # other location
        Path("src/assistant/api_info.yaml"),  # project root location
    ]

    config_path = None
    for path in possible_paths:
        if path.exists():
            config_path = path
            break

    if config_path is None:
        raise FileNotFoundError("api_info.yaml file not found")

    return load_yaml(str(config_path))
