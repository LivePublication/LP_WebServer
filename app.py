import flask
from flask import render_template

app = flask.Flask(__name__)


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
    # TODO: Build list of papers available
    return render_template('papers.html',
                           title='Live Publications',
                           papers=papers_list)


@app.route('/papers/<int:paper_id>')
def paper(paper_id):
    return render_template('paper.html',
                           title='Live Publications',
                           paper=papers_list[paper_id])


if __name__ == '__main__':
    app.run(debug=True)
