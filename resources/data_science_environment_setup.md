
# My Data Science Setup
- anaconda: 
- set your python path at the top of this repo
```bash
PYTHONPATH="/Users/bryparker/Documents/projects/mmf/credit_risk:$PYTHONPATH"
export PYTHONPATH
```

### Setup a Virtual Environment
- https://docs.python-guide.org/dev/virtualenvs/
    - use virtualenv not pipenv

### PSQL (Data Base)
```bash
docker run --name mmf_db  -d -p 5431:5432 postgres
```
- docker: https://towardsdatascience.com/how-docker-can-help-you-become-a-more-effective-data-scientist-7fc048ef91d5
   
### Pycharm (for python and sql development)
- using with psql: https://www.jetbrains.com/help/idea/running-a-dbms-image.html

#### helpful characteristics
- in sql (if you're connected to the db) notice white column names aren't correctly defined
    - hover over and see what is wrong

#### helpful shortcuts
- command + option + L => reformats all code properly (for both python and sql)
- shift + shift => search entire project (filename or class or method)
- highlight, right click -> refector or rename also both really useful

### Jupyter Notebook (For EDA)
- apart of anaconda already

### git 
- intro to git: https://guides.github.com/introduction/git-handbook/
- feature branches: https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow

#### vscode (for git)
-  nice for handling git conflicts