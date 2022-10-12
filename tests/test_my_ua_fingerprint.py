"""
Tests the package with pytest.
"""


from compare_user_agent_strings.ua_fingerprint import (
                                                        print_parsed_user_agent_string,
                                                        user_agent_strings_are_compatible,
                                                      )

# Compare similar user-agent strings that vary slightly; some of them are compatible (strict=False), and some of them
# are not.

def test_similar_user_agent_strings():
    """
    Compare similar user-agent strings that vary slightly; some of them are
    compatible (when strict=False), and some of them are not.
    """
    user_agent_strings = [
        # (strict=False, strict=True)
        # 00: Base case ✅ ✅
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:104.1) Gecko/20100101 Firefox/105.1' ,
        # 01: Constant OS major; decrease OS minor ❌ ❌
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:104.1) Gecko/20100101 Firefox/105.1' ,
        # 02: Constant OS major; increase OS minor ✅ ❌
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:104.1) Gecko/20100101 Firefox/105.1' ,
        # 03: Increase OS major; decrease OS minor ✅ ❌
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 11.14; rv:104.1) Gecko/20100101 Firefox/105.1' ,
        # 04: Decrease OS major; increase OS minor ❌ ❌
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 9.16; rv:104.1) Gecko/20100101 Firefox/105.1'  ,
        # 05: Increase UA-major; decrease UA-minor ✅ ❌
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:104.1) Gecko/20100101 Firefox/106.0' ,
        # 06: Decrease UA-major; increase UA-minor ❌ ❌
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:104.1) Gecko/20100101 Firefox/104.2' ,
        # 07: Constant UA-major; increase UA-minor ✅ ❌
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:104.1) Gecko/20100101 Firefox/105.2' ,
        # 08: Constant UA-major; decrease UA-minor  ❌ ❌
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:104.1) Gecko/20100101 Firefox/105.0' ,
        # 09: Change User-Agent Family to Chrome ❌ ❌
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
        # 10: Change OS to Windows ❌ ❌
        "Mozilla/5.0 (Windows NT 5.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1" ,
        # 11: Windows, Internet Explorer 6 ❌ ❌
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)" ,
        ]

    is_compatible_strict = [True, False, False, False, False, False, False, False, False, False, False, False]
    is_compatible_loose =  [True, False, True,  True,  False, True,  False, True,  False, False, False, False]

    index_base_case = 0
    ua_string_base = user_agent_strings[index_base_case]

    for strict in [True, False]:
        is_compatible_goal_list = is_compatible_strict if strict else is_compatible_loose
        zipped = zip(user_agent_strings, is_compatible_goal_list)
        is_compatible_actual_list = []
        for (user_agent_string, is_compatible_goal) in zipped:
            is_compatible = user_agent_strings_are_compatible(ua_string_base,
                                                              user_agent_string,
                                                              strict=strict)

            is_compatible_actual_list.append(is_compatible)

        assert is_compatible_actual_list == is_compatible_goal_list

def test_bunch_of_completely_different_user_agent_strings():
    """
    Run a large number of pairwise comparisons of distinct user-agent strings,
    with the main objective to confirm that the code doesn't choke.
    Test only that n vs. n is compatible, but n vs. m (for m≠n) is
    incompatible.
    """

    user_agent_strings = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:104.1) Gecko/20100101 Firefox/105.1' ,
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 5.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1" ,
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)" ,
        'Mozilla/5.0 (Symbian/3; Series60/5.2 NokiaN8-00/012.002; Profile/MIDP-2.1 Configuration/CLDC-1.1 ) AppleWebKit/533.4 (KHTML, like Gecko) NokiaBrowser/7.3.0 Mobile Safari/533.4 3gpp-gba',
        'Mozilla/5.0 (Linux; Android 7.1.1; Moto G (5S) Build/NPPS26.102-49-11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.91 Mobile Safari/537.36' ,
        'Roku/DVP-9.10 (519.10E04111A)' ,
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)' ,
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134' ,
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36' ,
        'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148' ,
        'WeatherReport/1.2.2 CFNetwork/485.13.9 Darwin/11.0.0' ,
        'Outlook-iOS/709.2226530.prod.iphone (3.24.1)' ,
        'Mozilla/5.0 (Linux; U; Android 2.3.4; en-us; Kindle Fire Build/GINGERBREAD) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1' ,
        'Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.18' ,
        'Mozilla/5.0 (Linux; Android 8.1.0; CPH1803 Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.116 Mobile Safari/537.36 OPR/44.6.2246.127414' ,
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15' ,
        'Mozilla/5.0 (X11; CrOS x86_64 14816.99.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36' ,
        ]

    is_compatible_goal_list = []
    is_compatible_actual_list = []
    for strict in [True, False]:
        for ua_0 in user_agent_strings:
            for ua_1 in user_agent_strings:
                is_compatible = user_agent_strings_are_compatible(ua_0, ua_1, strict=strict)
                is_compatible_actual_list.append(is_compatible)

                is_compatible_goal = True if (ua_0 == ua_1) else False
                is_compatible_goal_list.append(is_compatible_goal)
    
    assert is_compatible_actual_list == is_compatible_goal_list


def test_print_parsed_user_agent_string():
    ua_string = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:104.1) Gecko/20100101 Firefox/105.1'
    print_parsed_user_agent_string(ua_string)
    return

