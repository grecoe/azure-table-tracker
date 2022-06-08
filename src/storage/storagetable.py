##########################################################
# Copyright (c) Microsoft Corporation.
##########################################################

import typing
import datetime
from src.storage.tablerecord import ITableRecord
from azure.data.tables import TableServiceClient, TableClient, UpdateMode
from azure.data.tables._entity import EntityProperty
from azure.data.tables._deserialize import TablesEntityDatetime

class AzureTableStoreUtil:
    """
    Class encapsulating the calls to an Azure Storage Table 
    """

    CONN_STR = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix=core.windows.net"

    def __init__(self, account_name:str, account_key:str):
        self.connection_string = AzureTableStoreUtil.CONN_STR.format(
            account_name,
            account_key
        )

    def search(self, query:str, table_record_klass:type) -> typing.List[ITableRecord]:
        """
        Search the table for all records that are not processed yet. This will help
        if we ever need to re-run a container to retry failed records. 
        Params:
        table_name - required: Yes  Storage Table to search

        Returns:
        List of Record objects for each record that has not been processed
        """
        return_records = []
        with self._create_table(table_record_klass.TABLE_NAME) as table_client:
            raw_records = self._parse_query_results(table_client, query)
            for raw in raw_records:
                return_records.append(ITableRecord.from_entity(table_record_klass.TABLE_NAME, raw, table_record_klass))

        return return_records

    def add_or_update_record(self, entity:ITableRecord) -> None:
        """
        Update a record in the storage table. Creates the table if not already
        present.

        Params:
        table_name - required: Yes  Storage Table to search
        entity     - required: Yes  Record to update 

        Returns:
        """
        with self._create_table(entity.TableName) as table_client:
            table_client.upsert_entity(mode=UpdateMode.REPLACE, entity=entity.get_entity())

    def delete_record(self, table_name:str, entity:ITableRecord) -> None:
        """
        Delete a record from the storage table. 

        Params:
        table_name - required: Yes  Storage Table to search
        row_key    - required: Yes  RowKey of the record to delete
        partition  - required: Yes  Partition ID to use

        Returns:
        """

        if not isinstance(entity,ITableRecord):
            raise TypeError("entity is not ITableRecord")

        self.delete_records(table_name, [entity])

    def delete_records(self, table_name:str, records:typing.List[ITableRecord]) -> None:
        """
        Delete records from a table
        
        Parameters:
        table_name - name of table to remove. 
        records - List of tuples that are (RowKey,PartitionKey)
        """
        with self._create_table(table_name) as table_client:
            for entity in records:
                
                if not isinstance(entity,ITableRecord):
                    raise TypeError("entity is not ITableRecord")
                elif not entity.RowKey or not entity.PartitionKey:
                    print("Ignoring bad record on row or partition")
                else:
                    table_client.delete_entity(
                        row_key=entity.RowKey, 
                        partition_key=entity.PartitionKey
                        )

    def _parse_query_results(self, table_client:TableClient, query:str) -> typing.List[dict]:
        """
        Query the storage table with a given query and return the results as a list of 
        dictionaries. 

        Parameters:

        table_client:
            Client to perform the query on
        query:
            String query to execute

        Returns:
        List of dictionaries which represent individual records.
        """
        return_records = []

        results = table_client.query_entities(query)
        if results:
            for result in results:
                entity_record = {}
            
                for key in result:
                    value = result[key]

                    if isinstance(result[key], EntityProperty): 
                        value = result[key].value
                    if isinstance(result[key], TablesEntityDatetime):
                        value = datetime.datetime.fromisoformat(str(result[key]))

                    entity_record[key] = value
                
                return_records.append(entity_record)
        else:
            message = "Failed to get results for query: {}".format(query)
            print(message)

        return return_records

    def _create_table(self, table_name:str) -> TableClient:
        """
        Ensure a table exists in the table storage 
        """
        return_client = None
        try:
            return_client = self._get_table_client(table_name)
        except Exception as ex:
            pass


        if not return_client:
            with TableClient.from_connection_string(conn_str=self.connection_string, table_name=table_name) as table_client:
                try:
                    table_client.create_table()
                except Exception as ex:
                    pass
            
            return_client = self._get_table_client(table_name) 

        return return_client

    def _get_table_client(self, table_name: str) ->TableClient:
        """
        Searches for and returns a table client for the specified
        table in this account. If not found throws an exception.
        """
        return_client = None

        with TableServiceClient.from_connection_string(conn_str=self.connection_string) as table_service:
            name_filter = "TableName eq '{}'".format(table_name)
            queried_tables = table_service.query_tables(name_filter)

            found_tables = []
            for table in queried_tables:
                # Have to do this as its an Item_Paged object
                if table.name == table_name:
                    found_tables.append(table)
                    break 
        
            if found_tables and len(found_tables) == 1:
                return_client = TableClient.from_connection_string(conn_str=self.connection_string, table_name=table_name)
            else:
                raise Exception("Table {} not found".format(table_name))

        return return_client                