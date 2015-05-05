import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing


DATABASE = 'hw13.db'
DEBUG = False
SECRET_KEY = 'aZ\xbe\xd7\x17\x9f\xb6\x01\x9d\xaaf\xf4x\xfb\xfe'
USERNAME = 'admin'
PASSWORD = 'password'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

connect_db()
init_db()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
        
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You are logged in')
            return redirect(url_for('show_tests'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_tests'))

@app.route('/dashboard')
def show_tests():
    cur1 = g.db.execute('select ID, firstName, lastName from Students')
    students = [dict(firstName=row[1],lastName=row[2]) for row in cur1.fetchall()]
    cur2 = g.db.execute('select ID, subject, questions, testDate from Quizzes')
    quizzes = [dict(subject=row[1],questions=row[2],testDate=row[3])
                    for row in cur2.fetchall()]
    return render_template('show_tests.html'
                           , students=students
                           , quizzes=quizzes)

@app.route('/student/add', methods=['GET','POST'])
def add_student():
    if request.method == 'POST':
        if not session.get('logged_in'):
            abort(401)
        g.db.execute('insert into Students (firstName, lastName) values (?, ?)',
                     [request.form['firstName'], request.form['lastName']])
        g.db.commit()
        flash('New student successfully posted')
        return redirect(url_for('show_tests'))
    return render_template('add_student.html')

@app.route('/student/<id>')
def student_results(id):
    msg = None
    cur = g.db.execute('select quiz, grade from Results where student=?',
                       (id,))
    results = [dict(quiz=row[0],grade=row[1]) for row in cur.fetchall()]
    if not results:
        msg = 'No results'
    return render_template('student_results.html',results=results,msg=msg)

@app.route('/quiz/add', methods=['GET','POST'])
def add_quiz():
    if request.method == 'POST':
        if not session.get('logged_in'):
            abort(401)
        g.db.execute('insert into Quizzes (subject'\
                                     ', questions, testDate) '\
                                     'values (?, ?, ?)',
                     [request.form['subject']
                      , request.form['questions']
                      , request.form['testDate']])
        g.db.commit()
        flash('New quiz successfully posted')
        return redirect(url_for('show_tests'))
    return render_template('add_quiz.html')

@app.route('/results/add', methods=['GET','POST'])
def add_result():
    cur1 = g.db.execute('select ID from Students')
    students = [dict(ID=row[0]) for row in cur1.fetchall()]
    cur2 = g.db.execute('select ID from Quizzes')
    quizzes = [dict(ID=row[0]) for row in cur2.fetchall()]
    if request.method == 'POST':
        if not session.get('logged_in'):
            abort(401)
        g.db.execute(
    'insert into Results (quiz,student,grade) values (?,?,?)',
    (
        request.form.get('Quiz'),
        request.form.get('Student'),
        request.form.get('grade')
    )
    )
        g.db.commit()
        flash('New result successfully posted')
        return redirect(url_for('show_tests'))
    return render_template('add_result.html',students=students,quizzes=quizzes)
if __name__ == '__main__':
    app.run()
