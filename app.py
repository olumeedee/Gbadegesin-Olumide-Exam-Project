from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return "Hello world!"

@app.route('/<name>')
def greet_user(name):
    return f"Hello {name}! How are you doing?"

@app.route('/post/<int:id>')
def post_id(id):
    return f"This post has an ID of {id}"

if __name__ == "__main__":
    app.run(debug=True)