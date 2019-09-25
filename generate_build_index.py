
import argparse
import json
import os
import os.path
import subprocess
import sys
import shutil

import logging

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

def main():

    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Generate UE4 build index')
    parser.add_argument('ue4_base_directory', metavar='directory', type=str, help='UE4 base directory')
    parser.add_argument('output_directory', metavar='directory', type=str, help='Output directory')
    parser.add_argument('platform', metavar='platform', type=str, help='Build platofrm (Win64 etc)')
    parser.add_argument('configuration', metavar='configuration', type=str, help='Build configuration (Development etc)')
    parser.add_argument('target', metavar='target', type=str, help='Build target (UE4Editor etc)')
    args = parser.parse_args()

    generate_build_index(args.ue4_base_directory, args.platform, args.configuration, args.target, args.output_directory)

if __name__=='__main__':
    main()