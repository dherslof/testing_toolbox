#!/usr/bin/env python3
"""
YAML/JSON Tree Visualizer

A simple program to visualize YAML/JSON files as interactive tree structures.
Supports both text-based and GUI visualization modes.

Usage:
    python visualizer.py <file_path> [--mode gui|text] [--expand-all]

Dependencies:
    pip install pyyaml tkinter (tkinter usually comes with Python)

Author: dherslof
"""

import json
import yaml
import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Union
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class TreeVisualizer:
    """Main class for visualizing YAML/JSON data structures as trees."""

    def __init__(self):
        self.data = None
        self.file_path = None

    def load_file(self, file_path: str) -> bool:
        try:
            self.file_path = Path(file_path)

            if not self.file_path.exists():
                print(f"Error: File '{file_path}' not found")
                return False

            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Try to parse as JSON first, then YAML
            try:
                self.data = json.loads(content)
                print(f"Loaded as JSON: {self.file_path}")
            except json.JSONDecodeError:
                try:
                    self.data = yaml.safe_load(content)
                    print(f"Loaded as YAML: {self.file_path}")
                except yaml.YAMLError as e:
                    print(f"Error parsing YAML: {e}")
                    return False

            return True

        except Exception as e:
            print(f"Error loading file: {e}")
            return False

    def _format_value(self, value: Any) -> str:
        """Format a value for display in the tree."""
        if isinstance(value, str):
            if len(value) > 50:
                return f'"{value[:47]}..."'
            return f'"{value}"'
        elif isinstance(value, (int, float, bool)):
            return str(value)
        elif value is None:
            return "null"
        elif isinstance(value, (list, dict)):
            count = len(value)
            type_name = "array" if isinstance(value, list) else "object"
            return f"{type_name} ({count} items)"
        else:
            return str(value)

    def print_text_tree(self, expand_all: bool = False):
        """Print a text-based tree representation."""
        if not self.data:
            print("No data loaded")
            return

        print(f"\nTree structure of: {self.file_path}")
        print("=" * 50)
        self._print_node(self.data, "", True, expand_all)

    def _print_node(self, node: Any, prefix: str, is_last: bool, expand_all: bool, depth: int = 0):
        """Recursively print tree nodes."""
        # Limit depth to prevent extremely deep trees
        if depth > 20:
            print(f"{prefix}{'└── ' if is_last else '├── '}... (max depth reached)")
            return

        if isinstance(node, dict):
            items = list(node.items())
            for i, (key, value) in enumerate(items):
                is_last_item = i == len(items) - 1
                current_prefix = "└── " if is_last_item else "├── "

                if isinstance(value, (dict, list)) and value:
                    print(f"{prefix}{current_prefix}{key}: {self._format_value(value)}")
                    next_prefix = prefix + ("    " if is_last_item else "│   ")
                    # Auto-expand first 2 levels
                    if expand_all or depth < 2:
                        self._print_node(value, next_prefix, True, expand_all, depth + 1)
                else:
                    print(f"{prefix}{current_prefix}{key}: {self._format_value(value)}")

        elif isinstance(node, list):
            for i, item in enumerate(node):
                is_last_item = i == len(node) - 1
                current_prefix = "└── " if is_last_item else "├── "

                if isinstance(item, (dict, list)) and item:
                    print(f"{prefix}{current_prefix}[{i}]: {self._format_value(item)}")
                    next_prefix = prefix + ("    " if is_last_item else "│   ")
                    if expand_all or depth < 2:
                        self._print_node(item, next_prefix, True, expand_all, depth + 1)
                else:
                    print(f"{prefix}{current_prefix}[{i}]: {self._format_value(item)}")


class TreeVisualizerGUI:
    """GUI version of the tree visualizer using tkinter."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("JSON/YAML Tree Visualizer")
        self.root.geometry("800x600")

        self.visualizer = TreeVisualizer()
        self.setup_ui()

    def setup_ui(self):
        """Setup the GUI interface."""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open...", command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # File info frame
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(info_frame, text="Open File", command=self.open_file).pack(side=tk.LEFT)
        self.file_label = ttk.Label(info_frame, text="No file loaded")
        self.file_label.pack(side=tk.LEFT, padx=(10, 0))

        # Tree frame with scrollbar
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview with scrollbars
        self.tree = ttk.Treeview(tree_frame)

        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)

        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Configure treeview columns
        self.tree["columns"] = ("value", "type")
        self.tree.column("#0", width=300, minwidth=200)
        self.tree.column("value", width=300, minwidth=200)
        self.tree.column("type", width=100, minwidth=80)

        self.tree.heading("#0", text="Key/Index", anchor=tk.W)
        self.tree.heading("value", text="Value", anchor=tk.W)
        self.tree.heading("type", text="Type", anchor=tk.W)

    def open_file(self):
        """Open and load a file."""
        file_path = filedialog.askopenfilename(
            title="Select JSON or YAML file",
            filetypes=[
                ("JSON files", "*.json"),
                ("YAML files", "*.yml *.yaml"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            if self.visualizer.load_file(file_path):
                self.file_label.config(text=f"Loaded: {Path(file_path).name}")
                self.populate_tree()
            else:
                messagebox.showerror("Error", "Failed to load file")

    def populate_tree(self):
        """Populate the treeview with data."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not self.visualizer.data:
            return

        # Add root node
        root_type = "object" if isinstance(self.visualizer.data, dict) else "array"
        root_id = self.tree.insert("", "end", text="root", values=("", root_type))

        # Populate tree recursively
        self._populate_node(root_id, self.visualizer.data)

        # Expand root node
        self.tree.item(root_id, open=True)

    def _populate_node(self, parent_id: str, data: Any):
        """Recursively populate tree nodes."""
        if isinstance(data, dict):
            for key, value in data.items():
                value_str = self.visualizer._format_value(value)
                value_type = type(value).__name__

                node_id = self.tree.insert(parent_id, "end", text=str(key), 
                                         values=(value_str, value_type))

                if isinstance(value, (dict, list)) and value:
                    self._populate_node(node_id, value)

        elif isinstance(data, list):
            for i, item in enumerate(data):
                value_str = self.visualizer._format_value(item)
                value_type = type(item).__name__

                node_id = self.tree.insert(parent_id, "end", text=f"[{i}]", 
                                         values=(value_str, value_type))

                if isinstance(item, (dict, list)) and item:
                    self._populate_node(node_id, item)

    def run(self):
        """Start the GUI application."""
        self.root.mainloop()


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(description="Visualize YAML/JSON files as trees")
    parser.add_argument("file", nargs="?", help="Path to YAML or JSON file")
    parser.add_argument("--mode", choices=["gui", "text"], default="gui",
                       help="Visualization mode (default: gui)")
    parser.add_argument("--expand-all", action="store_true",
                       help="Expand all nodes in text mode")

    args = parser.parse_args()

    if args.mode == "gui":
        # GUI mode
        app = TreeVisualizerGUI()
        if args.file:
            if app.visualizer.load_file(args.file):
                app.file_label.config(text=f"Loaded: {Path(args.file).name}")
                app.populate_tree()
        app.run()

    else:
        # Text mode
        if not args.file:
            print("Error: File path required for text mode")
            sys.exit(1)

        visualizer = TreeVisualizer()
        if visualizer.load_file(args.file):
            visualizer.print_text_tree(args.expand_all)
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()