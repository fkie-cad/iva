weights = {'vendor': 2,
           'product': 2,
           'version': 1.5,
           'update': 1,
           'edition': 1,
           'language': 0.5,
           'sw_edition': 0.5,
           'target_sw': 0.5,
           'target_hw': 0.5,
           'other': 0.5}


def compare_wfn(wfn_a, wfn_b):
    coincidence = 0
    not_matches = []
    for key in weights.keys():
        if values_equal(wfn_a.get(key), wfn_b.get(key), key):
            coincidence += weights.get(key) * 10
        else:
            not_matches.append(key)
    return {'coincidence_rate': coincidence, 'not_matches': not_matches}


def versions_equal(version_a, version_b):
    version_elements_a, version_elements_b = get_version_elements(version_a, version_b)
    if ('*' not in version_elements_a) and ('*' not in version_elements_b):
        return values_equal(version_a, version_b, '')
    return version_elements_equal(version_elements_a, version_elements_b)


def values_equal(val_a, val_b, key):
    if key == 'version':
        return versions_equal(val_a, val_b)
    return (val_a == val_b) or (are_values_any(val_a, val_b))


def get_version_elements(version_a, version_b):
    return version_a.split('.'), version_b.split('.')


def version_elements_equal(version_elements_a, version_elements_b):
    version_elements_a, version_elements_b = swap(version_elements_a, version_elements_b)
    asterisk_index = version_elements_a.index('*')
    if asterisk_index > len(version_elements_b):
        return False
    for i in range(asterisk_index):
        if version_elements_a[i] != version_elements_b[i]:
            return False
    if asterisk_index < len(version_elements_a)-1:
        if len(version_elements_b) != len(version_elements_a):
            return False
        for j in range(asterisk_index+1, len(version_elements_a)):
            if version_elements_a[j] != version_elements_b[j]:
                return False
    return True


def swap(version_elements_a, version_elements_b):
    if '*' in version_elements_a and '*' in version_elements_b:
        index_a = version_elements_a.index('*')
        index_b = version_elements_b.index('*')
        if index_a <= index_b:
            return version_elements_a, version_elements_b
        return version_elements_b, version_elements_a
    elif '*' in version_elements_a:
        return version_elements_a, version_elements_b
    return version_elements_b, version_elements_a


def are_values_any(val_a, val_b):
    return (is_value_any(val_a) and not is_value_na(val_b)) or (is_value_any(val_b) and not is_value_na(val_a))


def is_value_any(val):
    return val == 'ANY' or val == '*'


def is_value_na(val):
    return val == 'NA' or val == '-'
