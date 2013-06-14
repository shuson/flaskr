# all the imports
from __future__ import with_statement
from contextlib import closing
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
	abort, render_template, flash

# configuration
DATABASE = 'flaskr.db'
DEBUG = True
SECRET_KEY = 'none'
USERNAME = 'admin'
PASSWORD = 'admin'

# create our little application :)
app = Flask(__name__)
#app.config.from_envvar('FLASKR_SETTINGS', silent=True)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql') as f:
			db.cursor().executescript(f.read())
		db.commit()

@app.before_request
def before_request():
	g.db = connect_db()

@app.after_request
def after_request(response):
	g.db.close()
	return response

@app.route('/')
def index():
	cur = g.db.execute('select title, text from entries order by id desc')
	entries = [dict(title=row[0],text=row[1]) for row in cur.fetchall()]
	return render_template('index.html',entries=entries)

@app.route('/add')
def add():
	return render_template('add.html')

@app.route('/add_entry',methods=['POST'])
def add_entry():
	g.db.execute("insert into entries (title,text) values (?,?)",[request.form['title'].strip(),request.form['text'].strip()])
	g.db.commit()
	flash('Create successfully!!')
	return redirect(url_for('index'))

@app.route('/title_validation/',methods=['POST'])
def title_validation():
	title = request.form['title']
	if title == '':
		return 'N'
	cur = g.db.execute("select * from entries where title = '%s'" %title)
	if cur.fetchone() is None:
		return "Y"
	else:
		return "N"

@app.route('/delete/<title>')
def delete(title):
	sql = "delete from entries where title = '%s'" %title
	print sql
	g.db.execute(sql)
	g.db.commit()
	flash('deleted!!')
	return redirect(url_for('index'))

@app.route('/edit/<title>')
def edit(title):
	sql = "select text from entries where title = '%s' " %title
	cur = g.db.execute(sql)
	text = cur.fetchone()[0]
	print cur.fetchone()
	return render_template('edit.html',title=title,text=text)

@app.route('/edit_entry',methods=['POST'])
def edit_entry():
	print request.form['title']
	sql = "update entries set text = '%s' where title = '%s'" %(request.form['text'],request.form['title'])
	g.db.execute(sql)
	g.db.commit()
	return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()