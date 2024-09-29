import smtplib
import os
from flask import Flask, render_template, url_for, flash, request, redirect
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, EmailField, SubmitField
from wtforms.validators import DataRequired
from smtplib import SMTP
import requests
import uuid


TODO_API = os.environ['TODO_API']
TODO_ENDPOINT = "https://api.todoist.com/sync/v9/sync"


# creating authorization header
headers = {
    "Authorization": f"Bearer {TODO_API}",
}


# creating function to deal with TODOist sync API
def handler(commands=None):
    data = {
        'token': TODO_API,
        'sync_token': '*',  # Full sync
        'resource_types': ["items"]  # Correctly formatted list
    }
    if commands:
        # Ensure commands are passed as a list, not a set
        if isinstance(commands, set):
            commands = list(commands)
        data['commands'] = commands
    response = requests.post(TODO_ENDPOINT, headers=headers, json=data)  # Use json= instead of data=
    return response.json()


def generate_uuid():
    return str(uuid.uuid4())


class SendLove(FlaskForm):
    subject = StringField("The Subject of Your Love..", validators=[DataRequired()], render_kw={'style': 'width: 100ch'})
    message = TextAreaField("The contents of your heart...", validators=[DataRequired()], render_kw={'style': 'width: 200ch'})
    email = EmailField("Where I can return your affection...", validators=[DataRequired()], render_kw={'style': 'width: 100ch'})
    submit = SubmitField('Send Love xoxo')


SECRET_KEY = os.urandom(32)
app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY
bootstrap = Bootstrap5(app)

# allows me to use the render_form function to render FlaskWTForms

@app.route('/')
def home():
    return render_template('index.html')

# TODO Add FAQ page

@app.route('/FAQs')
def faqs():
    return render_template('faqs.html')

# TODO Add email page with FLask WTForm -- UPDATE: DEPRECATED
@app.route('/singsingsing', methods=['GET', 'POST'])
def praises():
    form = SendLove()
    if form.validate_on_submit():
        try:
            with smtplib.SMTP('mail.idhoops.com', port=587) as server:
                server.starttls()
                # server.login(user='chris@idhoops.com', password=PASS)
                server.sendmail(from_addr='chris@idhoops.com', to_addrs='johncena2930@yahoo.com',
                                msg=f"\r\nSubject: {form.subject.data}\r\n\r\n"
                                    f"{form.message.data}\r\n\r\n"
                                    f"Sent from: {form.email.data}")
            flash("Your message has been sent. Please prepare a burnt offering for a quicker reply.")
        except Exception as e:
            flash(f"An error occurred: {e}")
        return render_template('praises.html', form=form)

    else:
        return render_template('praises.html', form=form)

@app.route('/feats')
def feat():
    return render_template('index.html')

# TODO Have 'Feats of Strength' tab scroll down to the marketing section[DONE]

@app.route('/feats/chest')
def chest():
    return render_template('chest.html')

@app.route('/feats/legs')
def legs():
    return render_template('legs.html')

@app.route('/feats/back')
def back():
    return render_template('back.html')

@app.route('/todo', methods=["GET", "POST"])
def todo():
    if request.method == 'POST':
        action = request.form["action"]
        todo_id = request.form.get('todo_id')
        content = request.form.get('content')

        if action == 'add':
            command = [{
                'type': 'item_add',
                'uuid': generate_uuid(),
                'temp_id': 'temp_id',
                'args': {'content': content}
            }]

            # Edit an existing todo
        elif action == 'edit' and todo_id:
            command = [{
                'type': generate_uuid(),
                'uuid': generate_uuid(),
                'args': {'id': int(todo_id), 'content': content}
            }]

            # Delete a todo
        elif action == 'delete' and todo_id:
            command = [{
                'type': 'item_delete',
                'uuid': generate_uuid(),
                'args': {'ids': [int(todo_id)]}
            }]


            # Complete a todo
        elif action == 'complete' and todo_id:
            command = [{
                'type': 'item_complete',
                'uuid': generate_uuid(),
                'args': {'ids': [int(todo_id)]}
            }]

            # Sync with Todoist
        try:
            response = handler(commands=command)
            print(response)
            if 'error' in response:
                print(f"Todoist API Error: {response['error']}")
        except Exception as e:
            print(f"Error syncing with Todoist: {e}")
        return redirect(url_for('todo'))
    else:
        data = handler()
        todos = data.get('items', [])
        return render_template('todo.html', todos=todos)



# TODO: Add some kind of API integration w/ Todoist API
# TODO: Maybe add a shop type thing (what does Angela even mean by that???)

if __name__ == "__main__":
    app.run(debug=True)