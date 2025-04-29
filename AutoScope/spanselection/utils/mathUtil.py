import json
import heapq


class SlidingWindowZScore:
    def __init__(self, window_size=100):
        self.window_size = window_size
        self.median_tracker = DynamicMedian()
        self.mad_tracker = MADApproximator()
        self.history = []

    def update(self, value):
        if len(self.history) >= self.window_size:
            old = self.history.pop(0)
            self.median_tracker.remove(old)
        self.history.append(value)
        self.median_tracker.insert(value)

        median = self.median_tracker.get_median()
        deviation = abs(value - median)
        self.mad_tracker.insert(deviation)

    def get_statistics(self):
        median = self.median_tracker.get_median()
        mad = self.mad_tracker.get_mad()
        return median, mad


class MADApproximator:
    def __init__(self):
        self.values = []

    def insert(self, deviation):
        self.values.append(deviation)
        if len(self.values) > 500:
            self.values.pop(0)

    def get_mad(self):
        if not self.values:
            return 1e-6
        sorted_vals = sorted(self.values)
        mid = len(sorted_vals) // 2
        if len(sorted_vals) % 2 == 0:
            return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2
        else:
            return sorted_vals[mid]


class DynamicMedian:
    def __init__(self):
        self.min_heap = []
        self.max_heap = []

    def insert(self, num):
        if not self.max_heap or num <= -self.max_heap[0]:
            heapq.heappush(self.max_heap, -num)
        else:
            heapq.heappush(self.min_heap, num)
        self._balance()

    def remove(self, num):
        try:
            if num <= -self.max_heap[0]:
                self.max_heap.remove(-num)
                heapq.heapify(self.max_heap)
            else:
                self.min_heap.remove(num)
                heapq.heapify(self.min_heap)
        except ValueError:
            pass
        self._balance()

    def _balance(self):
        if len(self.max_heap) > len(self.min_heap) + 1:
            val = -heapq.heappop(self.max_heap)
            heapq.heappush(self.min_heap, val)
        elif len(self.min_heap) > len(self.max_heap):
            val = heapq.heappop(self.min_heap)
            heapq.heappush(self.max_heap, -val)

    def get_median(self):
        if not self.max_heap and not self.min_heap:
            return None
        if len(self.max_heap) == len(self.min_heap):
            return (-self.max_heap[0] + self.min_heap[0]) / 2
        else:
            return -self.max_heap[0]


def update_mean(mean, value, n):
    return (1- 1 / n) * mean + 1 / n * value


def update_variance(variance, mean, value, n):
    if (1 - 1 / n) * (variance + (1 / n) * (value - mean)**2) == 0:
        a = 1
    return (1 - 1 / n) * (variance + (1 / n) * (value - mean)**2)


def calculate_coverage(json_file, sampled_span_id):
    with open(json_file, "r", encoding="utf-8") as f:
        problem_data = json.load(f)

    group1_faults = {'CPU_CONTENTION', 'DELAY', 'Origin'}
    group1_spans = set()
    group2_spans = set()

    all_fault_span = set()
    for info in problem_data.values():
        all_fault_span.update(info.get("span", []))

    for trace_id, info in problem_data.items():
        fault_type = info.get('FAULT')
        span_ids = info.get("span", [])
        for sid in span_ids:
            if fault_type in group1_faults:
                group1_spans.add(sid)
            else:
                group2_spans.add(sid)

    coverage_group1 = (len(sampled_span_id & group1_spans) / len(group1_spans)
                       if len(group1_spans) > 0 else 0.0)
    coverage_group2 = (len(sampled_span_id & group2_spans) / len(group2_spans)
                       if len(group2_spans) > 0 else 0.0)