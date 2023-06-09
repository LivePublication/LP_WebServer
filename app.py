import flask
from flask import render_template

app = flask.Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', title='Home', text='This is the home page')


if __name__ == '__main__':
    app.run(debug=True)
