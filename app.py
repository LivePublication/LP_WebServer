import flask

app = flask.Flask(__name__)


@app.route('/')
def index():
    return '<p>Hello world!</p>'


if __name__ == '__main__':
    app.run(debug=True)
