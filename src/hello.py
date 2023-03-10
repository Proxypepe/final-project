import uuid

from flask import Flask
import mysql.connector
from prometheus_flask_exporter import PrometheusMetrics


class DBManager:
    def __init__(
        self,
        database='example',
        host="db",
        user="root",
        password_file=None
    ):
        pf = open(password_file, 'r')
        self.connection = mysql.connector.connect(
            user=user,
            password=pf.read(),
            host=host,
            database=database,
            auth_plugin='mysql_native_password'
        )
        pf.close()
        self.cursor = self.connection.cursor()

    def populate_db(self):
        self.cursor.execute('DROP TABLE IF EXISTS blog')
        self.cursor.execute('CREATE TABLE blog (id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(255))')
        self.cursor.executemany('INSERT INTO blog (id, title) VALUES (%s, %s);', [(i, 'Blog post #%d' % i) for i in range(1, 5)])
        self.connection.commit()

    def query_titles(self):
        self.cursor.execute('SELECT title FROM blog')
        rec = []
        for c in self.cursor:
            rec.append(c[0])
        return rec


server = Flask(__name__)
conn = None
metrics = PrometheusMetrics(server)
instance_uuid = uuid.uuid4()


@server.route('/')
def listBlog():
    global conn, instance_uuid
    if not conn:
        conn = DBManager(password_file='/etc/secrets/db-password')
        conn.populate_db()
    rec = conn.query_titles()

    response = f'Instance UUID: {instance_uuid}\n'
    for c in rec:
        response = response + '<div>   Hello wd  ' + c + '</div>'
    return response


if __name__ == '__main__':
    server.run()
