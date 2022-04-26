#!/usr/bin/env python3

import argparse
import logging
import re
import subprocess
import time
import yaml

semantic_version_re = re.compile(r'^v(\d+)\.(\d+)\.(\d+)$')

def check_release_exists(release_name):
    ret = subprocess.run([
        "gh", "release", "view", release_name
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return ret.returncode == 0

def create_release(canvas_name, composition_name, logger, version):
    base_name = composition_name if composition_name else canvas_name
    release_name = f"{base_name}-{version}"
    if check_release_exists(release_name):
        logger.debug(f"Release {release_name} already exists")
        return
    major_version = version.split('.', 1)[0]
    last_git_tag = find_last_git_tag(base_name=base_name, major_version=major_version)
    print(last_git_tag)
    if last_git_tag:
        release_notes = f"Who knows?"
    else:
        release_notes = f"Initial release for {base_name}-{major_version}."
    #ret = subprocess.run([
    #    "gh", "release", "create", release_name,
    #    "--notes", release_notes,
    #    "--title", release_name,
    #], check=True, stdout=subprocess.PIPE)
    #release_url = ret.stdout.decode('utf-8').strip()
    #logger.info(f"Created release {release_url}")

#def create_releases(canvas, logger, releases):
#    for name, release_config in releases.items():
#        version = release_config.get('version')
#        assert version, "No version for release!"
#        assert semantic_version_re.match(version) , f'Invalid semantic version "{version}"'
#        try:
#            create_release(
#                canvas=canvas,
#                logger=logger,
#                name=name,
#                version=release_config['version'],
#                workloads=release_config.get('workloads', []),
#            )
#        except Exception as e:
#            logger.exception(f"Failed to create release for {name}")

def create_release_from_version_file(version_file, logger):
    logger.debug(f"Creating releases for {version_file}")
    canvas_or_composition, name, _ = version_file.split('/', 2)
    print(canvas_or_composition)
    try:
        if canvas_or_composition == "canvas":
            canvas_name = name
            composition_name = None
        elif canvas_or_composition == "compositions":
            canvas_name = get_canvas_name_for_composition(name)
            composition_name = name
        else:
            raise Exception(f"Unable to create release for {version_file}, not a canvas or composition!")
        print(canvas_name)
        print(composition_name)
        with open(version_file) as version_fh:
            version_data = yaml.safe_load(version_fh)
            if 'version' not in version_data:
                raise Exception(f"No version in {version_file}")
            create_release(
                canvas_name=canvas_name,
                composition_name=composition_name,
                logger=logger,
                version=version_data['version'],
            )
    except Exception as e:
        logger.exception(f"Failed to create releases for {version_file}")

def find_last_git_tag(major_version, base_name):
    ret = subprocess.run([
        "git", "tag", "--list", f"{base_name}-{major_version}.*"
    ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    highest_minor_version = highest_patch_version = None
    for tag in ret.stdout.decode('utf-8').strip().split("\n"):
        semantic_version_match = semantic_version_re.match(tag[len(base_name) + 1:])
        if not semantic_version_match:
            continue
        tag_minor_version = int(semantic_version_match.group(2))
        tag_patch_version = int(semantic_version_match.group(3))
        if highest_minor_version == None \
        or highest_minor_version < tag_minor_version \
        or (highest_minor_version == tag_minor_version and highest_patch_version < tag_patch_version):
            highest_minor_version = tag_minor_version
            highest_patch_version = tag_patch_version

    if highest_minor_version != None:
        return f"{base_name}-{major_version}.{highest_minor_version}.{highest_patch_version}"
    return None

def get_canvas_name_for_composition(name):
    defaults_file = f"compositions/{name}/defaults/main.yml"
    with open(defaults_file) as defaults_fh:
        defaults = yaml.safe_load(defaults_fh)
        if 'agnosticd_canvas' not in defaults:
            raise Exception(f"{default_file} does not define agnosticd_canvas!")
        return defaults['agnosticd_canvas']

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Create GitHub release based on version files")
    argparser.add_argument('version_file', metavar='VERSION_FILE', type=str, nargs="+")
    argparser.add_argument('--debug', action='store_const', const=True)
    args = argparser.parse_args()

    logger = logging.getLogger('release.py')
    logging_stream_handler = logging.StreamHandler()
    logging_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    logging_formatter.converter = time.gmtime
    logging_stream_handler.setFormatter(logging_formatter)
    logger.addHandler(logging_stream_handler)

    if args.debug:
        logging_stream_handler.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    else:
        logging_stream_handler.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)

    for version_file in args.version_file:
        create_release_from_version_file(logger=logger, version_file=version_file)
