from flask import Flask, render_template
from backend.routes import api
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os


load_dotenv()
app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')  
# Connect to MongoDB
mongo = PyMongo(app, uri=os.getenv("MONGO_URI"))  


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)  
