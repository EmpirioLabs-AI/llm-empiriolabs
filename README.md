# llm-empiriolabs

[![PyPI](https://img.shields.io/pypi/v/llm-empiriolabs.svg)](https://pypi.org/project/llm-empiriolabs/)

[LLM](https://llm.datasette.io/) plugin for accessing [EmpirioLabs AI](https://empiriolabs.ai) models.

EmpirioLabs AI is specialized AI model hosting for open, proprietary, and custom stacks. Every model it serves is listed, with its ID and price, in the live catalog at [empiriolabs.ai/models](https://empiriolabs.ai/models).

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
llm models list | grep empiriolabs
llm -m empiriolabs/MODEL_ID "Five surprising facts about octopuses"
```

Start an interactive chat:

```bash
llm chat -m empiriolabs/MODEL_ID
```

Pipe content in:

```bash
cat article.txt | llm -m empiriolabs/MODEL_ID "Summarize this in three bullet points"
```

Replace `MODEL_ID` with any chat model ID from [empiriolabs.ai/models](https://empiriolabs.ai/models). The plugin reads the live model list from `https://api.empiriolabs.ai/v1/models` (cached for an hour, and the cached copy is used when the call fails), so `llm models list` always shows the current chat models.

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
