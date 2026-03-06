# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import os
import json
import argparse
import tempfile
import pandas as pd
import httpx
from weaviate.util import generate_uuid5

SUBJECT_MAP = {'english': '영어', 'math': '수학'}

def process_data_for_weaviate(data_list):
    """기존 정제 로직"""
    if not data_list:
        return None

    df = pd.DataFrame(data_list)
    df = df.rename(columns={
        "id": "problem_id",
        'primary': 'section',
        'secondary': 'unit',
        'specific': 'topic'
    })

    if 'subject' in df.columns:
        df['subject'] = df['subject'].replace(SUBJECT_MAP)

    df["index"] = df.apply(
        lambda row: generate_uuid5(f"{row.get('problem_id', '')}{row.get('problem', '')}"),
        axis=1
    )

    df['correct_answers'] = df.get('correct_answers', pd.Series()).apply(
        lambda x: ",".join([str(i.get('answer', '')) for i in x if isinstance(i, dict)]) if isinstance(x, list) else str(x)
    )
    df['tags'] = df.get('tags', pd.Series()).apply(
        lambda x: ",".join(x) if isinstance(x, list) else str(x)
    )

    if 'choices' in df.columns: df = df.drop(columns=['choices'])

    final_columns = [
        "problem_id", "subject", "grade", "type", "category", "level", "url",
        "semester", "section", "unit", "topic", "problem",
        "correct_answers", "explanation", "hint", "tags", "index", "image_path"
    ]
    df = df.reindex(columns=final_columns, fill_value="")
    return df

def run_pipeline(base_url: str, file_path: str, index_name: str):
    # 1. 데이터 로드
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.csv':
        data = pd.read_csv(file_path).to_dict(orient='records')
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
            data = content.get('problems', content) if isinstance(content, dict) else content

    # 2. 데이터 정제
    print(f"✨ 데이터 정제 중... (대상: {file_path})")
    refined_df = process_data_for_weaviate(data)

    # 3. 임시 CSV 파일 생성 및 업로드
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        refined_df.to_csv(tmp.name, index=False, encoding='utf-8-sig')
        tmp_path = tmp.name

    try:
        print(f"🚀 서버로 전송 중... (URL: {base_url}/api/v1/vector/create, Index: {index_name})")

        # FastAPI @router.post("/create") 규격에 맞춤
        with open(tmp_path, "rb") as f:
            files = {"file": (f"refined_data_{index_name}.csv", f, "text/csv")}
            data = {"index_name": index_name}


            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{base_url}/create",
                    data=data,    # Form 데이터
                    files=files,  # File 데이터
                )

        if response.status_code == 200:
            print(f"✅ 완료: {response.json()['message']}")
        else:
            print(f"❌ 실패 ({response.status_code}): {response.text}")

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8001")
    parser.add_argument("--file", required=True, help="입력 JSON 또는 CSV 경로")
    parser.add_argument("--index", required=True, help="Weaviate 인덱스 이름")

    args = parser.parse_args()
    run_pipeline(args.url.rstrip('/'), args.file, args.index)