import copy
import hashlib

from lesspass__renderPwd import render_password

DEFAULT_PROFILE = {
    "site": "",
    "login": "",
    "options": {
        "counter": 1,
        "length": 16,
        "digits": True,
        "symbols": True,
        "uppercase": True,
        "lowercase": True
    },
    "crypto": {
        "keylen": 32,
        "digest": "sha256",
        "method": "pbkdf2",
        "iterations": 100000
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


def createFingerprint(string):
    import hmac
    hr = hmac.new(string.encode('utf-8'), digestmod="sha256")
    return hr.digest().hex()

def isSupported():
    try:
        simple_profile = copy.deepcopy(DEFAULT_PROFILE)
        simple_profile.update({'crypto': {'iterations': 1 }})
        x = generate_password(simple_profile, "LessPass")
        assert x == "n'LTsjPA#3E$e*2'"
    except Exception as e:
        pass



def test_calc_entropy():
    master_password = "password"
    test_profile = copy.deepcopy(DEFAULT_PROFILE)
    # testing line 5
    test_profile.update({
        "site": "example.org",
        "login": "contact@example.org"
    })
    test_val = _calc_entropy(test_profile, master_password)
    assert test_val == "dc33d431bce2b01182c613382483ccdb0e2f66482cbba5e9d07dab34acc7eb1e"
    # preparing for test @ line 50
    p1 = copy.deepcopy(test_profile)
    p2 = copy.deepcopy(test_profile)
    # done preparing for test @ line 50
    # testing line 29
    test_profile["crypto"].update({
        "iterations": 8192,
        "digest": "sha512",
        "keylen": 16
    })
    test_val = _calc_entropy(test_profile, master_password)
    assert test_val == "fff211c16a4e776b3574c6a5c91fd252"
    # testing line 50
    p1["options"].update({
        "counter": 1
    })
    t1 = _calc_entropy(p1, master_password)
    p2["options"].update({
        "counter": 2
    })
    t2 = _calc_entropy(p2, master_password)
    assert t1 != t2
    return

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

def test_createFingerprint():
    assert createFingerprint("password") == "e56a207acd1e6714735487c199c6f095844b7cc8e5971d86c003a7b6f36ef51e"

if __name__ == '__main__':
    from tester import run_tests
    run_tests()
