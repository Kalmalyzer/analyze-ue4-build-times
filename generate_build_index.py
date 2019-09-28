
import argparse
import logging

logger = logging.getLogger(__name__)

from src.build_index import generate_build_index

def main():

    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Generate UE4 build index')
    parser.add_argument('ue4_base_directory', metavar='directory', type=str, help='UE4 base directory')
    parser.add_argument('output_directory', metavar='directory', type=str, help='Output directory')
    parser.add_argument('platform', metavar='platform', type=str, help='Build platofrm (Win64 etc)')
    parser.add_argument('configuration', metavar='configuration', type=str, help='Build configuration (Development etc)')
    parser.add_argument('target', metavar='target', type=str, help='Build target (UE4Editor etc)')
    parser.add_argument('pch', metavar='pch', type=str, default='True', help='Use precompiled headers')
    args = parser.parse_args()

    pch = (args.pch != 'False')

    generate_build_index(args.ue4_base_directory, args.platform, args.configuration, args.target, args.output_directory, pch)

if __name__=='__main__':
    main()
