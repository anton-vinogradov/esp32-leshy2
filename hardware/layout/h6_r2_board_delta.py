#!/usr/bin/env python3
"""Report physical and copper deltas between two KiCad boards.

The report is deliberately semantic rather than a text diff, because pcbnew
may reorder or reformat the S-expression while preserving the board.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import pcbnew  # type: ignore


def point_mm(point: pcbnew.VECTOR2I) -> tuple[float, float]:
    return round(pcbnew.ToMM(point.x), 4), round(pcbnew.ToMM(point.y), 4)


def footprint_signature(footprint) -> tuple:
    pads = tuple(
        sorted(
            (
                pad.GetNumber(),
                pad.GetNetname(),
                point_mm(pad.GetPosition()),
                point_mm(pad.GetSize()),
            )
            for pad in footprint.Pads()
        )
    )
    return (
        footprint.GetValue(),
        point_mm(footprint.GetPosition()),
        round(footprint.GetOrientationDegrees(), 3),
        footprint.GetLayer(),
        pads,
    )


def copper_signature(board, item) -> tuple:
    if isinstance(item, pcbnew.PCB_VIA):
        return (
            "via",
            point_mm(item.GetPosition()),
            round(pcbnew.ToMM(item.GetWidth(item.TopLayer())), 4),
            round(pcbnew.ToMM(item.GetDrillValue()), 4),
            item.TopLayer(),
            item.BottomLayer(),
        )
    ends = sorted((point_mm(item.GetStart()), point_mm(item.GetEnd())))
    return (
        "track",
        board.GetLayerName(item.GetLayer()),
        ends[0],
        ends[1],
        round(pcbnew.ToMM(item.GetWidth()), 4),
    )


def board_state(path: Path) -> tuple[dict, dict[str, Counter]]:
    board = pcbnew.LoadBoard(str(path))
    footprints = {
        footprint.GetReference(): footprint_signature(footprint)
        for footprint in board.GetFootprints()
    }
    copper = defaultdict(Counter)
    for item in board.GetTracks():
        copper[item.GetNetname()][copper_signature(board, item)] += 1
    return footprints, copper


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    args = parser.parse_args()

    before_fp, before_copper = board_state(args.before)
    after_fp, after_copper = board_state(args.after)
    references = sorted(set(before_fp) | set(after_fp))
    footprint_changes = [ref for ref in references if before_fp.get(ref) != after_fp.get(ref)]

    copper_changes = []
    for net in sorted(set(before_copper) | set(after_copper)):
        removed = before_copper[net] - after_copper[net]
        added = after_copper[net] - before_copper[net]
        if removed or added:
            copper_changes.append(
                {
                    "net": net,
                    "removed": sum(removed.values()),
                    "added": sum(added.values()),
                }
            )

    print(
        json.dumps(
            {
                "before": str(args.before),
                "after": str(args.after),
                "footprint_changes": footprint_changes,
                "copper_changes": copper_changes,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
