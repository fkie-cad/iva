from collections import namedtuple
from wfn.wfn_converter import WFNConverter

CPE_KEYS = namedtuple('CPE_KEYS', ['uri', 'formatted_string'])('cpe_2_2', 'id')
IVA_CPE_KEYS = namedtuple('IVA_CPE_KEYS', ['wfn', 'uri', 'formatted_string'])('wfn', 'uri_binding', 'formatted_string_binding')

CVE_KEYS = namedtuple('CVE_KEYS', ['id', 'summary', 'cpes'])('id', 'summary', 'vulnerable_configuration_cpe_2_2')
IVA_CVE_KEYS = namedtuple('IVA_CVE_KEYS', ['id', 'summary', 'cpes'])('cve_id', 'cve_summary', 'cpe_entries')


def format_cve(cve):
    return {IVA_CVE_KEYS.id: cve.get(CVE_KEYS.id),
            IVA_CVE_KEYS.summary: cve.get(CVE_KEYS.summary),
            IVA_CVE_KEYS.cpes: get_cpe_entries(cve)}


def format_cpe(cpe):
    uri = get_uri(cpe)
    return {IVA_CPE_KEYS.uri: uri, IVA_CPE_KEYS.wfn: to_wfn(uri), IVA_CPE_KEYS.formatted_string: get_formatted_string(cpe)}


def get_cpe_entries(cve):
    cpe_entries = []
    for uri_binding in cve.get(CVE_KEYS.cpes):
        cpe_entries.append(create_cpe_doc(uri_binding))
    return cpe_entries


def create_cpe_doc(uri_binding):
    return {IVA_CPE_KEYS.uri: uri_binding, IVA_CPE_KEYS.wfn: to_wfn(uri_binding)}


def get_uri(cpe_doc):
    return cpe_doc.get(CPE_KEYS.uri)


def get_formatted_string(cpe_doc):
    return cpe_doc.get(CPE_KEYS.formatted_string)


def to_wfn(uri_binding):
    return WFNConverter().convert_cpe_uri_to_wfn(uri_binding)