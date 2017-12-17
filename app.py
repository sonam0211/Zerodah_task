import cherrypy,zipfile, io
import redis
import os
import subprocess

from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))

def redis_mass_insertion():
    ps = subprocess.Popen(('python', 'redis_commands.py'), stdout=subprocess.PIPE)
    output = subprocess.check_output(('redis-cli', '--pipe'), stdin=ps.stdout)

def top_stocks():
    r = redis.StrictRedis(decode_responses=True, host='localhost', port=6379, db=0)
    r.flushall()
    redis_mass_insertion()
    top_stocks = r.zrevrange(name='open', start=0, end=9, withscores=True )
    data = []
    for stock in top_stocks:
        data.append(r.hgetall(int(stock[0])))
    return data


class Root:
    @cherrypy.expose
    def index(self):
        data = top_stocks()
        tmpl = env.get_template('index.html')
        return tmpl.render(data = data)

conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/generator': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }

webapp = Root()
cherrypy.quickstart(webapp, '/', conf)
