<!---
Copyright 2024 The HuggingFace Team. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->
<p align="center">
    <!-- Uncomment when CircleCI is set up
    <a href="https://circleci.com/gh/huggingface/accelerate"><img alt="Build" src="https://img.shields.io/circleci/build/github/huggingface/transformers/master"></a>
    -->
    <a href="https://github.com/huggingface/smolagents/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/github/license/huggingface/smolagents.svg?color=blue"></a>
    <a href="https://huggingface.co/docs/smolagents"><img alt="Documentation" src="https://img.shields.io/website/http/huggingface.co/docs/smolagents/index.html.svg?down_color=red&down_message=offline&up_message=online"></a>
    <a href="https://github.com/huggingface/smolagents/releases"><img alt="GitHub release" src="https://img.shields.io/github/release/huggingface/smolagents.svg"></a>
    <a href="https://github.com/huggingface/smolagents/blob/main/CODE_OF_CONDUCT.md"><img alt="Contributor Covenant" src="https://img.shields.io/badge/Contributor%20Covenant-v2.0%20adopted-ff69b4.svg"></a>
</p>

<h3 align="center">
  <div style="display:flex;flex-direction:row;">
    <img src="https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/smolagents/mascot.png" alt="Hugging Face mascot as James Bond" width=100px>
    <p>smolagents - a smol library to build great agents!</p>
  </div>
</h3>

`smolagents` is a library that enables you to run powerful agents in a few lines of code. It offers:

✨ **Simplicity**: the logic for agents fits in ~thousand lines of code (see [agents.py](https://github.com/huggingface/smolagents/blob/main/src/smolagents/agents.py)). We kept abstractions to their minimal shape above raw code!

🧑‍💻 **First-class support for Code Agents**. Our [`CodeAgent`](https://huggingface.co/docs/smolagents/reference/agents#smolagents.CodeAgent) writes its actions in code (as opposed to "agents being used to write code"). To make it secure, we support executing in sandboxed environments via [E2B](https://e2b.dev/).

🤗 **Hub integrations**: you can [share/pull tools to/from the Hub](https://huggingface.co/docs/smolagents/reference/tools#smolagents.Tool.from_hub), and more is to come!

🌐 **Support for any LLM**: it supports models hosted on the Hub loaded in their `transformers` version or through our inference API, but also supports models from OpenAI, Anthropic and many others via our [LiteLLM](https://www.litellm.ai/) integration.
- 👁️ We even support vision models! Leverage this to build a web-browsing agent in [this tutorial](https://huggingface.co/docs/smolagents/examples/web_browser).

🛠️ **Support for a wide range of tools**: you can use tools from [LangChain](https://huggingface.co/docs/smolagents/reference/tools#smolagents.Tool.from_langchain), [Anthropic's MCP](https://huggingface.co/docs/smolagents/reference/tools#smolagents.ToolCollection.from_mcp), you can even use a [Hub Space](https://huggingface.co/docs/smolagents/reference/tools#smolagents.Tool.from_space) as a tool.

Full documentation can be found [here](https://huggingface.co/docs/smolagents/index).

> [!NOTE]
> Check the our [launch blog post](https://huggingface.co/blog/smolagents) to learn more about `smolagents`!

## Table of Contents
- [Introduction](#introduction)
- [Quick Demo](#quick-demo)
- [Command Line Interface](#command-line-interface)
- [Code Agents](#code-agents)
- [How Smol is it Really?](#how-smol-is-it-really)
- [How Strong are Open Models for Agentic Workflows?](#how-strong-are-open-models-for-agentic-workflows)
- [Contributing](#contributing)
- [Citing smolagents](#citing-smolagents)

## Quick demo

First install the package.
```bash
pip install smolagents
```
Then define your agent, give it the tools it needs and run it!
```py
from smolagents import CodeAgent, DuckDuckGoSearchTool, HfApiModel

mdoel = HfApiModel()
agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=model)

agent.run("How many seconds would it take for a leopard at full speed to run through Pont des Arts?")
```

https://github.com/user-attachments/assets/cd0226e2-7479-4102-aea0-57c22ca47884

Our library is LLM-agnostic: you could switch the example above to any inference provider.

<details>
<summary> <b>HfApiModel, gateway for 4 inference providers</b></summary>

```py
from smolagents import HfApiModel

model = HfApiModel(
    model_id="deepseek-ai/DeepSeek-R1",
    provider="together",
)
```
</details>
<details>
<summary> <b>LiteLLM for 100+ LLMs</b></summary>

```py
from smolagents import LiteLLMModel

model = LiteLLMModel(
    "anthropic/claude-3-5-sonnet-latest",
    temperature=0.2,
    max_tokens=10
)
```
</details>
<details>
<summary> <b>OpenAI-compatible servers</b></summary>

```py
import os
from smolagents import OpenAIServerModel

model = OpenAIServerModel(
    model_id="deepseek-ai/DeepSeek-R1",
    api_base="https://api.together.xyz/v1/", # Leave this blank to query OpenAI servers.
    api_key=os.environ["TOGETHER_API_KEY"], # Switch to the API key for the server you're targeting.
)
```
</details>
<details>
<summary> <b>Local `transformers` model</b></summary>

```py
from smolagents import TransformersModel

model = TransformersModel(
    model_id="Qwen/Qwen2.5-Coder-32B-Instruct",
    max_new_tokens=4096,
    device_map="auto"
)
```
</details>
<details>
<summary> <b>Azure models</b></summary>

```py
import os
from smolagents import AzureOpenAIServerModel

model = AzureOpenAIServerModel(
    model_id = os.environ.get("AZURE_OPENAI_MODEL"),
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    api_version=os.environ.get("OPENAI_API_VERSION")    
)
```
</details>

## Command Line Interface

You can accomplish multi-step agentic tasks using two commands: `smolagent` and `webagent`. `smolagent` is a more generalist command to run a multi-step `CodeAgent` that can be equipped with various tools, meanwhile `webagent` is an agent equipped with web browsing tools using [helium](https://github.com/helium).

**Web Browser Agent in CLI**

`webagent` allows users to automate web browsing tasks. It uses the Helium library to interact with web pages and uses defined tools to browse the web. Read more about it [here](https://github.com/huggingface/smolagents/blob/main/src/smolagents/vision_web_browser.py).

Run the following command to get started:
```bash
webagent {YOUR_PROMPT_HERE} --model "LiteLLMModel" --model-id "gpt-4o"
```

For instance:
```bash
webagent --prompt "go to xyz.com/women, get to sale section, click the first clothing item you see. Get the product details, and the price, return them. note that I'm shopping from France"
```
We redacted the website here, modify it with website of your choice.

**CodeAgent in CLI**

You can run `smolagent` command to run a multi-step agent with [tools](https://huggingface.co/docs/smolagents/en/reference/tools). It uses web search tool by default.
You can easily get started with `$ smolagent {YOUR_PROMPT_HERE}`. A more custom version of this one-liner is following, see more details [here](https://github.com/huggingface/smolagents/blob/main/src/smolagents/cli.py).

```bash
smolagent {YOUR_PROMPT_HERE} --model-type "HfApiModel" --model-id "Qwen/Qwen2.5-Coder-32B-Instruct" --imports "pandas numpy" --tools "web_search translation"
```

For instance:
```bash
smolagent "Plan a trip to Tokyo, Kyoto and Osaka between Mar 28 and Apr 7. Allocate time according to number of public attraction in each, and optimize for distance and travel time. Bring all the public transportation options."
``` 

## Code agents?

In our [`CodeAgent`](https://huggingface.co/docs/smolagents/reference/agents#smolagents.CodeAgent),  the LLM engine writes its actions in code. This approach is demonstrated to work better than the current industry practice of letting the LLM output a dictionary of the tools it wants to calls: [uses 30% fewer steps](https://huggingface.co/papers/2402.01030) (thus 30% fewer LLM calls) and [reaches higher performance on difficult benchmarks](https://huggingface.co/papers/2411.01747). Head to [our high-level intro to agents](https://huggingface.co/docs/smolagents/conceptual_guides/intro_agents) to learn more on that.

Especially, since code execution can be a security concern (arbitrary code execution!), we provide options at runtime:
  - a secure python interpreter to run code more safely in your environment (more secure than raw code execution but still risky)
  - a sandboxed environment using [E2B](https://e2b.dev/) (removes the risk to your own system).

On top of this [`CodeAgent`](https://huggingface.co/docs/smolagents/reference/agents#smolagents.CodeAgent) class, we still support the standard [`ToolCallingAgent`](https://huggingface.co/docs/smolagents/reference/agents#smolagents.ToolCallingAgent) that writes actions as JSON/text blobs. But we recommend always using `CodeAgent`.

## How smol is this library?

We strived to keep abstractions to a strict minimum: the main code in `agents.py` has <1,000 lines of code.
Still, we implement several types of agents: `CodeAgent` writes its actions as Python code snippets, and the more classic `ToolCallingAgent` leverages built-in tool calling methods. We also have multi-agent hierarchies, import from tool collections, remote code execution, vision models...

By the way, why use a framework at all? Well, because a big part of this stuff is non-trivial. For instance, the code agent has to keep a consistent format for code throughout its system prompt, its parser, the execution. So our framework handles this complexity for you. But of course we still encourage you to hack into the source code and use only the bits that you need, to the exclusion of everything else!

## How strong are open models for agentic workflows?

We've created [`CodeAgent`](https://huggingface.co/docs/smolagents/reference/agents#smolagents.CodeAgent) instances with some leading models, and compared them on [this benchmark](https://huggingface.co/datasets/m-ric/agents_medium_benchmark_2) that gathers questions from a few different benchmarks to propose a varied blend of challenges.

[Find the benchmarking code here](https://github.com/huggingface/smolagents/blob/main/examples/benchmark.ipynb) for more detail on the agentic setup used, and see a comparison of using LLMs code agents compared to vanilla (spoilers: code agents works better).

<p align="center">
    <img src="https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/smolagents/benchmark_code_agents.jpeg" alt="benchmark of different models on agentic workflows. Open model DeepSeek-R1 beats closed-source models." width=60%>
</p>

This comparison shows that open-source models can now take on the best closed models!

<details>
<summary> <h2>Contribute</h2></summary>

To contribute, follow our [contribution guide](https://github.com/huggingface/smolagents/blob/main/CONTRIBUTING.md).

At any moment, feel welcome to open an issue, citing your exact error traces and package versions if it's a bug.
It's often even better to open a PR with your proposed fixes/changes!

To install dev dependencies, run:
```
pip install -e ".[dev]"
```

When making changes to the codebase, please check that it follows the repo's code quality requirements by running:
To check code quality of the source code:
```
make quality
```

If the checks fail, you can run the formatter with:
```
make style
```

And commit the changes.

To run tests locally, run this command:
```bash
make test
```
</details>

## Citing smolagents

If you use `smolagents` in your publication, please cite it by using the following BibTeX entry.

```bibtex
@Misc{smolagents,
  title =        {`smolagents`: a smol library to build great agentic systems.},
  author =       {Aymeric Roucher and Albert Villanova del Moral and Thomas Wolf and Leandro von Werra and Erik Kaunismäki},
  howpublished = {\url{https://github.com/huggingface/smolagents}},
  year =         {2025}
}
```
