import flask
from flask import render_template
from markupsafe import escape, Markup
from werkzeug.middleware.proxy_fix import ProxyFix

from githubapp.app import get_all_repos, _get_quarto_metadata
from processing.artefacts import host_artefacts
from processing.paper import list_papers, paper_content

app = flask.Flask(__name__)
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)


@app.route('/')
def index():
    return render_template('index.html', title='Live Publications', text='This is the home page')


papers_list = [
    {'title': f'Paper {i}', 'authors': 'Author 1, Author 2', 'year': '2020',
     'link': f'papers/{i}'}
    for i in range(5)
]


@app.route('/papers')
def papers():
    papers = list_papers()

    list_view = [p['frontmatter'] for p in papers.values()]

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



if __name__ == '__main__':
    app.run(debug=False)
