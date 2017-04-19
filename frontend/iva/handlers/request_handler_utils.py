import ast


def is_get_request(request):
    return request.method == 'GET'


def is_post_request(request):
    return request.method == 'POST'


def create_dict_from_string(string):
    try:
        return ast.literal_eval(string)
    except:
        return False
