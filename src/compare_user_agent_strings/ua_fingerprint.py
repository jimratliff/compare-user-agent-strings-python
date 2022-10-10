"""
Compares two successive user-agent string to determine whether the second is
plausibly consistent with the second.
"""

import pprint

# pip install ua-parser
from ua_parser import user_agent_parser

pp = pprint.PrettyPrinter(indent=4)

class ClientFingerprint():
    """
    Object records parameters to fingerprint a web client from the user-agent
    string it sent to the server.
    """
    def __init__(self, uastring, verbose=False):
        parsed_string = user_agent_parser.Parse(uastring)

        if verbose:
            pp.pprint(parsed_string)

        self.string = parsed_string["string"]

        self.device = parsed_string["device"]
        self.device_brand = self.device["brand"]
        self.device_family = self.device["family"]
        self.device_model = self.device["model"]

        self.os = parsed_string["os"]
        self.os_family = self.os["family"]
        self.os_major = self.os["major"]
        self.os_minor = self.os["minor"]
        self.os_patch = self.os["patch"]
        self.os_patch_minor = self.os["patch_minor"]

        self.user_agent = parsed_string["user_agent"]
        self.user_agent_family = self.user_agent["family"]
        self.user_agent_major = self.user_agent["major"]
        self.user_agent_minor = self.user_agent["minor"]
        self.user_agent_patch = self.user_agent["patch"]


def print_parsed_user_agent_string(ua_string):
    """
    Pretty prints a fully parsed version of supplied user-agent string.
    """

    verbosely_parsed_user_agent_string = ClientFingerprint(ua_string, verbose=True)


def user_agent_strings_are_compatible(ua_string_1, ua_string_2, *, strict = False, verbose=False):
    """
    Compares two user-agent strings to determine whether the second one is
    compatible with the first in the sense that both could have been sent by
    the same machine/browser, optionally allowing for an intervening upgrade in
    the OS and/or browser.

    A third, optional, argument is “strict”, which if True, requires that the
    numerical version numbers (major, minor, etc.) for OS and browser are
    identical in both user-agent strings. This is appropriate for transient
    sessions (that end when the browser is closed; not “remember me”) because
    any upgrade of OS or browser would end the session.
    
    However, If the session is an extended, i.e., “remember me,” session, a
    user might upgrade the OS or browser during the extended session. Using
    `strict=True` would force that user to re-login after any browser or OS
    upgrade. For extended sessions, consider setting `strict=False` (the
    default) to allow for upgrades of the OS and/or browser during the extended
    session. A downgrade of either browser or OS is sufficient to trigger a
    return value of `False`, just as in the `strict=True` case. When testing
    version numbers, only major and minor components (not patch) components are
    considered.

    Some attributes are required to be equal across the two strings, because 
    those attributes should be immutable during any session, even an extended
    one. (E.g., "Apple", "Mac", "Mac OS X", "Chrome").

    Returns a tuple (is_compatible, discrepancy_message), where is_compatible =
        True    There is no conflict between the two user-agent strings
        False   There is a conflict between the two user-agent string.
                The session ID should be revoked because the session cookie
                may have been stolen by a different machine.
    """

    discrepancy_message_base = "Incompatible_discrepancy between user-agent strings: "
    discrepancy_message_if_compatible = ""
    discrepancy_message = discrepancy_message_if_compatible
    default_attribute_value = "not available"
    attributes_that_must_be_equal = ["device_brand",
                                     "device_family",
                                     "device_model",
                                     "os_family",
                                     "user_agent_family"
                                    ]

    attributes_that_must_be_equal_in_strict = ["os_major",
                                               "os_minor",
                                               "os_patch",
                                               "os_patch_minor",
                                               "user_agent_major",
                                               "user_agent_minor",
                                               "user_agent_patch"
                                              ]

    if strict:
        attributes_that_must_be_equal = attributes_that_must_be_equal + attributes_that_must_be_equal_in_strict

    # Parses each user-agent string into an object whose attributes are the
    # relevant components to test
    fingerprint_1 = ClientFingerprint(ua_string_1, verbose=verbose)
    fingerprint_2 = ClientFingerprint(ua_string_2, verbose=verbose)

    def _is_compatible_after_comparing_attributes_that_must_be_equal():
        """
        Inner function utility.

        Compares all the attributes that must be equal if the user-agent
        strings are compatible.
        """
        discrepancy_message = discrepancy_message_if_compatible

        for attribute in attributes_that_must_be_equal:
            value_1 = getattr(fingerprint_1, attribute, default_attribute_value)
            value_2 = getattr(fingerprint_2, attribute, default_attribute_value)

            if value_1 != value_2:
                discrepancy_message = f"{discrepancy_message_base}{attribute}: 1: {value_1}, 2: {value_2}."
                is_compatible = False
                break
            else:
                # if strict=False, this is a tentative assignment.
                is_compatible = True

        return(is_compatible, discrepancy_message)


    def _numeric_version_number_if_possible(fingerprint, attribute):
        """
        Inner function utility.

        If possible, converts supplied version number string (e.g., major or 
        minor) to an integer.

        Returns a tuple (is_numeric, returned_value), where
            is_numeric      is True if the string could be converted to int;
                            otherwise False
            returned_value  is the int form of the string if possible or, if
                            not, the original string.
        """

        version_number_string = getattr(fingerprint, attribute, default_attribute_value)

        try:
            numeric_version_number = int(version_number_string)
        except (ValueError, TypeError):
            returned_value = version_number_string
            is_numeric = False
        else:
            returned_value = numeric_version_number
            is_numeric = True

        return (is_numeric, returned_value)


    def _is_compatible_after_comparing_version_numbers():

        discrepancy_message = discrepancy_message_if_compatible

        for (major, minor) in [("os_major", "os_minor"), ("user_agent_major", "user_agent_minor")]:
            (value_1_major_is_numeric, value_1_major_value) = _numeric_version_number_if_possible(fingerprint_1, major)
            (value_1_minor_is_numeric, value_1_minor_value) = _numeric_version_number_if_possible(fingerprint_1, minor)
            (value_2_major_is_numeric, value_2_major_value) = _numeric_version_number_if_possible(fingerprint_2, major)
            (value_2_minor_is_numeric, value_2_minor_value) = _numeric_version_number_if_possible(fingerprint_2, minor)

            majors_agree_re_numeric = (value_1_major_is_numeric == value_2_major_is_numeric)
            minors_agree_re_numeric = (value_1_minor_is_numeric == value_2_minor_is_numeric)

            if  (majors_agree_re_numeric and minors_agree_re_numeric):

                majors_are_numeric = value_1_major_is_numeric and value_2_major_is_numeric
                minors_are_numeric = value_1_minor_is_numeric and value_2_minor_is_numeric
                
                if majors_are_numeric:
                    # If the major version number of the second user-agent string (or either OS or user-agent) is
                    # greater than or equal to the corresponding major version number of the first user-agent string,
                    # the major version number passes the test (so far).
                    if value_2_major_value < value_1_major_value:
                        discrepancy_message = f"{discrepancy_message_base}downgrade: {major}."
                        is_compatible = False
                        break
                    else:
                        # We know the major values are either equal or an upgrade, in either case we want to
                        # assign is_compatible=True at least tentatively.
                        is_compatible = True
                        if value_2_major_value > value_1_major_value:
                            # The major version has been upgraded, so no need to check minor version. We make
                            # the is_compatible=True assign final.
                            break
                else:
                    # Majors are not numeric, so we require them to be equal
                    if value_1_major_value != value_2_major_value:
                        discrepancy_message = f"{discrepancy_message_base}{major}."
                        is_compatible = False
                        break
                    else:
                        # This is a tentative assignment
                        is_compatible = True
                
                # If here, the two strings are tentatively compatible w.r.t. major version
                # (Because any is_compatible=False has broken out of the loop)

                # Now we check the minors
                if minors_are_numeric:
                    if value_2_minor_value < value_1_minor_value:
                        discrepancy_message = f"{discrepancy_message_base}downgrade: {minor}."
                        is_compatible = False
                else:
                    if value_1_minor_value != value_2_minor_value:
                        discrepancy_message = f"{discrepancy_message_base}{minor}."
                        is_compatible = False



            else:
                # At least one major or minor differs regarding numeric
                discrepancy_message = f"{discrepancy_message_base}{major} and/or {minor}."
                is_compatible = False
                break
            
            # Finished assessment of current (major, minor) tuple
            # If the first (major, minor) tuple is incompatible, no need to check the next tuple.
            if not is_compatible:
                break
    
        # end of for (major, minor) loop
        return(is_compatible, discrepancy_message)


    (is_compatible, discrepancy_message) = _is_compatible_after_comparing_attributes_that_must_be_equal()

    if ((not strict) and is_compatible):
        # If strict, comparisons are complete; if is_compatible, no discrepancy was found
        (is_compatible, discrepancy_message) = _is_compatible_after_comparing_version_numbers()

    return (is_compatible, discrepancy_message)
