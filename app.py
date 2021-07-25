from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    completed = db.Column(db.Boolean)

    def __repr__(self):
        return "<Title: {}>".format(self.title)

@app.route('/')
def say_hello():
    return 'Hello, World!'

@app.route('/todos')
def get_tasks():
    todos = Todo.query.all()
    return render_template("base.html", todos=todos)

@app.route("/todos/create", methods=["POST"])
def create():
    title = request.form.get("title")
    new_todo = Todo(title=title, completed=False)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("get_tasks"))

@app.route("/todos/update/<int:id>")
def update(id):
    todo = Todo.query.filter_by(id=id).first()
    todo.completed = not todo.completed
    db.session.commit()
    return redirect(url_for("get_tasks"))

@app.route("/todos/delete/<int:id>")
def delete(id):
    todo = Todo.query.filter_by(id=id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("get_tasks"))

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)