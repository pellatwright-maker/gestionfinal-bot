from flask import Flask
import threading

app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "Bot est en ligne H24"

def run_flask():
    app_flask.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_flask).start()
