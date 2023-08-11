import os
import tarfile

import requests
import yaml
from github import Github, GithubIntegration
from github.Installation import Installation
from github.Repository import Repository

from keys import github_app_id, github_key_file
from root import ROOT_DIR

with open(
        os.path.normpath(os.path.expanduser(github_key_file)),
        'r'
) as cert_file:
    app_key = cert_file.read()

# Create an GitHub integration instance
git_integration = GithubIntegration(
    github_app_id,
    app_key,
)


def get_git(owner, repo_name) -> Github:
    """Get a Github instance for a repo"""
    installation = git_integration.get_repo_installation(owner, repo_name)
    return installation.get_github_for_installation()


def get_repo(owner, repo_name) -> Repository:
    """Get a Github repo instance"""
    git = get_git(owner, repo_name)
    return git.get_repo(f"{owner}/{repo_name}")


def get_repos(installation: Installation) -> list[Repository]:
    """Get a list of repos for an installation"""
    return list(installation.get_repos())


def get_all_repos() -> list[Repository]:
    """Get a list of all repos for the app"""
    repos = []
    for installation in git_integration.get_installations():
        repos.extend(get_repos(installation))

    return repos


def download_repo(repo: Repository, ref: str = None) -> str:
    """Download a repo to a temporary folder"""
    if ref is None:
        download_url = repo.get_archive_link('tarball')
    else:
        download_url = repo.get_archive_link('tarball', ref)
    r = requests.get(download_url, allow_redirects=True)

    # Create a directory to store the repo
    if ref is None:
        repo_dir = os.path.join(ROOT_DIR, 'papers', repo.name, 'temp')
    else:
        repo_dir = os.path.join(ROOT_DIR, 'papers', repo.name, ref)

    if os.path.isdir(repo_dir):
        # TODO - consider what else might need to happen here
        return repo_dir

    os.makedirs(repo_dir, exist_ok=True)

    # Download, extract and discard archive
    with open(os.path.join(repo_dir, 'repo.tar.gz'), 'wb') as f:
        f.write(r.content)

    with tarfile.open(os.path.join(repo_dir, 'repo.tar.gz')) as tar:
        tar.extractall(repo_dir)

    os.remove(os.path.join(repo_dir, 'repo.tar.gz'))

    return repo_dir


def get_paper_version_list(repo: Repository) -> list[dict]:
    """Get table of commit details for a paper"""
    # TODO: this function only serves one page - could be modularised
    versions = [
        {'sha': c.sha,
         'date': c.last_modified,
         'message': c.commit.message,
         'tags': []}
        for c in repo.get_commits()]

    tags = get_tagged_commits(repo)
    for t, sha in tags.items():
        for c in versions:
            if c['sha'] == sha:
                c['tags'].append(t)

    return versions


def get_commits(repo: Repository) -> list[str]:
    """Get a list of commit SHAs"""
    return [c.sha for c in repo.get_commits()]


def get_tagged_commits(repo: Repository) -> dict[str, str]:
    """Get a dict of tag name to commit SHA"""
    tags = repo.get_tags()
    return {t.name: t.commit.sha for t in tags}


def _get_quarto_metadata(repo: Repository) -> dict:
    """This needs replaced once the metadata is somewhere more suitable"""
    c = repo.get_contents('_quarto.yml')
    data = yaml.safe_load(c.decoded_content)

    return data


if __name__ == '__main__':
    # Example usage
    owner = 'LivePublication'
    repo_name = 'LP_Pub_LID'

    # Get access
    repo = get_repo(owner, repo_name)

    repo_dir = download_repo(repo)