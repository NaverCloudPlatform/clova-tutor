# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import csv
import os
import re
import requests
from PIL import Image, ImageOps
import imghdr

# 설정
NCP_BASE_URL = "https://kr.object.ncloudstorage.com/edu-bucket/problem-image"

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
MAX_DIMENSION = 2240
MIN_DIMENSION = 4
MAX_RATIO = 5.0  # 5:1 이하


class ImageValidationError(Exception):
    """이미지 유효성 검사 실패 시 발생"""

def clean_category(value: str) -> str:
    """
    category 값 정제
    - 리스트 모양 문자열이면 쉼표로 join
    - 그냥 문자열이면 그대로
    """
    if not value:
        return ""

    # 대괄호로 시작하면 list literal 형태
    if value.strip().startswith("[") and value.strip().endswith("]"):
        # ' or " 제거하고 , 기준 split
        inner = value.strip()[1:-1]
        parts = re.split(r",\s*", inner)
        # 각 요소에서 따옴표 제거
        parts = [p.strip().strip("'\"") for p in parts if p.strip()]
        return ", ".join(parts)
    else:
        return value.strip()

def download_image(url, save_path):
    resp = requests.get(url, stream=True)
    resp.raise_for_status()
    with open(save_path, "wb") as f:
        for chunk in resp.iter_content(1024):
            f.write(chunk)
    return save_path


def fix_image(path: str):
    """비율, 크기 조건을 만족하지 않는 이미지를 보정"""
    with Image.open(path) as img:
        w, h = img.size
        long_side, short_side = max(w, h), min(w, h)

        # 1. 긴 변 줄이기 (2240px 초과 → 리사이즈)
        if long_side > MAX_DIMENSION:
            scale = MAX_DIMENSION / long_side
            w, h = int(w * scale), int(h * scale)
            img = img.resize((w, h), Image.LANCZOS)

        # 2. 짧은 변 늘리기 (4px 미만 → 리사이즈)
        if min(w, h) < MIN_DIMENSION:
            scale = MIN_DIMENSION / min(w, h)
            w, h = int(w * scale), int(h * scale)
            img = img.resize((w, h), Image.LANCZOS)

        # 3. 비율 보정 (5:1 이하로 맞추기 → 패딩 방식)
        long_side, short_side = max(w, h), min(w, h)
        ratio = long_side / short_side
        if ratio > MAX_RATIO:
            if w > h:
                target_h = w // MAX_RATIO
                pad = (target_h - h) // 2
                img = ImageOps.expand(img, border=(0, int(pad), 0, int(target_h - h - pad)), fill=(0, 0, 0, 0))
            else:
                target_w = h // MAX_RATIO
                pad = (target_w - w) // 2
                img = ImageOps.expand(img, border=(int(pad), 0, int(target_w - w - pad), 0), fill=(0, 0, 0, 0))

        base, _ = os.path.splitext(path)
        new_path = base + ".png"
        img.save(new_path, format="PNG")  # 강제로 PNG로 저장
    return new_path


def validate_and_fix_image(path: str):
    # 1. 파일 크기 검사
    size = os.path.getsize(path)
    if size == 0:
        raise ImageValidationError("0Byte 파일")
    if size > MAX_FILE_SIZE:
        raise ImageValidationError("20MB 초과 파일 (보정 불가)")

    # 2. 확장자 검사
    ext = imghdr.what(path)
    if ext not in ALLOWED_EXTENSIONS:
        raise ImageValidationError(f"허용되지 않는 확장자: {ext}")

    # 3. 조건 맞지 않으면 보정 시도
    with Image.open(path) as img:
        w, h = img.size
        long_side, short_side = max(w, h), min(w, h)
        ratio = long_side / short_side

        if (
            long_side > MAX_DIMENSION
            or short_side < MIN_DIMENSION
            or ratio > MAX_RATIO
        ):
            print(f"⚠️ 보정 시작: {path}")
            fix_image(path)


def process_tsv(input_tsv, output_tsv, start_index=10):
    os.makedirs("tmp_images", exist_ok=True)
    new_rows = []

    with open(input_tsv, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile, delimiter="\t")
        fieldnames = reader.fieldnames
        index = start_index

        for row in reader:
            if "category" in row:
                row["category"] = clean_category(row["category"])

            image_url = row.get("image", "")
            if image_url.startswith("https://"):
                local_path = f"tmp_images/{index}.png"
                download_image(image_url, local_path)

                try:
                    validate_and_fix_image(local_path)  # ✅ 정제 + 보정
                    # Default는 영어로 넣음
                    subject = row.get("subject", "english")
                    row["image"] = f"{NCP_BASE_URL}/{subject}/{index}.png"
                    index += 1
                except ImageValidationError as e:
                    print(f"❌ 이미지 불량 (url={image_url}): {e}")
                    # 이 경우는 정말 보정 불가니까 원래 url 유지

            new_rows.append(row)

    with open(output_tsv, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(new_rows)

    print(f"✅ 변환 완료. 새로운 TSV 파일: {output_tsv}")


if __name__ == "__main__":
    process_tsv("english-demo-problem-converted.tsv", "output2.tsv", start_index=10)
