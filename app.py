# Pour Render Web Service
flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "Bot Gestionfinal en ligne H24"
app = flask_app
