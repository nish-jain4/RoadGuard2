from flask import Flask
from config import Config
from database import init_db, db_session
from routes import auth, user, admin, worker

app = Flask(__name__)
app.config.from_object(Config)

# Register blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(user.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(worker.bp)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)