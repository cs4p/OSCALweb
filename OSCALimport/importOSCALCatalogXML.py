import xml.etree.ElementTree as ET

tree = ET.parse('/home/dan/PycharmProjects/OSCAL/files/NIST_SP-800-53_rev4_catalog.xml')
root = tree.getroot()
ns = {'n': "http://csrc.nist.gov/ns/oscal/1.0"}

for group in root.iter('{http://csrc.nist.gov/ns/oscal/1.0}group'):
    group_id = group.get('id')
    group_title = group.find('{http://csrc.nist.gov/ns/oscal/1.0}title').text
    for control in group.iter('{http://csrc.nist.gov/ns/oscal/1.0}control'):
        control_id = control.get('id')
        control_title = control.find('{http://csrc.nist.gov/ns/oscal/1.0}title').text
        for property in control.findall('{http://csrc.nist.gov/ns/oscal/1.0}prop'):
            if property.get('name') == 'label':
                control_label = property.text
            elif property.get('name') == 'sort-id':
                control_sort_id = property.text
        for param in control.iter('{http://csrc.nist.gov/ns/oscal/1.0}param'):
            param_id = param.get('id')
            param_label = list(param)[0].text
        for link in control.iter('{http://csrc.nist.gov/ns/oscal/1.0}link'):
            link_href = link.get('href')
            link_rel = link.get('rel')
            link_text = link.text

            print(group_id, group_title, control_id, control_title, control_label, control_sort_id, param_id, param_label, link_href, link_rel, link_text)








# sspDict = {}
# familyDict = {}
# controlDict = {}
#
# for family in root.findall("n:group", ns):
#     for control in family.findall('n:control', ns):
#         controlDict["controlTitle"] = control.find('n:title',ns).text #Access Control Policy and Procedures
#         # loop through properties
#         for prop in control.findall('n:prop', ns):
#             controlDict["control" + prop.get('name')] = prop.text
#         for param in control.findall('n:param', ns):
#             parameters = {}
#             parameters["param_id"] = param.get('id')
#             for value in param:
#                 parameters["param_" + str(value.tag).replace('{http://csrc.nist.gov/ns/oscal/1.0}','')] = value.text
#             controlDict["parameters"] = parameters
#         for part in control.findall('n:part', ns):
#             sections = part.iter
#             print sections
#             print "pausing"
#         # for links in control.findall('n:link', ns):
#         #     linkDict = {}
#         #     linkDict['Document'] = link.text
#         #     for link in links:
#         #         linkDict["link_" + str(value.tag).replace('{http://csrc.nist.gov/ns/oscal/1.0}', '')] = value.text
#         #     controlDict["parameters"] = parameters
#         #
#             # skipping this for now.  Will need to lookup actual link in the resources
#         familyDict[controlDict["controllabel"]] = controlDict
#         controlDict = {}
#     sspDict[family.find("n:title").text] = familyDict
#     familyDict = {}