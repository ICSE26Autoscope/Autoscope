import csv
from entity.Function import Function
from entity.Trace import Trace, Span
from typing import Dict, Optional
from graphviz import Digraph
import hashlib
from io import StringIO
from CSCFGConstruct.CSICFG.Util import find_eldest_brother
import re
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt


def sort_function_list(function_list):
    """
    Sort the function list so that parent functions appear before their children.
    """
    new_function_list = []
    for func in function_list:
        if func.parent is None:
            new_function_list.append(func)

    function_list_expect_root = [func for func in function_list if func.parent is not None]

    while len(new_function_list) != len(function_list):
        for func in function_list_expect_root:
            real_parent = find_eldest_brother(func.parent, func)
            if real_parent in new_function_list and func not in new_function_list:
                new_function_list.append(func)
    return new_function_list


def read_trace_function(trace: Trace):
    """
    Extract functions from the trace.
    """
    function_list = []
    span_sort_list = [span for span in trace.span_dict.values()]
    span_sort_list.sort(key=lambda x: x.start_time)
    for span in span_sort_list:
        func_name, clz_name = format_function_clz_name(span)
        valid_flag = check_valid_function(span)
        service_name = format_service_name(span)
        func = Function(func_name, clz_name, service_name, span.pod_name, span.span_id, span.start_time, valid_flag)
        function_list.append(func)

    span_id_func_dict = {func.span_id: func for func in function_list}
    for func in function_list:
        build_parent_child_function(trace, func, span_id_func_dict)

    function_list = sort_function_list(function_list)
    return function_list


def check_valid_function(span):
    if span.parent_id is None:
        return True
    if "." in span.operation_name and len(span.operation_name.split(".")) == 2:
        return True
    return False


def format_function_clz_name(span):
    if "." in span.operation_name and len(span.operation_name.split(".")) == 2:
        clz_name, func_name = span.operation_name.split(".")
    else:
        func_name = span.operation_name
        clz_name = ""
    return func_name, clz_name


def format_service_name(span):
    pod_name = span.pod_name
    service_name = "-".join(pod_name.split("-")[:-2])
    return service_name


def build_parent_child_function(trace: Trace, func: Function, span_id_func_dict):
    """
    Set the parent-child relationship for functions.
    """
    span = trace.span_dict[func.span_id]
    parent_id = span.parent_id
    if parent_id:
        func.parent = span_id_func_dict[parent_id]
        span_id_func_dict[parent_id].children.append(func)


def set_child_function(function_list):
    """
    Placeholder for setting child functions if needed.
    """
    return function_list


def parse_trace(trace_path):
    """
    Parse the CSV trace file into Trace objects.
    """
    with open(trace_path, "r") as f:
        csv_text = f.read()

    f = StringIO(csv_text.strip())
    reader = csv.reader(f)

    header = next(reader, None)

    trace_map: Dict[str, Trace] = {}
    temp_spans = {}

    for row in reader:
        if len(row) != 8:
            continue

        trace_id, span_id, parent_id, pod_name, operation_name, start_time, end_time, duration = row

        if parent_id == "None":
            parent_id = None

        span = Span(
            trace_id=trace_id,
            span_id=span_id,
            parent_id=parent_id,
            pod_name=pod_name,
            operation_name=operation_name,
            start_time=int(start_time),
            end_time=int(end_time),
            duration=int(duration)
        )

        if trace_id not in trace_map:
            trace_map[trace_id] = Trace()

        trace_map[trace_id].add_span(span)
        temp_spans[(trace_id, span_id)] = span

    for trace in trace_map.values():
        trace.index_spans(trace.get_root_span())

    return trace_map



def get_trace_sts_dict(trace: Trace, global_sts_dict):
    """
    Retrieve or initialize the statistics dictionary for a trace.
    """
    trace_value = trace.trace_hash()
    if trace_value not in global_sts_dict:
        global_sts_dict[trace_value] = {}
        return {}
    else:
        return global_sts_dict[trace_value]


def snyc_all_parent_child_relationship(trace_map):
    """
    Set parent-child relationships for all spans in the trace map.
    """
    for trace in trace_map.values():
        for span in trace.span_dict.values():
            if span.parent_id:
                span.parent = trace.span_dict[span.parent_id]
                if span not in trace.span_dict[span.parent_id].children:
                    trace.span_dict[span.parent_id].children.append(span)


def build_parent_child_for_trace(trace_map: dict) -> dict:
    """
    Establish parent-child relationships and identify root spans in the trace map.
    """
    for trace_id, trace in trace_map.items():
        for span in trace.span_dict.values():
            span.children = []

        for span in trace.span_dict.values():
            if span.parent_id:
                parent_span = trace.span_dict.get(span.parent_id)
                if parent_span:
                    parent_span.add_child(span)

    return trace_map


def aggregate_data(data):
    """
    Aggregate data into fixed bins: (1-10, 10-20, ..., 50+).
    """
    bins = [(1, 10), (10, 20), (20, 30), (30, 40), (40, 50), (50, float('inf'))]
    aggregated = defaultdict(list)

    for key, values in data.items():
        for bin_start, bin_end in bins:
            if bin_start <= key < bin_end:
                aggregated[(bin_start, bin_end)].extend(values)
                break

    aggregated_means = {k: np.mean(v) if v else 0 for k, v in aggregated.items()}
    return aggregated_means


def plot_data(dict1, dict2):
    """
    Plot aggregated data from two dictionaries for comparison.
    """
    aggregated1 = aggregate_data(dict1)
    aggregated2 = aggregate_data(dict2)

    bins = [(1, 10), (10, 20), (20, 30), (30, 40), (40, 50), (50, float('inf'))]
    x_labels = [f"{b[0]}-{int(b[1]) if b[1] != float('inf') else '50+'}" for b in bins]
    y1 = [aggregated1.get(b, 0) for b in bins]
    y2 = [aggregated2.get(b, 0) for b in bins]

    x = np.arange(len(bins))
    width = 0.4

    plt.figure(figsize=(10, 5))
    plt.bar(x - width / 2, y1, width, label='Dict 1', alpha=0.7)
    plt.bar(x + width / 2, y2, width, label='Dict 2', alpha=0.7)

    plt.xticks(x, x_labels, rotation=45)
    plt.xlabel("X Axis (Binned)")
    plt.ylabel("Mean Value")
    plt.legend()
    plt.title("Aggregated Data Visualization")
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.show()
