import re

REGEX_START = '^'
REGEX_END = '.*'


def create_regex(search_text):
    return REGEX_START + re.escape(search_text) + REGEX_END


def add_matches_to_list(matches, list_):
        for m in matches:
            if m not in list_:
                list_.append(m)


# def calculate_symmetric_difference_between_two_cpe_lists(cpe_list_a, cpe_list_b):
#     if len(cpe_list_a) > len(cpe_list_b):
#         return calculate_symmetric_difference(cpe_list_a, cpe_list_b)
#     return calculate_symmetric_difference(cpe_list_b, cpe_list_a)
#
#
# def calculate_symmetric_difference(cpe_list_a, cpe_list_b):
#     difference_set = []
#     for a in cpe_list_a:
#         is_common_element = False
#         for b in cpe_list_b:
#             if dict(a).get('uri_binding') == dict(b).get('uri_binding'):
#                 is_common_element = True
#                 break
#         if not is_common_element:
#             difference_set.append(a)
#     return difference_set
#
#
# def calculate_intersection_between_two_cpe_lists(cpe_list_a, cpe_list_b):
#     if len(cpe_list_a) > len(cpe_list_b):
#         return calculate_intersection(cpe_list_a, cpe_list_b)
#     return calculate_intersection(cpe_list_b, cpe_list_a)
#
#
# def calculate_intersection(cpe_list_a, cpe_list_b):
#     intersection_set = []
#     for a in cpe_list_a:
#         for b in cpe_list_b:
#             if dict(a).get('uri_binding') == dict(b).get('uri_binding'):
#                 intersection_set.append(a)
#     return intersection_set
