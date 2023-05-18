from setuptools import setup, find_packages

VERSION = '0.2.0'
DESCRIPTION = 'A motion tracking 3D movier render'
LONG_DESCRIPTION = 'A package that renders movies from 3D motion tracked data, for example from 3D skeleton joint tracking data'

setup(
    name="motionrender",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author="Derek Harter",
    author_email="Derek.Harter@tamuc.edu",
    license='GPL-3',
    packages=find_packages(),
    install_requires=[],
    keywords='motion tracking, 3D rendering',
    classifiers= [
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Visualization",
    ]
)
