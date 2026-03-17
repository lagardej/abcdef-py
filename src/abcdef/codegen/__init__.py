"""ABCDEF Codegen — scaffolding tool for modules and features.

Generates boilerplate directory trees and stub files for abcdef applications.

Public API:

    generate_module(name, module_type, root)  -- scaffold a new module
    generate_feature(module_name, use_case_name, root)  -- add a use case

CLI entry point (after install):

    abcdef-gen module <name> --type command|query [--root PATH]
    abcdef-gen feature <module> <use-case> [--root PATH]
"""

from abcdef.codegen.generator import generate_feature, generate_module

__all__ = [
    "generate_feature",
    "generate_module",
]
