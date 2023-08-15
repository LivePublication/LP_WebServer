import json
from os import path
from glob import glob
import uuid

from githubapp.app import get_repo, download_repo
from processing.artefacts import reference_artefacts, host_artefacts

import pandoc
if uuid.getnode() == 224948472755932:
    # For testing only - correct pandoc version on my laptop
    pandoc.configure(path='C:/Program Files/Pandoc/pandoc.exe')


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


def gh_paper_content(owner, repo_name, sha):
    # Get downloaded repo
    repo = get_repo(owner, repo_name)
    repo_dir = download_repo(repo, sha)

    # Check that we have an index file
    index_file = path.join(repo_dir, 'index.qmd')
    if not path.isfile(index_file):
        raise FileNotFoundError(f'No index.qmd file in {repo_dir}')

    with open(index_file, 'r') as f:
        doc = pandoc.read(f.read())

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
