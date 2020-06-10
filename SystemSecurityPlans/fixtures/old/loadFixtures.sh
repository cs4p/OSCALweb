#!/bin/bash

python manage.py loaddata 'system_status.json'
python manage.py loaddata 'address.json'
python manage.py loaddata 'system_properties.json'
python manage.py loaddata 'system_functions.json'
python manage.py loaddata 'system_privleges.json'
python manage.py loaddata 'system_roles.json'
python manage.py loaddata 'urls.json'
python manage.py loaddata 'orgsPeopleAndParties.json'
python manage.py loaddata 'implimentedRequirements.json'
python manage.py loaddata 'properties.json'
python manage.py loaddata 'systemParameters.json'
python manage.py loaddata 'statements.json'


#python manage.py dumpdata SystemSecurityPlans.implementedRequirements > SystemSecurityPlans/fixtures/implimentedRequirements.json
#python manage.py dumpdata SystemSecurityPlans.properties > SystemSecurityPlans/fixtures/properties.json
#python manage.py dumpdata SystemSecurityPlans.systemParameters > SystemSecurityPlans/fixtures/systemParameters.json
#python manage.py dumpdata SystemSecurityPlans.statements > SystemSecurityPlans/fixtures/statements.json
#
