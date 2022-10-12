"""
Compares two successive user-agent string to determine whether the second is
plausibly consistent with the second.

Exposes three functions publicly:
    print_parsed_user_agent_string(ua_string)
    user_agent_strings_are_compatible_strictly(ua_string_1, ua_string_2)
    user_agent_strings_are_compatible(ua_string_1, ua_string_2, *,
                                      strict = False)
where:
    ua_string, ua_string_1, ua_string_2 are user-agent strings such as:
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)'
    strict is a Boolean, signalling a stronger test for compatibility.

When a pair of user-agent strings is referenced,
    the first is interpreted as the user-agent string presented to the server
        when the legitimate user first authenticated;
    the second is interpreted as the user-agent string presented to the server
        along with the current request.

The question addressed by (a) `user_agent_strings_are_compatible_strictly()`
and (b) `user_agent_strings_are_compatible()` is whether the second user-agent
string appears to come from the same user/machine as did the first user-agent
string. The two functions can differ in the strictness of the criterion for 
compatibility. 

The function `user_agent_strings_are_compatible_strictly()` adopts a strict
standard.

The function `user_agent_strings_are_compatible(ua_string_1, ua_string_2, *,
strict = False)` adopts either (a) the strict standard, if strict==True, or
(b) a weaker standard that strives to reduce false positives, if
strict==False (the default value).

strict==True requires exact string equality between the two user-agent strings.
This is also sufficient, but not necessary, to satisfy the strict==False
standard.

When strict==False, we allow for an exemption from string equality when the
only “substantive difference” between the two strings is that one or both of
the operating system and/or browser has been upgraded between the time the
first string was provided and the time the second string was provided. (Note: 
an upgrade is detected only when the version is described *numerically*, not by
a string, e.g., “XP”.)

By “substantive difference,” we mean: first parse each user string into
attributes, using ua-parse, and compare the two strings on each parsed
attribute (other than version number attributes). If the two strings are
the same in that sense and the second string is an upgrade of the OS or browser
relative to the first (without the other entity, OS/browser, being a
downgrade), consider the two strings compatible (under strict==False).

Setting strict=True is appropriate for a transient cookie (i.e., a “session
cookie”), which is deleted automatically when the browser closes (if not before
when the user logs out), because there is no risk of a false positive in the
event of an operating system or browser upgrade. (Neither the operating system
nor the browser can be updated without deleting the transient cookie, because
performaing the upgrades would cause the browser to close and delete the
transient cookie.)

Setting strict=False can be appropriate in the case of a permanent cookie
(e.g.,“remember me” or “keep me logged in”), because such a cookie survives
browser restarts and system reboots and thus upgrades could occur without 
causing the cookie to be deleted.

(To be clear, if neither OS nor browser evinces an upgrade without either being
a downgrade, the standard of compatibility is the strict one: exact string 
equality. I.e., comparing components of parsed strings only has effect when it
turns out that the browser and/or OS was upgraded and neither downgraded.)
"""

import pprint

# pip install ua-parser
# The following import caused a problem after I added relative import statements into __init__.py.
# Moving the import into the constructor for ClientFingerprint for some reason fixed the problem.
#
# File "/Volumes/Avocado/Users/ada/Documents/GitHub_repos/compare-user-agent-strings-python/src/compare_user_agent_strings/__init__.py", line 7, in <module>
#   from ua_parser import user_agent_parser
#   ModuleNotFoundError: No module named 'ua_parser'
# vvvvvvvvvvvvvvv
# from ua_parser import user_agent_parser


class ClientFingerprint():
    """
    Object records parameters to fingerprint a web client from the user-agent
    string it sent to the server.
    """

    def __init__(self, uastring):

        # DEBUG (because of an importing problem)
        from ua_parser import user_agent_parser

        parsed_string = user_agent_parser.Parse(uastring)

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

    pp = pprint.PrettyPrinter(indent=4)
    parsed_string = ClientFingerprint(ua_string)
    pp.pprint(parsed_string)


def user_agent_strings_are_compatible_strictly(ua_string_1, ua_string_2):
    """
    Compares two user-agent stricts for strict string equality.

    Returns True if strict string equality holds; otherwise returns False.
    """

    is_compatible = (ua_string_1 == ua_string_2)
    return is_compatible


def user_agent_strings_are_compatible(ua_string_1, ua_string_2, *, strict = False):
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


    default_attribute_value = "not available"
    attributes_that_must_be_equal = ["device_brand",
                                     "device_family",
                                     "device_model",
                                     "os_family",
                                     "user_agent_family"
                                    ]


    def numeric_version_number_if_possible(fingerprint, attribute):
        """
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


    def analyze_parsed_user_agent_strings(ua_string_1, ua_string_2):
        """
        If called, we know that (a) strict==False and (b) the two strings are
        not exactly equal. Parses the pair of user-agent strings to determine
        whether the difference can be attributed to an upgrade.

        Returns is_compatible as either True or False
        """


        # Parses each user-agent string into an object whose attributes are the relevant components to test
        fingerprint_1 = ClientFingerprint(ua_string_1)
        fingerprint_2 = ClientFingerprint(ua_string_2)

        # We test the version numbers. Only if at least one version attribute is an upgrade might we go on to test the
        # non-version attributes
        further_analysis_is_justified = False

        def attribute_is_upgrade_or_compatible(attribute):
            """
            Tests a particular version attribute of the current pair of fingerprints to return:
                is_upgrade: True iff that attribute is numerically upgraded from the first to second fingerprint.
                is_compatible: True iff no red flags occurred w.r.t. attribute, such as a numerical downgrade or
                               this attribute was nonnumeric and nonequal.
            """
            is_upgrade = False

            (attribute_1_is_numeric, attribute_1_value) = numeric_version_number_if_possible(fingerprint_1, attribute)
            (attribute_2_is_numeric, attribute_2_value) = numeric_version_number_if_possible(fingerprint_2, attribute)

            if (attribute_1_is_numeric and attribute_2_is_numeric):
                if (attribute_2_value > attribute_1_value):
                    is_upgrade = True
                    is_compatible = True
                elif (attribute_2_value == attribute_1_value):
                    is_compatible = True
                else:
                    # Is a downgrade
                    is_compatible = False
            elif ((not attribute_1_is_numeric) and (not attribute_2_is_numeric)):
                # The attribute of each string is not numeric. Check for equality.
                is_compatible = (attribute_1_value == attribute_2_value)
            else:
                # One is numeric, but the other is not => FAIL
                is_compatible = False
            
            return (is_upgrade, is_compatible)
        

        def is_compatible_after_comparing_attributes_that_must_be_equal():
            """
            Inner function utility.

            Compares all the attributes that must be equal if the user-agent
            strings are compatible.
            """


            is_compatible = True
            for attribute in attributes_that_must_be_equal:
                value_1 = getattr(fingerprint_1, attribute, default_attribute_value)
                value_2 = getattr(fingerprint_2, attribute, default_attribute_value)

                if value_1 != value_2:
                    is_compatible = False
                    break

            return is_compatible

        # Beginning of actual comparison computation
        for (major, minor) in [("os_major", "os_minor"), ("user_agent_major", "user_agent_minor")]:
            (is_upgrade, is_compatible) = attribute_is_upgrade_or_compatible(major)

            if not is_compatible:
                return is_compatible

            if is_upgrade:
                further_analysis_is_justified = True
                break
            
            # Major is not incompatible but not an upgrade. Check minor.
            (is_upgrade, is_compatible) = attribute_is_upgrade_or_compatible(minor)

            if not is_compatible:
                return is_compatible

            if is_upgrade:
                further_analysis_is_justified = True
                
        if not further_analysis_is_justified:
            is_compatible = False
            return is_compatible

      
        # If here, (a) at least one version attribute is an upgrade and (b) neither version attribute is a downgrade.
        # Thus we check the non-version attributes for equality across the pair of user-agent strings.

        is_compatible = is_compatible_after_comparing_attributes_that_must_be_equal()

        return is_compatible

        # End of inner functions
    # Beginning of actual comparison computation

    is_compatible_strictly = user_agent_strings_are_compatible_strictly(ua_string_1, ua_string_2)

    # If strict, is_compatible_strictly is the only relevant criterion.
    # Even if not strict, if is_compatible_strictly is True, then the weaker not-strict criterion is also satisfied.
    if strict or is_compatible_strictly:
        is_compatible = is_compatible_strictly
        return is_compatible

    # If here, (a) strict==False and (b) the two UA strings are not exactly equal. This would be an immediate FAIL unless
    # the difference can be attributed to either the browser and/or OS being upgraded. To determine this we must parse
    # the strings to determine whether the version numbers imply an update in the OS and/or browser. If so, test
    # the non-version parsed fields for equality across the two user-agent strings.

    is_compatible = analyze_parsed_user_agent_strings(ua_string_1, ua_string_2)

    return is_compatible
