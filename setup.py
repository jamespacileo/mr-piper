from setuptools import setup, find_packages

import sys
sys.path.append(".")

import json

module_data = None
with open("piper.json", "r") as file:
    module_data = json.load(file)
    file.close()

# from mrpiper.vendor.requirements.parser import parse as parse_requirements
# dependencies = list(parse_requirements("-r requirements.txt"))

setup(
    name=module_data.get("name"),
    version=module_data.get("version", '0.1.2a3'),
    license=module_data.get("license"),
    py_modules=module_data.get("py_modules"),
    author=module_data.get("author"),
    author_email=module_data.get("author_email")
    packages=find_packages(),

    keywords=module_data.get("keywords"),

    url=module_data.get("repository"),

    install_requires=[_key for _key in module_data.get("dependencies", {})],

    extra_require={
        'dev': [_key for _key in module_data.get("dependencies", {})],

    }
    # install_requires=[item.line for item in dependencies],
    # install_requires=[
    #     'pytest',
    #     'click',
    #     'delegator.py',
    #     'pytest',
    #     'pip-tools',
    #     'requests',
    #     'parse',
    #     'simplejson',
    #     'crayons',
    #     'path.py',
    # ],
    entry_points=module_data.get("entry_points"),
    classifiers=module_data.get("classifiers"),
)
