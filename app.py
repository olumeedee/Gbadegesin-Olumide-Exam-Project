from flask import Flask, render_template, url_for

app = Flask(__name__)

posts = [
    {
        'author': 'Olumide Gbadegesin',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'November 2, 2022'
    },
    {
        'author': 'Bruce Wayne',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'November 2, 2022'
    }
]

@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/contact')
def contact():
    return render_template('contact.html', title='Contact Me')

@app.route('/protected')
def protected():
    return "The protected page"

if __name__ == "__main__":
    app.run(debug=True)