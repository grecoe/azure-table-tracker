##########################################################
# Copyright (c) Microsoft Corporation.
##########################################################

from src.storage.tablerecord import ITableRecord

class ProcessRecord(ITableRecord):
    """
    Instance of a class that can be used to read/write to an Azure Storage Table. 

    MUST have a class variable PARTITION_ID and TABLE_NAME which will be used to create/read
    records from the table. You will get an attribute error if these fields do not exist.

    Derive from ITableRecord to get CRUD operations, then you just need to provide the fields
    that will be read/written/search in the table records themselves.
    """
    PARTITION_ID = None
    TABLE_NAME = None

    def __init__(self):
        super().__init__(ProcessRecord.PARTITION_ID, None, ProcessRecord.TABLE_NAME)

        # Name of the file (path) in file share
        self.file_name = ""
        # Timestamp when the file was queued
        self.queued_time = ""
        # Timestamp when the file was processed
        self.processed_time = ""
        # Indicates if the file has been processed or not.
        self.processed = False
        # Add whatever fields make sense for your implementation which may 
        # or may not include any of the properties above. 
