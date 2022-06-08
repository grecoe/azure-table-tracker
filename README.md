# azure-table-tracker
<sub>Dan Grecoe - a Microsoft Employee</sub>

In larger projects there comes a need to run multiple processes, performing similar work, to expedite the job. For instance, processing thousands of records to extract intelligent data or simply to ingest to a different service. 

Each of the processes should be able to work standalone, but we clearly don't want any process to dulicate the work of another. 

While there are many different solutions to this problem, this repository is an example of using Azure Storage Tables to track items, work, and status of each record. 

Azure Storage is a simple and inexpensive solution in comparison to more complex database systems. You can find out more about [table storage here](https://docs.microsoft.com/en-us/azure/storage/tables/table-storage-overview).


### Contents
- [Pre-requisites](#pre-requisites)
- [Using the example](#using-the-example)
- [Code Design](#design)
    - [Record Implementation](#table-record-implementation)


## Pre-requisites

- An Azure Subscription in which to create an Azure Storage Account
    - Create a storage account and note the access key and account name. 
- A Python environment to execute the code in
    - Create a conda environment using the environment.yml file in this repository
    ```bash
    conda env create -f environment.yml
    conda activate TableTracker
    ```

## Using the example

To use the example, follow the [pre-requisites](#pre-requisites) section. This example will create a new table in your storage account, add 4 records to it, update one record to be completed and finally do a simple query to get any remaining unprocessed records. 

1. Open the file app.py and make the following replacements
    - Line 11: Change default values to your storage account name and storage account key
    - Line 14: Has a default table name, but you can change it to something else
    - Line 15: Has a default partition name, but you can change it to something else
2. Run the application
    ```bash
    conda activate TableTracker
    az login
    python app.py
    ```
3. Review the application code to see how CRUD operations are executed.

# Design

The complexity of working with Azure Storage Tables has been abstracted away from the developer who simply wants to use table storage in a straight forward way.

The code that enables this is in /src/storage

|File|Description|
|----|-----|
|storagetable.py|Implementation of a class that manages CRUD operations to a storage table in an easy to use fashion.|
|tablerecord.py|An abstract base class for specific types of records to be written to the table storage itself.|

## Table Record Implementation

Create a new class, deriving from tablerecord.py::ITableRecord. This new class (as seen in apprecord.py) represents the records that will be written to and read from the table store. 

- Your derived class MUST expose two class variables, expected within the AzureTableStoreUtil class
    - TABLE_NAME:str - The name of the storage table records should be written/read from. 
    - PARTITION_ID:str - The partition for these particular records to be tagged with.
- Add in properties to the class __init__ method that represent the data you want to track. 
- Use the new class with the AzureTableStoreUtil class