from flask import Flask,render_template,request

app = Flask(__name__)

@app.route('/')
def home_page():
    return render_template('welcome.html')

@app.route('/signup_form')
def signup_form():
    return render_template('signup.html')

@app.route('/signin_form')
def signin_form():
    return render_template('signin.html')

@app.route('/root')
def root():
    return render_template('Root.html')

@app.route('/canvas')
def canvas():
    return render_template('canvas.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404


if __name__ == '__main__':
    app.run(debug=True)