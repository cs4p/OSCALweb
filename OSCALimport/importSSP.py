import glob
import os

import dbFunctions as dbfct
import importSSPContentFromWord as content
import importSecurityControlsFromWord as controls

# run the import

db = dbfct.openDB()
# dbfct.createDB(db)

sql = "INSERT INTO information_systems (name) VALUES ('OMB Private Cloud')"
cursor = db.cursor()
cursor.execute(sql)
system_id = cursor.lastrowid
db.commit()

path = './files'
content.main(path + '/OMBPrivateCloudSystemSecurityPlan.docx',db,system_id)

for filename in glob.glob(os.path.join(path, 'FedRAMP Template -*.docx')):
   # print "Loading file " + filename
   controls.main(filename, db,system_id)