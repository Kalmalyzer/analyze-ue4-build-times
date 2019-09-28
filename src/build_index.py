import logging
import os
import os.path
import subprocess
import shutil

logger = logging.getLogger(__name__)

def generate_build_index(base_dir, platform, configuration, target, output_dir, pch):

    json_name = '%s.json' % (target,)
    actions_name = 'Actions.json'

    output_dir_for_files = os.path.join(output_dir, platform, configuration, target)
    os.makedirs(output_dir_for_files, exist_ok=True)

    logger.info("Running UBT to generate build index...")
    ubt = os.path.join(base_dir, 'Engine/Binaries/DotNET/UnrealBuildTool.exe')
    subprocess.check_call([ubt, platform, configuration, target, '' if pch else '-NoPCH', '-Mode=JsonExport'])

    logger.info("Copying build index...")
    ubt_build_manifest = os.path.join(base_dir, 'Engine', 'Binaries', platform, json_name)
    shutil.copyfile(ubt_build_manifest, os.path.join(output_dir_for_files, json_name))

    logger.info("Running UBT to generate actions...")
    ubt = os.path.join(base_dir, 'Engine/Binaries/DotNET/UnrealBuildTool.exe')
    subprocess.check_call([ubt, platform, configuration, target, '' if pch else '-NoPCH', '-Mode=Build', '-SkipBuild', '-WriteActions=%s' % (actions_name,)])

    logger.info("Copying actions...")
    actions_source_name = os.path.join(base_dir, 'Engine', 'Source', actions_name)
    shutil.copyfile(actions_source_name, os.path.join(output_dir_for_files, actions_name))
