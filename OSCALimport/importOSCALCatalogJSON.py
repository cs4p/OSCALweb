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
                if 'prose' in part: control_statement.append(part['prose'] + '\n')
                if 'parts' in part:
                    for item in part['parts']:
                        proseText = ''
                        if 'prose' in item: proseText = item['prose']
                        control_statement.append(item['properties'][0]['value'] + ' ' + proseText)
                    newControl.statement = '/n'.join(control_statement)
            if part['name'] == 'guidance':
                if 'prose' in part: newControl.guidance = part['prose']
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

def linkSystemControltoNISTControl(system_label,nist_label):
    systemControl = system_control.objects.get(control_id=system_label)
    nistControl = nist_control.objects.get(label=nist_label)
    logging.debug("Found possiable match! system_control = " + system_label + " and nist_control = " + nist_label)
    try:
        systemControl.nist_control = nistControl
        systemControl.save()
        logging.debug("Link Created! system_control = " + system_label + " and nist_control = " + nist_label)
    except:
        logging.debug("Match failed :(. system_control = " + system_label + " and nist_control = " + nist_label)

def linkSystemControltoNISTControlErrorHandling(system_label,nist_label):
    errors = []
    try:
        linkSystemControltoNISTControl(system_label,nist_label)
    except models.ObjectDoesNotExist:
        nist_label = str(nist_label).replace(' ','')
        logging.debug("Error occured linking " + system_label + ". Trying again with nist_label = " + nist_label)
        linkSystemControltoNISTControl(system_label,nist_label)
    except:
        errors.append({system_label:sys.exc_info()})
    return errors

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
