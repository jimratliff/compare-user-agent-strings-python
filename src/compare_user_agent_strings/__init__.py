# The following import (from . __version__ import __version__) is a component
# of the mechanism to provide a single source for the version number.
# For more information, see the docstring comments in the __version__.py file.

from . __version__ import __version__

from . ua_fingerprint import (
                              print_parsed_user_agent_string,
                              user_agent_strings_are_compatible_strictly,
                              user_agent_strings_are_compatible
                              )
