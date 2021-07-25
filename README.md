# How to build a CRUD app using Flask

[Flask](https://flask.palletsprojects.com/) is one of the most popular web frameworks written in Python. Flask is a lightweight framework that is perfect for beginners. It is designed to make getting started quick and easy, with the ability to scale up to complex applications.

## Background

We'll build a very basic todo app using [Flask](https://flask.palletsprojects.com/) that allows users to create task, read all the tasks entered, update the tasks, and delete them. These four operations, create, read, update, and delete, are more commonly referred to as "CRUD" in database theory. We'll use [SQLAlchemy](https://www.sqlalchemy.org/) in conjunction with SQLite to store information about tasks.

## Setup Environment

Before we can build our application, we need to install some dependencies.

To verify if Python is installed and configured correctly on your system, Open the terminal and type in the command `python --version` else you’ll need to install [Python](https://www.python.org/) 3.6+ on your system.

```bash
$ python --version
Python 3.7.6
```

We will start by creating our project's work directory and a virtual environment for our project. The virtual environment makes it possible to run our project and its dependencies in an isolated environment.

Run `mkdir flask_todo_app` to create our working directory.

```bash
mkdir flask_todo_app
cd flask_todo_app
```

1. To create a virtual environment for our project run:

      ```bash
      python -m venv env
      ```

    `env` is the name of our virtual environment

2. To activate the virtual environment for our project run:

   ```bash
   .\env\Scripts\activate
   ```

3. Now, install dependencies in our virtual environment:

    Flask, which we'll use to route web traffic through HTTP requests to specific functions in our code base.

    SQLAlchemy, which we'll use to make the interaction between Python and our database smoother.

    Flask-SQLAlchemy, which we'll use to make the interaction between Flask and SQLAlchemy smoother.

   ```bash
   $ pip install flask 
   $ pip install sqlalchemy 
   $ pip install flask-sqlalchemy
   ```

## Create a simple app

The reason I like Flask is because of the simplicity of getting a basic web page running — we can do this in only a few lines of code.

Create the `flask_todo_app/app.py` file. open `app.py` in code editor and add the following lines of code:

```python
# import packages
from flask import Flask

# create an instance of the flask app
app = Flask(__name__)

# map home page (/) to `say_hello()` using python decorator
@app.route('/')
def say_hello():
    return 'Hello, World!'
    
if __name__ == "__main__":
    app.run(debug=True)
```

Note that we set `debug=True` so we don't have to reload our server each time we make a change in our code.

## Run the app

Run below command:

```bash
python app.py
```

Now we can go to `http://127.0.0.1:5000/` and inspect our first running app!

## Add the database

We want to remember our tasks, so we'll want to be able to add items to a database. We'll use the SQLite database, which is a file-based database, so we can store our data in a file on our file system, without needing to install a huge Relational Database Management System (RDBMS). We'll use SQLite through SQLAlchemy.

### Configuring database connection

Now we need to set up a database, open a connection to it, and associate this connection with our web application.

Open `flask_todo_app/app.py` in code editor and add the following lines of code before the first function definition:

```python
# import packages
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# create an instance of the flask app
app = Flask(__name__)

# database path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# initialize a connection to the database
db = SQLAlchemy(app)
...
```

Now we can define the concept of a `task` and how we'll store this in our database.

### Creating the `Todo` model

Add the following code to `flask_todo_app/app.py`, which represents how we'll store each task in our database. Make sure you add the code below the `db = SQLAlchemy(app)` line, as we use `db` to define the `Todo` model.

```python
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    completed = db.Column(db.Boolean, default=False)

    # represent `Todo` object as a string
    def __repr__(self):
        return "<Title: {}>".format(self.title)
```

### Initializing our database

To initialize our database, run the following commands in a Python shell in your project directory in order to create our database and create the `todo` table where we'll store our tasks.

```python
>>> from app import db
>>> db.create_all()
>>> exit()
```

## Retrieve all tasks

Every time the user visits our web application, we want to get all of the current tasks out of the database and display them. SQLAlchemy makes it easy to load all of the tasks stored in our database into a Python variable in one line of code.

Open `flask_todo_app/app.py` in code editor and add the following lines of code:

```python
from flask import Flask, render_template
...

@app.route('/todos')
def get_tasks():
    todos = Todo.query.all()
    return render_template("base.html", todos=todos)
```

## Create template

Now we need template to render each of the tasks as HTML by using a [Jinja](https://jinja.palletsprojects.com/en/3.0.x/) for loop. For this, create a folder named `templates` in the root folder of your project. Now create the `templates/base.html` file in this folder and add code as follows:

```html
<!doctype html>
<html lang="en">
  <head>
    <!-- Required meta tags -->
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />

     <!-- CSS -->

    <title>Todo App</title>
  </head>

  <body>
    <h1>Todo App</h1>

    <!-- Todo Input -->

    <!-- Todo List -->
    {% for todo in todos %}
        <p>{{ todo.title }}</p>

        {% if todo.completed == False %}
            <span>Incomplete</span>
        {% else %}
            <span>Complete</span>
        {% endif %} 

        <a href="#">Edit</a>
        <a href="#">Delete</a>

    {% endfor %}

    <!-- Optional JavaScript -->    
  </body>
</html>

```

## Create new task

Now, when a user enters a task `title`, we can create a `Todo` object and store this in our database. To do this, open `flask_todo_app/app.py` in code editor and add the following lines of code:

```python
@app.route("/todos/create", methods=["POST"])
def create():
    title = request.form.get("title")
    new_todo = Todo(title=title, completed=False)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("get_tasks"))
```

In the `templates/base.html` file, add the below line of code before Jinja for loop to look as follows:

```html
<form action="/todos/create" method="POST">
    <div>
        <label>Title</label>
        <input type="text" name="title" placeholder="Add Todo...">
        <br>
        <button type="submit">Add</button>
    </div>
</form>
```

Next up, we'll look at how to Update the existing tasks.

## Update task

We will create a function to update a task in our database. After we filter by `id`, we will update the details of `Todo` object and then commit our changes.

```python
@app.route("/todos/update/<int:id>")
def update(id):
    todo = Todo.query.filter_by(id=id).first()
    todo.completed = not todo.completed
    db.session.commit()
    return redirect(url_for("get_tasks"))
```

In the `templates/base.html` file, add the code inside Jinja for loop to look as follows:

```html
{% for todo in todos %}
    <p>{{ todo.title }}</p>

    {% if todo.completed == False %}
        <span>Incomplete</span>
    {% else %}
        <span>Complete</span>
    {% endif %} 

    <a href="/todos/update/{{ todo.id }}">Edit</a>
    <a href="#">Delete</a>

{% endfor %}
```

Now the last thing we need to do is Delete task that we no longer want.

## Delete task

We will create a function to delete a task from our database. We will filter by the `id` and the `delete()` method will delete the task.

```python
@app.route("/todos/delete/<int:id>")
def delete(id):
    todo = Todo.query.filter_by(id=id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("get_tasks"))
```

In the `templates/base.html` file, add the code inside Jinja for loop to look as follows:

```html
{% for todo in todos %}
    <p>{{ todo.title }}</p>

    {% if todo.completed == False %}
        <span>Incomplete</span>
    {% else %}
        <span>Complete</span>
    {% endif %} 

    <a href="/todos/update/{{ todo.id }}">Edit</a>
    <a href="/todos/delete/{{ todo.id }}">Delete</a>

{% endfor %}
```

Our app is now fully functional! Now let's improve the UI by styling with bootstrap.

## Add styling with bootstrap

Now we'll make the application more aesthetically pleasing by adding some CSS, through a framework like [Bootstrap](http://getbootstrap.com/).

For integrating the Bootstrap in our html, we use a CDN, see the official [docs](https://getbootstrap.com/docs/4.0/getting-started/introduction/) for more info.

Open `templates/base.html` file and add below code:

```html
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" crossorigin="anonymous">
```

Now we just have to add some class names to add the styling. The final html looks like this:

```html
<!doctype html>
<html lang="en">
  <head>
    <!-- Required meta tags -->
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />

    <!-- CSS -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" crossorigin="anonymous">

    <title>Todo App</title>
  </head>

  <body>
    <div class="container">
        <h1 class="text-black text-uppercase text-center my-4">Todo App</h1>
        <div class="row">
            <div class="col-md-12">
                <div class="card card-white">
                    <div class="card-body">                        
                
                        <!-- Todo Input -->                        
                        <form action="/todos/create" method="POST">
                            <div class="form-group">
                                <label>Title</label>
                                <input type="text" class="form-control" name="title" placeholder="Add Todo...">
                                <br>
                                <button type="submit" class="btn btn-primary">Add</button>
                            </div>
                        </form>
                
                        <hr>
                
                        <!-- Todo List -->                
                        {% for todo in todos %}
                            <div class="card-body">
                                
                                <p class="h4">{{ todo.title }}</p>
                    
                                {% if todo.completed == False %}
                                    <span class="badge badge-secondary">Incomplete</span>
                                {% else %}
                                    <span class="badge badge-success">Complete</span>
                                {% endif %} 
                                <a href="/todos/update/{{ todo.id }}"><button type="button" class="btn btn-primary btn-sm">Edit</button></a>
                                <a href="/todos/delete/{{ todo.id }}"><button type="button" class="btn btn-danger btn-sm">Delete</button></a>
                                <hr>
                            </div>                
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div> 
    </div>    

    <!-- Optional JavaScript -->
  </body>
</html>

```

## Conclusion

That's all! I have covered quite a lot: setting up a database, creating model, migrating the database, and handling the CRUD functionality of the app, which is allowing user to add, list, edit, and delete tasks.

Happy Coding!
