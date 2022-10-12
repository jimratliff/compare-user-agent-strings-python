from . ua_fingerprint import user_agent_strings_are_compatible

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
    for ua_string in ua_strings:
        for strict in (False, True):
            print(20*" – ")
            print(ua_string[1])
            print(f"Strict = {strict}")
            are_compatible = user_agent_strings_are_compatible(ua_0[0], ua_string[0], strict=strict)
            print(f"Compatible?: {are_compatible}")
            print(20*" 🎃 ")
        print(20*" 👹 ")
                




if __name__ == "__main__":
    main()
    exit(0)