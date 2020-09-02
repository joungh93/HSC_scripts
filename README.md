# hscPipe6_scripts
(updated on 2020. 09. 02.)


## Description
Simple Python codes to automatically write the shell scripts for running [hscPipe6](https://hsc.mtk.nao.ac.jp/pipedoc/pipedoc_6_e/index.html)

* ``mkscr_hsc_server.py`` - when you run hscPipe6 in a single server
* ``mkscr_hsc_cluster.py`` - when you run hscPipe6 in a cluster with multiple nodes


## Prerequisites
* The hscPipe6 pipeline should be installed. ([Reference link](https://hsc.mtk.nao.ac.jp/pipedoc/pipedoc_6_e/install_env_e/install.html))
* The following Python modules should be installed.
  * ``numpy >= 1.18.1``
  * ``pandas >= 1.0.1``
  * ``sqlite3`` ([Reference link](https://docs.python.org/3/library/sqlite3.html))


## Workflows
* Making working directory
```
ipython
run start_drz.py
run opt_1.py
run mat_1.py
run twk_1.py
run drz_1.py
```

