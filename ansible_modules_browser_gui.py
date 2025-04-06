#!/usr/bin/env python

import json
import os
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox

CACHE_FILE = "ansible_windows_modules.json"

def load_modules():
    if not os.path.exists(CACHE_FILE):
        messagebox.showerror("Error", f"Module cache file not found: {CACHE_FILE}")
        return {}
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

class ModuleBrowserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ansible Module Browser")
        self.root.geometry("900x600")
        self.modules = load_modules()
        self.filtered_modules = []

        self.create_widgets()
        self.populate_list()

    def create_widgets(self):
        self.search_var = tk.StringVar()
        search_frame = ttk.Frame(self.root)
        search_frame.pack(padx=10, pady=10, fill=tk.X)

        tk.Label(search_frame, text="Search Modules:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.populate_list())

        self.module_list = tk.Listbox(self.root, height=25)
        self.module_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.module_list.bind("<<ListboxSelect>>", self.show_details)

        self.details_text = tk.Text(self.root, height=10, wrap="word")
        self.details_text.pack(fill=tk.BOTH, expand=False, padx=10, pady=5)

    def populate_list(self):
        keyword = self.search_var.get().lower()
        self.module_list.delete(0, tk.END)
        self.filtered_modules.clear()

        for collection, items in self.modules.items():
            for item in items:
                if keyword in item["name"].lower() or keyword in item["description"].lower():
                    display_name = f"[{collection}] {item['name']}"
                    self.module_list.insert(tk.END, display_name)
                    self.filtered_modules.append(item)

    def show_details(self, event):
        selection = self.module_list.curselection()
        if not selection:
            return
        index = selection[0]
        module = self.filtered_modules[index]
        self.details_text.delete("1.0", tk.END)

        self.details_text.insert(tk.END, f"Module: {module['name']}\n")
        self.details_text.insert(tk.END, f"Description: {module['description']}\n\n")
        self.details_text.insert(tk.END, f"Docs URL: {module['url']}\n")
        self.details_text.insert(tk.END, "Click to open in browser.")
        self.details_text.tag_add("url", "4.11", "4.end")
        self.details_text.tag_config("url", foreground="blue", underline=True)
        self.details_text.tag_bind("url", "<Button-1>", lambda e: webbrowser.open(module['url']))

if __name__ == "__main__":
    root = tk.Tk()
    app = ModuleBrowserApp(root)
    root.mainloop()
