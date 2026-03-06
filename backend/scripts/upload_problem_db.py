# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import json
import os
import subprocess
import sys
import argparse

import httpx
import pandas as pd
from src.config.config import internal_api_key

def print_step(step: int, text: str) -> None:
    print(f"\n{'='*10} STEP {step}: {text} {'='*10}")

def check_uv() -> None:
    print_step(1, "uv 설치 확인")
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        print("✅ uv가 설치되어 있습니다.")
    except:
        print("❌ 오류: uv를 찾을 수 없습니다. 설치 후 다시 실행해주세요.")
        sys.exit(1)

def install_deps(skip_confirm: bool = False) -> None:
    print_step(2, "의존성 설치")
    if skip_confirm:
        confirm = 'y'
    else:
        confirm = input("📦 uv sync --group setup을 실행할까요? (Y/n): ").lower()

    if confirm in ['', 'y', 'yes']:
        try:
            subprocess.run("uv sync --group setup", shell=True, check=True)
            print("✅ 의존성 설치 완료.")
        except subprocess.CalledProcessError:
            print("❌ 의존성 설치 중 오류가 발생했습니다.")
            sys.exit(1)
    else:
        print("⏭️ 의존성 설치를 건너뜁니다.")

def load_data(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == '.csv':
            df = pd.read_csv(file_path)
            df = df.where(pd.notnull(df), None)
            data_list = df.to_dict(orient='records')
        elif ext == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                data_list = content.get('problems', content) if isinstance(content, dict) else content
        else:
            print(f"❌ 지원하지 않는 확장자입니다: {ext}")
            sys.exit(1)
        return data_list
    except Exception as e:
        print(f"❌ 파일 로드 중 오류 발생: {e}")
        sys.exit(1)

def run_backend_pipeline(base_url: str, api_key: str, file_path: str):
    print_step(4, "서비스 상태 확인")
    headers = {
        "accept": "application/json",
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }

    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        try:
            resp = client.get("/health")
            if resp.status_code == 200:
                print(f"✅ 서비스 작동 중 ({base_url})")
            else:
                print(f"⚠️ 서비스 응답 이상 (Status: {resp.status_code})")
                sys.exit(1)
        except Exception as e:
            print(f"❌ 서비스 연결 실패: {e}")
            sys.exit(1)

        print_step(5, "문제 생성 API 호출")
        try:
            items = load_data(file_path)
            payload = {"problems": items}
            resp = client.post("/problems", json=payload, headers=headers)
            if resp.status_code in [200, 201]:
                print(f"✅ 문제 생성 완료 (Status: {resp.status_code})")
            else:
                print(f"❌ 생성 실패: {resp.status_code}\n{resp.text}")
                sys.exit(1)
        except Exception as e:
            print(f"❌ 파일 읽기 또는 API 호출 중 오류: {e}")
            sys.exit(1)

def get_runtime_configs(args) -> tuple[str, str, str]:
    """CLI 인자가 있으면 사용하고, 없으면 대화형 입력을 받음"""
    print_step(3, "실행 환경 설정")

    # 1. Base URL
    base_url = args.url or input(f"🌐 서비스 BASE URL (기본값: http://localhost:8000): ").strip() or "http://localhost:8000"

    # 2. API Key (설정 파일 우선, 인자 있으면 인자 사용)
    api_key = args.api_key or internal_api_key.INTERNAL_API_KEY

    # 3. File Path
    file_path = args.file or input(f"📄 대상 파일 경로 (기본값: scripts/problem.json): ").strip() or "scripts/problem.json"

    if not os.path.exists(file_path):
        print(f"❌ 오류: 파일을 찾을 수 없습니다: {file_path}")
        sys.exit(1)

    return base_url.rstrip('/'), api_key, file_path

def main():
    parser = argparse.ArgumentParser(description="문제 업로드 파이프라인 CLI")
    parser.add_argument("--url", help="서비스 Base URL")
    parser.add_argument("--file", help="업로드할 JSON/CSV 파일 경로")
    parser.add_argument("--api-key", help="API Key (미입력 시 config 사용)")
    parser.add_argument("--yes", action="store_true", help="의존성 설치 시 확인 절차 건너뜀")

    args = parser.parse_args()

    print("🚀 문제 업로드 파이프라인")
    check_uv()
    install_deps(skip_confirm=args.yes)
    base_url, api_key, file_path = get_runtime_configs(args)
    run_backend_pipeline(base_url, api_key, file_path)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 종료합니다.")