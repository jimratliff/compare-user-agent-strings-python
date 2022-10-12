# Testing two user-agent strings for “compatibility” in order to detect a stolen authentication cookie
## Provides a screen to aid the detection of a stolen authentication cookie so you can revoke the session ID before any damage is done
This project provides an additional layer in a defense-in-depth strategy to ensure security of web sessions—specifically, to add a particular, perhaps additional, test to detect a hijacked session cookie so that it can be revoked before any damage is done.

This test—call the function `user_agent_strings_are_compatible()`—compares (a) the “[user-agent string](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent)” sent to the server from the user’s browser that accompanies the most-recent request to (b) the user-agent string sent at the time the user originally authenticated.

Two example user-agent strings are:
* `'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:104.1) Gecko/20100101 Firefox/105.1'`
* `'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)'`

If the two user-agent strings are not compatible (in a well-defined sense), it raises a concern that the most-recent request was made by a different browser/computer than was used when the legitimate user first authenticated—and hence the most-recent session cookie was stolen from the legitimate user for use on a different machine. In this case, it would be prudent to revoke the associated session ID, preventing the bad actor from using that stolen cookie to gain access to functionalities of the web application that require authentication.

This test, while having positive value, is not perfectly reliable in that it can suffer from both false negatives and false positives:
* The test may fail to detect a stolen cookie (false negative) because in some cases a bad actor can successfully spoof a victim’s user-agent string.
    * This would require that the bad actor either (a) learns what the user’s user-agent string is or (b) guesses it. Note that, if the bad actor is guessing, theirº guess must be right the first time, otherwise you would revoke the session ID immediately—before theyº’re able to make a second guess.
* The test may falsely infer a stolen cookie (false positive) when the user-agent string changed for a benign reason.
    * This can’t happen, AFAIK, with a transient cookie, i.e., which is automatically deleted when the session ends when the browser closes.
    * The user-agent string *could* change for a benign reason in a “permanent session,” i.e., “keep me logged in.” For example, if the user upgrades theirº browser or operating system after theyº initially authenticated. This project attempts to account for this scenario in its non-strict mode (`strict=False`, which is the default). See below.

Despite the possibility of a false positive or a false negative, this test usefully erects one additional hurdle a bad actor must surmount to successfully pull off the session hijack. Employing this additional test can have a significant upside. Cases of downside are relatively rare and in the worst case simply require the legitimate user to re-authenticate when theyº otherwise would have remained passively logged in.
* Only a false positive imposes a cost on a legitimate user, requiring themº to re-authenticate needlessly.
    * This can occur only during a permanent session (“remember me” or “keep me logged in”), not during a transient session.
    * This possibility would arise in a permanent session whenever something changes the legitimate user’s user-agent string. In particular this could happen if the user changes the version of theirº browser or theirº operating system.
        * In strict mode (`strict=True`), any such change in the user-agent string would result in a false positive.
        * Non-strict mode (`strict=False`) is designed to avoid one source of false positive: the case of the legitimate user *upgrading* their browser and/or operating system during the permanent session. If the user-agent string reports *in a numerical form* the version number of the browser and/or operating system, this project examines the new user-agent string to see whether the only difference between it and the original user-agent string is the version number *and* that the change is an *upgrade* not a downgrade. (Upgrades are common; downgrades are not. Therefore there is a substantial convenience benefit to permit the user to upgrade the browser or operating system without re-authentication. If a downgrade is detected, the likelihood tilts in the direction of it arising from a stolen cookie rather than action by the legitiate user.) In this case, the project declares the two user-agent strings as compatible.
* A false negative imposes no additional cost on a user compared to not conducting the test at all.

The justification of conducting the test lies in the existence of cases where the false finding is valid.

## WARNING: Secure web sessions require much more than this project!

This project offers but a single component of a secure-session strategy. And this component is nowhere near the most important component.

The scope of this project <em>begins</em> in a scenario that <em>you should take every effort to prevent</em>: a session cookie has been stolen by a bad actor to use to impersonate the legitimate user. Do everything you can to prevent this, including by using HTTPS for the entire web session (not only for authentication) and using the [`Secure`](https://owasp.org/www-community/controls/SecureCookieAttribute) and [`HttpOnly` cookie attributes](https://owasp.org/www-community/HttpOnly). To get a start, see the OWASP <a href="https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html">Session Management Cheat Sheet</a>. Even after the above precautions have been taken, however, it is still possible for a nefarious actor to acquire a user’s session cookie. This project adds one additional tool , in such a scenario, might detect a stolen session cookie, allowing its session ID to be revoked, denying further access to the bad actor.

## Dependency
This project relies on the [Python implementation](https://github.com/ua-parser/uap-python) of [ua-parser](https://github.com/ua-parser/uap-core), which parses a user-agent string into numerous attributes about the device (e.g., `{'brand': 'Apple', 'family': 'Mac', 'model': 'Mac'}`), the operating system (e.g., `{'family': 'Mac OS X', 'major': '10', 'minor': '9', 'patch': '4', 'patch_minor': None}`), and the user agent itself (e.g.,`{'family': 'Chrome', 'major': '41', 'minor': '0', 'patch': '2272'}`). To install:
```py
pip install ua-parser
```
The parsing by ua-parser provides a kind of “reduced form” of a user-agent string, ignoring some differences between user-agent strings. For example, the following two distinct user-agent strings have identical parsed forms according to ua-parser:
```
'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)'
'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)'
```
That common parsed form is:
```
{   'device': {'brand': None, 'family': 'Other', 'model': None},
    'os': {   'family': 'Windows',
              'major': 'XP',
              'minor': None,
              'patch': None,
              'patch_minor': None},
    'string': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET '
              'CLR 1.1.4322)',
    'user_agent': {'family': 'IE', 'major': '6', 'minor': '0', 'patch': None}}
```

## Installation and usage
### Installation
To install
```py
pip install compare-user-agent-strings
```
### Usage
This project exposes three functions:
```py
from compare_user_agent_strings import (print_parsed_user_agent_string,
                                        user_agent_strings_are_compatible,
                                        user_agent_strings_are_compatible)

print_parsed_user_agent_string(ua_string)

is_compatible = user_agent_strings_are_compatible_strictly(ua_string_1, ua_string_2)

is_compatible = user_agent_strings_are_compatible(ua_string_1, ua_string_2, strict=False)
```
where:
* `ua_string_1` is a user-agent string for some earlier request that serves as a benchmark
* `ua_string_2` is the user-agent string for the most-recent request
* `strict` is a keyword-only parameter, i.e., if supplied at all it must be supplied as either `strict=False` or `strict=True`, not as simply a bare `False` or `True`.

The focus here is on `user_agent_strings_are_compatible()`.

### Sample script:
```py
# run.py
from compare_user_agent_strings import user_agent_strings_are_compatible

def main():
    ua_0 = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:104.1) Gecko/20100101 Firefox/105.1'

    # Constant OS major; decrease OS minor ❌ NOT a match with ua_0
    ua_1 = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:104.1) Gecko/20100101 Firefox/105.1'

    # Increase OS major; decrease OS minor
    # ✅ IS a match with ua_0   (strict=False)
    # ❌ NOT a match with ua_0  (strict=True)
    ua_2 = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11.15; rv:104.1) Gecko/20100101 Firefox/105.1'

    are_compatible_1 = user_agent_strings_are_compatible(ua_0, ua_1, strict=False)
    are_compatible_2 = user_agent_strings_are_compatible(ua_0, ua_2, strict=False)
    are_compatible_3 = user_agent_strings_are_compatible(ua_0, ua_2, strict=True)

    print(f"Should be False: {are_compatible_1=}")
    print(f"Should be True:  {are_compatible_2=}")
    print(f"Should be False: {are_compatible_3=}")

if __name__ == "__main__":
    main()
    exit(0)
```
Output:
```py
$ python run.py
Should be False: are_compatible_1=False
Should be True:  are_compatible_2=True
Should be False: are_compatible_3=False
```

## What it means for two user-agent strings to be “compatible” and how that depends on `strict` mode
The question addressed by (a) `user_agent_strings_are_compatible_strictly()` and (b) `user_agent_strings_are_compatible()` is whether the second user-agent string appears to come from the same user/machine as did the first user-agent string. The two functions can differ in the strictness of the criterion for compatibility.

The function `user_agent_strings_are_compatible_strictly()` adopts a strict standard.

The function `user_agent_strings_are_compatible(ua_string_1, ua_string_2, *, strict = False)` adopts either (a) the strict standard, if `strict==True`, or (b) a weaker standard that strives to reduce false positives, if `strict==False` (the default value).

`strict==True` requires exact string equality between the two user-agent strings. This is also sufficient, but not necessary, to satisfy the `strict==False` standard.

When `strict==False`, we allow for an exemption from string equality when the only “substantive difference” between the two strings is that one or both of the operating system and/or browser has been upgraded between the time the first string was provided and the time the second string was provided. (Note: an upgrade is detected only when the version is described *numerically*, not by a string, e.g., “XP”.)

By “substantive difference,” we mean: first parse each user string into attributes, using `ua-parse`, and compare the two strings with respect to each parsed attribute (other than version-number attributes). If the two strings are the same in that sense and the second string is an upgrade of the OS or browser relative to the first (without the other entity, OS/browser, being a downgrade), consider the two strings compatible (under `strict==False`).

(To be clear, if neither OS nor browser evinces an upgrade without either being a downgrade, the standard of compatibility is the strict one: exact string equality. I.e., comparing components of parsed strings only has effect when it turns out that the browser and/or OS was upgraded and neither downgraded.)

## When to use `strict=True` or instead `strict=False`

Setting `strict=True` is appropriate for a transient cookie (i.e., a “session cookie”), which is deleted automatically when the browser closes (if not before when the user logs out), because there is no risk of a false positive resulting from an upgrade of the operating system or browser. (Neither the operating system nor the browser can be updated without deleting the transient cookie, because performing the upgrades would cause the browser to close and delete the transient cookie.)

Setting `strict=False` can be appropriate in the case of a permanent cookie (e.g., “remember me” or “keep me logged in”), because such a cookie survives browser restarts and system reboots and thus upgrades could occur without causing the cookie to be deleted.

The decision to use `strict=False` with a permanent cookie involves a tradeoff between user convenience and security. The user can upgrade theirº browser and/or operating system without being forced to reauthenticate on theirº next visit.

On the countervailing side, as is true quite generally, reducing false positives comes at the cost of increase the likelihood of false negatives. There is a larger set of fraudently user-agent strings that would evade detection. This greater risk of a false positive occurs for two reasons:
* The test accepts additional (higher) version numbers for the operating system and browser.
* When either the operating system or browser appears to have been upgraded, the equality criterion for the non-versions parts of the user-agent string is weaker: Rather than requiring strict string equality, the test requires only equality of the reduced-form representations of the user-agent strings resulting from the parsing.


## Linguistic note
I attach a degree symbol (“º”) to the end of pronouns when that pronoun (a) has traditionally been understood as a plural pronoun but (b) which I use in the current instance as a singular pronoun. I do this as an uncomforable adaptation to the lack of any other widely accepted gender-neutral pronouns (though I’d be thrilled if [ze/zir](https://pronouns.org/ze-hir) were widely adopted), while preventing confusion caused by the usurpation of a plural pronoun in a singular context.

## Version history
* 1.0.2:  October 12, 2022.
    * Initial release.

## License
This project is licensed under the MIT License. See the LICENSE.md file for details.