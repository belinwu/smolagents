import os
from typing import Optional

import datasets
import pandas as pd
from dotenv import load_dotenv
from huggingface_hub import login
from scripts.mdconvert import MarkdownConverter
from scripts.run_agents import answer_questions
from scripts.text_web_browser import (
    ArchiveSearchTool,
    FinderTool,
    FindNextTool,
    NavigationalSearchTool,
    PageDownTool,
    PageUpTool,
    SearchInformationTool,
    VisitTool,
)
from scripts.visual_qa import VisualQAGPT4Tool, visualizer

from smolagents import CodeAgent, HfApiModel, LiteLLMModel, ManagedAgent, MessageRole, Tool, ToolCallingAgent


load_dotenv(override=True)
login(os.getenv("HF_TOKEN"))

### IMPORTANT: EVALUATION SWITCHES

print("Make sure you deactivated Tailscale VPN, else some URLs will be blocked!")

OUTPUT_DIR = "output"
USE_OPEN_MODELS = False

SET = "validation"

proprietary_model = LiteLLMModel("o1")

websurfer_model = proprietary_model

repo_id_llama3 = "meta-llama/Meta-Llama-3-70B-Instruct"
repo_id_command_r = "CohereForAI/c4ai-command-r-plus"
repo_id_gemma2 = "google/gemma-2-27b-it"
repo_id_llama = "meta-llama/Meta-Llama-3.1-70B-Instruct"

hf_model = HfApiModel(model=repo_id_llama)


### LOAD EVALUATION DATASET

eval_ds = datasets.load_dataset("gaia-benchmark/GAIA", "2023_all")[SET]
eval_ds = eval_ds.rename_columns(
    {"Question": "question", "Final answer": "true_answer", "Level": "task"}
)


def preprocess_file_paths(row):
    if len(row["file_name"]) > 0:
        row["file_name"] = f"data/gaia/{SET}/" + row["file_name"]
    return row


eval_ds = eval_ds.map(preprocess_file_paths)

eval_df = pd.DataFrame(eval_ds)
print("Loaded evaluation dataset:")
print(pd.Series(eval_ds["task"]).value_counts())

### BUILD AGENTS & TOOLS

WEB_TOOLS = [
    SearchInformationTool(),
    NavigationalSearchTool(),
    VisitTool(),
    PageUpTool(),
    PageDownTool(),
    FinderTool(),
    FindNextTool(),
    ArchiveSearchTool(),
]

text_limit = 70000
if USE_OPEN_MODELS:
    text_limit = 20000

class TextInspectorTool(Tool):
    name = "inspect_file_as_text"
    description = """
You cannot load files yourself: instead call this tool to read a file as markdown text and ask questions about it.
This tool handles the following file extensions: [".html", ".htm", ".xlsx", ".pptx", ".wav", ".mp3", ".flac", ".pdf", ".docx"], and all other types of text files. IT DOES NOT HANDLE IMAGES."""

    inputs = {
        "file_path": {
            "description": "The path to the file you want to read as text. Must be a '.something' file, like '.pdf'. If it is an image, use the visualizer tool instead! DO NOT USE THIS TOOL FOR A WEBPAGE: use the search tool instead!",
            "type": "string",
        },
        "question": {
            "description": "[Optional]: Your question, as a natural language sentence. Provide as much context as possible. Do not pass this parameter if you just want to directly return the content of the file.",
            "type": "string",
            "nullable": True
        },
    }
    output_type = "string"
    md_converter = MarkdownConverter()

    def forward_initial_exam_mode(self, file_path, question):
        result = self.md_converter.convert(file_path)

        if file_path[-4:] in ['.png', '.jpg']:
            raise Exception("Cannot use inspect_file_as_text tool with images: use visualizer instead!")

        if ".zip" in file_path:
            return result.text_content

        if not question:
            return result.text_content

        messages = [
            {
                "role": MessageRole.SYSTEM,
                "content": "Here is a file:\n### "
                + str(result.title)
                + "\n\n"
                + result.text_content[:text_limit],
            },
            {
                "role": MessageRole.USER,
                "content": question,
            },
        ]
        return websurfer_model(messages)

    def forward(self, file_path, question: Optional[str] = None) -> str:

        result = self.md_converter.convert(file_path)

        if file_path[-4:] in ['.png', '.jpg']:
            raise Exception("Cannot use inspect_file_as_text tool with images: use visualizer instead!")

        if ".zip" in file_path:
            return result.text_content

        if not question:
            return result.text_content

        messages = [
            {
                "role": MessageRole.SYSTEM,
                "content": "You will have to write a short caption for this file, then answer this question:"
                + question,
            },
            {
                "role": MessageRole.USER,
                "content": "Here is the complete file:\n### "
                + str(result.title)
                + "\n\n"
                + result.text_content[:text_limit],
            },
            {
                "role": MessageRole.USER,
                "content": "Now answer the question below. Use these three headings: '1. Short answer', '2. Extremely detailed answer', '3. Additional Context on the document and question asked'."
                + question,
            },
        ]
        return websurfer_model(messages)


surfer_agent = ToolCallingAgent(
    model=websurfer_model,
    tools=WEB_TOOLS,
    max_steps=10,
    verbosity_level=2,
    # grammar = DEFAULT_JSONAGENT_REGEX_GRAMMAR,
    planning_interval=4,
)


search_agent = ManagedAgent(
    surfer_agent,
    "web_search",
    description="""A team member that will browse the internet to answer your question.
Ask him for all your web-search related questions, but he's unable to do problem-solving.
Provide him as much context as possible, in particular if you need to search on a specific timeframe!
And don't hesitate to provide him with a complex search task, like finding a difference between two webpages.""",
    additional_prompting="""You can navigate to .txt or .pdf online files using your 'visit_page' tool.
If it's another format, you can return the url of the file, and your manager will handle the download and inspection from there.
Additionally, if after some searching you find out that you need more information to answer the question, you can use `final_answer` with your request for clarification as argument to request for more information.""",
    provide_run_summary=True
)

ti_tool = TextInspectorTool()

TASK_SOLVING_TOOLBOX = [
    visualizer,  # VisualQATool(),
    ti_tool,
]


model = hf_model if USE_OPEN_MODELS else proprietary_model

manager_agent = CodeAgent(
    model=model,
    tools=TASK_SOLVING_TOOLBOX,
    max_steps=12,
    verbosity_level=1,
    # grammar=DEFAULT_CODEAGENT_REGEX_GRAMMAR,
    additional_authorized_imports=[
        "requests",
        "zipfile",
        "os",
        "pandas",
        "numpy",
        "sympy",
        "json",
        "bs4",
        "pubchempy",
        "xml",
        "yahoo_finance",
        "Bio",
        "sklearn",
        "scipy",
        "pydub",
        "io",
        "PIL",
        "chess",
        "PyPDF2",
        "pptx",
        "torch",
        "datetime",
        "csv",
        "fractions",
    ],
    planning_interval=4,
    managed_agents=[search_agent]
)

### EVALUATE

results = answer_questions(
    eval_ds,
    manager_agent,
    "code_gpt4o_22-01_managedagent-summary_planning",
    output_folder=f"{OUTPUT_DIR}/{SET}",
    visual_inspection_tool = VisualQAGPT4Tool(),
    text_inspector_tool = ti_tool,
)
