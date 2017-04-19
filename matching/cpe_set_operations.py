

def calculate_symmetric_difference_between_two_cpe_lists(cpe_list_a, cpe_list_b):
    asymmetric_difference_a_b = calculate_asymmetric_difference(cpe_list_a, cpe_list_b)
    asymmetric_difference_b_a = calculate_asymmetric_difference(cpe_list_b, cpe_list_a)
    asymmetric_difference_a_b.extend(asymmetric_difference_b_a)
    return asymmetric_difference_a_b


def calculate_asymmetric_difference(cpe_list_a, cpe_list_b):
    difference_set = []
    for a in cpe_list_a:
        if a not in cpe_list_b:
            difference_set.append(a)
    return difference_set


def calculate_intersection_between_two_cpe_lists(cpe_list_a, cpe_list_b):
    if len(cpe_list_a) > len(cpe_list_b):
        return calculate_intersection(cpe_list_a, cpe_list_b)
    return calculate_intersection(cpe_list_b, cpe_list_a)


def calculate_intersection(cpe_list_a, cpe_list_b):
    intersection_set = []
    for a in cpe_list_a:
        if a in cpe_list_b:
            intersection_set.append(a)
    return intersection_set
