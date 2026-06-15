from flask import Flask
import os
app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<h1>Up and running!👍</h1>"
    
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)





