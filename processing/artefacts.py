import os
import shutil
from os import path
import json

import pandoc


def host_artefacts(folder):
    """
    Host all artefacts in a paper
    """
    assert path.isdir(folder), f'Folder {folder} does not exist'

    with open(path.join(folder, 'crate.json'), 'r') as f:
        metadata = json.load(f)

    slug = metadata['frontmatter']['slug']

    static_folder = path.join('static', 'paper-artefacts', slug)
    os.makedirs(static_folder, exist_ok=True)

    for artefact in metadata['artefacts']:
        # Create a copy in the static folder
        shutil.copyfile(path.join(folder, artefact), path.join(static_folder, artefact))


def reference_artefacts(metadata, content):
    """
    Replace all references to artefacts with links to the static folder
    """
    slug = metadata['frontmatter']['slug']
    static_folder = path.join('static', 'paper-artefacts', slug)

    for elt in pandoc.iter(content):
        if isinstance(elt, pandoc.types.Image):
            original_link = elt[2][0]
            elt[2] = (path.join("/", static_folder, original_link), 'fig:')

    return content
