"""
Lesspass's render password module implemented in python
this file tries to mimic index.js, all necessary functions are defined in this
file itself
"""

import string
from collections import namedtuple

TransPassword = namedtuple("TransPassword", ["value", "entropy"])

##############################################################################
# file: chars.js
##############################################################################

CHAR_SET = {
    "digits":    string.digits,
    "symbols":   string.punctuation,
    "uppercase": string.ascii_uppercase,
    "lowercase": string.ascii_lowercase
}

def _get_active_rules(password_profile):
    # earlier it was just--
    # rules = list(filter(lambda k: options[k] is True, options))
    # but I was getting strange bugs, first because
    # Py's dict key odering problem and the fact illustrated below
    ORIGINAL_LESSPASS_S_RULE_FILTERATION_ORDER = \
        ['lowercase', 'uppercase', 'digits', 'symbols']
        # had to give this eye-catchy name because this ARBITARY order decided
        # by lesspass authors decides order in which chars appear in
        # `valid_chars` of render_password
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

def test_getOneCharPerRule():
    # test on-- https://bit.ly/2uxYPAg
    test_val = _getOneCharPerRule(26*26, ["lowercase", "uppercase"])
    assert test_val.value[:2] == "aA"
    assert len(test_val.value) == 2
    assert test_val.entropy == 1
    return

def test_insertStringPseudoRandomly():
    # test on-- https://bit.ly/2GJIBcg
    test_val = _insertStringPseudoRandomly("123456", 7*6 + 2, "uT")
    assert test_val == "T12u3456"
    return

##############################################################################
# file: entropy.js
##############################################################################

def consume_entropy(generatedPassword, quotient, valid_chars, max_len):
    if len(generatedPassword) >= max_len:
        return TransPassword(generatedPassword, quotient)
    quotient, remainder = divmod(quotient, len(valid_chars))
    generatedPassword += valid_chars[remainder]
    return consume_entropy(
        generatedPassword, quotient, valid_chars, max_len
    )

def test_consume_entropy():
    # test on-- https://bit.ly/2GruTrj
    test_val = consume_entropy("", 4*4 + 2, "abcd", 2)
    assert test_val.value == "ca"
    assert test_val.entropy == 1
    return

##############################################################################
# file: index.js
##############################################################################

def render_password(entropy, options):
    # see-- return of `https://bit.ly/2pZCCq3` is hexadecimal str only
    rules = _get_active_rules(options)
    char_set = _get_char_set(rules)
    password = consume_entropy(
        generatedPassword = "",
        valid_chars = char_set,
        quotient = int(entropy, 16), # BUG: possibly, cuz quot... is now decimal not 0xDEADBEEF kinda stuff
        max_len = options["length"] - len(rules)
    )
    chars_to_add = _getOneCharPerRule(password.entropy, rules)
    ans = _insertStringPseudoRandomly(
        generatedPassword = password.value,
        entropy = chars_to_add.entropy,
        string = chars_to_add.value
    )
    return ans

def test_render_password():
    # fails test-- https://bit.ly/2H11eGv
    test_options = {
        "length": 16,
        "lowercase": True,
        "uppercase": True,
        "digits": True,
        "symbols": True
    }
    test_entropy = "dc33d431bce2b01182c613382483ccdb0e2f66482cbba5e9d07dab34acc7eb1e"
    check_value = render_password(test_entropy, test_options)
    assert check_value[0] == "W"
    assert check_value[1] == "H"
    assert len(check_value) == 16
    test_options.update({"length": 20})
    check_value = render_password(test_entropy, test_options)
    assert len(check_value) == 20
    test_options.update({"length": 6})
    check_value = render_password(test_entropy, test_options)
    assert any([x.islower() for x in check_value])
    assert any([x.isupper() for x in check_value])
    assert any([x.isdigit() for x in check_value])
    assert all(x for x in check_value if x in string.punctuation)
    return 

if __name__ == '__main__':
    from tester import run_tests
    run_tests()
