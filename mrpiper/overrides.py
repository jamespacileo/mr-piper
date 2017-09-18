

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
