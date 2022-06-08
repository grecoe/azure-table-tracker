##########################################################
# Copyright (c) Microsoft Corporation.
##########################################################

import uuid
import typing
from abc import ABC

class ITableRecord(ABC):

    def __init__(self, partition_key:str, row_key:str = None, table_name:str = None):

        if not partition_key:
            raise ValueError("partition_key cannot be None")
        if not table_name:
            raise ValueError("table_name cannot be None")


        self.TableName = table_name
        self.PartitionKey = partition_key

        self.RowKey = row_key
        if not self.RowKey:
            self.RowKey = str(uuid.uuid4())        

    def get_entity(self) -> dict:
        """
        Entity is everyting in self.__dict__ EXCEPT the 
        table name. This is used to pass to the storage API for creating
        or updating a table record. 
        """
        entity = {}
        for prop in self.__dict__:
            if prop != 'TableName':
                entity[prop] = self.__dict__[prop]

        return entity

    @staticmethod
    def get_query(field:str, value:typing.Any) -> str:
        return_value = None
        if field:
            if isinstance(value, bool):
                return_value = "{} eq {}".format(field, str(value).lower())
            elif isinstance(value, str):
                return_value = "{} eq '{}'".format(field, value)
            elif value:
                return_value = "{} eq {}".format(field, value)
                
        return return_value


    @staticmethod
    def from_entity(table:str, obj:dict, return_klass:type) -> object:
        """
        Create an instance of Record from a dictionary of data retrieved
        from the table storage API
        """

        record = obj
        if isinstance(record,list):
            record = record[0]

        return_obj = return_klass()
        return_obj.TableName = table

        for val in record:
            setattr(return_obj, val, record[val])
        return return_obj    