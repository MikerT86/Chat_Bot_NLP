**Notes for using files**

The _Main_files_ directory contains all main functions for all different parts. The dstc2 data is NOT included, due to the size (900 MB+)of those files. Please edit the path in _global_variables.py._ 

After doing so, the files can be used independently. 

For creating the seperate training and test data files with the provided code, one need to manually create a file. The file was not included due to the size (900 MB+) of this file. This file is the concatination of dstc2_traindev and dstc2_test. It can be called dtsc2_merge, hence the path for DATA_PATH. In this file there has to be another file. This second file has to contains the data from dstc2_traindev and dstc2_test (Mar13_S0A0, Mar13_S0A1, Mar13_S1A0, Mar13_S1A1, Mar13_S2A0 and Mar13_S2A1).

**Project Docs**

Please refer to conda docs when trying to import the virtualenv _(which is necessary for being on the same page concerning packages)_. Make sure to update the _environment_MAIR20.yml_ when you're using not-included libraries, then the rest of us can easily use the same packages.

* Importing a virtual environment for conda from a _.yml_ file: 
https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file

* Creating a _.yml_ environment file (make sure to do this in the root folder to overwrite environment_MAIR20.py):
https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#sharing-an-environment

 
