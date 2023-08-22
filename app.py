import logging
import flask
from bs4 import BeautifulSoup
from flask import render_template
from markupsafe import escape, Markup
from werkzeug.middleware.proxy_fix import ProxyFix

from githubapp.app import get_all_repos, _get_quarto_metadata, get_repo, get_paper_version_list, repo_dir_name, \
    get_next_prev_slug, get_commits
from processing.artefacts import host_artefacts
from processing.paper import list_papers, paper_content, gh_paper_content

app = flask.Flask(__name__)
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

# Tie in gunicorn logger
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers.extend(gunicorn_logger.handlers)
app.logger.setLevel(logging.DEBUG)
info = app.logger.info

@app.route('/')
def index():
    return render_template('index.html', title='Live Publications', text='This is the home page')


@app.route('/papers')
def papers():
    papers = list_papers()

    list_view = [p['frontmatter'] for p in papers.values()]

    for p in list_view:
        p['slug'] = f'/papers/{p["slug"]}'

    return render_template('papers.html',
                           title='Live Publications',
                           papers=list_view)


@app.route('/papers/<paper_slug>')
def paper(paper_slug):
    papers = list_papers()

    # Check paper exists
    safe_slug = escape(paper_slug)
    if safe_slug not in papers:
        flask.abort(404)

    # Host artefacts
    host_artefacts(f'papers/{safe_slug}')

    # Render paper
    content = paper_content(f'papers/{safe_slug}')

    return render_template('paper.html',
                           title='Live Publications',
                           metadata=papers[safe_slug]['frontmatter'],
                           content=Markup(content))


@app.route("/gh_papers")
def gh_papers():
    """List available papers, for each paper navigate to list of versions"""
    repos = get_all_repos()

    def slug(repo):
        return f'/gh_papers/{repo.owner.name}/{repo.name}'

    # Build list of metadata similar to the papers() function
    list_view = []
    for r in repos:
        metadata = _get_quarto_metadata(r)
        list_view.append({
            'title': metadata['title'],
            'authors': [a['name'] for a in metadata['authors']],
            'year': metadata.get('year', 'unknown'),
            'slug': slug(r)
        })

    return render_template('papers.html',
                            title='Live Publications (github)',
                            papers=list_view)


@app.route('/gh_papers/<owner>/<repo_name>')
def gh_paper_versions(owner, repo_name):
    """List available versions of a paper"""
    repo = get_repo(owner, repo_name)

    # Get versions
    versions = get_paper_version_list(repo)

    # TODO: convert tags to colored badges
    for v in versions:
        v['tags'] = ', '.join(v['tags'])
        v['slug'] = f'{owner}/{repo_name}/{v["sha"]}'

    return render_template('paper_versions.html',
                           title='Live Publications (github)',
                           versions=versions)


@app.route('/gh_papers/<owner>/<repo_name>/<sha>/')
def gh_paper(owner, repo_name, sha):
    """Render a paper version"""
    _owner = escape(owner)
    _repo_name = escape(repo_name)
    _sha = escape(sha)
    info(f'gh_paper - Paper request: {_owner}/{_repo_name}/{_sha}')

    try:
        html_src = gh_paper_content(_owner, _repo_name, _sha)
        info(f'gh_paper - HTML source: {html_src}')

        with open(html_src, 'r', encoding='utf-8') as f:
            html = f.read()

        # Extract html so that we can insert it correctly into templates
        soup = BeautifulSoup(html, 'html.parser')

        for t in soup.findAll('section', 'level2'):
            new_tag = soup.new_tag('div')
            new_tag['class'] = 'carousel'
            new_tag['id'] = t['id']
            t.replace_with(new_tag)

        head = ''.join(str(c) for c in soup.head.contents)
        header = ''.join(str(c) for c in soup.header.contents)
        body = soup.find(id='quarto-content')

        # Link to next/previous version if available
        next_slug, prev_slug = get_next_prev_slug(_owner, _repo_name, _sha)

        info(f'gh_paper - Returning HTML')

        return render_template('quarto_paper.html',
                                 title='Live Publications',
                                 head=Markup(head),
                                 header=Markup(header),
                                 content=Markup(body),
                                 next_slug=next_slug,
                                 prev_slug=prev_slug,
                                 shas=','.join(get_commits(get_repo(_owner, _repo_name))),
                                 current_sha=_sha)
    except FileNotFoundError as e:
        logging.error(e)
        flask.abort(404)


@app.route('/gh_papers/<owner>/<repo_name>/<sha>/sections/<section>')
def gh_paper_section(owner, repo_name, sha, section):
    _owner = escape(owner)
    _repo_name = escape(repo_name)
    _sha = escape(sha)
    _section = escape(section)
    info(f'gh_paper - Paper request: {_owner}/{_repo_name}/{_sha}')

    try:
        html_src = gh_paper_content(_owner, _repo_name, _sha)
        info(f'gh_paper - HTML source: {html_src}')

        with open(html_src, 'r', encoding='utf-8') as f:
            html = f.read()

        # Extract html so that we can insert it correctly into templates
        soup = BeautifulSoup(html, 'html.parser')
        head = ''.join(str(c) for c in soup.head.contents)
        header = ''.join(str(c) for c in soup.header.contents)
        body = soup.find(id='quarto-content')

        sections = soup.findAll('section', 'level2')
        section_dict = {
            s['id']: s
            for s in sections
        }

        if _section not in section_dict:
            flask.abort(404)

        # Links to next/prev version
        next_slug, prev_slug = get_next_prev_slug(_owner, _repo_name, _sha)
        if next_slug:
            next_slug += f'/sections/{_section}'
        if prev_slug:
            prev_slug += f'/sections/{_section}'

        # return section_dict[_section].prettify()
        return render_template('section.html',
                                 content=Markup(section_dict[_section]),
                                 next_slug=next_slug,
                                 prev_slug=prev_slug)
    except FileNotFoundError as e:
        logging.error(e)
        flask.abort(404)


@app.route('/gh_papers/<owner>/<repo_name>/<sha>/<path:filespec>')
def paper_files(owner, repo_name, sha, filespec):
    """Serve files (libraries and artefacts) from a paper"""
    _owner = escape(owner)
    _repo_name = escape(repo_name)
    _sha = escape(sha)
    _filespec = escape(filespec)

    try:
        repo_dir = repo_dir_name(_owner, _repo_name, _sha)

        return flask.send_from_directory(repo_dir, _filespec)
    except FileNotFoundError:
        flask.abort(404)


if __name__ == '__main__':
    app.run(debug=False)
