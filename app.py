from flask import Flask

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return "Hello world!"

@app.route('/about')
def about():
    return "The about page"

@app.route('/contact')
def contact():
    return "The contact page"

@app.route('/protected')
def protected():
    return "The protected page"
    
if __name__ == "__main__":
    app.run(debug=True)