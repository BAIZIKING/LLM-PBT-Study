"""
This file generates the PBT tests using Claude Opus 4.8
Using both 1-stage and 2-stage approaches
full responses for 1-stage stored in "claude responses" folder
full responses for 2-stage stored in "opus 4.8 2-stage responses" folder
actual python test cases stored in proptests/claude-4.8-opus/<function_name>
I modified the folder names to be consistent
"""


import re
import sys
from pathlib import Path
import anthropic
from extract_prompt import build_pbt_prompt, build_properties_prompt, build_pbt_properties_prompt
from prompts import SYSTEM_PROMPT

client = anthropic.Anthropic()


def extract_code(response: str) -> str | None:
    matches = re.findall(r"```python\n(.*?)```", response, re.DOTALL)
    return matches[-1].strip() if matches else None


# 1-stage
def generate_pbt(function_name: str, iteration: int) -> str | None:
    prompt = build_pbt_prompt(function_name)
    message = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    response = message.content[0].text
    stem = function_name.replace(".", "_")

    responses_dir = Path("responses/claude4.8 responses")
    responses_dir.mkdir(exist_ok=True)
    (responses_dir / f"{stem}_response {iteration}.txt").write_text(response, encoding="utf-8")

    code = extract_code(response)
    if code:
        out_dir = Path(f"proptests/claude-4.8-opus/{stem}/single_stage")
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"pbt_{iteration}.py").write_text(code, encoding="utf-8")

    return code


def generate_two_stage_pbt(function_name: str, iteration: int) -> str | None:
    stem = function_name.replace(".", "_")
    responses_dir = Path("responses/opus 4.8 2-stage responses")
    responses_dir.mkdir(exist_ok=True)

    prompt1 = build_properties_prompt(function_name)
    messages = [{"role": "user", "content": prompt1}]
    message1 = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    response1 = message1.content[0].text
    (responses_dir / f"{stem}_response1 {iteration}.txt").write_text(response1, encoding="utf-8")

    messages += [
        {"role": "assistant", "content": response1},
        {"role": "user", "content": build_pbt_properties_prompt(function_name)},
    ]
    message2 = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    response2 = message2.content[0].text
    (responses_dir / f"{stem}_response2 {iteration}.txt").write_text(response2, encoding="utf-8")

    code = extract_code(response2)
    if code:
        out_dir = Path(f"proptests/claude-4.8-opus/{stem}/two_stage")
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
            response_file = Path("claude responses") / f"{stem}_response {i}.txt"
            if response_file.exists():
                print(f"  [single] Iteration {i}/5 exists — re-extracting code.")
                code = extract_code(response_file.read_text(encoding="utf-8"))
                if code:
                    out_dir = Path(f"proptests/claude-4.8-opus/{stem}/single_stage")
                    out_dir.mkdir(parents=True, exist_ok=True)
                    (out_dir / f"pbt_{i}.py").write_text(code, encoding="utf-8")
            else:
                print(f"  [single] Iteration {i}/5...")
                generate_pbt(function_name, i)

        for i in range(1, 6):
            response_file = Path("opus 4.8 2-stage responses") / f"{stem}_response2 {i}.txt"
            if response_file.exists():
                print(f"  [two-stage] Iteration {i}/5 exists — re-extracting code.")
                code = extract_code(response_file.read_text(encoding="utf-8"))
                if code:
                    out_dir = Path(f"proptests/claude-4.8-opus/{stem}/two_stage")
                    out_dir.mkdir(parents=True, exist_ok=True)
                    (out_dir / f"pbt_{i}.py").write_text(code, encoding="utf-8")
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
        # runs both 1-stage and 2-stage
        print("Usage: python opus4.8.py [<function_name>|--no-confirm]")
        print("  No argument: run all functions with confirmation between each")
        print("  --no-confirm: run all functions without confirmation")
        print("  <function_name>: run a single function, e.g. numpy.sum")
        sys.exit(1)
