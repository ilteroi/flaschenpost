import sqlite3
from bottle import Bottle, route, run, debug, template, request, static_file, error, redirect
from paste import httpserver

app = Bottle()

#alternative middleware, needs a redis server ...
#from drsession import SessionMiddleware
#sessionname = 'drsession'
#sessionapp = SessionMiddleware(app,sessionstore)

#alternative middleware
#from secure_cookie.sessions import SessionMiddleware, FilesystemSessionStore
#sessionname = 'secure_cookie.session'
#sessionapp = SessionMiddleware(app,FileSystemSessionStore())

from beaker.middleware import SessionMiddleware
sessionname = 'beaker.session'
sessionopts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': '.',
    'session.auto': True
}
sessionapp = SessionMiddleware(app,sessionopts)

@app.hook('before_request')
def setup_session():
  request.session = request.environ.get(sessionname)

def login_valid(user, password):
	#fixme: store passwords in salted and hashed form!
	conn = sqlite3.connect('users.db')
	c = conn.cursor()
	c.execute("SELECT password FROM users WHERE name like ?", (user,))
	result = c.fetchone()
	c.close()
	return result and result[0] == password

def have_user():
	return 'activeuser' in request.session and request.session['activeuser'] != ''

@app.route('/')
def entrypoint():
	conn = sqlite3.connect('users.db')
	c = conn.cursor()
	c.execute("SELECT name FROM users")
	result = c.fetchall()
	c.close()
	
	if have_user():
		return template('index', summary='You are %s' % request.session['activeuser'], rows=result)
	else:
		redirect('/login')

@app.route('/login', method='GET')
def login():
	return static_file('login.html', root='.')

@app.route('/login', method='POST')
def check_login():
	username = request.forms.get('username')
	password = request.forms.get('password')
	if login_valid(username, password):
		request.session['activeuser'] = username
		return "<p>Your login information was correct.</p><p><a href='/'>to overview</a></p>"
	else:
		request.session['activeuser'] = ''
		return "<p>Login failed.</p><p><a href='/login'>try again</a></p>"

@app.route('/logout')
def logout():
	request.session['activeuser'] = ''
	return "<p>You're no longer logged in</p>"
	
#just for debugging
@app.route('/auth')
def auth_check():
	return ['hooray, you are authenticated! your info is: {}'.format(request.auth)]

#list existing items
@app.route('/todo')
def todo_list():
	conn = sqlite3.connect('todo.db')
	c = conn.cursor()
	c.execute("SELECT id, task FROM todo WHERE status LIKE '1'")
	result = c.fetchall()
	c.close()
	return template('make_table', summary='all open items', rows=result)

@app.route('/todo/<user>', method='GET')
def todo_list_user(user):
	conn = sqlite3.connect('todo.db')
	c = conn.cursor()
	c.execute("SELECT id, task FROM todo WHERE owner LIKE ?", (user,))
	result = c.fetchall()
	c.close()
	return template('make_table', summary='all items for user %s' % user, rows=result)

#create a new item
@app.route('/new', method='GET')
def new_item():

	#can also use request.POST if the form template uses POST
	if request.GET.save:
		text = request.GET.task.strip()
		conn = sqlite3.connect('todo.db')
		c = conn.cursor()

		c.execute("INSERT INTO todo (owner,task,status) VALUES (?,?,?)", (request.auth[0],text,1))
		new_id = c.lastrowid

		conn.commit()
		c.close()

		return '<p>The new task was inserted into the database, the ID is %s. <a href="/todo">Back to overview</a></p>' % new_id
	else:
		return template('new_task.tpl')	

#edit an existing item, parse the id from the url
@app.route('/edit/<no:int>', method='GET')
def edit_item(no):

	if request.GET.save:
		edit = request.GET.task.strip()
		status = request.GET.status.strip()

		if status == 'open':
			status = 1
		else:
			status = 0

		conn = sqlite3.connect('todo.db')
		c = conn.cursor()
		c.execute("UPDATE todo SET task = ?, status = ? WHERE id LIKE ?", (edit, status, no))
		conn.commit()
		c.close()

		return '<p>Item number %s was successfully updated. <a href="/todo">Back to overview</a></p>' % no
	else:
		conn = sqlite3.connect('todo.db')
		c = conn.cursor()
		c.execute("SELECT task FROM todo WHERE owner LIKE ? AND id LIKE ?", (request.auth[0],str(no),))
		result = c.fetchone()
		c.close()
		
		if result:
			return template('edit_task', old=result, no=no)
		else:
			return '<p>Item number %s does not seem to exist, or you don\'t have access rights</p>' % no

#static help page
@app.route('/help')
def help():
	return static_file('help.html', root='.')

#demonstrates dynamic regex route and raw json output
@app.route('/json<json:re:[0-9]+>')
def show_json(json):
	conn = sqlite3.connect('todo.db')
	c = conn.cursor()
	c.execute("SELECT task FROM todo WHERE id LIKE ?", (json,))
	result = c.fetchall()
	c.close()

	if not result:
		return {'task': 'This item number does not exist!'}
	else:
		return {'task': result[0]}

#simple error handling
@app.error(403)
def mistake403(code):
	return 'The parameter you passed has the wrong format!'

@app.error(404)
def mistake404(code):
	return 'Sorry, this page does not exist!'

#----------------------------------------------------------------------------------------------

#verbose errors
debug(True)
#default localhost:8080
#run(reloader=True)
#run(port=8080, host='192.168.1.35')

#-------------------------------
httpserver.serve(sessionapp, host='0.0.0.0', port=8080)