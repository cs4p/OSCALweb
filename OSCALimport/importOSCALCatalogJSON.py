import json
import sys
from django.db import models
from SystemSecurityPlans.models import link, nist_control, nist_control_parameter, system_control
import logging

def addNewControl(group_id,group_title,control):
    newControl = nist_control()
    newControl.group_id = group_id
    newControl.group_title = group_title
    newControl.control_id = control['id']
    newControl.source = control['class']
    newControl.control_title = control['title']
    for property in control['properties']:
        if property['name'] == 'label':
            newControl.label = property['value']
        elif property['name'] == 'sort-id':
            newControl.sort_id = property['value']
        elif property['name'] == 'status':
            newControl.status = property['value']
    if 'parts' in control:
        for part in control['parts']:
            if part['name'] == 'statement':
                control_statement = []
                if 'prose' in part: control_statement.append('<p>' + part['prose'] + '</p>')
                if 'parts' in part:
                    for item in part['parts']:
                        proseText = ''
                        if 'prose' in item: proseText = item['prose']
                        control_statement.append('<p>' + item['properties'][0]['value'] + ' ' + proseText + '</p>')
                    combined_statement = ''.join(control_statement)
                    newControl.statement = combined_statement.replace('/n','<br>')
            if part['name'] == 'guidance':
                if 'prose' in part: newControl.guidance = '<p>' + part['prose'] + '</p>'
    else:
        logging.debug(control['id'] + ' has no parts?')
    newControl.save()
    if 'parameters' in control:
        for parameter in control['parameters']:
            parameter_id = parameter['id']
            if 'label' in parameter: label=parameter['label']
            if 'select' in parameter: label=','.join(parameter['select']['alternatives'])
            newParameter = nist_control_parameter(parameter_id=parameter_id,label=label)
            newParameter.save()
            newControl.parameters.add(newParameter.id)
    if 'links' in control:
        for l in control['links']:
            newLink, created = link.objects.get_or_create(text=l['text'], href=l['href'], rel=l['rel'])
            if created: newLink.save()
            newControl.links.add(newLink.id)

def cleanNISTControls():
    nist_control.objects.all().delete()
    nist_control_parameter.objects.count()
    from django.db import connection

    reset_countersSQL = "delete from sqlite_sequence where name in ('nist_control','property','nist_control_parameter');"

    with connection.cursor() as cursor:
        cursor.execute(reset_countersSQL)

def linkSystemControltoNISTControl():
    logging.basicConfig(  # filename=logFile,
        filemode='w',
        format='%(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
    )
    for item, key in system_control.objects.all().values_list('control_id', 'pk'):
        control = system_control.objects.get(pk=key)
        logging.debug('Opened control ' + control.control_id)
        nist_control_id = item.lower().replace(' ','').replace('(', '.').replace(')', '')
        logging.debug('Looking up ' + nist_control_id)
        try:
            control.nist_control = nist_control.objects.get(control_id=nist_control_id)
            control.save()
            logging.debug('Found nist control, link established')
        except nist_control.DoesNotExist:
            logging.debug("".join(item[0].lower().split()).replace('(', '.').replace(')', '') + ' not found')

def runLink():
    logging.basicConfig(  # filename=logFile,
        filemode='w',
        format='%(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
    )
    logging.debug("Starting Link Process.  Good Luck, we're all counting on you.")
    for item in system_control.objects.all():
        error_list = {}
        logging.debug("trying to link " + item.control_id)
        r = linkSystemControltoNISTControlErrorHandling(item.control_id,item.control_id)
        error_list[item.control_id] = r
    if len(error_list) > 0:
        for id, error in error_list:
            logging.debug(id,':',error[0],error[1],error[2])
    else:
        logging.debug("No errors!!!!")


def runImport():
    cleanNISTControls()
    catalogDict = json.loads(open("/Users/dan/PycharmProjects/OSCALweb/OSCALimport/NIST_SP-800-53_rev4_catalog.json", 'r').read())

    for group in catalogDict['catalog']['groups']:
        for control in group['controls']:
            try:
                addNewControl(group['id'], group['title'], control)
            except KeyError:
                printKeyError(control['id'],sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
            if 'controls' in control:
                for enhancement in control['controls']:
                    try:
                        addNewControl(group['id'], group['title'],enhancement)
                    except KeyError:
                        printKeyError(enhancement['id'],sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
    runLink()

def printKeyError(id,error_type,value,traceback):
    print(id + 'failed import. Missing key:  error: ', error_type, value, traceback, ' skipping..')

# from OSCALimport.importOSCALCatalogJSON import *
# TODO: Sometimes control statement not imported.  Look at ca-7.1 (OSCALimport/NIST_SP-800-53_rev4_catalog.json:31009)


def getControlStatement(control_id):
    stmnt = ''
    catalogDict = json.loads(
        open("/Users/dan/PycharmProjects/OSCALweb/OSCALimport/NIST_SP-800-53_rev4_catalog.json", 'r').read())
    for group in catalogDict['catalog']['groups']:
        if group['id'] == control_id[:2]:
            for control in group['controls']:
                if control['id'] == control_id[:control_id.find('.')]:
                    if 'controls' in control:
                        for control_enhancement in control['controls']:
                            if control_enhancement['id'] == control_id:
                                for part in control_enhancement['parts']:
                                    if part['name'] == 'statement':
                                        stmnt = part['prose']
                    else:
                        for part in control['parts']:
                            if part['name'] == 'statement':
                                stmnt = part['prose']
    return stmnt


list(filter( \
    lambda part : part["name"] == "statement", \
    list(filter( \
        lambda control : control['id'] == 'ac-2', \
        list(filter( \
            lambda group : group["id"] == 'ac', \
            catalogDict['catalog']['groups'])) \
        [0]['controls']))[0]['controls'][0]))[0]['parts'])[0]['prose']

