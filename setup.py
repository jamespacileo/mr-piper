from setuptools import setup, find_packages

setup(
    name='mrpiper',
    version='0.1',
    license="MIT",
    py_modules=['mrpiper.cli'],
    author='James Pacileo',
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
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
)
