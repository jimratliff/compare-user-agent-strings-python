# Testing two user-agent strings for “compatibility”
## Provides a supplemental test to detect a stolen authentication cookie so you can revoke the session ID before any damage is done
This project provides an additional layer in a defense-in-depth strategy to ensure security of web sessions—specifically, to add a particular, perhaps additional, test to detect a hijacked session cookie so that it can be revoked before any damage is done.

This test—call the function `user_agent_strings_are_compatible()`—compares (a) the “[user-agent string](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent)” sent to the server from the user’s browser along with the most-recent request to (b) the user-agent string at the time the user originally authenticated.

Two example user-agent strings are:
* `'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:104.1) Gecko/20100101 Firefox/105.1'`
* `'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)'`

If the two user-agent strings are not compatible (in a well-defined sense), it raises a concern that the most-recent request was made with a stolen session cookie. In this case, it would be prudent to revoke the associated session ID, preventing the bad actor from using that stolen cookie to gain access to areas of the web application that require authentication.

This test is not full proof in that it can suffer from both false negatives and false positives:
* The test may fail to detect a stolen cookie (false negative) because in some cases a bad actor can successfully spoof a victim’s user-agent string.
    * This would require that the bad actor either (a) learns what the user’s user-agent string is or (b) guesses it. Note that, if the bad actor is guessing, theirº guess must be right the first time, otherwise you would revoke the session ID immediately—before theyº’re able to make a second guess.
* The test may falsely infer a stolen cookie (false positive) when the user-agent string changed for a benign reason.
    * This can’t happen, AFAIK, in a transient session, i.e., where the session ends when the browser closes.
    * The user-agent string *could* change for a benign reason in a “permanent session,” i.e., “keep me logged in.” For example, if the user upgrades theirº browser or operating system after theyº initially authenticated. This project attempts to account for this scenario in its non-strict mode (`strict=False`, which is the default). See below.

Despite the possibility of a false positive or a false negative, this test usefully erects one additional hurdle a bad actor must surmount to successfully pull off the session hijack. Employing this additional test can have a significant upside. Cases of downside are relatively rare and in the worst case simply require the legitimate user to re-authenticate when theyº otherwise would have remained passively logged in.
* Only a false positive needlessly imposes a cost on a legitimate user, requiring themº to re-authenticate needlessly.
    * This can occur only during a permanent session (“remember me” or “keep me logged in”), not during a transient session.
    * This possibility would arise in a permanent session whenever something changes the legitimate user’s user-agent string. In particular this could happen if the user changes the version of theirº browser or theirº operating system.
        * In strict mode (`strict=True`), any such change in the user-agent string would result in a false positive.
        * Non-strict mode (`strict=False`) is designed to avoid one source of false positive: the case of the legitimate user *upgrading* their browser and/or operating system during the permanent session. If the user-agent string reports *in a numerical form* the version number of the browser and/or operating system, this project examines the new user-agent string to see whether the only difference between it and the original user-agent string is the version number *and* that the change is an *upgrade* not a downgrade. (Upgrades are common; downgrades are not. Therefore there is a substantial convenience benefit to permit the user to upgrade the browser or operating system without re-authentication. If a downgrade is detected, the likelihood tilts in the direction of it arising from a stolen cookie rather than action by the legitiate user.) In this case, the project declares the two user-agent strings as compatible.
    
    
    Because this can occur only when the user downgrades theirº operating system or browser during the pendency of a permanent session (i.e., “remember me” or “keep me logged in”), this is an unlikely scenario.
* A false negative imposes no additional cost on a user compared to not conducting the test at all. The justification of conducting the test lies in the existence of cases where the false finding is valid.

## WARNING: Secure web sessions require much more than this project!

This project offers but a single component of a secure-session strategy. And this component is nowhere near the most important component.

The scope of this project <em>begins</em> in a scenario that <em>you should take every effort to prevent</em>: a session cookie has been stolen by a bad actor to use to impersonate the legitimate user. Do everything you can to prevent this, including by using HTTPS for the entire web session (not only for authentication) and using the [`Secure`](https://owasp.org/www-community/controls/SecureCookieAttribute) and [`HttpOnly` cookie attributes](https://owasp.org/www-community/HttpOnly). To get a start, see the OWASP <a href="https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html">Session Management Cheat Sheet</a>.

Even after the above precautions have been taken, however, it is still possible for a nefarious actor to acquire a user’s session cookie. This project adds one additional tool , in such a scenario, might detect a stolen session cookie, allowing its session ID to be revoked, denying further access to the bad actor.

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

## Usage
This project exposes a function:
```py
from compare_user_agent_strings import user_agent_strings_are_compatible

(is_compatible, message) = user_agent_strings_are_compatible(ua_string_1, ua_string_2, strict=False)
```
where:
* `ua_string_1` is a user-agent string for some earlier request that serves as a benchmark
* `ua_string_2` is the user-agent string for the most-recent request
* `strict` is a keyword-only parameter, i.e., if supplied at all it must be supplied as either `strict=False` or `strict=True`, not as simply a bare `False` or `True`.

The function returns a tuple (Boolean, string):
* `is_compatible`: `True` if the two user-agent strings are sufficiently similar (in light of the choice of `strict`) to be compatible with concluding that the second user-agent string came from the same computer and user as did the first user-agent string; otherwise `False`.
* a discrepancy message, when `is_compatible = False`, that verbally describes the first fatal difference between the two user-agent strings that led to the conclusion that they didn’t sufficiently likely come from the same computer/user. (If `is_compatible` is `True`, this string is empty.)

## What it means for two user-agent strings to be “compatible” and how that depends on `strict` mode
This project tests a pair of user-agent strings to see whether they are compatible in the following sense:

>Is the second user-agent string (assumed to be the one associated with the most-recent request to the server) sufficiently similar to the first user-agent string (assumed to be the one supplied to the server at the time of original authentication) that it’s safe to conclude that the second user-agent string came from the same computer/user that originally authenticated?

The comparison of the two user-agent strings is conducted either with `strict=False`, which is the default, or with `strict=True`.

As suggested by the terminology, `strict=True` is a stronger test of compatibility, and requires that each component of the second user-agent string match exactly the corresponding component of the first user-agent string.

When `strict=False`, the test allows user-agent strings to be compatible even when the browser and/or operating-system version numbers are different, as long as the version number for each in the second string is the same or greater than the version number in the first string. In other words, an *upgrade* of either/both the operating system and/or browser does not disqualify the second user-agent string from being judged to be compatible with the first user-agent string.