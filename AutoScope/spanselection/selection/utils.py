from AutoScope.spanselection.identifyPath import node2span
from  AutoScope.spanselection.selection.utilityBased.calculateUtility import form_span_index, calculate_utility


def select_span_from_branch(trace, span_in_branch, utility_dict, span_num):
    span_list = []
    for span_str in span_in_branch:
        span = node2span(trace, span_str)
        span_duration = span.duration
        span_idx = form_span_index(trace, span)
        utility = calculate_utility(span_duration, span_idx, utility_dict)
        span_list.append((span, utility))
    span_list = sorted(span_list, key=lambda x: x[1], reverse=True)
    return [span[0] for span in span_list[:span_num]]


def split_span_num_by_branch(span_different_branch, expect_span_num):
    span_num_disribution = []
    whole_span_num = sum([len(span_list) for span_list in span_different_branch])
    for span_list in span_different_branch:
        span_num_disribution.append(len(span_list) / whole_span_num * expect_span_num)
    return span_num_disribution


