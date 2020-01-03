python -m cProfile -s cumtime manage.py importdata vocabulario-castellano-aragones.xlsx --dry-run


ncalls  tottime  percall  cumtime  percall filename:lineno(function)
1108/1    0.019    0.000   52.489   52.489 {built-in method builtins.exec}
     1    0.000    0.000   52.489   52.489 manage.py:2(<module>)
     1    0.000    0.000   52.451   52.451 __init__.py:378(execute_from_command_line)
     1    0.000    0.000   52.451   52.451 __init__.py:301(execute)
     1    0.000    0.000   52.014   52.014 base.py:299(run_from_argv)
     1    0.001    0.001   52.012   52.012 base.py:335(execute)
     1    0.000    0.000   51.803   51.803 importdata.py:67(handle)
     1    0.133    0.133   50.244   50.244 importdata.py:232(populate_models)
 18146    0.030    0.000   34.956    0.002 importdata.py:129(populate_word)
 18146   34.458    0.002   34.922    0.002 importdata.py:120(get_or_create_word)
 18146    0.110    0.000   13.351    0.001 importdata.py:137(populate_gramcats)
 20019    0.119    0.000   13.125    0.001 manager.py:81(manager_method)

