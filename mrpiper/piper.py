# encoding: utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
from builtins import map, filter, zip

import contextlib
import codecs
import json
import os
import sys
import distutils.spawn
import shutil
import signal
import tempfile
import pdb
import crayons
import time
import logging
logger = logging.getLogger(__name__)


import tabulate
from path import Path
import parse
import click
import delegator
import semantic_version
import click_spinner

from pkg_resources import Requirement as Req
from pkg_resources import RequirementParseError
from pip.req.req_file import parse_requirements, process_line

from .vendor.requirements.requirement import Requirement
from .vendor.requirements.parser import parse as parse_requirements
from .vendor import pipdeptree

# import pipfile



from .utils import add_to_requirements_file, compile_requirements, add_to_requirements_lockfile,  \
    remove_from_requirements_file, get_packages_from_requirements_file, get_package_from_requirement_file, \
    shellquote
from . import overrides
from .project import PythonProject

project = PythonProject()

def which(command):
    if os.name == 'nt':
        if command.endswith('.py'):
            return os.sep.join([project.virtualenv_dir] + ['Scripts\{0}'.format(command)])
        return os.sep.join([project.virtualenv_dir] + ['Scripts\{0}.exe'.format(command)])
    return os.sep.join([project.virtualenv_dir] + ['bin/{0}'.format(command)])


def which_pip(allow_global=False):
    """Returns the location of virtualenv-installed pip."""
    if allow_global:
        return distutils.spawn.find_executable('pip')

    return which('pip')

def get_dependency_tree():
    vendor_path = Path(pipdeptree.__file__)
    command = "{0} {1} --json".format(which("python"), shellquote(vendor_path))
    c = delegator.run(command)
    if c.return_code != 0:
        return {}
    return json.loads(c.out)

def pip_freeze():
    # temp = tempfile.TemporaryFile()
    # pip_command = '{0} freeze > {1}'.format(which_pip(), temp.name)
    pip_command = '{0} freeze'.format(which_pip())
    c = delegator.run(pip_command)

    # click.echo(pip_command)
    # click.echo(c2.out)

    frozen_reqs = c.out
    frozen_reqs = [req for req in parse_requirements(frozen_reqs)]

    # click.echo(frozen_reqs)
    return frozen_reqs

    # if c.return_code == 0:
    #     return False

    # # Return the result of the first one that runs ok, or the last one that didn't work.
    # return c

def pip_install_list(packages, allow_global=False):

    pip_command = "{0} install --no-deps {1}".format(
        which_pip(),
        " ".join(packages)
    )
    c = delegator.run(pip_command)
    return c

    # pip_commands = []
    # for package in packages:
    #     pip_command = "{0} install --no-deps {1}".format(
    #         which_pip(),
    #         package
    #     )
    #     pip_commands.append(pip_command)


    # delegated_commands = []
    # for cmd in pip_commands:
    #     click.echo(cmd)
    #     c = delegator.run(cmd, block=True)
    #     delegated_commands.append(c)

    # map(lambda x: x.block(), delegated_commands)
    # return delegated_commands

def pip_install(
    package_name=None, r=None, allow_global=False, no_deps=False, block=True, upgrade=False
):

    # Create files for hash mode.
    # if (not ignore_hashes) and (r is None):
    #     r = tempfile.mkstemp(prefix='pipenv-', suffix='-requirement.txt')[1]
    #     with open(r, 'w') as f:
    #         f.write(package_name)

    if r:
        install_reqs = ' -r {0}'.format(r)
    elif package_name.startswith('-e '):
        install_reqs = ' -e "{0}"'.format(package_name.split('-e ')[1])
    else:
        install_reqs = ' "{0}"'.format(package_name)

    no_deps = '--no-deps' if no_deps else ''
    upgrade_str = '-U' if upgrade else ''

    pip_command = '"{0}" install {2} {1} {3} --exists-action w'.format(
        which_pip(allow_global=allow_global),
        install_reqs,
        no_deps,
        upgrade_str
    )
    logger.debug(pip_command)
    c = delegator.run(pip_command, block=block)

    # if c.return_code == 0:
    #     return c

    # Return the result of the first one that runs ok, or the last one that didn't work.
    return c

def pip_uninstall(packages):
    pip_command = "{0} uninstall --yes {1}".format(which_pip(), " ".join(packages))
    logger.debug(pip_command)
    c = delegator.run(pip_command)
    return c

def pip_versions(package_name):
    pip_command = "{0} install {1}==0.xx".format(which_pip(), package_name)
    c = delegator.run(pip_command)
    no_matching = "No matching distribution found for mrpiper" in c.err
    if no_matching:
        return False

    result = parse.search("from versions: {})", c.err)
    # click.echo([package_name, c.err])
    # click.echo([package_name, result.fixed[0], [item for item in parse.findall(" {:S},", result.fixed[0] + ",")]])
    results = [result.fixed[0] for result in parse.findall(" {:S},", result.fixed[0] + ",")]
    # last_result = [result.fixed[0] for result in parse.findall(" {:w})", result.fixed[0])]
    # click.echo(results)
    return results


def pip_outdated():
    pip_command = "{0} list -o --format columns".format(which_pip())
    logger.debug(pip_command)
    c = delegator.run(pip_command)
    return c


def init(noinput=False, private=False):
    # create requirements structure
    # create virtualenv
    if noinput:
        init_data = {
            "private": private
        }
    project.setup(noinput=noinput, init_data=init_data)

def add(package_line, editable=False, dev=False, dont_install=False):
    # create requirements
    # init()
    if editable:
        click.secho("Installing {0} in editable mode...".format(crayons.yellow(package_line)))
    else:
        click.secho("Installing {0}...".format(crayons.yellow(package_line)))

    # req = Req.parse(package_line)
    # logger.debug("{}".format(req.__dict__))

    # if editable:
    #     req = Requirement.parse_editable(package_line)
    # else:
    #     req = Requirement.parse_line(package_line)

    if editable:
        req = overrides.SmartRequirement.from_editable(package_line)
    else:
        req = overrides.SmartRequirement.from_line(package_line)

    # click.echo(req.__dict__)

    logger.debug("Requirement parsed: {}".format(req.__dict__))

    has_specs = len(req.specs) > 0
    is_vcs = req.vcs
    is_local_file = req.local_file
    is_editable = req.editable

    # if is_vcs and (not is_editable):
    #     # print("Make sure ")
    #     req.editable = True
    #     package_line = "-e {0}".format(package_line)

    if is_vcs and (not req.name):
        click.secho("Make sure to add #egg=<name> to your url", fg="red")
        return

    c = pip_install(package_line, allow_global=False, block=True)

    # counter = 0
    # with click.progressbar(length=10) as bar:
    #     while time.sleep(0.5):
    #         counter = max(counter + 1, 10)
    #         bar.update(counter)
    #         if not (c.blocking == None):
    #             click.echo("Return code is:" + c.return_code)
    #             bar.update(10)
    #             break
    # result = parse.search("Successfully installed {} \n", c.out)

    if not (c.return_code == 0):
        click.secho(c.err, fg="red")
        click.echo(
            crayons.red("Failed to install ") + crayons.yellow(req.name) + crayons.red(" ✗")
        # "Package {0} removed ✓".format(req.name), fg="green"
        )
        sys.exit()
    else:
        click.secho(c.out.rstrip(), fg="blue")

        click.echo(
            crayons.green("Package ") + crayons.yellow(req.name) + crayons.green(" installed ✓")
            # crayons.green("Package {0} installed ✓".format(crayons.yellow(req.name)))
            )

    result = parse.search("Successfully installed {}\n", c.out)
    succesfully_installed = result.fixed[0].split() if result else []
    succesfully_installed = [item.rsplit('-', 1)[0] for item in succesfully_installed]
    existing_packages = [result.fixed[0] for result in parse.findall("Requirement already satisfied: {} in", c.out)]

    all_pkgs = succesfully_installed + existing_packages
    all_pkgs = [Req.parse(pkg).unsafe_name for pkg in all_pkgs]

    # click.secho("Locking requirements...")

    frozen_deps = pip_freeze()
    frozen_dep = next(filter(lambda x: x.name.lower() == req.name.lower(), frozen_deps), None)
    project.update_frozen_dependencies_in_piper_lock(frozen_deps)

    dependency = {
        "name": frozen_dep.name,
        "line": req.line if ((not req.vcs) and (not req.local_file) and req.specs) else frozen_dep.line,
        "specs": frozen_dep.specs,
        "dependencies": [pkg for pkg in all_pkgs if not (pkg == frozen_dep.name)]
    }
    project.add_dependency_to_piper_lock(dependency, dev=dev)
    project.update_requirement_files_from_piper_lock()

    click.secho("Requirements locked ✓", fg="green")

    # click.echo("All pkgs: {}".format(all_pkgs))

    # click.secho("Updating requirement files...")

    # if (not req.vcs) and (not req.local_file) and req.specs:
    #     add_to_requirements_file(req, os.path.join(".", "requirements", "dev.txt"))
    # else:
    #     add_to_requirements_file(frozen_dep, os.path.join(".", "requirements", "dev.txt"))
    # add_to_requirements_lockfile(frozen_deps, os.path.join(".", "requirements", "base-locked.txt"))

    click.secho("Requirements updated ✓", fg="green")
    # compile_requirements(os.path.join(".", "requirements", "base.txt"), os.path.join(".", "requirements", "base-locked.txt"))

    # print(req.__dict__)



def find_removable_dependencies(package_name):
    pass

def remove(package_line, dev=False):
    req = Requirement.parse(package_line)
    logger.debug(req.__dict__)
    logger.debug(package_line)
    click.secho("Removing package {0}...".format(crayons.yellow(req.name)) )

    removable_packages = project.find_removable_dependencies(req.name)
    if removable_packages:
        removable_packages.append(req.name)
        c = pip_uninstall(removable_packages)
    else:
        c = pip_uninstall([req.name])
    if not (c.return_code == 0):
        click.secho(c.err, fg="red")
        click.echo(
            crayons.red("Failed to remove ") + crayons.yellow(req.name) + crayons.red(" ✗")
        # "Package {0} removed ✓".format(req.name), fg="green"
        )
        sys.exit()
    else:
        click.secho(c.out.rstrip(), fg="blue")
    click.echo(
        crayons.green("Package ") + crayons.yellow(req.name) + crayons.green(" removed ✓")
        # "Package {0} removed ✓".format(req.name), fg="green"
        )

    # click.secho("Locking packages...")
    frozen_deps = pip_freeze()
    project.update_frozen_dependencies_in_piper_lock(frozen_deps)
    project.remove_dependency_to_piper_lock(req.name)
    click.secho("Packaged locked ✓", fg="green")

    project.update_requirement_files_from_piper_lock()

    # add_to_requirements_lockfile(frozen_deps, os.path.join(".", "requirements", "base-locked.txt"))

    # click.secho("Updating requirement files...")
    # remove_from_requirements_file(req, os.path.join(".", "requirements", "base.txt"))
    click.secho("Requirement files updated ✓", fg="green")

def install(dev=False, force_lockfile=False):
    # should run project setup

    virtualenv_exists = project.virtualenv_dir.exists()
    lock_exists = project.piper_lock_dir.exists()
    piper_file_exists = project.piper_file_dir.exists()
    dev_locked_txt_exists = project.requirements_file("dev-locked.txt").exists()
    base_locked_txt_exists = project.requirements_file("base-locked.txt").exists()
    dev_txt_exists = project.requirements_file("dev.txt").exists()
    base_txt_exists = project.requirements_file("base.txt").exists()

    project.setup(noinput=True)

    # first choice piper.json
    # second choice requirements

    packages = None

    if lock_exists:
        click.echo("Installing from the piper lock file")
        packages = [item["line"] for item in project.piper_lock["frozen_deps"]]
    else:
        click.echo("Piper lock doesn't exist. Using next best option...")

    if piper_file_exists and (not packages):
        click.echo("Installing from the piper file piper.json")
        packages = [x[1] for x in project.piper_file["dependencies"].items()]
        if dev:
            packages += [x[1] for x in project.piper_file["devDependencies"].items()]
    else:
        click.echo("No piper.json file. Using next best option...")

    if dev:
        if dev_locked_txt_exists and (not packages):
            click.echo("Installing from requirements/dev-locked.txt")
            packages = [item.line for item in get_packages_from_requirements_file(project.requirements_file("dev-locked.txt"))]
        if dev_txt_exists and (not packages):
            click.echo("Installing from requirements/dev.txt")
            packages = [item.line for item in get_packages_from_requirements_file(project.requirements_file("dev.txt"))]

    if base_locked_txt_exists and (not packages):
        click.echo("Installing from requirements/base-locked.txt")
        packages = [item.line for item in get_packages_from_requirements_file(project.requirements_file("base-locked.txt"))]
    if base_txt_exists and (not packages):
        click.echo("Installing from requirements/base.txt")
        packages = [item.line for item in get_packages_from_requirements_file(project.requirements_file("base.txt"))]

    if not packages:
        click.echo(
            crayons.red("No available files to install packages from. Please run ") + crayons.yellow("piper init")
            )
        sys.exit()

    # if dev:
    #     packages = get_packages_from_requirements_file(project.requirements_file("dev-locked.txt"))
    # else:
    #     packages = get_packages_from_requirements_file(project.requirements_file("base-locked.txt"))

    c = pip_install_list(packages)
    click.secho(c.out, fg="blue")

    tree = get_dependency_tree()
    project.update_piper_lock_from_piper_file_and_tree(tree)


    # cmds = pip_install_list(packages)
    # for cmd in cmds:
    #     click.echo(cmd.out + cmd.err)
    click.secho("Install completed ✓", fg="green")

def outdated(all_pkgs=False, verbose=False, format="table"):
    # format can be table, json

    # logger.error("test error 2")

    click.echo("Fetching outdated packages")
    # c = pip_outdated()
    # click.echo([c.return_code, c.out, c.err])

    lock = project.piper_lock
    all_deps = map(lambda x: x[1], lock["frozen_deps"].items())
    prime_deps = filter(lambda x: not (x in lock["dependables"]), all_deps)

    which_deps = all_deps if all_pkgs else prime_deps

    outdated_map = []

    with click_spinner.spinner():
        for dep in all_deps:
            logger.debug("checking versions for {}".format(dep["name"]))
            found_versions = pip_versions(dep["name"])
            if found_versions == False:
                # TODO: Address failure to find versions for package
                logger.debug("Couldn't find versions for {}".format(dep["name"]))
                continue
            versions = list(found_versions)
            versions.reverse()
            try:
                current_version = overrides.Version.coerce(dep["specs"][0][1], partial=True)

                coerced_versions = list(map(lambda x: overrides.Version.coerce(x, partial=True), versions))
                version_mapping = map(lambda index, x: (x.__str__(), versions[index] ), enumerate(coerced_versions))

                if dep["specifier"]:
                    spec = next(map(lambda x: semantic_version.Spec("".join(x) ), dep["specs"]))
                # click.echo("{} {} {}".format(versions, spec, upgrade_specifier))
                valid_versions = list(spec.filter(coerced_versions))
                wanted_version = spec.select(valid_versions).original_version
                patch_version = semantic_version.Spec("~={}".format(current_version.major, current_version.minor, current_version.patch)).select(valid_versions).original_version
                minor_version = semantic_version.Spec("~={}".format(current_version.major, current_version.minor, current_version.patch)).select(valid_versions).original_version

            except ValueError as err:
                logger.debug("ValueError for {0} with {1}".format(dep["name"], err))
                current_version = dep["specs"][0][1]
                # click.echo(err)
                wanted_version = "not semantic"
                patch_version = ""
                minor_version = ""
            latest_version = versions[0]

            # outdated_map.append({
            #     'name': dep["name"],
            #     'current': current_version,
            #     'wanted': wanted_version.__str__(),
            #     'latest': latest_version.__str__(),
            # })

            if verbose:
                outdated_map.append([
                    dep["name"],
                    current_version,
                    crayons.yellow(wanted_version.__str__()),
                    patch_version.__str__(),
                    minor_version.__str__(),
                    latest_version.__str__(),
                ])
            else:
                outdated_map.append([
                    dep["name"],
                    current_version,
                    crayons.yellow(wanted_version.__str__()),
                    latest_version.__str__(),
                ])

    if format == "table":
        if verbose:
            click.echo(tabulate.tabulate(outdated_map, headers=["Name", "Current", "Wanted", "Patch", "Minor", "Latest"]))
        else:
            click.echo(tabulate.tabulate(outdated_map, headers=["Name", "Current", "Wanted", "Latest"]))
    else:
        headers = headers=["Name", "Current", "Wanted", "Patch", "Minor", "Latest"] if verbose else ["Name", "Current", "Wanted", "Latest"]
        output = [dict(zip(headers,item)) for item in outdated_map]
        click.echo(json.dumps(output, indent="    "))
    # frozen_reqs = [req for req in parse_requirements(os.path.join(".", "requirements", "base-locked.txt"))]

    # versions = pip_versions("django")
    # click.echo(versions)
    return

def upgrade(package_line, upgrade_level="latest", noinput=False):
    # get current version

    req = Requirement.parse(package_line)
    click.secho("Installing {0}...".format(crayons.yellow(req.name)))

    logger.debug(req.__dict__)

    is_flag_latest = upgrade_level in ["major", "latest"]

    dep_type = project.detect_type_of_dependency(req.name)
    dev = dep_type == "dev"
    if dep_type == "dev":
        local_package = get_package_from_requirement_file(req.name, project.requirements_file("dev-locked.txt"))
    else:
        local_package = get_package_from_requirement_file(req.name, project.requirements_file("base-locked.txt"))

    if not local_package:
        click.secho("Package is not installed", fg="red")
        sys.exit(1)

    if local_package.vcs or local_package.editable:
        click.secho("Skipped. Editable sources not supported at the moment")
        return

    if (not is_flag_latest) and (local_package.vcs):
        click.secho("Can't do patch or minor upgrade for packages installed via version control. Please use --latest")

    from pip._vendor.distlib.version import NormalizedVersion
    local_version = local_package.specs[0][1]
    norm = NormalizedVersion(local_version)
    clause = [str(item) for item in norm._release_clause]
    if len(clause) < 2:
        clause.extend(["0", "0"])
    elif len(clause) < 3:
        clause.append("0")

    upgrade_specifier = ""
    if upgrade_level == "patch":
        upgrade_specifier = "~={0}".format(".".join(clause))
    elif upgrade_level == "minor":
        del clause[2]
        upgrade_specifier = "~={0}".format(".".join(clause))

    if not noinput:
        versions = pip_versions(local_package.name)
        versions = list(map(lambda x: semantic_version.Version(x, partial=True), versions))
        versions.reverse()
        if upgrade_specifier:
            spec = semantic_version.Spec(upgrade_specifier)
        else:
            spec = map(lambda x: semantic_version.Spec("".join(x) ), req.specs)
        # click.echo("{} {} {}".format(versions, spec, upgrade_specifier))
        valid_versions = list(spec.filter(versions))
        wanted_version = spec.select(versions)

        echo_list = crayons.white("")
        for index, version in enumerate(valid_versions):
            echo_list = echo_list + crayons.yellow("[{}] ".format(index+1)) + crayons.white("{} ".format(version))


        chosen_index = click.prompt("Select one of the following versions: {}".format(echo_list), default=1)
        chosen_version = valid_versions[chosen_index-1]

        package_line = req.name + "==" + chosen_version.__str__()
    else:
        package_line = req.name + upgrade_specifier

    c = pip_install(package_line, allow_global=False, upgrade=True)
    # result = parse.search("Successfully installed {} \n", c.out)

    if not (c.return_code == 0):
        click.secho(c.err, fg="red")
        click.echo(
            crayons.red("Failed to install ") + crayons.yellow(req.name) + crayons.red(" ✗")
        # "Package {0} removed ✓".format(req.name), fg="green"
        )
        sys.exit()
    else:
        click.secho(c.out.rstrip(), fg="blue")

        click.echo(
            crayons.green("Package ") + crayons.yellow(req.name) + crayons.green(" installed ✓")
            # crayons.green("Package {0} installed ✓".format(crayons.yellow(req.name)))
            )


    result = parse.search("Successfully installed {}\n", c.out)
    succesfully_installed = result.fixed[0].split() if result else []
    succesfully_installed = [item.rsplit('-', 1)[0] for item in succesfully_installed]
    existing_packages = [result.fixed[0] for result in parse.findall("Requirement already satisfied: {} in", c.out)]

    all_pkgs = succesfully_installed + existing_packages
    all_pkgs = [Req.parse(pkg).unsafe_name for pkg in all_pkgs]

    # click.secho("Locking requirements...")

    frozen_deps = pip_freeze()
    frozen_dep = next(filter(lambda x: x.name.lower() == req.name.lower(), frozen_deps), None)
    project.update_frozen_dependencies_in_piper_lock(frozen_deps)

    dependency = {
        "name": frozen_dep.name,
        "line": frozen_dep.line,
        "specs": frozen_dep.specs,
        "dependencies": [pkg for pkg in all_pkgs if not (pkg == frozen_dep.name)]
    }
    project.add_dependency_to_piper_lock(dependency, dev=dev)
    project.update_requirement_files_from_piper_lock()

    click.secho("Requirements locked ✓", fg="green")

    # click.echo("All pkgs: {}".format(all_pkgs))

    # click.secho("Updating requirement files...")

    # if (not req.vcs) and (not req.local_file) and req.specs:
    #     add_to_requirements_file(req, os.path.join(".", "requirements", "base.txt"))
    # else:
    #     add_to_requirements_file(frozen_dep, os.path.join(".", "requirements", "base.txt"))
    # add_to_requirements_lockfile(frozen_deps, os.path.join(".", "requirements", "base-locked.txt"))

    click.secho("Requirements updated ✓", fg="green")
    # compile_requirements(os.path.join(".", "requirements", "base.txt"), os.path.join(".", "requirements", "base-locked.txt"))

    # print(req.__dict__)

def upgrade_all(upgrade_level="latest"):

    pkgs = get_packages_from_requirements_file(project.requirements_file("dev-locked.txt"))
    for package in pkgs:
        upgrade(upgrade_level)

def clear():
    project.clear()

if __name__ == "__main__":
    os.chdir("..")
    # init()
    # add("fabric==1.5")
    # add("fabric")
    # add("django>1.10")
    # add("-e git+https://github.com/requests/requests.git#egg=requests")
    # remove("fabric")
    # remove("django")
    # remove("requests")
    # install()
    outdated()
