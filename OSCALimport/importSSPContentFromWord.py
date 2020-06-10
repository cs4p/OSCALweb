from docx import Document

def main(document, db, system_id):
    SSP = {}
    SectionTitle = ''
    SectionText = []
    ignoreSections = ['table of figures', 'GSA Title-YES for TOC', u'Caption', 'toc 2', 'toc 1']

    d = Document(document)
    p = d.paragraphs

    for item in p:
        if len(item.text) > 0:
            for s in ignoreSections:
                if item.style.name == s:  # ignore this line and move onto the next paragraph
                    break
            else:
                if item.style.name != 'Heading 1':
                    if item.style.name == 'Heading 2':
                        SectionText.append('**' + item.text + '**')
                    else:
                        SectionText.append(item.text)
                elif SectionTitle == '': #this is the first Section
                    SectionTitle = item.text
                else:
                    SSP[SectionTitle] = "\n".join(SectionText)
                    sql = "INSERT INTO sspSections(sectionTitle,sectionText, system_id) VALUES(%s,%s,%s)"
                    cursor = db.cursor()
                    data = (SectionTitle, SSP[SectionTitle], str(system_id))
                    cursor.execute(sql, data)
                    db.commit()
                    SectionTitle = item.text
                    SectionText = []
    return SSP