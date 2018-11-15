from flask import (
    Blueprint, 
    request,
    render_template, 
    flash,
    g, 
    session,
    redirect,
    url_for
)
from app.mod_tests.models import (
    Type,
    Subject,
    Node
)
from app.mod_auth.models import User
from app.handlers import db
from app.mod_tests.forms import ResponseForm
from app.mod_tests.helpers import get_node_file_path

mod_tests = Blueprint('tests',
                      __name__,
                      url_prefix='/tests')

@mod_tests.route('/dashboard', methods=['GET'])
def dashboard():
    subjects = Subject.query.order_by(Subject.id).all()

    return render_template('tests/test_dashboard.html', subjects = subjects)

@mod_tests.route('/<string:subject_name>', methods=['GET'], defaults={'node_id': None})
@mod_tests.route('/<string:subject_name>/<int:node_id>', methods=['GET'])
def subject_test(subject_name, node_id):
    subject_name = subject_name.replace('+', ' ')
    subject      = Subject.query.filter_by(name = subject_name).first()

    if subject is None:
        return render_template('404.html')

    try:
        if node_id is None:
            node = list(filter(lambda x: x.parent_node == 0, subject.nodes))[0]
        else: 
            node = list(filter(lambda x: x.id == node_id, subject.nodes))[0]
    except IndexError as ie:
        return render_template('404.html')

    child_nodes = Node.query.filter_by(parent_node=node.id).all()
    if len(child_nodes) > 0:
        try:
            node_code = open(get_node_file_path(subject_name, node.id), 'r').read()
        except FileNotFoundError as fnfe:
            return render_template('404.html')

        tree_data = {
            "code"        : node_code,
            "subject"     : subject.name,
            "children"    : child_nodes,
            "current_node": node.id
        }

        form = ResponseForm()
        form.answered_node.choices = [(node.id, node.answer_parent) for node in child_nodes]
        
        return render_template('tests/test.html', 
                               branch = tree_data, 
                               form = form)
    
    return redirect(url_for('tests.dashboard'))

@mod_tests.route('/validate-response', methods=['POST'])
def validate_route():
    form    = ResponseForm(request.form)
    subject = Subject.query.filter_by(name = form.subject_name.data).first()
    node    = list(filter(lambda x: x.id == int(form.current_node.data), subject.nodes))[0]

    child_nodes = Node.query.filter_by(parent_node=node.id).all()
    form.answered_node.choices = [(node.id, node.answer_parent) for node in child_nodes]
    if form.validate_on_submit():
        return redirect(url_for('tests.subject_test', 
                                subject_name = form.subject_name.data,
                                node_id      = form.answered_node.data))

    return redirect(url_for('tests.subject_test', 
                            subject_name = form.subject_name.data,
                            node_id      = None))
