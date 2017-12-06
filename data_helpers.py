from datetime import datetime
from fhirclient_file import *

import pandas
import simplejson
import ipdb

#Read in population Data
population_data = pandas.read_csv('mocked_population_health_data.csv')
aggregated_popdata= pandas.read_csv('aggregated_population_health_data.csv')
#End App Setup


condition_name_to_snomed = {
'diabetes':'44054006', 
'high_blood_pressure':'38341003'
}

def get_population_dict(age, race, marital_status, gender, condition_snomed):
    relevant_population_data = population_data[(population_data['race']==race) &
    (population_data['marital_status']==marital_status) &
    (population_data['gender']==gender) &
    (population_data['condition_snomed']==condition_snomed) &
    (population_data['min_age']<age) &
    (population_data['max_age']>=age)
    ]
    return relevant_population_data.to_json()

def get_population_results_for(reading_type, race, gender, marital_status, age):
    data=aggregated_popdata[
    	(aggregated_popdata['type']==reading_type)
    	& (aggregated_popdata['race']==race)
    	& (aggregated_popdata['gender']==gender)
    	& (aggregated_popdata['marital_status']==marital_status)
    	& (aggregated_popdata['max_age']>int(age))
    	& (aggregated_popdata['min_age']<int(age))
    	].set_index("program")
    result={} #OrderedDict()
    groups=[]
    group=[]
    min_max_age = set()
    prg=""
    for index, row in data.iterrows():
       if index is not prg:
          group=[]
          prg=index
          if prg is not "":
            groups.append(group)
       new_index=index+' ('+row['status']+')'
       result[new_index]=[row['before_less_count'],row['before_more_count'],row['12mon_less_count'],row['12mon_more_count']]
       min_max_age.add((row['min_age'],row['max_age']))
       group.append(new_index)
    groups.append(group)
    return result,groups,list(min_max_age)[0]

def condition_check(user_id):
    referrals_results_dict={'diabetes':False, 'high_blood_pressure': False}
    patient_conditions = get_conditions_for_subject(user_id)
    for entry in patient_conditions['entry']:
        snomed_code = entry['resource']['code']['coding'][0]['code']
        if snomed_code == '44054006':
            referrals_results_dict['diabetes']=True
        if snomed_code == '38341003':
            referrals_results_dict['high_blood_pressure']=True

    return referrals_results_dict

def get_latest_observations(user_observations):
    latest_obs = {'bmi':"Not Available", 'a1c':"Not Available", 'systolic_bp':"Not Available", 'diastolic_bp':"Not Available"}

    try:
        for entry in sorted(user_observations['entry'], key=lambda x: x['resource']['effectiveDateTime']):
            try:
                # Body Mass Index
                if entry['resource']['code']['coding'][0]['code'] == '39156-5':
                    latest_obs['bmi']=round(entry['resource']['valueQuantity']['value'],1)
            except KeyError:
                pass

            try:
                # Hemoglobin A1c/Hemoglobin.total in Blood
                if entry['resource']['code']['coding'][0]['code'] == '4548-4':
                    latest_obs['a1c']=entry['resource']['valueQuantity']['value']
            except KeyError:
                pass

            try:
                # Blood pressure
                if entry['resource']['code']['coding'][0]['code'] == '55284-4':
                    for component in entry['resource']['component']:
                        # Systolic Blood Pressure
                        if component['code']['coding'][0]['code'] == '8480-6':
                            latest_obs['systolic_bp']=component['valueQuantity']['value']

                        # Diastolic Blood Pressure
                        if component['code']['coding'][0]['code'] == '8462-4':
                            latest_obs['diastolic_bp']=component['valueQuantity']['value']
            except KeyError:
                pass
    except KeyError:
        pass

    return latest_obs

def get_patient_data_for_patient_page(user_id, condition_name):
    #Get FHIR info for user_id
    pat_fhir_info = get_fhir_resource_from_id(user_id, resourceType='Patient')
    #Lookup demographics from Mocked Data
    patient_conditions = get_conditions_for_subject(user_id)
    #Lookup observations for the Patient
    patient_observations = get_latest_observations(get_observations_for_subject(user_id))
    #print patient_observations
    conditions = condition_check(user_id)
    patient_data = {
    'name':pat_fhir_info['name'][0]['given'][0]+' '+pat_fhir_info['name'][0]['family'][0],
    'conditions':conditions, 
    'age':get_age_of_patient(pat_fhir_info), 
    'race':get_race_of_patient(pat_fhir_info), 
    'marital_status':pat_fhir_info['maritalStatus']['text'], 
    'gender':pat_fhir_info.get('gender'),
    'bmi':patient_observations['bmi'],
    'a1c':patient_observations['a1c'],
    'systolic_bp':patient_observations['systolic_bp'],
    'diastolic_bp':patient_observations['diastolic_bp']
    }

    return patient_data




