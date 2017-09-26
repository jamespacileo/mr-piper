
import os
import semantic_version

class Version(semantic_version.Version):
    original_version = None

    @classmethod
    def coerce(self, version_string, partial=False):
        version = super(Version, self).coerce(version_string, partial)
        version.original_version = version_string
        return version

class Spec(semantic_version.Spec):
    pass


from pip.req.req_install import InstallRequirement
from pip.req.req_file import parse_requirements, process_line
from .vendor.requirements.requirement import Requirement

class SmartRequirement(InstallRequirement):

    original_line = None
    line = None
    vcs = None
    specs = None

    helper_req = None

    @classmethod
    def from_line(cls, line):
        req = super(SmartRequirement, cls).from_line(line)
        req.original_line = line
        req.helper_req = Requirement.parse_line(line)
        req.specs = req.helper_req.specs
        req.vcs = req.helper_req.vcs
        req.local_file = req.helper_req.local_file
        if req.req:
            req.line = req.req.__str__()
        else:
            req.line = req.link.__str__()
        return req

    @classmethod
    def from_editable(cls, line):
        req = super(SmartRequirement, cls).from_editable(line)
        req.original_line = line
        req.helper_req = Requirement.parse_editable(line)
        req.specs = req.helper_req.specs
        req.vcs = req.helper_req.vcs
        req.local_file = req.helper_req.local_file
        if req.req:
            req.line = req.req.__str__()
        else:
            req.line = req.link.__str__()
        return req


def parse(reqstr):
    """
    Parse a requirements file into a list of Requirements

    See: pip/req.py:parse_requirements()

    :param reqstr: a string or file like object containing requirements
    :returns: a *generator* of Requirement objects
    """
    filename = getattr(reqstr, 'name', None)
    try:
        # Python 2.x compatibility
        if not isinstance(reqstr, basestring):
            reqstr = reqstr.read()
    except NameError:
        # Python 3.x only
        if not isinstance(reqstr, str):
            reqstr = reqstr.read()

    for line in reqstr.splitlines():
        line = line.strip()
        if line == '':
            continue
        elif not line or line.startswith('#'):
            # comments are lines that start with # only
            continue
        elif line.startswith('-r') or line.startswith('--requirement'):
            _, new_filename = line.split()
            new_file_path = os.path.join(os.path.dirname(filename or '.'),
                                         new_filename)
            with open(new_file_path) as f:
                for requirement in parse(f):
                    yield requirement
        elif line.startswith('-f') or line.startswith('--find-links') or \
                line.startswith('-i') or line.startswith('--index-url') or \
                line.startswith('--extra-index-url') or \
                line.startswith('--no-index'):
            warnings.warn('Private repos not supported. Skipping.')
            continue
        elif line.startswith('-Z') or line.startswith('--always-unzip'):
            warnings.warn('Unused option --always-unzip. Skipping.')
            continue
        elif line.startswith('-e'):
            yield SmartRequirement.from_editable(line)
        else:
            yield SmartRequirement.from_line(line)
