import sys
import getpass

# RENDER PASSWORD ------------------------------------------------------------

import string
from collections import namedtuple

TransPassword = namedtuple("TransPassword", ["value", "entropy"])

CHAR_SET = {
    "digits":    string.digits,
    "symbols":   string.punctuation,
    "uppercase": string.ascii_uppercase,
    "lowercase": string.ascii_lowercase
}

def _get_active_rules(password_profile):
    ORIGINAL_LESSPASS_S_RULE_FILTERATION_ORDER = \
        ['lowercase', 'uppercase', 'digits', 'symbols']
    answer = list()
    for a_rule in ORIGINAL_LESSPASS_S_RULE_FILTERATION_ORDER:
        if password_profile[a_rule] is True:
            answer.append(a_rule)
    return answer

def _get_char_set(rules):
    ans = str()
    for a_rule in rules:
        ans += CHAR_SET[a_rule]
    return ans

def _getOneCharPerRule(entropy, rules):
    ocpr = str()
    for rule in rules:
        password = consume_entropy("", entropy, CHAR_SET[rule], 1)
        ocpr += password.value
        entropy = password.entropy
    return TransPassword(ocpr, entropy)

def _insertStringPseudoRandomly(generatedPassword, entropy, string):
    for char in string:
        quotient, remainder = divmod(entropy, len(generatedPassword))
        generatedPassword = generatedPassword[0:remainder] + \
                    char + generatedPassword[remainder:]
        entropy = quotient
    return generatedPassword

def consume_entropy(generatedPassword, quotient, valid_chars, max_len):
    if len(generatedPassword) >= max_len:
        return TransPassword(generatedPassword, quotient)
    quotient, remainder = divmod(quotient, len(valid_chars))
    generatedPassword += valid_chars[remainder]
    return consume_entropy(
        generatedPassword, quotient, valid_chars, max_len
    )

def render_password(entropy, options):
    rules = _get_active_rules(options)
    char_set = _get_char_set(rules)
    password = consume_entropy(
        generatedPassword = "",
        valid_chars = char_set,
        quotient = int(entropy, 16),
        max_len = options["length"] - len(rules)
    )
    chars_to_add = _getOneCharPerRule(password.entropy, rules)
    ans = _insertStringPseudoRandomly(
        generatedPassword = password.value,
        entropy = chars_to_add.entropy,
        string = chars_to_add.value
    )
    return ans

# core -----------------------------------------------------------------------

import copy
import hashlib

DEFAULT_PROFILE = {
    "site": "",
    "login": "",
    "options": {
        "uppercase": True,
        "lowercase": True,
        "digits": True,
        "symbols": True,
        "length": 16,
        "counter": 1
    },
    "crypto": {
        "method": "pbkdf2",
        "iterations": 100000,
        "keylen": 32,
        "digest": "sha256"
    }
}

def generate_password(user_prefrences, master_password):
    final_profile = copy.deepcopy(DEFAULT_PROFILE)
    final_profile.update(user_prefrences)
    entropy = _calc_entropy(final_profile, master_password)
    del master_password
    lesspass_password = render_password(entropy, final_profile['options'])
    return lesspass_password

def _calc_entropy(profile, master_password):
    salt = profile['site'] + profile['login'] + \
            str(  int(str(profile['options']['counter']), 16)  )
    entropy = hashlib.pbkdf2_hmac(
        password = master_password.encode('utf-8'),
        salt = salt.encode('utf-8'),
        dklen = profile['crypto']['keylen'],
        hash_name = profile['crypto']['digest'],
        iterations = profile['crypto']['iterations']
    )
    return entropy.hex()

def test_generate_password():
    master_password = "password"
    test_profile = copy.deepcopy(DEFAULT_PROFILE)
    test_profile.update({
        "site": "example.org",
        "login": "contact@example.org"
    })
    test_pwd = generate_password(test_profile, master_password)
    assert test_pwd == "WHLpUL)e00[iHR+w"
    test_profile["options"].update({
        "counter": 2,
        "symbols": False,
        "length": 14
    })
    test_pwd = generate_password(test_profile, master_password)
    assert test_pwd == "MBAsB7b1Prt8Sl"
    assert len(test_pwd) == 14
    return

# ----------------------------------------------------------------------------

def get_opts():
    ans = dict()
    curr = DEFAULT_PROFILE["options"]
    print("* Password contains uppercase chars")
    if input("press n to remove uppercase: ") in ['n', 'N']:
        ans['uppercase'] = False
    print("* Password contains lowercase")
    if input("press n to remove lowercase: ") in ['n', 'N']:
        ans['lowercase'] = False
    print("* Password contains digits")
    if input("press n to remove digits:    ") in ['n', 'N']:
        ans['digits'] = False
    print("* Password contains symbols")
    if input("press n to remove symbols:   ") in ['n', 'N']:
        ans['symbols'] = False
    i = input("* Password length (default 16): ")
    try:    int(i)
    except: pass
    else:   ans['length'] = i
    i = input("* Password iteration (default 1st): ")
    try:    int(i)
    except: pass
    else:   ans['counter'] = i
    return ans

def main():
    args = sys.argv[1:]
    try:
        site, login = args
    except IndexError:
        return
    print("Site:  ", site)
    print("Login: ", login)
    i = input(
"""
Press
  [q] to quit and start over
  [f] to fine tune settings
  or just [Enter] to proceed
"""
    )
    if i in ["q", "Q"]:
        return
    session_pref = copy.deepcopy(DEFAULT_PROFILE)
    session_pref.update({
        "site": site,
        "login": login
    })
    if i in ['f', 'F']:
        session_pref["options"].update(get_opts())
    master_password = getpass.getpass("Enter master password:\n")
    ans = generate_password(session_pref, master_password)
    del master_password
    print("Generate password:")
    print(ans)
    return

if __name__ == '__main__':
    test_generate_password()
    main()
