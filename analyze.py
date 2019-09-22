
import argparse
import json
import os.path
import sys

def load_json_export(base_dir):

    file_name = os.path.join(base_dir, 'Engine/Binaries/Win64/UE4Editor.json')
    with open(file_name, 'rt') as file:
        json_export = json.load(file)

    return json_export

def main():

    parser = argparse.ArgumentParser(description='Analyze UE4 build results')
    parser.add_argument('ue4_base_directory', metavar='directory', type=str, help='UE4 base directory')
    args = parser.parse_args()

    json_export = load_json_export(args.ue4_base_directory)

    print(json_export['Name'])

if __name__=='__main__':
    main()