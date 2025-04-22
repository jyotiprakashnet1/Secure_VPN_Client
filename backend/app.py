from flask import Flask, render_template
from routes.client import client_bp
from routes.admin import admin_bp

app = Flask(__name__)
app.secret_key = "your_super_secret_key"

# Register blueprints
app.register_blueprint(client_bp, url_prefix="/client")
app.register_blueprint(admin_bp, url_prefix="/admin")

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)

