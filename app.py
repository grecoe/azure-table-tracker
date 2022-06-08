##########################################################
# Copyright (c) Microsoft Corporation.
##########################################################

import typing
from datetime import datetime
from apprecord import ProcessRecord, ITableRecord
from src.storage.storagetable import AzureTableStoreUtil

# Create a table utility so we can CRUD records
stg_table_util = AzureTableStoreUtil("STORAGE_ACCT_NAME", "STORAGE_ACCOUNT_KEY")

# In all instances if ITableRecord, you must expose these class variables.
ProcessRecord.TABLE_NAME = "recordtablename"
ProcessRecord.PARTITION_ID = "recordpartitionid"

# 0. Series of records to create
test_files = ["test.txt", "test.xls", "test.pdf", "test.doc"]

# 1. Create a new records in your table
for test in test_files:
    # Generate record
    new_record = ProcessRecord()
    new_record.file_name = test
    new_record.queued_time = datetime.utcnow()
    
    # Add it to the table
    print("Adding record to the storage table.....")
    stg_table_util.add_or_update_record(new_record)

# Do some processing on the file now, or later.


# Search for one of the original records
print("Searching for record ({}) in the storage table.....".format(test_files[0]))
query = ITableRecord.get_query("file_name", test_files[0])
search_result:typing.List[ProcessRecord] = stg_table_util.search(query, ProcessRecord)

print("Found result:", len(search_result) > 0)

if len(search_result):
    print("Update the record")
    proc_record = search_result[0]
    proc_record.processed_time = datetime.utcnow()
    proc_record.processed = True
    stg_table_util.add_or_update_record(proc_record)


# Finally sanity check 
unprocessed_query = ITableRecord.get_query("processed", False)
unprocessed_result:typing.List[ProcessRecord] = stg_table_util.search(unprocessed_query, ProcessRecord)

print("Started adding {} records, {} are unprocessed".format(
    len(test_files),
    len(unprocessed_result)
))
