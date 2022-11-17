<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [quality tools for development](#quality-tools-for-development)
- [about git repository clone](#about-git-repository-clone)
- [generic tool](#generic-tool)
- [tool for importdata](#tool-for-importdata)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# quality tools for development

This project is checked using sonarqube. Sonarqube has a server and client architecture

The server part is deployed using a [docker container](https://docs.docker.com/samples/library/sonarqube/) particularly it is used [the production deployment](https://github.com/SonarSource/docker-sonarqube/blob/master/recipes/docker-compose-postgres-example.yml) to improve performance. The essential plugins for this project are: SonarPython, SonarCSS, SonarJS, SonarHTML

There are two clients used:

- a client inside some of the supported [IDEs](https://en.wikipedia.org/wiki/Integrated_development_environment) through [sonarlint](https://www.sonarlint.org/)
- a client in the same server running sonarqube with a command line tool called [sonar-scanner](https://docs.sonarqube.org/display/SCAN/Analyzing+with+SonarQube+Scanner). This client runs with the help of a script every hour with a cronjob:
    - [the run-bandit.sh script](../tests/run-bandit.sh)
    - [the run-coverage.sh script](../tests/run-coverage.sh)
    - [the run-sonar.sh script](../tests/run-sonar.sh)
    - [the /etc/cron.d/sonarqube cronjob](../tests/sonarqube.cronjob)

references:

- [configure quality profiles](https://docs.sonarqube.org/latest/instance-administration/quality-profiles/). [Our critical profiles](https://ast.aragon.es/sites/default/files/ast.sonar_perfiles.zip) taken from [this website](https://ast.aragon.es/servicios/pruebas-de-resistencia-y-calidad-del-software)
- [SonarPython's Advanced Usage](https://docs.sonarqube.org/display/PLUG/SonarPython) talks about interesting quality tools
    - [bandit in sonarqube](https://docs.sonarqube.org/display/PLUG/Import+Bandit+Issues+Reports)
    - [coverage in sonarqube](https://docs.sonarqube.org/display/PLUG/Python+Coverage+Results+Import)
        - [integration of coverage in django project](https://docs.djangoproject.com/en/2.1/topics/testing/advanced/#integration-with-coverage-py)
        - [coverage](https://coverage.readthedocs.io/en/latest/)
    - [pylint in sonarqube](https://docs.sonarqube.org/display/PLUG/Import+Pylint+Issues+Report) it justs requires to be installed and after that use the sonarqube UI to configure it

# about git repository clone

to fetch the source code of backend use

    git clone https://github.com/lenguasdearagon/aragonario.git

or

    git clone git@github.com:lenguasdearagon/aragonario.git

You have to know that this repository uses `git lfs`. [Git LFS](https://git-lfs.github.com/) is the tool intended to manage large files in git repositories such as audio samples, videos, datasets, and graphics. If you just `git clone` (without `apt install git-lfs`) you are going to be missing [this kind of files](../.gitattributes). Hence, in a simple usage, you just need to install it and address file targets through `.gitattributes`; the rest is using the common git operations.

If you have git lfs installed and you don't want to download media files do it like: `GIT_LFS_SKIP_SMUDGE=1 git clone (...)` src https://github.com/git-lfs/git-lfs/issues/2406

# generic tool

When I reach errors I like to do this kind of breakpoint:

    import code; code.interact(local=dict(globals(), **locals()));exit() # src https://gist.github.com/obfusk/208597ccc64bf9b436ed

that helps to try things interactively taking in account the current variables in use

# tool for importdata

to do fast iterations about the process of importdata first of all I place to

```
path/to/mysite/
```

activate.sh, that I execute as `. activate.sh`, with:

```
#!/bin/bash
source ../env/bin/activate
```

Each modification and change you want to try on importdata script, do `./cycle.sh`, that have these lines:

```
#!/bin/bash
python3 manage.py flush --noinput
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | python3 manage.py shell
python3 manage.py importdata
```
