#!/usr/bin/env python

import os
import subprocess
import questionary
import shutil
import re
import datetime
from prompt_toolkit.styles import Style
from ansible_toolkit_extended import generate_playbook, generate_dynamic_inventory

ascii_logo = r"""
        ⚔️  ANSIBLE TOOLKIT CLI TO SEARCH FOR WINDOWS MODULE
              ~ “Created because Ken is too lazy” ~
"""

# 💅 Optional: unified style
custom_style = Style.from_dict({
    "qmark": "#00d787 bold",
    "question": "bold",
    "answer": "#00d787 bold",
    "pointer": "#00d787 bold",
    "highlighted": "#00d787 bold",
    "selected": "#00d787 bold",
})

# 🚀 Menu function
def show_menu():
    print(ascii_logo)
    while True:
        choice = questionary.select(
            "📘 Select a tool to use:",
            choices=[
                "1. Update Module Cache",
                "2. Search & Copy Module Snippet",
                "3. Clean & Validate YAML Files",
		"4. Generate Service Playbook",
		"5. Generate Dynamic Inventory",
                "6. Exit",
            ],
            style=custom_style
        ).ask()

        if choice.startswith("1"):
            run_update_module_cache()
        elif choice.startswith("2"):
            run_snippet_search_tool()
        elif choice.startswith("3"):
            run_yaml_cleaner_tool()
        elif choice.startswith("4"):
            generate_playbook()
        elif choice.startswith("5"):
            generate_dynamic_inventory()
        elif choice.startswith("6"):
            print("👋 Exiting. See you again!")
            break

# 🛠 Tool 1
def run_update_module_cache():
    print("\n🔄 Updating module cache...")
    subprocess.run(["python", "fetch_modules.py"])

# 🛠 Tool 2
def run_snippet_search_tool():
    print("\n🔍 Launching module snippet search...")
    subprocess.run(["python", "ansible_snippet_menu.py"])

# 🛠 Tool 3 (p

def run_yaml_cleaner_tool():
    path = questionary.path("📁 Enter directory to scan for YAML playbooks:", only_directories=True).ask()

    if not path or not os.path.isdir(path):
        print("❌ Invalid directory.")
        return

    print(f"\n🔍 Scanning '{path}' for .yml and .yaml files...\n")

    yaml_files = []
    for root, _, files in os.walk(path):
        for f in files:
            if f.endswith((".yml", ".yaml")):
                yaml_files.append(os.path.join(root, f))

    if not yaml_files:
        print("⚠️ No YAML files found.")
        return

    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    report_lines = [f"# YAML Validation Report - {timestamp}\n"]

    for file in yaml_files:
        print(f"🧹 Cleaning + validating: {file}")
        report_lines.append(f"\n## {file}")

        # 📦 Step 1: Backup original file
        backup_path = file + ".bak"
        try:
            shutil.copy(file, backup_path)
            print(f"   💾 Backup created: {backup_path}")
            report_lines.append(f"- Backup created: {backup_path}")
        except Exception as e:
            print(f"   ❌ Backup failed: {e}")
            report_lines.append(f"- ❌ Backup failed: {e}")

        # ✅ Step 2: yamllint (if available)
        if shutil.which("yamllint"):
            result = subprocess.run(["yamllint", file], capture_output=True, text=True)
            if result.returncode == 0:
                print("   ✅ yamllint passed.")
                report_lines.append("- ✅ yamllint passed.")
            else:
                print("   ⚠️ yamllint issues:\n" + result.stdout)
                report_lines.append("- ⚠️ yamllint issues:\n" + result.stdout)
        else:
            print("   ⚠️ yamllint not installed.")
            report_lines.append("- ⚠️ yamllint not installed.")

        # ✅ Step 3: Clean formatting
        try:
            with open(file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            cleaned = []
            for line in lines:
                line = line.rstrip().replace("\t", "  ")
                cleaned.append(line)

            with open(file, "w", encoding="utf-8") as f:
                f.write("\n".join(cleaned) + "\n")

            print("   ✅ Formatting cleaned.")
            report_lines.append("- ✅ Formatting cleaned.")
        except Exception as e:
            print(f"   ❌ Cleaning error: {e}")
            report_lines.append(f"- ❌ Cleaning error: {e}")

        # ✅ Step 4: Ansible syntax check
        if shutil.which("ansible-playbook"):
            result = subprocess.run(["ansible-playbook", "--syntax-check", file], capture_output=True, text=True)
            if result.returncode == 0:
                print("   ✅ Syntax check passed.")
                report_lines.append("- ✅ Syntax check passed.")
            else:
                print("   ❌ Syntax check failed:\n" + result.stderr)
                report_lines.append("- ❌ Syntax check failed:\n" + result.stderr)
        else:
            print("   ⚠️ ansible-playbook not found.")
            report_lines.append("- ⚠️ ansible-playbook not found.")

        # ✅ Step 5: ansible-lint (optional)
        if shutil.which("ansible-lint"):
            result = subprocess.run(["ansible-lint", file], capture_output=True, text=True)
            if result.returncode == 0:
                print("   ✅ ansible-lint passed.")
                report_lines.append("- ✅ ansible-lint passed.")
            else:
                print("   ⚠️ ansible-lint issues:\n" + result.stdout)
                report_lines.append("- ⚠️ ansible-lint issues:\n" + result.stdout)
        else:
            print("   ⚠️ ansible-lint not installed.")
            report_lines.append("- ⚠️ ansible-lint not installed.")

    # 📄 Save report
    report_file = f"yaml_validation_report_{timestamp}.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"\n📄 Validation report saved to: {report_file}")

# ✅ Run menu
if __name__ == "__main__":
    try:
        show_menu()
    except KeyboardInterrupt:
        print("\n👋 Exiting.")
