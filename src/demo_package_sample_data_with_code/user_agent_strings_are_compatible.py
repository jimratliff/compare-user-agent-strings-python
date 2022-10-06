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

def user_agent_strings_are_compatible(ua_string_1, ua_string_2, *, strict = False, verbose=False):
    """
    Compares two user-agent strings to determine whether the second one
    is compatible with the first in the sense that both could have been
    sent by the same machine/browser, allowing for an intervening
    upgrade in the OS and/or browser.

    A third, optional, argument is “strict”, which if True, requires that the
    numerical version numbers (major, minor, etc.) for OS and browser are
    identical in both user-agent strings. This is appropriate for sessions 
    that are not extended (i.e., not “remember me”) because any upgrade of OS
    or browser would end the session.
    
    However, If the session is an extended, i.e., “remember me,” session, a
    user might upgrade the OS or browser during the extended session. Using
    `strict=True` would force that user to re-login after any browser or OS
    upgrade. For extended sessions, consider setting `strict=False` (the
    default) to allow for upgrades of the OS and/or browser during the extended
    session. In this case, only major and minor components (not patch)
    components are tested.

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
                    else:
                        # This is a tentative assignment
                        is_compatible = True
                else:
                    if value_1_major_value != value_2_major_value:
                        discrepancy_message = f"{discrepancy_message_base}{major}."
                        is_compatible = False
                    else:
                        # This is a tentative assignment
                        is_compatible = True
                
                if is_compatible:
                    # If here, either (a) majors are equal or (b) major_2 > major_1. If (b), we can quit.
                    # Only if (a) do we need to check the minors.
                    if value_2_major_value == value_1_major_value:
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
                        pass
                else:
                    pass
            else:
                discrepancy_message = f"{discrepancy_message_base}{major} and/or {minor}."
                is_compatible = False
        return(is_compatible, discrepancy_message)


    (is_compatible, discrepancy_message) = _is_compatible_after_comparing_attributes_that_must_be_equal()

    if ((not strict) and is_compatible):
        # If strict, comparisons are complete; if is_compatible, no discrepancy was found
        (is_compatible, discrepancy_message) = _is_compatible_after_comparing_version_numbers()

    return (is_compatible, discrepancy_message)

def main():
    

    # Base case
    ua_0 = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:104.1) Gecko/20100101 Firefox/105.1',
            "Base case ✅ ✅")
    # Constant OS major; decrease OS minor ❌ ❌
    ua_1 = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:104.1) Gecko/20100101 Firefox/105.1',
            "Constant OS major; decrease OS minor ❌ ❌")
    # Constant OS major; increase OS minor ✅ ❌
    ua_2 = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:104.1) Gecko/20100101 Firefox/105.1',
            "Constant OS major; increase OS minor ✅ ❌")
    # Increase OS major; decrease OS minor ✅ ❌
    ua_3 = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 11.14; rv:104.1) Gecko/20100101 Firefox/105.1',
            "Increase OS major; decrease OS minor ✅ ❌")
    # Decrease OS major; increase OS minor ❌ ❌
    ua_4 = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 9.16; rv:104.1) Gecko/20100101 Firefox/105.1',
            "Decrease OS major; increase OS minor ❌ ❌")
    # Increase UA-major; decrease UA-minor ✅ ❌
    ua_5 = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:104.1) Gecko/20100101 Firefox/106.0',
            "Increase UA-major; decrease UA-minor ✅ ❌")
    # Decrease UA-major; increase UA-minor ❌ ❌
    ua_6 = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:104.1) Gecko/20100101 Firefox/104.2',
            "Decrease UA-major; increase UA-minor ❌ ❌")
    # Constant UA-major; increase UA-minor ✅ ❌
    ua_7 = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:104.1) Gecko/20100101 Firefox/105.2',
            "Constant UA-major; increase UA-minor ✅ ❌")
    # Constant UA-major; decrease UA-minor  ❌ ❌
    ua_8 = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:104.1) Gecko/20100101 Firefox/105.0',
            "Constant UA-major; decrease UA-minor  ❌ ❌")
    # Change User-Agent Family to Chrome ❌ ❌
    ua_9 = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
            "Change User-Agent Family to Chrome ❌ ❌")
    # Change OS to Windows ❌ ❌
    ua_10 = ("Mozilla/5.0 (Windows NT 5.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1",
            "Change OS to Windows ❌ ❌")
    # Windows, Internet Explorer 6
    ua_11 = ("Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)", "Windows, Internet Explorer 6 ❌ ❌")

    ua_strings = [ua_0, ua_1, ua_2, ua_3, ua_4, ua_5, ua_6, ua_7, ua_8, ua_9, ua_10, ua_11]

    print(8 * "\n", 20 * " 👁 ", 8 * "\n")
    # for ua_string in ua_strings:
    #     for strict in (False, True):
    #         print(20*" – ")
    #         print(ua_string[1])
    #         print(f"Strict = {strict}")
    #         are_compatible = user_agent_strings_are_compatible(ua_0[0], ua_string[0], strict=strict, verbose=False)
    #         print(f"Compatible?: {are_compatible}")
    #         print(20*" 🎃 ")
    #     print(20*" 👹 ")

    for ua_string_1 in ua_strings:
        for ua_string_2 in ua_strings:
            print(20*" 👹 ")
            print(ua_string_1[0])
            print(ua_string_2[0])
            # for strict in (False, True):
            for strict in {True}:
                print(f"Strict = {strict}")
                are_compatible = user_agent_strings_are_compatible(ua_string_1[0], ua_string_2[0], strict=strict, verbose=False)
                char = "✅" if are_compatible[0] else "❌"
                print(f"Compatible?: {char} {are_compatible}")
                print(20*" – ")
                # print(20*" 🎃 ")
                




if __name__ == "__main__":
    main()
    exit(0)