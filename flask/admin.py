from flask import Flask, render_template
app = Flask(__name__)


@app.route("/admin")
@app.route("/admin/<planetname>")
def index(name=None):
    return render_template('admin.html', name=name)

if __name__ == "__main__":
    app.run(debug=True)