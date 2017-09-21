from setuptools import setup, find_packages
import os
import json
import codecs

here = os.path.abspath(os.path.dirname(__file__))

module_data = None
with open(os.path.join(here, "piper.json")) as file:
    module_data = json.load(file)
    file.close()

readme_filename = module_data.get("readme_filename")
long_description = ""
if readme_filename:
    with codecs.open(os.path.join(here, readme_filename), encoding='utf-8') as file:
        long_description = "\n" + file.read()
        file.close()
# from mrpiper.vendor.requirements.parser import parse as parse_requirements
# dependencies = list(parse_requirements("-r requirements.txt"))

setup(
    name=module_data.get("name"),
    version=module_data.get("version", '0.1.2a3'),
    license=module_data.get("license"),
    py_modules=module_data.get("py_modules"),
    author=module_data.get("author"),
    author_email=module_data.get("author_email"),
    packages=find_packages(),

    description=module_data.get("description", ""),
    long_description=long_description,

    keywords=module_data.get("keywords"),

    url=module_data.get("repository"),

    install_requires=[_item[1] for _item in module_data.get("dependencies", {}).items()],

    extra_require={
        'dev': [_item[1] for _item in module_data.get("dev_dependencies", {}).items()],

    },

    include_package_data=True,
    # include_package_data=module_data.get("include_package_data", True),
    # package_data=module_data.get("package_data", {}),
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
