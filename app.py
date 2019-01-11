"""Display the queue.

The user will be able to view, queue, dequeue.
"""
import flask
from flask import Flask, render_template, request, redirect, session
from customer_queue import CustomerQueueLL, Customer
from time import gmtime, time
import uuid

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.customer_queue = CustomerQueueLL()
app.customer_queue.append(Customer('Alan', 2, False))
app.customer_queue.append(Customer('Braus', 4, True))
app.customer_queue.append(Customer('Caroline', 12, True))
app.currently_serving = {}


@app.before_request
def before_request():
    method = request.form.get('_method', '').upper()
    if method:
        request.environ['REQUEST_METHOD'] = method
        ctx = flask._request_ctx_stack.top
        ctx.url_adapter.default_method = method
        assert request.method == method


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r
    

@app.route('/queue', methods = ['GET', 'POST', 'DELETE', 'PUT'])
def view_queue():

    if request.method == 'POST':
        if 'uid' in session:
            new_customer = Customer(request.form.get('name'), request.form.get('party-num'), uid=session['uid'])
            app.customer_queue.find_by_uid_and_update(session['uid'], new_customer)
        else:
            new_customer = Customer(request.form.get('name'), request.form.get('party-num'))
            print(request.form)
            app.customer_queue.append(new_customer)
            session['uid'] = new_customer.uid
        return redirect('/queue')

    elif request.method == 'DELETE':
        if 'uid' in session:
            app.customer_queue.delete_by_uid(session['uid'])
        return redirect('/queue')

    elif request.method == 'PUT':
        if 'uid' in session:
            target = app.customer_queue.find(lambda x: x.uid == session['uid'])
            if target:
                target.present = not target.present
            # new_customer = Customer(request.form.get('name'), request.form.get('party-num'), present=True, uid=session['uid'])
            # app.customer_queue.find_by_uid_and_update(session['uid'], new_customer)
        return redirect('/queue')

    else:
        print(session)
        return render_template('index.html', queue = app.customer_queue, cur = app.currently_serving)


@app.route('/queue/new')
def show_enqueue_form():
    return render_template('queue_form.html')


@app.route('/admin')
def admin_panel():
    return render_template('admin.html', queue = app.customer_queue, cur = app.currently_serving)


@app.route('/admin/next')
def process_next():
    processing = app.customer_queue.find_next_eligible()
    if not processing:
        return redirect('/admin')
    print(processing.name)
    processing.exp = time() + 300
    app.currently_serving[processing.uid] = processing
    print('expiring at ', app.currently_serving[processing.uid].exp)
    return redirect('/admin')


@app.route('/admin/finish')
def finish():
    app.customer_queue.delete_by_uid(uuid.UUID(request.args.get('finish')))
    del app.currently_serving[uuid.UUID(request.args.get('finish'))]
    return redirect('/admin')
