"""CI orchestration/acceptance negatives; no native tools or router required."""
import copy
import unittest

from tools.route_474 import campaign, cohort, failed_first, ResourceBudget, finish_registry
from threading import Event


def cases():
    return {kind: {"id": kind, "scope": {"expected_connections": count},
                   "nets": [{"kicad_net": "a"}, {"kicad_net": "b"}]}
            for kind, count in (("ui", 252), ("rf", 222))}


def row(job, *, passed=True, signature="a" * 64):
    target = 252 if job["kind"] == "ui" else 222
    flags = ("geometry_pass", "candidate_pass", "preservation_recipe_pass", "dependencies_unchanged",
             "selected_complete", "drc_checked", "candidate_unchanged_during_checks")
    grade = {**dict.fromkeys(flags, True), "selected_remaining": [target, 0 if passed else 1],
             "native_unconnected": [1000, 1000 - target], "resolved_connections": target,
             "drc_violations": 0, "schematic_parity_errors": 0, "drc_selected_unconnected": 0,
             "kicad_version": "10.0.5", "failures": {}, "roi_escaped_objects": [],
             "all_net_regressions": {}, "electrically_qualified": False,
             "added_geometry_signature": signature, "new_vias": 10, "new_trace_length_mm": 100,
             "per_net": {"a": [1, 0], "b": [1, 0 if passed else 1]}}
    if not passed:
        grade.update(geometry_pass=False, candidate_pass=False, selected_complete=False)
    return {"profile": {"id": job["id"], **({"replay_of": job["replay_of"]} if "replay_of" in job else {})},
            "recipe": copy.deepcopy(job["recipe"]), "folder": "/fixture/" + job["id"], "cold_from_original": True,
            "geometry_pass": passed, "engine": {"exit_code": 0, "seconds": 1},
            "validation_process": {"exit_code": 0}, "validation": grade}


def plans(count=1):
    return {kind: {"profiles": [{"name": f"p-{i}"} for i in range(count)]} for kind in ("ui", "rf")}


class CampaignTests(unittest.TestCase):
    def test_complete_both_boards_and_three_replays(self):
        jobs = []
        def execute(batch, wave):
            jobs.extend(batch)
            return [row(j) for j in batch]
        result = campaign(cases(), plans(), execute)
        self.assertEqual((result["status"], result["resolved"]), ("pass", 474))
        self.assertEqual(len(jobs), 8)
        self.assertEqual(sum("replay_of" in j for j in jobs), 6)
        self.assertFalse(result["production_ready"])

    def test_partial_never_credited(self):
        result = campaign(cases(), plans(3), lambda jobs, _: [row(j, passed=j["kind"] == "rf") for j in jobs])
        self.assertEqual((result["status"], result["resolved"]), ("fail", 222))
        self.assertEqual(len(result["cases"]["ui"]["attempts"]), 3)

    def test_bounded_search_does_not_run_remaining_profiles_after_winner(self):
        result = campaign(cases(), plans(8), lambda jobs, _: [row(j) for j in jobs], wave_size=2)
        self.assertEqual(result["resolved"], 474)
        self.assertEqual(len(result["cases"]["ui"]["attempts"]), 4)

    def test_adaptive_failed_first_freezes_exact_scope(self):
        plan = plans()
        plan["ui"]["adaptive"] = [{"name": "template", "direction": "backward"}]
        def execute(jobs, wave):
            return [row(j, passed=j["kind"] == "rf" or j["recipe"]["name"].startswith("failed-first")) for j in jobs]
        result = campaign(cases(), plan, execute)
        self.assertEqual(result["resolved"], 474)
        self.assertEqual(result["cases"]["ui"]["winner"]["recipe"]["net_order"], ["b", "a"])

    def test_replay_mismatch_fails_case(self):
        def execute(jobs, wave):
            return [row(j, signature="b" * 64 if j["id"] == "ui-replay-3" else "a" * 64) for j in jobs]
        result = campaign(cases(), plans(), execute)
        self.assertEqual((result["status"], result["resolved"]), ("fail", 222))

    def test_cancelled_no_credit(self):
        result = campaign(cases(), plans(), lambda *_: self.fail("Called after cancellation"), cancelled=lambda: True)
        self.assertEqual(result["resolved"], 0)

    def test_wrong_job_identity_raises(self):
        def execute(jobs, wave):
            r = [row(j) for j in jobs]
            r[0]["profile"]["id"] = "wrong"
            return r
        with self.assertRaises(ValueError):
            campaign(cases(), plans(), execute)

    def test_missing_result_raises(self):
        with self.assertRaises(ValueError):
            campaign(cases(), plans(), lambda *_: [])

    def test_cohort_negative_mutations(self):
        winner = row({"id": "ui-initial", "kind": "ui", "recipe": {"name": "p"}})
        replays = [row({"id": f"ui-replay-{i}", "kind": "ui", "recipe": {"name": "p"},
                        "replay_of": "ui-initial"}) for i in range(1, 4)]
        self.assertTrue(cohort(cases()["ui"], winner, replays)["accepted"])
        self.assertFalse(cohort(cases()["ui"], winner, replays[:-1])["accepted"])
        changed_winner = copy.deepcopy(winner)
        changed_winner["cold_from_original"] = False
        self.assertFalse(cohort(cases()["ui"], changed_winner, replays)["accepted"])
        for location, key, value in ((None, "folder", winner["folder"]),
                                    (None, "cold_from_original", False),
                                    (None, "recipe", {"name": "other"}),
                                    ("validation", "drc_violations", 1),
                                    ("validation", "roi_escaped_objects", ["escape"]),
                                    ("validation", "all_net_regressions", {"other": 1}),
                                    ("validation", "schematic_parity_errors", 1),
                                    ("validation_process", "exit_code", 1)):
            with self.subTest(key=key):
                changed = copy.deepcopy(replays)
                (changed[-1][location] if location else changed[-1])[key] = value
                self.assertFalse(cohort(cases()["ui"], winner, changed)["accepted"])

    def test_adaptive_requires_checked_no_regression(self):
        r = row({"id": "partial", "kind": "ui", "recipe": {}}, passed=False)
        r["validation"]["all_net_regressions"] = {"bad": 1}
        self.assertIsNone(failed_first(cases()["ui"], [r], {}, 1))

    def test_resource_budget_released_on_exception(self):
        budget = ResourceBudget(8, Event())
        with self.assertRaises(RuntimeError):
            with budget.acquire(2):
                self.assertEqual(budget.available, 6)
                raise RuntimeError("failure")
        self.assertEqual(budget.available, 8)

    def test_normal_cleanup_is_not_user_cancellation(self):
        cancel, abort = Event(), Event()
        class Registry:
            def cancel_all(self):
                cancel.set()
        report = {"status": "pass", "resolved": 474}
        finish_registry(Registry(), cancel, abort, report)
        self.assertEqual(report, {"status": "pass", "resolved": 474, "cancelled": False})

    def test_explicit_cancel_during_cleanup_removes_credit(self):
        cancel, abort = Event(), Event()
        class Registry:
            def cancel_all(self):
                cancel.set()
                abort.set()
        report = {"status": "pass", "resolved": 474}
        finish_registry(Registry(), cancel, abort, report)
        self.assertEqual(report, {"status": "fail", "resolved": 0, "cancelled": True})


if __name__ == "__main__":
    unittest.main()
