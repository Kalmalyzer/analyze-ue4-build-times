import logging
import os
import os.path
import subprocess
import shutil

logger = logging.getLogger(__name__)

def generate_build_index(base_dir, platform, configuration, target, output_dir):
    logger.info("Running UBT to generate build index...")
    ubt = os.path.join(base_dir, 'Engine/Binaries/DotNET/UnrealBuildTool.exe')
    subprocess.check_call([ubt, platform, configuration, target, '-Mode=JsonExport'])

    logger.info("Copying build index...")
    ubt_build_manifest = os.path.join(base_dir, 'Engine', 'Binaries', platform, '%s.json' % (target,))
    output_dir_for_json = os.path.join(output_dir, platform, configuration, target)
    os.makedirs(output_dir_for_json, exist_ok=True)
    shutil.copyfile(ubt_build_manifest, os.path.join(output_dir_for_json, '%s.json' % (target,)))
