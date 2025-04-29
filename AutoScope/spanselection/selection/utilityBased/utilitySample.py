from AutoScope.spanselection.selection.branchPartition import branch_partition
from AutoScope.spanselection.selection.utils import select_span_from_branch


def sample_span_from_trace_utility(trace_data, x_cscfg, utility_dict, sample_ratio=0.01):
    sperated_trace = branch_partition(trace_data, x_cscfg, utility_dict)
    expected_span_num = int(len(trace_data.span_dict) * sample_ratio)
    prunned_trace = select_span_by_utility(trace_data, sperated_trace, utility_dict, expected_span_num)
    return prunned_trace


def select_span_by_utility(trace, span_different_branch, utility_dict, expect_span_num):
    filtered_span = []
    for branch_idx, span_in_branch in enumerate(span_different_branch):
         filtered_span.append(select_span_from_branch(trace, span_in_branch, utility_dict, expect_span_num))
    return filtered_span


def distribute_span_num_by_branch(span_different_branch, expect_span_num):
    span_num_disribution = {}
    whole_span_num = sum([len(span_list) for span_list in span_different_branch])
    for idx, span_list in enumerate(span_different_branch):
        if len(span_list) / whole_span_num * expect_span_num < 1:
            span_num_disribution[idx] = 1
        else:
            span_num_disribution[idx] = (len(span_list) // whole_span_num) * expect_span_num
    return span_num_disribution