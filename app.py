import sys

import flask
from flask import render_template
from markupsafe import escape, Markup
from werkzeug.middleware.proxy_fix import ProxyFix

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

    print(papers[safe_slug], file=sys.stderr)

    return render_template('paper.html',
                           title='Live Publications',
                           metadata=papers[safe_slug]['frontmatter'],
                           content=Markup(content))


if __name__ == '__main__':
    app.run(debug=False)
