import os.path

from enum import Enum, auto

class Action(object):
    def __init__(self, name):
        self.name = name
        self.dependencies = set()

class Binary(Action):
    def __init__(self, name, json):
        super().__init__(name)
        self.json = json

        self.import_library = None
        self.modules = set()

    def __str__(self):
        return '{ Name: \"%s\", Import library: \"%s\", Modules: {%s}, Dependencies: {%s} }' % (self.name, self.import_library.name if self.import_library else '<None>', ', '.join('\"%s\"' % (binary.name if binary else '<None>',) for binary in self.modules), ', '.join('\"%s\"' % (binary.name if binary else '<None>',) for binary in self.dependencies))

class ImportLibrary(Action):
    def __init__(self, name):
        super().__init__(name)

        self.binary = None
        self.modules = set()

    def __str__(self):
        return '{ Name: \"%s\", Binary: \"%s\", Dependencies: {%s} }' % (self.name, (self.binary.name if self.binary else '<None>'), ', '.join('\"%s\"' % (module.name if module else '<None>',) for module in self.dependencies))

class Module(Action):

    class Type(Enum):
        CPlusPlus = auto()
        External = auto()

    def __init__(self, name, json):
        super().__init__(name)
        self.json = json

        self.private_dependency_modules = set()
        self.public_dependency_modules = set()
        self.binary = None
        self.import_library = None
        self.type = Module.Type[json['Type']]

    def __str__(self):
            return '{ Name: \"%s\", Binary: \"%s\", Dependencies: {%s} }' % (self.name, self.binary.name if self.binary else '<None>', ', '.join('\"%s\"' % (module.name if module else '<None>',) for module in self.dependencies))


def binary_name_to_import_library_name(binary_name):
    return binary_name[0:-4] + '.lib'

def gather_binary_dependencies_for_module_sub(module, modules_processed, dependencies):
    if not module in modules_processed:
        modules_processed.add(module)
        if module.type == Module.Type.CPlusPlus:
            dependencies.add(module.import_library)

def gather_binary_dependencies_for_module(module):

    modules_processed = set()

    binary_dependencies = set()

    for private_dependency_module in module.private_dependency_modules:
        gather_binary_dependencies_for_module_sub(private_dependency_module, modules_processed, binary_dependencies)

    for public_dependency_module in module.public_dependency_modules:
        gather_binary_dependencies_for_module_sub(public_dependency_module, modules_processed, binary_dependencies)

    if module.type == Module.Type.CPlusPlus:
        binary_dependencies.add(module.import_library)

    return binary_dependencies

def gather_binary_dependencies_for_modules(modules):

    dependencies = set()

    for module in modules:
        dependencies.update(gather_binary_dependencies_for_module(module))

    return dependencies


def gather_import_library_dependencies_for_modules(modules):

    dependencies = set()

    for module in modules:
        if module.type == Module.Type.CPlusPlus:
            dependencies.add(module)

    return dependencies

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
        binary_name = os.path.basename(binary_json['File'])
        binary = Binary(binary_name, binary_json)
        binaries.add(binary)
        binary_names_to_binaries[binary_name] = binary

    import_libraries = set()
    import_library_names_to_import_libraries = {}

    for binary_json in json_export['Binaries']:
        binary_name = os.path.basename(binary_json['File'])
        import_library_name = binary_name_to_import_library_name(binary_name)
        import_library = ImportLibrary(import_library_name)
        import_libraries.add(import_library)
        import_library_names_to_import_libraries[import_library_name] = import_library

    # Link binaries to import libraries

    for binary in binaries:
        import_library = import_library_names_to_import_libraries[binary_name_to_import_library_name(binary.name)]
        binary.import_library = import_library
        import_library.binary = binary

    # Link binaries & import libraries to modules

    for binary in binaries:
        import_library = binary.import_library
        for module_name in binary.json['Modules']:
            dependent_module = module_names_to_modules[module_name]
            binary.modules.add(dependent_module)
            if dependent_module.type == Module.Type.CPlusPlus:
                import_library.modules.add(dependent_module)
                dependent_module.binary = binary
                dependent_module.import_library = import_library

    # Link modules to their dependencies

    for module in modules:
        for module_name in module.json['PrivateDependencyModules']:
            module.private_dependency_modules.add(module_names_to_modules[module_name])

        for module_name in module.json['PublicDependencyModules']:
            module.public_dependency_modules.add(module_names_to_modules[module_name])

    # Link import libraries to their dependent modules

    for import_library in import_libraries:
        import_library.dependencies.update(gather_import_library_dependencies_for_modules(import_library.modules))

    # Link binaries to their dependent import libraries

    for binary in binaries:
        binary.dependencies.update(gather_binary_dependencies_for_modules(binary.modules))

    return (modules, import_libraries, binaries)
