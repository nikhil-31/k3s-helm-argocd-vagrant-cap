import sqlite3
import logging
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    connection.close()
    return post


def get_post_count():
    """
    Post count
    :return: int - total number of posts
    """
    connection = get_db_connection()
    cursor = connection.execute('SELECT COUNT(id) FROM posts')
    post_count = cursor.fetchall()[0][0]
    connection.close()
    return post_count


def count_db_connections():
    """
    This method counts the number of article views for the database
    :return: int
    """
    connection = get_db_connection()
    cursor = connection.execute('SELECT SUM(view_count) FROM posts')
    conn_count = cursor.fetchall()[0][0]
    connection.close()
    return conn_count


def update_db_connections(post_id):
    """
    This method updates the number of article views for the database
    """
    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute('UPDATE posts SET view_count = view_count + 1 WHERE id = ?',
                (post_id,)).fetchone()
    connection.commit()
    connection.close()


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


# Define the main route of the web application
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)


# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    update_db_connections(post_id)
    post = get_post(post_id)
    if post is None:
        return render_template('404.html'), 404
    else:
        return render_template('post.html', post=post)


# Define the About Us page
@app.route('/about')
def about():
    return render_template('about.html')


# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/healthz')
def healthcheck():
    result = 'OK - healthy'
    response = app.response_class(
        response=json.dumps({"result": result}),
        status=200,
        mimetype='application/json'
    )
    app.logger.info('Status request successful')
    app.logger.info(f"result: {result}")
    return response


@app.route('/metrics')
def metrics():
    db_connections = count_db_connections()
    total_post = get_post_count()
    app.logger.info('Metrics request successful')
    app.logger.info(f"db_connection_count: {db_connections} and total_posts: {total_post}")
    response = app.response_class(
        response=json.dumps({"db_connection_count": db_connections,
                             "post_count": total_post}),
        status=200,
        mimetype='application/json'
    )
    return response


# start the application on port 3111
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3111, debug=True)
