"""App entry point."""
from games import create_app
from flask import send_file

app = create_app()

app.static_folder = 'static'


@app.route('/favicon.ico')
def favicon():
    return send_file('static/gaming_logo.jpg')


if __name__ == "__main__":
    app.run(host='localhost', port=5000, threaded=False)
