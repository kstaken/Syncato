#!/usr/bin/env python 

from bsddb.db import *
from dbxml import *

environment = DBEnv()
environment.open("../../../data/blog-data", DB_CREATE|DB_INIT_LOCK|DB_INIT_LOG|DB_INIT_MPOOL|DB_INIT_TXN|DB_THREAD|DB_RECOVER, 0)

txn = environment.txn_begin()

# Open the main database
# convert to use XMLManager
#self.db = XmlContainer(self.environment, "blog.dbxml")
manager = XmlManager(environment, 0)
#uc = self.manager.createUpdateContext()
xtxn = manager.createTransaction(txn)
db = manager.openContainer(xtxn, "blog.dbxml", DB_CREATE|DBXML_TRANSACTIONAL)

txn.commit(0)

metadata = "<status id='500'><db-status>0</db-status><next-id>500</next-id></status>"
document = manager.createDocument()
document.setContent(metadata)
document.setName('db-status')

txn = manager.createTransaction()
#try:
#uc = manager.createUpdateContext()
#db.putDocument(document, uc)
  #  txn.commit(0)
#except:
    #txn.abort()
    
result = db.getDocument(txn, 'db-status')
print result.getContent()

txn.commit(0)