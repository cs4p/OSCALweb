import docx
from SystemSecurityPlans import models
import logging

def listDataTables(d):
    for para in d.paragraphs:
        if para.text[0:5] == 'Table':
            print(para.text)

def listTables(document):
    d = docx.Document(document)
    for table in d.tables:
        row1 = []
        for cell in table.row_cells(0):
            row1.append(cell.text)
        print('|' + '|'.join(row1))

def getCheckedOptions(cell):
    results = []
    cell_elm = cell._element
    # checkBoxes = cell_elm.xpath('.//w14:checkBox')
    checkBoxes = cell_elm.xpath(".//*[local-name()='checked']")
    labels = cell_elm.xpath(".//*[local-name()='t']")
    c = 0
    for item in labels:
        if type(item.text) == str and len(item.text) > 1:
            if item.text != "Implementation Status (check all that apply):" \
                    and item.text != "Control Origination (check all that apply):" \
                    and c < len(checkBoxes):
                if checkBoxes[c].values()[0] == '1':
                    results.append(item.text)
                c = c + 1
    return ','.join(results)

def cleanData():
    models.implementedRequirements.objects.all().delete()
    models.properties.objects.all().delete()
    models.systemParameters.objects.all().delete()
    models.statements.objects.all().delete()


def main(document):
    logFile = '/home/parallels/PycharmProjects/OSCALweb/importSecurityControlsFromWord.log'
    #open(logFile,'w').close()
    logging.basicConfig(#filename=logFile,
                        filemode='w',
                        format='%(name)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG
                        )
    d = docx.Document(document)
    logging.debug('Starting import from ' + document)
    for table in d.tables:
        firstRow = True
        # There are 2 kinds of tables, Control Summary and solution
        # Sometimes the solution table has only 1 column and sometimes it has 2
        columns = len(table.rows[0].cells)
        if table.rows[0].cells[0].text != table.rows[0].cells[columns-1].text:
            if table.rows[0].cells[1].text == "Control Summary Information" or table.rows[0].cells[1].text == "Control Enhancement Summary Information":
                logging.debug('Starting import for ' + table.rows[0].cells[0].text + ' control')
                newControl = models.implementedRequirements(controlID=table.rows[0].cells[0].text)
                newControl.save()
                logging.debug('Control ' + table.rows[0].cells[0].text + ' created')
                # Find and Add Roles
                roleText = table.rows[1].cells[0].text
                roleList = (roleText[roleText.find(':') + 1:]).split(',')
                for item in roleList:
                    item = item.strip()
                    logging.debug('Adding role ' + item)
                    newControl.responsibleRoles.get_or_create(title=item[:100], shortName=item[:25], desc=item[:100])
                # Find and Add Parameters, Implementation Status, and Control Origination
                for row in table.rows:
                    content = row.cells[0].text
                    logging.debug('Adding parameter ' + content)
                    if content[0:9] == "Parameter":
                        newControl.parameters.create(paramID=content[10:content.find(':')].strip()[:25],
                                                     value=content[content.find(':') + 1:].strip())
                    elif content[0:14] == "Implementation":
                        newControl.properties.create(name='Implementation Status',
                                                     value=getCheckedOptions(row.cells[0]))
                    elif content[0:7] == "Control":
                        newControl.properties.create(name='Control Origination', value=getCheckedOptions(row.cells[0]))
            else:
                msg = '|'
                for item in table.rows[0].cells:
                    msg = msg + item.text + '|'
                logging.debug('Table not imported. First Row text was ' + msg)
        else:
            rowCount = 0
            for row in table.rows:
                #skip header row
                if firstRow:
                    firstRow = False
                    t = row.cells[0].text
                    conID = t[0:t.find(' What')]
                else:
                    logging.debug('Importing statements for ' + conID)
                    control = models.implementedRequirements.objects.get(controlID=conID)
                    # Handle the case where the table has only 1 column
                    if len(row.cells) == 1:
                        controlName = 'Part a'
                        controlValue = row.cells[0].text
                    else:
                        controlName = row.cells[0].text
                        controlValue = row.cells[1].text
                    logging.debug('Adding property ' + controlName + ': ' + controlValue)
                    control.statements.create(statementID=controlName, description=controlValue)
                    rowCount = rowCount+1

f = 'MAX.gov System Security Plan Controls.docx'
