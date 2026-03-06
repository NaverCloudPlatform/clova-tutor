# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import json
import os
import re

import pandas as pd
import yaml

from assistant.src.schema import ModelParam
from config.config import model_config


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


def load_jsonl(path: str, encoding: str = "utf-8") -> list:
    data = []
    with open(path, "r", encoding=encoding) as f:
        for line in f.readlines():
            data.append(json.loads(line))
    return data


def load_data(file_name: str):
    file_path = os.path.join(model_config.DATA_PATH, file_name)
    if file_name.endswith(".yaml"):
        return load_yaml(file_path)
    elif file_name.endswith(".csv"):
        return pd.read_csv(file_path)
    elif file_name.endswith(".jsonl"):
        return load_jsonl(file_path)
    else:
        raise ValueError("지원하지 않는 파일 형식입니다. (.yaml 또는 .csv)")


def load_questions(
    file_name: str = "[EDU TECH] 250109 데모용 데이터", sheet_name: str = None
):
    file_path = os.path.join(model_config.DATA_PATH, f"{file_name}.xlsx")
    section = [sheet_name] if sheet_name else ["Filtering", "ENGvoca"]
    return {name.lower(): pd.read_excel(file_path, sheet_name=name) for name in section}


def load_template(file_name: str = "ai_messages"):
    path = os.path.join(model_config.ANSWER_TEMPLATE_PATH, f"{file_name}.yaml")
    return load_yaml(path)


def load_default_prompt(file_name: str = "eduqa"):
    path = os.path.join(model_config.DEFAULT_PROMPT_PATH, f"{file_name}.yaml")
    return load_yaml(path)


def load_content_template(file_name: str = "eng"):
    path = os.path.join(model_config.CONTENT_TEMPLATE_PATH, f"{file_name}.yaml")
    return load_yaml(path)


def load_model_param(section: str) -> ModelParam:
    with open("assistant/src/options/model_param.yaml", "r") as f:
        config = yaml.safe_load(f)
    return ModelParam(**config[section])


def load_additional_model_param(section: str) -> dict:
    with open("assistant/src/options/model_param.yaml", "r") as f:
        config = yaml.safe_load(f)
    return config[section]


def load_voca():
    eng_voca_integrated = load_data("eng_voca_integrated.jsonl")
    return eng_voca_integrated
