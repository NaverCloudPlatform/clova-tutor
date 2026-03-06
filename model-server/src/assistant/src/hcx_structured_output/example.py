# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

"""
HCX Structured Output Package - Usage Examples
"""

import json
import sys
from pathlib import Path

SRC_DIR = Path(__file__).parent / "src"
sys.path.insert(0, str(SRC_DIR))

from src.schemas import AtLeastOneSegments, ImageDescription, build_model_from_spec
from src.tasks.image_caption import run_image_caption
from src.tasks.translation import run_bilingual_segments
from src.utils import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    GENERIC_PROMPT_TEMPLATE,
    IMAGE_CAPTION_PROMPT_TEMPLATE,
    TRANSLATION_PROMPT_TEMPLATE,
    load_prompt_yaml,
    run_structured_task,
    with_structured_output_like,
)


def test_dynamic_schema():
    """Dynamic Schema Creation Test"""
    print("\n🔨 Dynamic Schema Creation Test:")

    # Use actual testset example
    spec = {
        "name": "str",
        "role": "str",
        "skills": "List[str]",
        "experience_years": "int",
    }

    # Dynamic Pydantic model creation
    PersonSummary = build_model_from_spec("PersonSummary", spec)
    print(f"✅ Dynamic Schema Creation Completed: {PersonSummary.__name__}")

    # Schema information
    print(f"   - Fields: {list(PersonSummary.model_fields.keys())}")
    print(f"   - JSON Schema: {PersonSummary.model_json_schema()}")

    return PersonSummary


def test_generic_task():
    """Generic Structured Output Task Test - Using dynamic schemas"""
    print("\n📋 Generic Structured Output Task Test (Dynamic Schemas):")

    # Dynamic schema creation
    PersonSummary = test_dynamic_schema()

    # Use actual testset example
    person_doc = "홍길동은 데이터 엔지니어이며 Python, Spark, Airflow에 능숙하다. 경력은 5년이다."

    try:
        # Load prompt
        system_rules, fewshots = load_prompt_yaml("../prompt/prompt_generic.yaml")

        # Use GENERIC_PROMPT_TEMPLATE like evaluation.py
        schema_hint = json.dumps(PersonSummary.model_json_schema(), ensure_ascii=False)
        user_text = GENERIC_PROMPT_TEMPLATE.format(schema=schema_hint) + person_doc

        # Run structured output
        result = run_structured_task(
            system_rules=system_rules,
            fewshots=fewshots,
            user_content={
                "role": "user",
                "content": [{"type": "text", "text": user_text}],
            },
            response_model=PersonSummary,
            model=DEFAULT_MODEL,
            temperature=DEFAULT_TEMPERATURE,
            max_retries=DEFAULT_MAX_RETRIES,
        )

        print("✅ Structured Output Success!")
        print(f"   Result: {result.model_dump_json(indent=2)}")

        print("=" * 50)
        print("LangChain-style Structured Output:")
        structured = with_structured_output_like(
            response_model=PersonSummary,
            system_rules=system_rules,
            fewshots=fewshots,
            model=DEFAULT_MODEL,
        )
        res = structured.invoke(
            {"role": "user", "content": [{"type": "text", "text": user_text}]}
        )
        print(f"   Result: {res.model_dump_json(indent=2)}")

    except Exception as e:
        print(f"❌ Generic Task Failed: {e}")


def test_image_caption():
    """Image Captioning Test"""
    print("\n🖼️  Image Captioning Test:")

    test_image_url = "https://kr.object.ncloudstorage.com/edu-bucket/problem-image/math/20595053_000.png"

    try:
        # High-level function usage
        result = run_image_caption(test_image_url)
        print("✅ Image Captioning Success!")
        print(f"   Description: {result.image_description}")

    except Exception as e:
        print(f"❌ Image Captioning Failed: {e}")
        print("   (Test URL so failure is expected)")


def test_translation():
    """Translation Task Test"""
    print("\n🌐 Translation Task Test:")

    # Test 1: Long paragraph (multiple segments)
    print("\n   📝 Test 1: Long Paragraph")
    long_text = (
        "Language Models are Few-Shot Learners\n\n"
        "Recent work has demonstrated substantial gains on many NLP tasks and benchmarks "
        "by pre-training on a large corpus of text followed by fine-tuning on a specific task. "
        "While typically task-agnostic in architecture, this method still requires task-specific "
        "fine-tuning datasets of thousands or tens of thousands of examples. By contrast, humans "
        "can generally perform a new language task from only a few examples or from simple "
        "instructions - something which current NLP systems still largely struggle to do."
    )
    try:
        result = run_bilingual_segments(long_text)
        print("   ✅ Long paragraph translation success!")
        print(f"   Segment count: {len(result.segments)}")

    except Exception as e:
        print(f"   ❌ Long paragraph translation failed: {e}")


def test_direct_structured_task():
    """Direct Structured Task Test - Using predefined schemas"""
    print("\n⚙️ Direct Structured Task Test (Predefined Schemas):")

    # Test 1: Short translation with run_structured_task (single segment)
    print("\n   📝 Test 1: Short Translation Task (Single Segment)")
    try:
        system_rules, fewshots = load_prompt_yaml("src/prompt/prompt_translation.yaml")

        short_text = "Machine learning is a subset of artificial intelligence."
        prompt = TRANSLATION_PROMPT_TEMPLATE + f"텍스트:\n{short_text}"

        result = run_structured_task(
            system_rules=system_rules,
            fewshots=fewshots,
            user_content={"role": "user", "content": prompt},
            response_model=AtLeastOneSegments,
            model=DEFAULT_MODEL,
            temperature=DEFAULT_TEMPERATURE,
            max_retries=DEFAULT_MAX_RETRIES,
        )

        print("   ✅ Short translation with run_structured_task Success!")
        # print(f"   Result: {result.model_dump_json(indent=2)}")
        print(f"   Result: {result}")
        print("=" * 50)
        print("LangChain-style Structured Output:")
        structured = with_structured_output_like(
            response_model=AtLeastOneSegments,
            system_rules=system_rules,
            fewshots=fewshots,
            model=DEFAULT_MODEL,
        )
        res = structured.invoke(
            {"role": "user", "content": [{"type": "text", "text": short_text}]}
        )
        # print(f"   Result: {res.model_dump_json(indent=2)}")
        print(f"   Result: {res}")

    except Exception as e:
        print(f"   ❌ Short translation with run_structured_task Failed: {e}")

    # Test 2: Image Captioning with run_structured_task
    print("\n   🖼️ Test 2: Image Captioning Task")
    try:
        system_rules, fewshots = load_prompt_yaml("src/prompt/prompt_image.yaml")

        # Use IMAGE_CAPTION_PROMPT_TEMPLATE like evaluation.py
        user_msg = {
            "role": "user",
            "content": [
                {"type": "text", "text": IMAGE_CAPTION_PROMPT_TEMPLATE},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://kr.object.ncloudstorage.com/edu-bucket/problem-image/math/20595053_000.png"
                    },
                },
            ],
        }

        result = run_structured_task(
            system_rules=system_rules,
            fewshots=fewshots,
            user_content=user_msg,
            response_model=ImageDescription,
            model=DEFAULT_MODEL,
            temperature=DEFAULT_TEMPERATURE,
            max_retries=DEFAULT_MAX_RETRIES,
        )

        print("   ✅ Image Captioning with run_structured_task Success!")
        # print(f"   Result: {result.model_dump_json(indent=2)}")
        print(f"   Result: {result}")

        print("=" * 50)
        print("LangChain-style Structured Output:")
        structured = with_structured_output_like(
            response_model=ImageDescription,
            system_rules=system_rules,
            fewshots=fewshots,
            model=DEFAULT_MODEL,
        )
        res = structured.invoke(user_msg)
        # print(f"   Result: {res.model_dump_json(indent=2)}")
        print(f"   Result: {res}")

    except Exception as e:
        print(f"   ❌ Image Captioning with run_structured_task Failed: {e}")
        print("   (Test URL so failure is expected)")


def main():
    """Main Test Function"""
    print("🚀 HCX Structured Output Test Start")
    print("=" * 50)

    # Run tests
    # test_generic_task()
    # test_image_caption()
    # test_translation()
    test_direct_structured_task()

    print("\n" + "=" * 50)
    print("🎉 Test Completed!")
    print("\n💡 Tips:")
    print("   - Set valid API keys for actual use")
    print("   - Use actual accessible image URLs")
    print("   - Check logs for errors to resolve issues")


if __name__ == "__main__":
    main()
