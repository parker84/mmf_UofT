
# My Data Science Setup
- anaconda: 
- set your python path at the top of this repo
    - check with $PYTHONPATH
    - if its off, try in a brand new cli window
```bash
PYTHONPATH="/Users/bryparker/Documents/projects/mmf/credit_risk:$PYTHONPATH"
export PYTHONPATH
```

### Setup a Virtual Environment
- https://docs.python-guide.org/dev/virtualenvs/
    - use virtualenv not pipenv

```bash
virtualenv mmf_venv
source ./mmf_venv/bin/activate
pip install -r ./requirements.txt # install the provided requirements.txt file
```


### PSQL (Data Base)

#### Docker
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
- just move to the top of the directory you want, make sure the python path is set and run:

```bash
jupyter notebook
```
- if you get frozen see if you can run anything in another cell
    - if not, try to stop the kernel, still not working restart it
- make sure to exit ipdbs before running a cell again
    - notice you'll also need to redefine classes
- save the notebook to see changes in other cells register in your cell
- using a virtaul env with jupyter: https://anbasile.github.io/programming/2017/06/25/jupyter-venv/
- https://www.dataquest.io/blog/jupyter-notebook-tips-tricks-shortcuts/ 
    - l -> shows line numbers on cell
    - b -> new cell below
    - m -> switch to markdown
    - y -> switch to code
    - i -> stop the kernel
    - r -> restart the kernel

### git 
- intro to git: https://guides.github.com/introduction/git-handbook/
- feature branches: https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow

#### vscode (for git)
-  nice for handling git conflicts