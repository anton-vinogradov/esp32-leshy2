import unittest
from hardware.layout.h6_r2_benchmark_usage import measure


def counter(time, inputs, cached, outputs):
    return {"timestamp": time, "type": "event_msg", "payload": {"type": "token_count", "info": {
        "total_token_usage": {"input_tokens": inputs, "cached_input_tokens": cached,
                              "output_tokens": outputs, "total_tokens": inputs + outputs}}}}


class UsageTests(unittest.TestCase):
    def test_cumulative_delta_deduplicates_and_does_not_export_content(self):
        old = counter("2026-09-16T00:00:00Z", 100, 80, 10)
        new = counter("2026-09-16T00:02:00Z", 400, 320, 30)
        events = [old, new, new, {"timestamp": "2026-09-16T00:02:30Z", "type": "response_item",
            "payload": {"type": "function_call_output", "output": "secret text"}}]
        result = measure(events, "2026-09-16T00:01:00Z", "2026-09-16T00:03:00Z")
        self.assertEqual(320, result["token_delta"]["total_tokens"])
        self.assertEqual(80, result["uncached_input_plus_output_proxy"])
        self.assertEqual(11, result["proxies"]["tool_result_characters"])
        self.assertNotIn("secret", str(result))

    def test_no_baseline_is_unknown_not_zero(self):
        result = measure([], "2026-09-16T00:01:00Z", "2026-09-16T00:03:00Z")
        self.assertIsNone(result["token_delta"])

    def test_reset_rejected(self):
        with self.assertRaises(ValueError):
            measure([counter("2026-09-16T00:00:00Z", 100, 80, 10),
                     counter("2026-09-16T00:02:00Z", 1, 0, 1)],
                    "2026-09-16T00:01:00Z", "2026-09-16T00:03:00Z")

    def test_timezone_required(self):
        with self.assertRaises(ValueError):
            measure([], "2026-09-16T00:01:00", "2026-09-16T00:03:00Z")

    def test_intermediate_reset_cannot_be_hidden_by_later_growth(self):
        with self.assertRaises(ValueError):
            measure([counter("2026-09-16T00:00:00Z", 100, 80, 10),
                     counter("2026-09-16T00:01:30Z", 1, 0, 1),
                     counter("2026-09-16T00:02:00Z", 900, 800, 90)],
                    "2026-09-16T00:01:00Z", "2026-09-16T00:03:00Z")
