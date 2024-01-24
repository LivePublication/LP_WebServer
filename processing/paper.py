import contextlib
import json
import os
import subprocess
import time
import uuid
from glob import glob
from os import path

import pandoc
import quarto
import logging

from githubapp.app import get_repo, download_repo
from processing.artefacts import reference_artefacts

if uuid.getnode() == 224948472755932:
    # For testing only - correct pandoc version on my laptop
    pandoc.configure(path='C:/Program Files/Pandoc/pandoc.exe')

logger = logging.getLogger('paper')
info = logger.info


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


def gh_paper_update_links(folder, render_file):
    """Update any links in the rendered file to point to the correct location"""
    # Rename all references to artefacts
    with open(render_file, 'r', encoding='utf-8') as f:
        html = f.read()

    # TODO - we shouldn't move everything to static, but consider just serving index_files from there
    # targets = os.listdir(path.join(repo_dir, 'render'))
    # static_dir = path.join('static', 'paper-artefacts', owner, repo_name, sha)
    # os.makedirs(static_dir, exist_ok=True)
    # for target in targets:
    #     if target != 'temp.html':
    #         html = html.replace(target, path.join('/', static_dir, target).replace('\\', '/'))
    #         target_path = path.join(repo_dir, 'render', target)
    #         if path.isfile(target_path):
    #             shutil.copyfile(target_path, path.join(static_dir, target))
    #         else:
    #             shutil.copytree(path.join(repo_dir, 'render', target), path.join(static_dir, target))

    with open(render_file, 'w', encoding='utf-8') as f:
        f.write(html)


def gh_paper_content(owner, repo_name, sha):
    # Get downloaded repo
    repo = get_repo(owner, repo_name)
    repo_dir = download_repo(repo, sha)
    info(f'gh_paper_content - Downloaded repo to {repo_dir}')

    # Check that we have an index file
    index_file = path.join(repo_dir, 'index.qmd')
    if not path.isfile(index_file):
        info(f'gh_paper_content - No index.qmd file in {repo_dir}')
        raise FileNotFoundError(f'No index.qmd file in {repo_dir}')

    # Check if we have a cached version
    # TODO: implement some way of invalidating the cache
    render_file = path.join(repo_dir, 'paper_render.html')

    if path.isfile(render_file):
        # For testing only, invalidate file after 1 minute
        if time.time() - path.getmtime(render_file) > 60:
            info(f'gh_paper_content - Using cached version of {render_file}')
            return render_file

    # If we don't have a version, render it
    info(f'gh_paper_content - using quarto at {os.system("which quarto")}')
    with contextlib.chdir(repo_dir):
        info(f'gh_paper_content - Rendering {index_file} to {render_file}')
        subprocess.check_call(['quarto', 'render', index_file,
                               '--to', 'html', '--output', path.basename(render_file),
                               # '--output-dir', 'render'  # TODO: consider rendering in a different folder to the repo download
                               '--execute'])

    info(f'gh_paper_content - Render complete, returing {render_file}')
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
