
from flask import Flask
from app.routes import app_routes
from config import Config
import os

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'app', 'templates'))
app.config.from_object(Config)
app.register_blueprint(app_routes)

if __name__ == "__main__":
    app.run(debug=True)