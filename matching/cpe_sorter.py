from matching.cpe_set_operations import calculate_symmetric_difference_between_two_cpe_lists
from wfn.wfn_converter import WFNConverter


def sort_cpes_by_version(cpes, software_version):
    version_prefixes = create_version_prefixes(software_version)
    if len(version_prefixes) > 0:
        return sort_cpes_by_version_prefixes(cpes, version_prefixes)
    if is_year(software_version):
        return sort_cpes_by_year_version(cpes, software_version)
    return cpes


def sort_cpes_by_version_prefixes(cpes, version_prefixes):
    # Example:
    # version = 4.7.2-3
    # version_prefixes = [4, 4.7, 4.7.2-3]
    sorted_cpes = []
    for prefix in version_prefixes:
        for cpe in cpes:
            cpe_version = get_cpe_version(cpe)
            if has_prefix(prefix, cpe_version) and not_in_sorted_list(cpe, sorted_cpes):
                sorted_cpes.append(cpe)
    unsorted_cpes = calculate_symmetric_difference_between_two_cpe_lists(sorted_cpes, cpes)
    sorted_cpes.extend(unsorted_cpes)
    return sorted_cpes


def sort_cpes_by_year_version(cpes, software_version):
    sorted_cpes = []
    cpes_year_not_equal = []
    for cpe in cpes:
        cpe_version = get_cpe_version(cpe)
        if cpe_version == software_version:
            sorted_cpes.append(cpe)
        elif str(cpe_version).isdigit():
            cpes_year_not_equal.append(cpe)
    sorted_cpes.extend(cpes_year_not_equal)
    unsorted_cpes = calculate_symmetric_difference_between_two_cpe_lists(sorted_cpes, cpes)
    sorted_cpes.extend(unsorted_cpes)
    return sorted_cpes


def sort_cpes_by_operating_system(cpes, os):
    sorted_cpes = []
    for cpe in cpes:
        cpe_target_software = get_cpe_target_sw(cpe)
        if is_same_os(cpe_target_software, os) and not_in_sorted_list(cpe, sorted_cpes):
            if len(cpe_target_software) == len(os):
                sorted_cpes.insert(0, cpe)
            else:
                sorted_cpes.append(cpe)
    unsorted_cpes = calculate_symmetric_difference_between_two_cpe_lists(sorted_cpes, cpes)
    sorted_cpes.extend(unsorted_cpes)
    return sorted_cpes


def create_version_prefixes(software_version):
    version_elements = str(software_version).split('.')
    if len(version_elements) > 1:
        prefixes = [version_elements[0]]
        for i in range(1, len(version_elements)):
            prefixes.append(prefixes[i - 1] + '.' + str(version_elements[i]))
        prefixes = list(reversed(prefixes))
        return prefixes
    return []


def has_prefix(version_prefix, uri_binding_version):
    return version_prefix in uri_binding_version and version_prefix[0] == uri_binding_version[0]


def is_same_os(uri_binding_os, os):
    return (uri_binding_os in os) or (os in uri_binding_os)


def not_in_sorted_list(uri_binding, sorted_uri_bindings):
    return not sorted_uri_bindings.__contains__(uri_binding)


def is_year(software_version):
    return len(software_version) == 4 and str(software_version).isdigit()


def get_cpe_version(cpe):
    return cpe.get('wfn').get('version')


def get_cpe_target_sw(cpe):
    return cpe.get('wfn').get('target_sw')