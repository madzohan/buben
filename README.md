# Buben
## python dev test task
### local deployment using Docker & docker-compose:

<ol><li><strong>Required (tested) software versions:</strong>
<pre>Docker version 19.03.13, build 4484c46d9d
docker-compose version 1.27.4, build 40524192</pre></li>
<li>Create <code>.env</code> file in root project directory within populated ...
<ol><li>api settings:
    <pre><code>FLASK_ENV=development
FLASK_DEBUG=true
SQLALCHEMY_ECHO=true
POSTGRES_USER=postgres
POSTGRES_PASSWORD=1111
POSTGRES_DB=postgres</code></pre></li>
</ol></li></ol>