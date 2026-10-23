# llm-empiriolabs

[![PyPI](https://img.shields.io/pypi/v/llm-empiriolabs.svg)](https://pypi.org/project/llm-empiriolabs/)

[LLM](https://llm.datasette.io/) plugin for accessing [EmpirioLabs AI](https://empiriolabs.ai) models.

EmpirioLabs AI is specialized AI model hosting for open, proprietary, and custom stacks. Its chat models include Qwen3, DeepSeek V4, GLM-5.1, Kimi K2.7 Code and MiniMax M3; browse the full catalog at [docs.empiriolabs.ai](https://docs.empiriolabs.ai).

## Installation

Install this plugin in the same environment as [LLM](https://llm.datasette.io/).

```bash
llm install llm-empiriolabs
```

## Configuration

Set an [API key](https://platform.empiriolabs.ai) for EmpirioLabs:

```bash
llm keys set empiriolabs
# Paste your EMPIRIOLABS_API_KEY when prompted
```

You can also set the `EMPIRIOLABS_API_KEY` environment variable instead.

## Usage

List the available EmpirioLabs AI models:

```bash
llm models list | grep -i empiriolabs
```

Run a prompt:

```bash
llm -m empiriolabs/qwen3-7-plus "Five surprising facts about octopuses"
```

Start an interactive chat:

```bash
llm chat -m empiriolabs/deepseek-v4-pro
```

Pipe content in:

```bash
cat article.txt | llm -m empiriolabs/glm-5-1 "Summarize this in three bullet points"
```

The plugin fetches the live model list from `https://api.empiriolabs.ai/v1/models` on first use (cached for an hour). If that call is unavailable it falls back to a built-in list of popular slugs:

- `empiriolabs/qwen3-7-plus`
- `empiriolabs/qwen3-7-max`
- `empiriolabs/deepseek-v4-pro`
- `empiriolabs/deepseek-v4-1-flash`
- `empiriolabs/glm-5-1`
- `empiriolabs/kimi-k2-7-code`
- `empiriolabs/minimax-m3`

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:

```bash
cd llm-empiriolabs
python -m venv venv
source venv/bin/activate
```

Now install the dependencies and test dependencies:

```bash
pip install -e '.[test]'
```

To run the tests:

```bash
pytest
```

## License

Apache-2.0
