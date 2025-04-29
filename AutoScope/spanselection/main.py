from AutoScope.spanselection.utils.TraceUtil import parse_trace, get_trace_sts_dict, build_parent_child_for_trace
from AutoScope.spanselection.selection.utilityBased.utilitySample import sample_span_from_trace_utility
from utils.mathUtil import calculate_coverage
from utils.GraphUtil import read_graph_from_file

GRAPH_PATH = "../CSCFG/Xmerge/XCSCFG.txt"
TRACE_PATH = "../data/CSCFG/trace/0111_0112.csv"

global_sts_dict = {}
global_length_stats = []
global_matching_time = []
global_selecting_time = []


def convert_to_chrome_trace(trace_list):
    events = []

    def add_span_events(span, pid):
        start_event = {
            "name": span.operation_name,
            "cat": "function",
            "ph": "B",
            "ts": span.start_time * 1e6,
            "pid": pid,
            "tid": span.span_id,
            "args": {
                "pod_name": span.pod_name,
                "operation_name": span.operation_name
            }
        }
        events.append(start_event)

        for child in span.children:
            add_span_events(child, pid)

        end_event = {
            "name": span.operation_name,
            "cat": "function",
            "ph": "E",
            "ts": span.end_time * 1e6,
            "pid": pid,
            "tid": span.span_id,
            "args": {
                "pod_name": span.pod_name,
                "operation_name": span.operation_name
            }
        }
        events.append(end_event)

    for trace in trace_list:
        if trace.root:
            pid = hash(trace.root.pod_name)
            add_span_events(trace.root, pid)

    return events


def main():
    trace_data = parse_trace(TRACE_PATH)
    build_parent_child_for_trace(trace_data)
    x_cscfg = read_graph_from_file(GRAPH_PATH)

    compresion_ratio = {}
    dss_num = {}
    selected_span = []

    for trace_id, trace in trace_data.items():
        try:
            span_num = len(trace.span_dict)
            if span_num not in compresion_ratio:
                compresion_ratio[span_num] = []
            if span_num not in dss_num:
                dss_num[span_num] = []

            prunned_trace = sample_span_from_trace_utility(trace, x_cscfg, get_trace_sts_dict(trace, global_sts_dict), sample_ratio=0.01)
            for branch in prunned_trace:
                for span in branch:
                    selected_span.append(span.span_id)

        except Exception as e:
            print(f"Sample trace {trace_id} failed: {e}")
            continue

    print(f"Matching time: {sum(global_matching_time)}, Selecting time: {sum(global_selecting_time)}")
    calculate_coverage(selected_span, "../data/trace/merged_span.json")


if __name__ == "__main__":
    main()