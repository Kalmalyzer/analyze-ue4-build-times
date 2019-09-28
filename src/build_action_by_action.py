import logging
import os.path
import subprocess

from src.build_graph import Module

logger = logging.getLogger(__name__)

def build_action(base_dir, output_dir, platform, configuration, target, pch, action_name):
    logger.info("Running UBT to build %s..." % (action_name,))
    ubt = os.path.join(base_dir, 'Engine/Binaries/DotNET/UnrealBuildTool.exe')
    result = subprocess.run([ubt, platform, configuration, target, '-Mode=Build', '-Actions=%s' % (action_name,), '' if pch else '-NoPCH', '-Verbose'], capture_output=True)

    if result.returncode != 0:
        logger.error("UBT terminated with error code %d. Error output:\n%s" % (result.returncode, result.stderr))

    action_log_name = os.path.join(output_dir, platform, configuration, target, '%s.log' % (action_name,))
    with open(action_log_name, 'wt') as action_log:
        action_log.write(result.stdout)
    logger.info("Written output to %s" % (action_log_name,))

def build_module(base_dir, output_dir, platform, configuration, target, pch, module):
    if module.type == Module.Type.CPlusPlus:
        action_name = "Module.%s.*cpp" % (module.name,)
        build_action(base_dir, output_dir, platform, configuration, target, pch, action_name)
    else:
        logger.info("Skipping build of %s since it is an external module" % (module.name,))

def build_import_library(base_dir, output_dir, platform, configuration, target, pch, import_library):
    build_action(base_dir, output_dir, platform, configuration, target, pch, import_library.name)

def build_binary(base_dir, output_dir, platform, configuration, target, pch, binary):
    build_action(base_dir, output_dir, platform, configuration, target, pch, binary.name)

def build_action_by_action(base_dir, output_dir, platform, configuration, target, pch, modules, import_libraries, binaries):

    for module in modules:
        build_module(base_dir, output_dir, platform, configuration, target, pch, module)

    for import_library in import_libraries:
        build_import_library(base_dir, output_dir, platform, configuration, target, pch, import_library)
    
    for binary in binaries:
        build_binary(base_dir, output_dir, platform, configuration, target, pch, binary)
