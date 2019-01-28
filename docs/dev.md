<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [generic tool](#generic-tool)
- [tool for data-import](#tool-for-data-import)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# generic tool

When I reach errors I like to do this kind of breakpoint:

    import code; code.interact(local=dict(globals(), **locals()));exit() # src https://gist.github.com/obfusk/208597ccc64bf9b436ed

that helps to try things interactively taking in account the current variables in use

# tool for data-import

to do fast iterations about the process of data-import first of all I place to

```
path/to/mysite/
```

activate.sh, that I execute as `. activate.sh`, with:

```
#!/bin/bash
source ../env/bin/activate
```

Each modification and change you want to try on data-import script, do `./cycle.sh`, that have these lines:

```
#!/bin/bash
python3 manage.py flush --noinput
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | python3 manage.py shell
python3 manage.py data-import
```
