from flask import Flask
from endpoints.ping_server import ping_bp
from endpoints.top_news import top_news_bp

app = Flask(__name__)
app.register_blueprint(ping_bp)
app.register_blueprint(top_news_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080) 