
import argparse
import json
import os.path
import sys

import logging

logger = logging.getLogger(__name__)


class Binary(object):
    def __init__(self, name, json):
        self.name = name
        self.json = json

        self.dependent_binary_import_libraries = set()
        self.modules = set()

    def __str__(self):
#        return '{ Name: \"%s\", Dependent import libraries: %d, Modules: %d' % (self.name, len(self.dependent_binary_import_libraries), len(self.modules))
        return '{ Name: \"%s\", Dependent import libraries: {%s}, Modules: {%s}' % (self.name, ', '.join('\"%s\"' % (binary.name,) for binary in self.dependent_binary_import_libraries), ', '.join('\"%s\"' % (module.name,) for module in self.modules))

class Module(object):
    def __init__(self, name, json):
        self.name = name
        self.json = json

        self.private_dependency_modules = set()
        self.public_dependency_modules = set()
        self.binary = None

def gather_binary_dependencies_for_module_recursive(module, modules_processed, binary_dependencies):
    if not module in modules_processed:
        modules_processed.add(module)

        binary_dependencies.add(module.binary)

        for public_dependency_module in module.public_dependency_modules:
            gather_binary_dependencies_for_module_recursive(public_dependency_module, modules_processed, binary_dependencies)

def gather_binary_dependencies_for_module(module):

    modules_processed = set()

    binary_dependencies = set()

    for private_dependency_module in module.private_dependency_modules:
        gather_binary_dependencies_for_module_recursive(private_dependency_module, modules_processed, binary_dependencies)

# Why does the 'UE4Editor-Core' module appear after scanning the private dependency modules?
    if module.name == "Core":
        print(', '.join(str(x) for x in binary_dependencies))

    for public_dependency_module in module.public_dependency_modules:
        gather_binary_dependencies_for_module_recursive(public_dependency_module, modules_processed, binary_dependencies)

    if module.name == "Core":
        print(', '.join(str(x) for x in binary_dependencies))

    return binary_dependencies

def create_build_graph(json_export):

    modules = set()
    module_names_to_modules = {}

    for module_key, module_value in json_export['Modules'].items():
        module = Module(module_key, module_value)
        modules.add(module)
        module_names_to_modules[module_key] = module

    binaries = set()
    binary_names_to_binaries = {}

    for binary_json in json_export['Binaries']:
        binary = Binary(binary_json['File'], binary_json)
        binaries.add(binary)
        binary_names_to_binaries[binary_json['File']] = binary

    # Link binaries to modules

    for binary in binaries:
        for module_name in binary.json['Modules']:
            dependent_module = module_names_to_modules[module_name]
            binary.modules.add(dependent_module)
            dependent_module.binary = binary

    # Link modules to their dependencies

    for module in modules:
        for module_name in module.json['PrivateDependencyModules']:
            module.private_dependency_modules.add(module_names_to_modules[module_name])

        for module_name in module.json['PublicDependencyModules']:
            module.public_dependency_modules.add(module_names_to_modules[module_name])

    # Link binaries to their dependent binaries

    for binary in binaries:
        for module in binary.modules:
            binary.dependent_binary_import_libraries.update(gather_binary_dependencies_for_module(module))

    return binaries

def can_binary_be_built(processed_binaries, remaining_binaries, binary):
    return binary.dependent_binary_import_libraries.isdisjoint(remaining_binaries)

def find_next_binary_to_build(processed_binaries, remaining_binaries):

    for binary in remaining_binaries:
        if (can_binary_be_built(processed_binaries, remaining_binaries, binary)):
            return binary

    return None

def simulate_build(json_export):

    build_graph = create_build_graph(json_export)

    # for binary in build_graph:
    #     if ("Core" in binary.name):
    #         print(binary)

    processed_binaries = set()
    remaining_binaries = build_graph.copy()

    while len(remaining_binaries) > 0:

        binary = find_next_binary_to_build(processed_binaries, remaining_binaries)

        logger.info("Building binary %s" % binary.name)

        remaining_binaries.remove(binary)
        processed_binaries.add(binary)

        

def load_json_export(base_dir, platform, configuration, target):

    file_name = os.path.join(base_dir, platform, configuration, target, '%s.json' % (target,))
    with open(file_name, 'rt') as file:
        json_export = json.load(file)

    return json_export

def main():

    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Analyze UE4 build results')
    parser.add_argument('base_dir', metavar='directory', type=str, help='Base directory')
    parser.add_argument('platform', metavar='platform', type=str, help='Build platofrm (Win64 etc)')
    parser.add_argument('configuration', metavar='configuration', type=str, help='Build configuration (Development etc)')
    parser.add_argument('target', metavar='target', type=str, help='Build target (UE4Editor etc)')
    args = parser.parse_args()

    json_export = load_json_export(args.base_dir, args.platform, args.configuration, args.target)

    simulate_build(json_export)

if __name__=='__main__':
    main()