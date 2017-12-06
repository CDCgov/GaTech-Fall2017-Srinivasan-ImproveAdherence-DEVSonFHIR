import os
import simplejson
from urllib2 import urlopen
from datetime import datetime
from datetime import date

api_base = os.getenv('FHIR_URL', 'http://localhost:8100/hapi-fhir-jpaserver-example/baseDstu2')

def get_fhir_resource_from_id(id, resourceType='Patient'):
    #fhirclient lib is not working properly so I just wrote our own thing
    return simplejson.loads(urlopen(api_base+'/{resourceType}/{id}'.format(resourceType=resourceType, id=id)).read())

# Observation text to (LOINC) code:
# Body Mass Index: 39156-5
# Hemoglobin A1c/Hemoglobin.total in Blood: 4548-4
# Blood Pressure: 55284-4
#
# Also, retrievals appear to be limited to 10 results by default
# Specifying _count=50 here because the max number of returned results seems
# to be 50 without pagination. This might be an issue if a patient has >50
# observations that meet the criteria.
def get_observations_for_subject(patient_id):
    return simplejson.loads(urlopen(api_base+'/Observation?&patient={id}&code=39156-5,4548-4,55284-4&_count=50'.format(id=patient_id)).read())

def get_conditions_for_subject(patient_id):
    return simplejson.loads(urlopen(api_base+'/Condition?&patient={id}'.format(id=patient_id)).read())

def get_race_of_patient(patient_fhir_resource):
    for extension in  patient_fhir_resource['extension']:
        if extension.has_key('valueCodeableConcept'):
            if extension['valueCodeableConcept']['text']=='race':
                return extension['valueCodeableConcept']['coding'][0]['display']

def get_age_of_patient(patient_fhir_resource):
    birthday = datetime.strptime(patient_fhir_resource['birthDate'], '%Y-%M-%d')
    today = date.today()
    return today.year - birthday.year
