import json
# from SystemSecurityPlans.models import link, nist_control, nist_control_parameter, system_control, nist_control_part, annotation, prop
# import logging
# import uuid
from scripts.usefullFunctions import *

def addControlBase(group_id,group_title,control):
    logging.debug("Creating control " + control['id'])
    newControl, created = nist_control.objects.get_or_create(group_id=group_id,group_title = group_title,control_id = control['id'],source = control['class'],control_title = control['title'])
    return newControl


def saveControlParam(p):
    newParameter = nist_control_parameter()
    newParameter.param_id = p['parameter_id']
    newParameter.param_text = p['parameter_text']
    newParameter.param_type=p['parameter_type']
    newParameter.param_class=p['parameter_class']
    newParameter.param_depends_on=p['parameter_depends_on']
    newParameter.save()
    logging.debug("Save complete...")
    return newParameter.id

def addControlParam(parameter):
    logging.debug("Extracting Parameter " + parameter['id'])
    p = {}
    p['parameter_id'] = parameter['id']
    if 'class' in parameter:
        p['parameter_class'] = parameter['class']
    else:
        p['parameter_class'] = ''
    if 'depends-on' in parameter:
        p['parameter_depends_on'] = parameter['depends-on']
    else:
        p['parameter_depends_on'] = ''
    if 'label' in parameter:
        p['parameter_text'] = parameter['label']
        p['parameter_type'] = 'label'
    if 'descriptions' in parameter:
        for description in parameter:
            p['parameter_text'] = description['summary']
            p['parameter_type'] = 'description'
    if 'constraints' in parameter:
        for constraint in parameter['constraints']:
            p['parameter_text'] = constraint['detail']
            p['parameter_type'] = 'constraint'
    if 'guidance' in parameter:
        for guideline in parameter['guidance']:
            p['parameter_text'] = guideline['prose']
            p['parameter_type'] = 'guidance'
    if 'value' in parameter:
        p['parameter_text'] = parameter['value']
        p['parameter_type'] = 'value'
    if 'select' in parameter:
        for alternatives in parameter['select']:
            for choice in alternatives:
                p['parameter_text'] = choice
                p['parameter_type'] = 'select'
    logging.debug("Saving parameter...")
    controlParameter = saveControlParam(p)
    return controlParameter


def addControlProperties(property,newControl):
    logging.debug("adding property: " + property['name'])
    if property['name'] == 'label':
        logging.debug("Adding Label...")
        newControl.label = property['value']
    elif property['name'] == 'sort-id':
        logging.debug("Adding sort_id...")
        newControl.sort_id = property['value']
    elif property['name'] == 'status':
        logging.debug("Adding status...")
        newControl.status = property['value']
    else:
        logging.error("No instructions for property of type " + property['name'] + ', skipping...')
    newControl.save()
    return property['name']


def addLink(text, href, rel):
    """
    This isn't working right now
    """
    logging.debug("adding link...")
    newLink = link.objects.create(text=text, href=href, rel=rel)
    newLink.save()
    logging.debug("Link added")
    return newLink.uuid


def addControlPart(part,control_id,parent_part=None):
    logging.debug("Extracting Part...")
    newPart = nist_control_part()
    newPart.control_id = control_id
    if parent_part != None:
        newPart.parent_part_id = parent_part
    newPart.part_name = part['name']
    newPart.save()
    if 'title' in part:
        logging.debug("Found part Title...")
        newPart.part_title = part['title']
    if 'properties' in part:
        logging.debug("Found properties, extracting...")
        for p in part['properties']:
            if 'name' in p:
                prop_name = p['name']
            else:
                prop_name = ''
            newProperty = prop.objects.create(uuid=uuid.uuid4(),name=prop_name, value=p['value'])
            newProperty.save()
            newPart.part_properties.add(newProperty.uuid)
            logging.debug("Property added...")
    if 'prose' in part:
        logging.debug("Found prose, extracting...")
        newPart.prose = part['prose']
    if 'parts' in part:
        newPart.save()
        for subpart in part['parts']:
            logging.debug("Found subpart, extracting...")
            addControlPart(subpart,control_id,newPart.id)
            logging.debug("Added subpart...")
    # This isn't working right now
    # TODO: Fix links
    # if 'links' in part:
    #     logging.debug("Found links, extracting...")
    #     for link in part['links']:
    #         if 'href' in link:
    #             href = link['href']
    #         else:
    #             href = ''
    #         if 'rel' in link:
    #             rel = link['rel']
    #         else:
    #             rel = ''
    #         l = addLink(link['text'],href,rel)
    #         newPart.links.add(l)
    #         logging.debug("Added Link...")
    newPart.save()
    return newPart.id


def addNewControl(group_id,group_title,control):
    logging.debug("Adding basic control elements...")
    newControl = addControlBase(group_id,group_title,control)
    if 'parameters' in control:
        logging.debug('Found parameters, extracting...')
        for parameter in control['parameters']:
            newParameter = addControlParam(parameter)
            newControl.parameters.add(newParameter)
    if 'properties' in control:
        logging.debug("Found properties, extracting...")
        for property in control['properties']:
            addControlProperties(property,newControl)
    if 'annotations' in control:
        logging.debug("Found Annotations...")
        for a in control['annotations']:
            annotation_name = a['name']
            if 'id' in a:
                annotation_id = a['id']
            else:
                annotation_id = None
            if 'ns' in a:
                annotation_ns = a['ns']
            else:
                annotation_ns = None
            if 'value' in a:
                annotation_value = a['value']
            else:
                annotation_value = None
            if 'remarks' in a:
                annotation_remarks = a['remarks']
            else:
                annotation_remarks = None
            newAnnotation = annotation.objects.get_or_create(name=annotation_name,annotationID=annotation_id,ns=annotation_ns,value=annotation_value,remarks=annotation_remarks)
            newControl.annotations.add(newAnnotation)
    # This is also not working right now
    # TODO: Fix links
    # if 'links' in control:
    #     logging.debug("Found links, extracting...")
    #     for l in control['links']:
    #         newControl.links.add(addLink(l['text'],l['href'],l['rel']))
    if 'parts' in control:
        logging.debug("Found parts, extracting (better strap in, this could get messy)...")
        for part in control['parts']:
            addControlPart(part,newControl.id)
    newControl.nist_control_statement = newControl.statement_view('statement')
    newControl.nist_control_guidance = newControl.statement_view('guidance')
    newControl.nist_control_objectives = newControl.statement_view('objectives')
    newControl.nist_control_objects = newControl.statement_view('objects')
    newControl.save()
    if 'controls' in control:
        logging.debug("Found control enhancements, extracting...")
        for enhancement in control['controls']:
            addNewControl(group_id,group_title,enhancement)


def cleanNISTControls():
    """
    Deletes all NIST Control objects from the database
    """
    nist_control.objects.all().delete()

def run():
    startLogging()
    logging.debug("Clearing all NIST Control Tables...")
    cleanNISTControls()
    logging.debug("Loading JSON...")
    catalogDict = json.loads(open("/Users/dan/PycharmProjects/OSCALweb/Documents/NIST_SP-800-53_rev4_catalog.json", 'r').read())
    for group in catalogDict['catalog']['groups']:
        logging.debug("Extracting " + group['title'] + " family...")
        for control in group['controls']:
            logging.debug("Extracting " + control['title'] + "(" + control['id'] + ") control...")
            addNewControl(group['id'], group['title'], control)
            if 'controls' in control:
                logging.debug("Found control enhancements, extracting...")
                for enhancement in control['controls']:
                    logging.debug("Extracting " + control['title'] + " enhancement...")
                    addNewControl(group['id'], group['title'],enhancement)