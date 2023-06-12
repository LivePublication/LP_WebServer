import json
from os import path
from glob import glob

import pandoc

from processing.artefacts import reference_artefacts, host_artefacts


def paper_metadata(folder):
    assert path.isdir(folder), f'Folder {folder} does not exist'

    with open(path.join(folder, 'crate.json'), 'r') as f:
        metadata = json.load(f)

    return metadata


def paper_content(folder):
    assert path.isdir(folder), f'Folder {folder} does not exist'

    with open(path.join(folder, 'crate.json'), 'r') as f:
        metadata = json.load(f)

    content_file = metadata['content']

    with open(path.join(folder, content_file), 'r') as f:
        doc = pandoc.read(f.read())

    doc = reference_artefacts(metadata, doc)

    return pandoc.write(doc, format='html')


def list_papers():
    """
    List all valid papers in the papers folder
    :return: dict of paper_id: paper_metadata
    """
    papers = {}
    for i, folder in enumerate(glob('papers/*')):
        crate_file = path.join(folder, 'crate.json')
        if not path.isfile(crate_file):
            continue

        with open(crate_file, 'r') as f:
            metadata = json.load(f)

        papers[metadata['frontmatter']['slug']] = metadata

    return papers
