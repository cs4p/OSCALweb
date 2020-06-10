import docx
from SystemSecurityPlans import models

def getCheckedOptions(cell):
    results = []
    cell_elm = cell._element
    # checkBoxes = cell_elm.xpath('.//w14:checkBox')
    checkBoxes = cell_elm.xpath(".//*[local-name()='checked']")
    labels = cell_elm.xpath(".//*[local-name()='t']")
    c = 0
    for item in labels:
        if type(item.text) == str:
            if item.text != "Implementation Status (check all that apply):" and item.text != "Control Origination (check all that apply):" and c < len(checkBoxes):
                if checkBoxes[c].values()[0] == '1':
                    results.append(item.text)
                c = c + 1
    return ','.join(results)

def importSecurityControls():
    f = '/home/parallels/Documents/MAX.gov System Security Plan Controls.docx'
    d = docx.Document(f)
    table = d.tables[2]
    newControl = models.implementedRequirements(controlID=table.rows[0].cells[0].text)
    newControl.save()
    # Find and Add Roles
    roleText = table.rows[1].cells[0].text
    roleList = table.rows[1].cells[0].text
    roleList = (roleText[roleText.find(':') + 1:]).split(',')
    for item in roleList:
        item = item.strip()
        newControl.responsibleRoles.get_or_create(title=item, shortName=item, desc=item)
    # Find and Add Parameters, Implementation Status, and Control Origination
    for row in table.rows:
        content = row.cells[0].text
        if content[0:9] == "Parameter":
            newControl.parameters.create(paramID=content[10:content.find(':')].strip(),
                                         value=content[content.find(':') + 1:].strip())
        if content[0:14] == "Implementation":
            newControl.properties.create(name='Implementation Status', value=getCheckedOptions(row.cells[0]))
        if content[0:7] == "Control":
            newControl.properties.create(name='Control Origination', value=getCheckedOptions(row.cells[0]))