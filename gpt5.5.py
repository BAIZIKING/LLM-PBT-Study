"""
This file generates the PBT tests using ChatGPT 5.5
Using both 1-stage and 2-stage approaches
full responses for 1-stage stored in "gpt5.5 responses" folder
full responses for 2-stage stored in "gpt 5.5 2-stage responses" folder
actual python test cases stored in proptests/gpt-5.5/
I modified the folder names to be consistent
"""

import os
import re
import sys
from pathlib import Path
from openai import OpenAI
from extract_prompt import build_pbt_prompt, build_properties_prompt, build_pbt_properties_prompt
from prompts import SYSTEM_PROMPT

client = OpenAI(
  api_key=os.environ["OPENAI_API_KEY"]
)

def extract_code(response: str) -> str | None:
    match = re.search(r"```python\n(.*?)```", response, re.DOTALL)
    return match.group(1).strip() if match else None


def generate_pbt(function_name: str, iteration: int) -> str | None:
    prompt = build_pbt_prompt(function_name)
    response = client.responses.create(
        model="gpt-5.5",
        instructions=SYSTEM_PROMPT,
        input=prompt,
    )
    text = response.output_text
    stem = function_name.replace(".", "_")

    responses_dir = Path("responses/gpt5.5 responses")
    responses_dir.mkdir(exist_ok=True)
    (responses_dir / f"{stem}_response {iteration}.txt").write_text(text, encoding="utf-8")

    code = extract_code(text)
    if code:
        out_dir = Path(f"proptests/gpt-5.5/{stem}/single_stage")
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"pbt_{iteration}.py").write_text(code, encoding="utf-8")

    return code


def generate_two_stage_pbt(function_name: str, iteration: int) -> str | None:
    stem = function_name.replace(".", "_")
    responses_dir = Path("responses/gpt 5.5 2-stage responses")
    responses_dir.mkdir(exist_ok=True)

    response1 = client.responses.create(
        model="gpt-5.5",
        instructions=SYSTEM_PROMPT,
        input=build_properties_prompt(function_name),
    )
    text1 = response1.output_text
    (responses_dir / f"{stem}_response1 {iteration}.txt").write_text(text1, encoding="utf-8")

    response2 = client.responses.create(
        model="gpt-5.5",
        instructions=SYSTEM_PROMPT,
        input=build_pbt_properties_prompt(function_name),
        previous_response_id=response1.id,
    )
    text2 = response2.output_text
    (responses_dir / f"{stem}_response2 {iteration}.txt").write_text(text2, encoding="utf-8")

    code = extract_code(text2)
    if code:
        out_dir = Path(f"proptests/gpt-5.5/{stem}/two_stage")
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"pbt_{iteration}.py").write_text(code, encoding="utf-8")

    return code


API_DOCS_DIR = Path(__file__).parent / "api_docs"


def get_all_function_names() -> list[str]:
    return [p.stem.replace("_", ".", 1) for p in sorted(API_DOCS_DIR.glob("*.txt"))]


def run_all(confirm: bool = True) -> None:
    functions = get_all_function_names()
    print(f"Found {len(functions)} functions: {', '.join(functions)}\n")
    for idx, function_name in enumerate(functions, 1):
        print(f"[{idx}/{len(functions)}] Running {function_name}...")
        stem = function_name.replace(".", "_")
        for i in range(1, 6):
            response_file = Path("gpt5.5 responses") / f"{stem}_response {i}.txt"
            if response_file.exists():
                print(f"  [single] Iteration {i}/5 already exists, skipping.")
            else:
                print(f"  [single] Iteration {i}/5...")
                generate_pbt(function_name, i)

        for i in range(1, 6):
            response_file = Path("gpt 5.5 2-stage responses") / f"{stem}_response2 {i}.txt"
            if response_file.exists():
                print(f"  [two-stage] Iteration {i}/5 already exists, skipping.")
            else:
                print(f"  [two-stage] Iteration {i}/5...")
                generate_two_stage_pbt(function_name, i)
        print(f"Done with {function_name}.")
        if confirm and idx < len(functions):
            answer = input(f"Move on to {functions[idx]}? [y/n/all]: ").strip().lower()
            if answer == "all":
                confirm = False
            elif answer != "y":
                print("Stopping.")
                break


if __name__ == "__main__":
    if len(sys.argv) == 1:
        run_all()
    elif len(sys.argv) == 2 and sys.argv[1] == "--no-confirm":
        run_all(confirm=False)
    elif len(sys.argv) == 2:
        function_name = sys.argv[1]
        for i in range(1, 6):
            print(f"Running iteration {i}/5...")
            generate_pbt(function_name, i)
    else:
        print("Usage: python gpt5.5.py [<function_name>|--no-confirm]")
        print("  No argument: run all functions with confirmation between each")
        print("  --no-confirm: run all functions without confirmation")
        print("  <function_name>: run a single function, e.g. numpy.sum")
        sys.exit(1)
