import sqlite3
from bottle import route, run, debug, template, request, static_file, error

@route('/')
def entrypoint():
    return static_file('index.html', root='.')

#list existing items
@route('/todo')
def todo_list():
	conn = sqlite3.connect('todo.db')
	c = conn.cursor()
	c.execute("SELECT id, task FROM todo WHERE status LIKE '1'")
	result = c.fetchall()
	c.close()
	output = template('make_table', rows=result)
	return output

#create a new item
@route('/new', method='GET')
def new_item():

	#can also use request.POST if the form template uses POST
	if request.GET.save:
		new = request.GET.task.strip()
		conn = sqlite3.connect('todo.db')
		c = conn.cursor()

		c.execute("INSERT INTO todo (task,status) VALUES (?,?)", (new,1))
		new_id = c.lastrowid

		conn.commit()
		c.close()

		return '<p>The new task was inserted into the database, the ID is %s. <a href="/todo">Back to overview</a></p>' % new_id
	else:
		return template('new_task.tpl')	

#edit an existing item, parse the id from the url
@route('/edit/<no:int>', method='GET')
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

		return '<p>Item number %s was successfully updated. <a href="/todo">Back to overview</a></p>' % no
	else:
		conn = sqlite3.connect('todo.db')
		c = conn.cursor()
		c.execute("SELECT task FROM todo WHERE id LIKE ?", (str(no),))
		cur_data = c.fetchone()
		
		if cur_data:
			return template('edit_task', old=cur_data, no=no)
		else:
			return '<p>Item number %s does not seem to exist</p>' % no

#static help page
@route('/help')
def help():
    return static_file('help.html', root='.')

#demonstrates dynamic regex route and raw json output
@route('/json<json:re:[0-9]+>')
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
@error(403)
def mistake403(code):
    return 'The parameter you passed has the wrong format!'

@error(404)
def mistake404(code):
    return 'Sorry, this page does not exist!'

#verbose errors
debug(True)
#default localhost:8080
run(reloader=True)