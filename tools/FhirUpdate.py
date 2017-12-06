# Mock and modify the HAPI FHIR sample data
#
# This was written as a quick one-off script specifically for use with the sample HAPI FHIR data in the context of this
# project. There's a lot of repeated code, assumptions, and hardcoded values here that would make this script useless
# for other purposes.
#
# The patients with the target conditions will be
# Peggy Howe (075786e8-383c-4eee-abb6-264b3b967482): Hypertension
# Dwight Upton (9128b189-f7c4-4f45-b5a8-718f5f3c6ed7): Diabetes
# Kenneth Wilderman (8c6ece7b-4edb-423b-9dd6-3f677e6f878a) (no mocking necessary): Diabetes, Hypertension

import os
from fhirclient import client
import fhirclient.models.condition as c
import fhirclient.models.patient as p
import fhirclient.models.observation as o

class FhirUpdate:

    # Initialize FHIR server connection
    def __init__(self):
        settings = {
            'app_id': 'my_web_app',
            'api_base': os.getenv('BASE_URL', 'http://localhost') + ':8100/hapi-fhir-jpaserver-example/baseDstu2'
        }
        self.smart = client.FHIRClient(settings=settings)

    # Update an *existing* condition (specified by ID) to either diabetes or hypertension
    def update_condition(self, condition_id, diabetes=True):
        # Fetch condition by ID from FHIR server and convert to a JSON dictionary
        condition = c.Condition.read(condition_id, self.smart.server)
        condition_json = condition.as_json()
        # Update the JSON dictionary with the specified condition
        if diabetes:
            condition_json['code'] = {
                'text': u'Diabetes',
                'coding': [
                    {
                        'code': u'44054006',
                        'display': u'Diabetes',
                        'system': u'http://snomed.info/sct'
                    }
                ]
            }
        else:
            condition_json['code'] = {
                'text': u'Hypertension',
                'coding': [
                    {
                        'code': u'38341003',
                        'display': u'Hypertension',
                        'system': u'http://snomed.info/sct'
                    }
                ]
            }
        # Update the condition from the JSON and then write changes to the server
        condition.update_with_json(condition_json)
        c.Condition.update(condition, self.smart.server)

        # Get patient name from reference string
        patient_id = condition.patient.reference.split('/', 1)[-1]
        patient = p.Patient.read(patient_id, self.smart.server)
        patient_name = self.smart.human_name(patient.name[0])

        print 'Updated condition', condition_id, 'for', patient_name
        print condition.as_json()
        #print json.dumps(condition.as_json(), indent=4)


    def update_patient_info(self, patient_id, update_dict):
        # Fetch patient by ID from FHIR server and convert to a JSON dictionary
        patient = p.Patient.read(patient_id, self.smart.server)
        patient_json = patient.as_json()
        index = 0
        for extension in patient_json['extension']:
            if extension['url'] == update_dict['url']:
                extension['valueCodeableConcept']['coding'][0]['code'] = update_dict['code']
                extension['valueCodeableConcept']['coding'][0]['display'] = update_dict['display']
                print 'Updated patient info for ' + self.smart.human_name(patient.name[0])
                print patient_json['extension']
            index += 1
        # Update the patient from the JSON and then write changes to the server
        patient.update_with_json(patient_json)
        p.Patient.update(patient, self.smart.server)


    def add_observation(self, patient_id, observation_data):
        # This is the common structure for observations
        # Values of None will be filled in later
        observation_template = {
            'id': '',
            'status': 'final',
            'category': {
                'coding': [
                    {
                        'system': 'http://hl7.org/fhir/observation-category',
                        'code': None
                    }
                ]
            },
            'code': None,
            'subject': {
                'reference': 'Patient/' + str(patient_id)
            },
            'effectiveDateTime': observation_data['datetime'],
            'issued': observation_data['datetime'],
            'valueQuantity': {
                'value': None,
                'unit': None,
                'system': 'http://unitsofmeasure.org/',
                'code': None
            }
        }

        # Fill in value based on observation type (name)
        if observation_data['name'] == 'a1c':
            category_coding_code = 'laboratory'
            code = {
                'coding': [
                    {
                        'system': 'http://loinc.org',
                        'code': '4548-4',
                        'display': 'Hemoglobin A1c/Hemoglobin.total in Blood'
                    }
                ],
                'text': 'Hemoglobin A1c/Hemoglobin.total in Blood'
            }
            value_quantity = {
                'value': observation_data['value'],
                'unit': observation_data['unit'],
                'system': 'http://unitsofmeasure.org/',
                'code': observation_data['unit']
            }
            observation_template['category']['coding'][0]['code'] = category_coding_code
            observation_template['code'] = code
            observation_template['valueQuantity'] = value_quantity
        elif observation_data['name'] == 'bmi':
            category_coding_code = 'vital-signs'
            code = {
                'coding': [
                    {
                        'system': 'http://loinc.org',
                        'code': '39156-5',
                        'display': 'Body Mass Index'
                    }
                ],
                'text': 'Body Mass Index'
            }
            value_quantity = {
                'value': observation_data['value'],
                'unit': observation_data['unit'],
                'system': 'http://unitsofmeasure.org/',
                'code': observation_data['unit']
            }
            observation_template['category']['coding'][0]['code'] = category_coding_code
            observation_template['code'] = code
            observation_template['valueQuantity'] = value_quantity
        elif observation_data['name'] == 'bp':
            category_coding_code = 'vital-signs'
            code = {
                'coding': [
                    {
                        'system': 'http://loinc.org',
                        'code': '55284-4',
                        'display': 'Blood Pressure'
                    }
                ]
            }
            component = [
                {
                    'code':
                        {
                            'coding':
                                [
                                    {
                                        'system': 'http://loinc.org',
                                        'code': '8480-6',
                                        'display': 'Systolic Blood Pressure'
                                    }
                                ],
                            'text': 'Systolic Blood Pressure'
                        },
                    'valueQuantity':
                        {
                            'value': observation_data['value'][0],
                            'unit': observation_data['unit'],
                            'system': 'http://unitsofmeasure.org/',
                            'code': observation_data['unit']
                        }
                },
                {
                    'code':
                        {
                            'coding':
                                [
                                    {
                                        'system': 'http://loinc.org',
                                        'code': '8462-4',
                                        'display': 'Diastolic Blood Pressure'
                                    }
                                ],
                            'text': 'Diastolic Blood Pressure'
                        },
                    'valueQuantity':
                        {
                            'value': observation_data['value'][1],
                            'unit': observation_data['unit'],
                            'system': 'http://unitsofmeasure.org/',
                            'code': observation_data['unit']
                        }
                }
            ]
            observation_template['category']['coding'][0]['code'] = category_coding_code
            observation_template['code'] = code
            observation_template['component'] = component
        else:
            print 'No valid observation specified'
            return

        observation = o.Observation(observation_template)
        print observation.as_json()
        o.Observation.create(observation, self.smart.server)
        print 'Finished adding ' + observation_data['name'] + ' observation'


updater = FhirUpdate()

# Peggy Howe
updater.update_patient_info('075786e8-383c-4eee-abb6-264b3b967482',
                            {
                                'url': 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-race',
                                'code': '2056-0',
                                'display': 'Black'
                            })
updater.update_condition('046a77ea-7311-441f-a6ea-8348f0fdaf25', diabetes=False)
updater.add_observation('075786e8-383c-4eee-abb6-264b3b967482',
                        {'name': 'a1c', 'datetime': '2006-02-11T16:32:00-06:00', 'value': 5.2, 'unit': '%'})
updater.add_observation('075786e8-383c-4eee-abb6-264b3b967482',
                        {'name': 'bmi', 'datetime': '2005-07-09T14:55:00-06:00', 'value': 28, 'unit': 'kg/m2'})
updater.add_observation('075786e8-383c-4eee-abb6-264b3b967482',
                        {'name': 'bp', 'datetime': '2006-03-14T09:52:00-06:00', 'value': (145,90), 'unit': 'mmHg'})

# Dwight Upton
updater.update_condition('fbfd838c-c30d-4528-8621-9835385e9cab')
updater.add_observation('9128b189-f7c4-4f45-b5a8-718f5f3c6ed7',
                        {'name': 'a1c', 'datetime': '2017-03-09T12:39:00-03:00', 'value': 6.8, 'unit': '%'})

# Kenneth Wilderman
updater.update_patient_info('8c6ece7b-4edb-423b-9dd6-3f677e6f878a',
                            {
                                'url': 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-race',
                                'code': '2028-9',
                                'display': 'Asian'
                            })
