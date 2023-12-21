
# A research data management tool

A SQL and Python-based tool for managing research data throughout its lifecycle from acquisition to publication. The method enables FAIR-compatible data management, minimizes user interaction, and provides customizability for diverse research domains. 

This software and data repository is supplement to an article submitted by N.C. Röttcher *et al.* to J. Mat. Chem. A.

Please consider citing the linked Zenodo repository: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10417756.svg)](https://doi.org/10.5281/zenodo.10417756) 

# What is included?
- data belonging to the mentioned publication stored in a SQLite database (database/sqlite.db). This includes:
  - raw experimental data
  - experimental metadata
  - analyzed data
- the database schema:
  - an overview of the database schema (database/schema.pdf) 
  - the MySQL schema file to initialize the database (database/mysql_init.sql)
  - documentation of tables and columns can be found within the tables *documentation_tables* and *documentation_columns* within in the SQLite database file.
- Python scripts in libs/evaluation/...
  - for insertion of acquired raw data (insert/...)
  - for analysis of experimental data, including interactive Jupyter tools (processing/...)
  - for visualization of experiment sets (visualization/...)
  - for exporting research data linked to a publication and creating such a repo (publication_export/...)

# Usage
- The repository is compatible with mybinder to interactively explore data without any software installation.
Interactive version: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/zenodo/10.5281/zenodo.10417756/)
(It might take a while until the jupyter instance is loaded)

- If mybinder is not available, you can take a look at the code in a non-interactive version: [![nbviewer](https://img.shields.io/badge/render-nbviewer-orange.svg)](https://nbviewer.org/github/NicoRottcher/research-data-management-tool/tree/main/)

- Alternatively, you can create a python environment on your local machine and copy the repo files (see below).

# Local installation
- (if necessary) Install Anaconda following the [installation guide](https://docs.continuum.io/free/anaconda/install/).
- create a new environment based on the given environment.yml to install all required Python packages:
  ```
  conda env create -f /path/to/environment.yml
  ```
- activate the environment. Replace 'myenv' with the name given in the first line of th environment.yml file.
  ```
  conda activate myenv
  ```
- ensure a new environment is created
  ```
  conda env list
  ```
- Navigate to the path of the repo files and start jupyter notebook (or jupyter lab)
  ```
  jupyter notebook
  ```
  
# Deploy the tool on an own server
## MySQL database server 
The repo is running with a SQLite database file. To run the database as a server accessible by multiple user,
in our group we rely on MySQL.
- Install MySQL Server and configure to your needs
  - The tool is tested with: MySQL 8.0.34-0ubuntu0.22.04.1 ((Ubuntu))
- Initialize the database schema by running (database/mysql_init.sql). You might need to substitute the user in the definition of views and stored procedures.
- In the python module substitute the evaluation/utils/db_config.py with evaluation/utils/db_config_mysql.py
- Configure the Python module so that you can connect to your database:
  - a) Create a database connection configuration file and add the file path to the connect() function in evaluation/utils/db_config.py (The required style of this configuration file is outlined in that function)
  - b) Adjust the connect() function to your preferences  

## Python+JupyterHub
- Install miniconda following the [installation guide](https://docs.conda.io/projects/miniconda/en/latest/)
- Install a JupyterHub according to your preferences following the [installation guide](https://jupyterhub.readthedocs.io/en/stable/tutorial/quickstart.html)
- In the supplementary information of the above-mentioned article you find an overview of further software infrastructure to get started.
