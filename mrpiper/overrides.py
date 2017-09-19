

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
