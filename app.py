from flask import Flask, request
from flask import render_template
from flask import jsonify
from datetime import datetime
from fhirclient_file import *
from data_helpers import *
from jinja2 import Environment

import pandas
import simplejson
import ipdb
#import json

app = Flask(__name__)
jinja_env = Environment(extensions=['jinja2.ext.loopcontrols'])
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

programs = [{ 'program': 'YMCA',
'refer_count': 257,
'accept_rate': 79,
'reject_rate': 21,
'address': '1234 5th Ave. Apple, AB'
},
{ 'program': 'FitPlus',
'refer_count': 197,
'accept_rate': 64,
'reject_rate': 36,
'address': '678 B Street Bananas, CD'
},
{ 'program': 'HealthEdu',
'refer_count': 207,
'accept_rate': 61,
'reject_rate': 39,
'address': '901 Front St. Coconut, EF'
}]

#Jinja custome filter
@app.template_filter()
def to_obj(value):
    return (eval(str(value)))

#Route Functions
@app.route('/')
def generate_homepage():
    #TODO Change index.html to page that frontend client will be and then we can serve that
    return render_template('index.html',title='Home',user="ElvisPresley")

@app.route('/patient', methods=['GET'])
def generate_patientpage():
    user_id = request.args.get('user_id')
    condition = request.args.get('conditions')
    patient_data = get_patient_data_for_patient_page(user_id, condition)
    a1c_data,groups,min_max_age=get_population_results_for('a1c',patient_data['race'], patient_data['gender'], patient_data['marital_status'], patient_data['age'])
    bmi_data,groups,min_max_age=get_population_results_for('bmi',patient_data['race'], patient_data['gender'], patient_data['marital_status'], patient_data['age'])
    sbp_data,groups,min_max_age=get_population_results_for('sbp',patient_data['race'], patient_data['gender'], patient_data['marital_status'], patient_data['age'])
    dbp_data,groups,min_max_age=get_population_results_for('dbp',patient_data['race'], patient_data['gender'], patient_data['marital_status'], patient_data['age'])
    refer_link='/refer?user_id=' + user_id + '&conditions=' + condition
    marital_status_dict = {'A': 'Annulled', 'D': 'Divorced', 'I': 'Interlocutory', 'L': 'Legally Separated', 'M': 'Married', 'P': 'Polygamous', 'S': 'Never Married', 'T': 'Domestic Partner', 'W': 'Widowed'}
    return render_template('patient.html',
        a1c_data=a1c_data,
        bmi_data=bmi_data,
        sbp_data=sbp_data,
        dbp_data=dbp_data,
        groups=groups,
        name=patient_data['name'],
        diagnosis=" ".join(map(lambda k: k[0].title().replace('_', ' '), filter(lambda k: k[1], patient_data['conditions'].items()))),
        selected_condition=condition.replace('_', ' '),
        race=patient_data['race'],
        age=patient_data['age'],
        marital_status=patient_data['marital_status'],
        marital_status_full=marital_status_dict[patient_data['marital_status']],
        a1c_reading=patient_data['a1c'],
        systolic_bp=patient_data['systolic_bp'],
        diastolic_bp=patient_data['diastolic_bp'],
        bmi=patient_data['bmi'],
        gender=patient_data['gender'].title(),
        refer_link=refer_link,
        programs = programs,
        minage = min_max_age[0],
        maxage = min_max_age[1]
        )

@app.route('/refer')
def generate_referform():
    user_id = request.args.get('user_id')
    condition = request.args.get('conditions')
    program = request.args.get('program')
    refer_program = ""
    for p in programs:
        if p["program"]==program:
            refer_program=p
    patient_data = get_patient_data_for_patient_page(user_id, condition)
    return render_template('refer.html',
        name=patient_data['name'],
        diagnosis=" ".join(map(lambda k: k[0].title().replace('_', ' '), filter(lambda k: k[1], patient_data['conditions'].items()))),
        selected_condition=condition.replace('_', ' '),
        race=patient_data['race'],
        age=patient_data['age'],
        marital_status=patient_data['marital_status'],
        a1c_reading=patient_data['a1c'],
        systolic_bp=patient_data['systolic_bp'],
        diastolic_bp=patient_data['diastolic_bp'],
        bmi=patient_data['bmi'],
        gender=patient_data['gender'].title(),
        current_date=datetime.now().date().strftime("%m/%d/%Y"),
        refer_program=refer_program,
        user_id=user_id
        )

@app.route('/submit', methods=['POST'])
def process_referform():
    user_id = request.form.get('user_id')
    diagnosis = request.form.get('referDiagnosis')
    program = request.form.get('referProgram')
    reason = request.form.get('referReason')
    refersrc = request.form.get('referGroup')
    referdr = request.form.get('referBy')
    requester = {"agent" : referdr,"onBehalfOf" : refersrc}
    ref_obj = {
        'resourceType':'ReferralRequest',
        'authoredOn':datetime.now().date().strftime("%m/%d/%Y"),
        'occurrencePeriod':"6 Months",
        'status':"active",
        'intent':"order",
        'priority':"routine",
        'reasonReference':diagnosis,
        'description':reason,
        'requester':requester,
        'recipient':program,
        'subject':user_id
    }
    return  render_template('submit.html',
        ref_obj=ref_obj
    )

@app.route('/referrals/user/user_id=<user_id>')
def has_referrals(user_id):
    return jsonify(results=condition_check(user_id))


if __name__ == '__main__':
    #Leaving this as a quick access example for now
    app.run(debug=True,host='0.0.0.0', port=5000)
