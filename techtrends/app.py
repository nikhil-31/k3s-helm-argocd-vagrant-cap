import sqlite3
import logging
import sys
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

connections_to_db = 0


def update_connection_to_db():
    """
    Counts the number of db connections that have taken place
    """
    global connections_to_db
    connections_to_db += 1


def get_connections_to_db():
    """
    Returns the number of db connections that have taken place so far
    :return: int - total number of database connections
    """
    return connections_to_db


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    update_connection_to_db()
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


# def count_total_article_views():
#     """
#     This method counts the number of article views for the database
#     :return: int
#     """
#     connection = get_db_connection()
#     cursor = connection.execute('SELECT SUM(view_count) FROM posts')
#     conn_count = cursor.fetchall()[0][0]
#     connection.close()
#     return conn_count


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
    app.logger.info('Displaying the homepage')
    return render_template('index.html', posts=posts)


# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.error('A non-existing article was accessed! "404"')
        return render_template('404.html'), 404
    else:
        update_db_connections(post_id)
        app.logger.info('POST ' + '"' + post['title'] + '"' + ' retrieved!')
        return render_template('post.html', post=post)


# Define the About Us page
@app.route('/about')
def about():
    app.logger.info("Displaying the about page")
    return render_template('about.html')


# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
            app.logger.debug(f"The title is required field, current input is: {title}")

        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
            connection.commit()
            connection.close()

            app.logger.info(f"Successfully created a new post with title: {title}")

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
    db_connections = get_connections_to_db()
    total_post = get_post_count()

    response = app.response_class(
        response=json.dumps({"db_connection_count": db_connections,
                             "post_count": total_post}),
        status=200,
        mimetype='application/json'
    )

    app.logger.info('Metrics request successful')
    app.logger.info(f"db_connection_count: {db_connections} and total_posts: {total_post}")

    return response


# start the application on port 3111
if __name__ == "__main__":
    # Set logger to handle STDOUT and STDERR
    stdout_handler = logging.StreamHandler(sys.stdout)
    stderr_handler = logging.StreamHandler(sys.stderr)
    handlers = [stderr_handler, stdout_handler]

    format_output = "[%(levelname)s] %(asctime)s: %(message)s"
    logging.basicConfig(format=format_output, level=logging.DEBUG, handlers=handlers)

    app.run(host='0.0.0.0', port=3111, debug=True)
