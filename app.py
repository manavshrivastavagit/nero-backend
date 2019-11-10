# app.py
from flask import Flask, request, jsonify
import os
import dialogflow
import pandas as pd
import psycopg2
import requests
from flask_cors import CORS
from engine import decision
from exception.employee_not_found import EmployeeNotFound
from exception.account_not_found import AccountNotFound

# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\SridharRamakrishnanI\\Development\\github\\nero-heroku-python\\NERO-95a41ac7c5b2.json"

url = requests.utils.urlparse(
        'postgres://uadqvrzvvhsgvl:76e9e53176d897f8bb1290fec47bcdde69043710aecb602067de96961e1c7bc0@ec2-107-21-126-201.compute-1.amazonaws.com:5432/d7d2gs1qbqj579')

db = "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname)

print(url.path)
print(url.username)
conn = psycopg2.connect(db)

app = Flask(__name__)
CORS(app)

@app.route('/getmsg/', methods=['GET'])
def respond():
    # Retrieve the name from url parameter
    name = request.args.get("name", None)

    # For debugging
    print("got name: " + name)

    response = {}

    # Check if user sent a name at all
    if not name:
        response["ERROR"] = "no name found, please send a name."
    # Check if the user entered a number not a name
    elif str(name).isdigit():
        response["ERROR"] = "name can't be numeric."
    # Now the user entered a valid name
    else:
        response["MESSAGE"] = "Welcome "+ name +" to our awesome platform!!"

    # Return the response in json format
    return jsonify(response)

@app.route('/post/', methods=['POST'])
def post_something():
    param = request.form.get('name')
    print(param)
    # You can add the test cases you made in the previous function, but in our case here you are just testing the POST functionality
    if param:
        return jsonify({
            "Message": "Welcome {name} to our awesome platform!!",
            # Add this option to distinct the POST request
            "METHOD" : "POST"
        })
    else:
        return jsonify({
            "ERROR": "no name found, please send a name."
        })

@app.route('/getallemployees', methods=['GET'])
def get_all_employee_names():
    print('Connected to Heroku')
    cur = conn.cursor()
    try:
        cur.execute("""SELECT first_name, last_name from public.enq_emp_details""")
        rows = cur.fetchall()
        employee_list = []
        for row in rows:
            employee_list.append(row[0])
        return jsonify(results = employee_list )
    except Exception as e:
        return jsonify(e)


@app.route('/getenqueroaccounts', methods=['GET'])
def get_enquero_accounts():
    cur = conn.cursor()
    try:
        cur.execute("""select count(account) from (select distinct account from public.enq_emp_details) a """)
        account_count = cur.fetchall()
        return jsonify(result = account_count)
    except Exception as e:
        return jsonify(e)


@app.route('/getprojectname', methods=['GET'])
def get_project_name():
    firstname = request.args.get('firstname')
    lastname = request.args.get('lastname')
    cur = conn.cursor()
    try:
        cur.execute("""select account from public.enq_emp_details where lower(first_name) = '%s' and lower(last_name) = '%s' """ % (firstname.lower(), lastname.lower()))
        account_name = cur.fetchall()
        return jsonify(result=account_name)
    except Exception as e:
        return jsonify(e)


@app.route('/getjoiningdate', methods=['GET'])
def get_hire_date():
    firstname = request.args.get('firstname')
    lastname = request.args.get('lastname')
    cur = conn.cursor()
    try:
        cur.execute("""select hire_date from public.enq_emp_details where lower(first_name) = '%s' and lower(last_name) = '%s' """ % (firstname.lower(), lastname.lower()))
        hire_date = cur.fetchall()
        return jsonify(result = hire_date)
    except Exception as e:
        return jsonify(e)

@app.route('/getbusinessunit', methods=['GET'])
def get_business_unit():
    firstname = request.args.get('firstname')
    lastname = request.args.get('lastname')
    cur = conn.cursor()
    try:
        cur.execute("""select business_unit_description from public.enq_emp_details where lower(first_name) = '%s' and lower(last_name) = '%s' """ % (firstname.lower(), lastname.lower()))
        business_unit = cur.fetchall()
        return jsonify(result=business_unit)
    except Exception as e:
        return jsonify(e)

@app.route('/location', methods=['GET'])
def get_location():
    firstname = request.args.get('firstname')
    lastname = request.args.get('lastname')
    cur = conn.cursor()
    try:
        cur.execute("""select location_description from public.enq_emp_details where lower(first_name) = '%s' and lower(last_name) = '%s' """ % (firstname.lower(), lastname.lower()))
        location = cur.fetchall()
        return jsonify(result=location)
    except Exception as e:
        return jsonify(e)


@app.route('/getpractielead', methods=['GET'])
def get_practice_lead():
    firstname = request.args.get('firstname')
    lastname = request.args.get('lastname')
    cur = conn.cursor()
    try:
        cur.execute("""select practice_lead from public.enq_emp_details where lower(first_name) = '%s' and lower(last_name) = '%s' """ % (firstname.lower(), lastname.lower()))
        practice_lead = cur.fetchall()
        return jsonify(result=practice_lead)
    except Exception as e:
        return jsonify(e)


@app.route('/countbybusinesstitle', methods=['GET'])
def count_by_business_title():
    cur = conn.cursor()
    title = request.args.get('title')
    try:
        cur.execute("""select count(*) from public.enq_emp_details where lower(business_title) = '%s' """ % (title.lower()))
        count = cur.fetchall()
        return jsonify(result=count)
    except Exception as e:
        return jsonify(e)


@app.route('/largestaccount', methods=['GET'])
def largest_account():
    cur = conn.cursor()
    try:
        cur.execute("""select account from (select account, count(*) c from public.enq_emp_details group by account order by c desc) a  limit 1""" )
        account = cur.fetchall()
        return jsonify(result=account)
    except Exception as e:
        return jsonify(e)


@app.route('/bucount/', methods=['GET'])
def count_under_bu():
    cur = conn.cursor()
    bu = request.args.get('bu')
    try:
        cur.execute("""select count(*) from public.enq_emp_details where lower(business_unit_description) = '%s' """  %  (bu.lower()))
        bu_count = cur.fetchall()
        return jsonify(result=bu_count)
    except Exception as e:
        return jsonify(e)


@app.route('/reporteecount', methods=['GET'])
def reportee_count():
    reporting_lead = request.args.get('reporting_lead')
    cur = conn.cursor()
    try:
        cur.execute("""select payroll_name from public.enq_emp_details where lower(reporting_lead) = '%s' """ % (reporting_lead.lower()))
        rp_count = cur.fetchall()
        return jsonify(result=rp_count)
    except Exception as e:
        return jsonify(e)


@app.route('/getreportingmanager', methods=['GET'])
def get_reporting_manager():
    cur = conn.cursor()
    first_name = request.args.get('firstname')
    last_name = request.args.get('lastname')
    try:
        stm = "select reporting_lead from public.enq_emp_details where lower(first_name) = '%s' and lower(last_name) = '%s' " % (first_name.lower(), last_name.lower())
        cur.execute(stm)
        reporting_manager = cur.fetchall()
        if len(reporting_manager) == 0:
            raise EmployeeNotFound
        return jsonify(result = reporting_manager )
    except EmployeeNotFound as e:
        return jsonify('No employee found by that name')
    except Exception as e:
        return jsonify(e)


@app.route('/getaccountheadcount', methods=['GET'])
def get_account_head_count(account):
    cur = conn.cursor()
    try:
        stm = "select count(*) from public.enq_emp_details where lower(account) = '%s' " % (account.lower())
        cur.execute(stm)
        account_head_count = cur.fetchall()
        if len(account_head_count) == 0:
            raise AccountNotFound
        return jsonify(result = account_head_count )
    except AccountNotFound as e:
        return jsonify('No account found by that name')
    except Exception as e:
        return jsonify(e)


@app.route('/getteammembers', methods=['GET'])
def get_team_members():
    myfirstname = request.args.get('firstname')
    mylastname = request.args.get('lastname')
    cur = conn.cursor()
    try:
        query = "select account, business_unit_description, reporting_lead, delivery_lead from public.enq_emp_details where lower(first_name) = '%s' and lower(last_name) = '%s'" % (myfirstname, mylastname)
        df = pd.read_sql_query(query, conn)
        team_member_query = "select concat(first_name, ' ' , last_name) from public.enq_emp_details where lower(account) = '%s'  and lower(business_unit_description) = '%s' and lower(reporting_lead) = '%s' and lower(delivery_lead) = '%s' and lower(first_name) != '%s' and lower(last_name) != '%s' " % (df['account'][0].lower(), df['business_unit_description'][0].lower(), df['reporting_lead'][0].lower(), df['delivery_lead'][0].lower(), myfirstname.lower(), mylastname.lower())
        print(team_member_query)
        cur.execute(team_member_query)
        team_members = cur.fetchall()
        return jsonify(result=team_members)
    except Exception as e:
        return e



@app.route('/validuser', methods=['GET'])
def isvaliduser():
    first_name = request.args.get('firstname')
    last_name = request.args.get('lastname')
    cur = conn.cursor()
    try:
        stm = "select first_name, last_name from public.enq_emp_details where lower(first_name) = '%s' and lower(last_name) = '%s' " % (first_name.lower(), last_name.lower())
        cur.execute(stm)
        emp = cur.fetchall()
        if len(emp) == 0:
            raise EmployeeNotFound
        return jsonify(result = emp )
    except EmployeeNotFound as e:
        return jsonify('No employee found by that name')
    except Exception as e:
        return jsonify(e)

# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>Welcome to our server !!</h1>"

# check DF server connection
@app.route('/api/v1/ask-nero', methods=['GET'])
def askNero():
     # Retrieve the name from url parameter
    query = request.args.get("query", None)
    firstname = request.args.get("firstname", None)
    lastname = request.args.get("lastname", None)
    return detect_intent_texts("nero-sgiuhb", "123", query, firstname, lastname, "en-US" )

# check DF server connection
@app.route('/df', methods=['GET'])
def df():
     # Retrieve the name from url parameter
     # query = request.args.get("query", None)
    return detect_intent_texts("nero-sgiuhb", "123", "Hi", "en-US" )    


def detect_intent_texts(project_id, session_id, texts, firstname, lastname, language_code):
    """Returns the result of detect intent with texts as inputs.

    Using the same `session_id` between requests allows continuation
    of the conversation."""
    
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)
    print('Session path: {}\n'.format(session))

    
    text_input = dialogflow.types.TextInput(
        text=texts, language_code=language_code)

    query_input = dialogflow.types.QueryInput(text=text_input)

    response = session_client.detect_intent(
        session=session, query_input=query_input)

    res = decision.response_parser(response, firstname, lastname)

    # print('=' * 20)
    # # print('Query text: {}'.format(response.query_result.query_text))
    # print('Query text: {}'.format(response.query_result.query_text))
    # print('Detected intent: {} (confidence: {})\n'.format(
    #     response.query_result.intent.display_name,
    #     response.query_result.intent_detection_confidence))
    # print('Fulfillment text: {}\n'.format(
    #     response.query_result.fulfillment_text))
    # print('Fulfillment query_result: {}\n'.format(
    #     response.query_result))
    # print (json.dumps(response, indent=2))
    return res

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(debug=True, port=5000)