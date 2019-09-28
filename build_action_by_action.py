import argparse
import json
import logging
import os.path
import sys

from src.build_graph import create_build_graph
from src.build_action_by_action import build_action_by_action

logger = logging.getLogger(__name__)


def load_json_export(base_dir, platform, configuration, target):

    file_name = os.path.join(base_dir, platform, configuration, target, '%s.json' % (target,))
    with open(file_name, 'rt') as file:
        json_export = json.load(file)

    return json_export

def main():

    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Build action by action')
    parser.add_argument('base_dir', metavar='directory', type=str, help='UE4 base directory')
    parser.add_argument('output_dir', metavar='directory', type=str, help='Output directory')
    parser.add_argument('platform', metavar='platform', type=str, help='Build platofrm (Win64 etc)')
    parser.add_argument('configuration', metavar='configuration', type=str, help='Build configuration (Development etc)')
    parser.add_argument('target', metavar='target', type=str, help='Build target (UE4Editor etc)')
    parser.add_argument('pch', metavar='pch', type=bool, default=True, help='Use precompiled headers')
    args = parser.parse_args()

    json_export = load_json_export(args.output_dir, args.platform, args.configuration, args.target)

    (modules, import_libraries, binaries) = create_build_graph(json_export)

    build_action_by_action(args.base_dir, args.output_dir, args.platform, args.configuration, args.target, args.pch, modules, import_libraries, binaries)

if __name__=='__main__':
    main()
