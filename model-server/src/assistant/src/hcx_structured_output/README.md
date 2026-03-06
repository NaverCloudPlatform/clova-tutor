<!-- CLOVA Tutor
Copyright (c) 2026-present NAVER Cloud Corp.
MIT -->

# HCX Structured Output

Utilities and examples to get structured output from HyperCLOVA X via [Instructor](https://github.com/567-labs/instructor).

## Prerequisites
- Python 3.11.x (tested on 3.11.13)
- HyperCLOVA X API key
- OpenAI API key
- uv package manager (recommended)

## Setup

### Using uv (Recommended)
```bash
# 1. Create a new virtual environment
uv venv --python 3.11 venv_name

# 2. Activate the virtual environment
source venv_name/bin/activate

# 3. Install the project in editable mode
uv pip install -e .
```

## Environment variables
Set api_info.yaml (hcx_structured_output/api_info.yaml)

## Quick Start

### 1. Test Basic Functionality
Run the comprehensive example to test all features:
```bash
python example.py
```

This will test:
- Environment variable loading
- Dynamic schema creation
- Generic structured output tasks
- Image captioning
- Bilingual text segmentation

Please refer to `example.py` for comprehensive usage examples.

## Project Structure
```
hcx_structured_output/
├── src/
│   ├── adapters/            # ClovaX ↔ OpenAI adapter
│   ├── examples/            # Usage examples (executable scripts)
│   ├── prompt/              # YAML prompts per task
│   ├── schemas/             # Pydantic schemas (dynamic/image/primitives)
│   ├── tasks/               # High-level task functions 
│   └── utils/               # Core utilities (runner, chunk, merge, constants)
├── example.py               # Comprehensive usage examples
├── pyproject.toml           # Project configuration and dependencies
```
