[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/mms-fcul/PypKa/blob/master/pypka/example/notebook/pypka.ipynb) [![PyPI version](https://badge.fury.io/py/pypka.svg)](https://badge.fury.io/py/pypka) [![CircleCI](https://circleci.com/gh/mms-fcul/PypKa.svg?style=svg)](https://circleci.com/gh/mms-fcul/PypKa) [![Codacy Badge](https://api.codacy.com/project/badge/Coverage/77db3bc226c94625acd3cea0e14c23ad)](https://www.codacy.com/app/pedrishi/PypKa?utm_source=github.com&utm_medium=referral&utm_content=mms-fcul/PypKa&utm_campaign=Badge_Coverage) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/77db3bc226c94625acd3cea0e14c23ad)](https://www.codacy.com/app/pedrishi/PypKa?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=mms-fcul/PypKa&amp;utm_campaign=Badge_Grade) [![Documentation Status](https://readthedocs.org/projects/pypka/badge/?version=latest)](https://pypka.readthedocs.io/en/latest/?badge=latest)


# PypKa

A python module for flexible Poisson-Boltzmann based pKa calculations with proton tautomerism
DOI: <a href="https://doi.org/10.1021/acs.jcim.0c00718">10.1021/acs.jcim.0c00718</a>

```
@article{reis2020jcim,
author = {Reis, Pedro B. P. S. and Vila-Viçosa, Diogo and Rocchia, Walter and Machuqueiro, Miguel},
title = {PypKa: A Flexible Python Module for Poisson–Boltzmann-Based pKa Calculations},
journal = {Journal of Chemical Information and Modeling},
volume = {60},
number = {10},
pages = {4442-4448},
year = {2020},
doi = {10.1021/acs.jcim.0c00718}
}
```

# Documentation & Basic Usage

  Documentation can be found [here](https://pypka.readthedocs.io/en/latest/)

  Starting templates for the the API and CLI usage can be found [here](https://pypka.readthedocs.io/en/latest/example.html) while a online notebook is hosted at [Google Colab](https://colab.research.google.com/github/mms-fcul/PypKa/blob/master/pypka/example/notebook/pypka.ipynb)


# Installation & Dependencies

  - python2.6>= & python3.5>=
  - libgfortran4
  - gawk
  - pytest
  - numpy

```
  pip3 install pypka
  apt install gawk gcc gfortran libgfortran4 python2
```

# License

  pypka is distributed under a LGPL-3.0, however delphi4py depends on
  DelPhi which is proprietary. To use DelPhi the user is required to
  download the DelPhi license
  [here](https://honiglab.c2b2.columbia.edu/software/cgi-bin/software.pl?input=DelPhi)

# Contacts

  Please submit a github issue to report bugs and to request new features.
  Alternatively you may find the developer [here](mailto:pdreis@fc.ul.pt). Please visit ou [website](http://mms.rd.ciencias.ulisboa.pt/) for more information.
