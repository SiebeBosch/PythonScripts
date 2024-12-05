from flask import Flask, send_from_directory, render_template, redirect, request, url_for, session

app = Flask(__name__)

# Set the secret key
app.secret_key = 'your_random_secret_key'  # Replace with a securely generated key

# Fake user credentials (for testing)
VALID_USERNAME = "user"
VALID_PASSWORD = "password"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == VALID_USERNAME and request.form['password'] == VALID_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('report'))
        else:
            return "Invalid credentials. Please try again.", 401
    return render_template('login.html')

@app.route('/')
def report():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return send_from_directory('docs', 'index.html')

# Serve all static files under /docs
@app.route('/<path:filename>')
def serve_static_files(filename):
    return send_from_directory('docs', filename)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
