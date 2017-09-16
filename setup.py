from setuptools import setup, find_packages

setup(
    name='mrpiper',
    version='0.1',
    py_modules=['mrpiper.cli'],
    packages=find_packages(),
    install_requires=[
        'pytest',
        'click',
        'delegator.py',
        'pytest',
        'pip-tools',
        'requests',
        'parse',
        'simplejson',
        'crayons',
        'path.py',
    ],
    entry_points='''
        [console_scripts]
        piper=mrpiper.cli:cli
    ''',
)