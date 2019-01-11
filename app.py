"""Display the queue.

The user will be able to view, queue, dequeue.
"""
import flask
import pickle
import redis
from flask import Flask, render_template, request, redirect, session
from customer_queue import CustomerQueueLL, Customer
from time import gmtime, time
from redis import Redis
import uuid

app = Flask(__name__)
# redis = Redis(host='localhost', port=6379, db=0)
redis = redis.from_url(os.environ['REDISCLOUD_URL'])
app.secret_key = 'secret'
app.config['REDIS_QUEUE_KEY'] = 'my_queue'

# These hard-coded stuff will be moved once I complete the implementations of Redis with Flask.
app.customer_queue = CustomerQueueLL()
app.customer_queue.append(Customer('Alan', 2, False))
app.customer_queue.append(Customer('Braus', 4, True))
app.customer_queue.append(Customer('Caroline', 12, True))

redis.set('c_q', pickle.dumps(app.customer_queue))

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
    # print(pickle.loads(redis.get('c_q')))
    customer_queue = pickle.loads(redis.get('c_q'))
    if request.method == 'POST':
        if 'uid' in session:
            new_customer = Customer(request.form.get('name'), request.form.get('party-num'), uid=session['uid'])
            customer_queue.find_by_uid_and_update(session['uid'], new_customer)
        else:
            new_customer = Customer(request.form.get('name'), request.form.get('party-num'))
            print(request.form)
            customer_queue.append(new_customer)
            session['uid'] = new_customer.uid
        redis.set('c_q', pickle.dumps(customer_queue))
        return redirect('/queue')

    elif request.method == 'DELETE':
        if 'uid' in session:
            customer_queue.delete_by_uid(session['uid'])
        redis.set('c_q', pickle.dumps(customer_queue))
        return redirect('/queue')

    elif request.method == 'PUT':
        if 'uid' in session:
            target = customer_queue.find(lambda x: x.uid == session['uid'])
            if target:
                target.present = not target.present
            # new_customer = Customer(request.form.get('name'), request.form.get('party-num'), present=True, uid=session['uid'])
            # app.customer_queue.find_by_uid_and_update(session['uid'], new_customer)
        redis.set('c_q', pickle.dumps(customer_queue))
        return redirect('/queue')

    else:
        print(session)
        return render_template('index.html', queue = customer_queue, cur = app.currently_serving)


@app.route('/queue/new')
def show_enqueue_form():
    return render_template('queue_form.html')


@app.route('/admin')
def admin_panel():
    customer_queue = pickle.loads(redis.get('c_q'))
    return render_template('admin.html', queue = customer_queue, cur = app.currently_serving)


@app.route('/admin/next')
def process_next():
    customer_queue = pickle.loads(redis.get('c_q'))
    processing = customer_queue.find_next_eligible()
    if not processing:
        return redirect('/admin')
    print(processing.name)
    processing.exp = time() + 300
    app.currently_serving[processing.uid] = processing
    print('expiring at ', app.currently_serving[processing.uid].exp)
    return redirect('/admin')


@app.route('/admin/finish')
def finish():
    customer_queue = pickle.loads(redis.get('c_q'))
    customer_queue.delete_by_uid(uuid.UUID(request.args.get('finish')))
    del app.currently_serving[uuid.UUID(request.args.get('finish'))]
    redis.set('c_q', pickle.dumps(customer_queue))
    return redirect('/admin')
