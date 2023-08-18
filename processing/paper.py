import contextlib
import json
import subprocess
import uuid
from glob import glob
from os import path

import pandoc
import quarto

from githubapp.app import get_repo, download_repo
from processing.artefacts import reference_artefacts

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

    # Check if we have a cached version
    # TODO: implement some way of invalidating the cache
    render_file = path.join(repo_dir, 'paper_render.html')
    if path.isfile(render_file):
        return render_file

    # If we don't have a version, render it
    with contextlib.chdir(repo_dir):
        subprocess.check_call([quarto.quarto.find_quarto(), 'render', index_file,
                               '--to', 'html', '--output', path.basename(render_file),
                               # '--output-dir', 'render'  # TODO: consider rendering in a different folder to the repo download
                               '--execute'])

    return render_file


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
