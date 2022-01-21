# Copyright (C) 2020 INAF
# This software is distributed under the terms of the BSD-3-Clause license
#
# Authors:
#    Parmiggiani Nicolò <nicolo.parmiggiani@inaf.it>
#    Bulgarelli Andrea <andrea.bulgarelli@inaf.it>
#    Baroncelli Leonardo <leonardo.baroncelli@inaf.it>
#    Addis Antonio <antonio.addis@inaf.it>

from setuptools import setup

setup( name='gammaflash-pipe',
       version='1.0.0',
       author="Antonio Addis",
       author_email='antonio.addis@inaf.it',
       packages=['gammaflash'],
       package_dir={ 'gammaflash': 'gammaflash' }
    )
