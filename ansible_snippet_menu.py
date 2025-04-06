#!/usr/bin/env python

import json
import os
import requests
import pyperclip
import questionary
from bs4 import BeautifulSoup
from prompt_toolkit.styles import Style

# ✅ Style: No gray background, high contrast green/white
custom_style = Style.from_dict({
    "qmark": "#00d787 bold",
    "question": "bold",
    "answer": "#00d787 bold",
    "pointer": "#00d787 bold",
    "highlighted": "#00d787 bold",
    "selected": "#00d787 bold",
    "separator": "#cc5454",
    "instruction": "#888888 italic",
    "text": "",
    "disabled": "#858585 italic",

    # 🧽 Clean up autocomplete background
    "completion-menu": "bg:default",
    "completion-menu.completion": "fg:#00d787 bg:default",
    "completion-menu.completion.current": "fg:#ffffff bg:default",
})

CACHE_FILE = "ansible_windows_modules.json"

# 🔹 Load from local cache
def load_modules():
    if not os.path.exists(CACHE_FILE):
        print(f"❌ Cache file '{CACHE_FILE}' not found.")
        print("Run your fetcher script first to generate it.")
        exit(1)
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# 🔹 Flatten modules into a searchable list
def get_flat_module_list(modules):
    flat_list = []
    for collection, items in modules.items():
        for item in items:
            flat_list.append({
                "collection": collection,
                "display": f"{item['name']} ({item['description']})",
                "name": item["name"],
                "description": item["description"],
                "url": item["url"]
            })
    return sorted(flat_list, key=lambda x: x["name"].lower())

# 🔹 Scrape example snippet from docs
def fetch_snippet(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # ✅ Find any header where the visible text contains 'Examples'
        examples_header = None
        for tag in soup.find_all(["h2", "h3"]):
            if "examples" in tag.get_text(strip=True).lower():
                examples_header = tag
                break

        if not examples_header:
            return "# No 'Examples' section found."

        # ✅ Traverse forward and collect snippets under that section
        example_blocks = []
        current = examples_header

        for _ in range(20):
            current = current.find_next()
            if not current:
                break
            if current.name in ["h2", "h3"]:
                break  # Stop at next major section
            if current.name == "div" and "highlight" in current.get("class", []):
                pre = current.find("pre")
                if pre:
                    example_blocks.append(pre.get_text())

        if example_blocks:
            return "\n\n".join(example_blocks)

    except Exception as e:
        return f"# Error fetching snippet: {str(e)}"

    return "# No example snippet found."

# 🔹 Main menu
def show_main_menu(modules):
    flat_modules = get_flat_module_list(modules)

    print("\n📘 Welcome to the Ansible Snippet CLI")
    print("🔎 Type to search Ansible modules by name or description.")
    print("📄 After selecting, a usage snippet will be fetched and displayed.")
    print("📋 You can optionally copy it to your clipboard.\n")
    print("🚪 Press Ctrl+C at any time to exit.\n")

    while True:
        selected = questionary.autocomplete(
            "Search module:",
            choices=[m["display"] for m in flat_modules],
            style=custom_style,
            ignore_case=True
        ).ask()

        if not selected:
            print("❌ Cancelled or no input.")
            return

        selected_module = next(
            (m for m in flat_modules if selected.startswith(m["name"])), None
        )

        if not selected_module:
            print("❌ Module not found.")
            continue

        print(f"\n🔍 Fetching snippet for: {selected_module['name']}")
        print(f"🌐 {selected_module['url']}")

        snippet = fetch_snippet(selected_module["url"])
        print("\n📄 Example Snippet:\n")
        print(snippet)

        copy = questionary.confirm("📋 Copy snippet to clipboard?", style=custom_style).ask()
        if copy:
            pyperclip.copy(snippet)
            print("✅ Snippet copied to clipboard!")

        again = questionary.confirm("🔁 Search for another module?", style=custom_style).ask()
        if not again:
            break

# 🔹 Entry point
if __name__ == "__main__":
    try:
        modules = load_modules()
        show_main_menu(modules)
    except KeyboardInterrupt:
        print("\n👋 Exiting...")
