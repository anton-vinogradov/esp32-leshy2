#!/usr/bin/env python3
"""Relocate one routed via and every copper endpoint attached to it.

This intentionally small helper is used for local, DRC-first routing repairs:
write a candidate board, run native KiCad DRC, and only then replace the source.
It never edits the input board in place.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pcbnew  # type: ignore


def mm(point: pcbnew.VECTOR2I) -> tuple[float, float]:
    return pcbnew.ToMM(point.x), pcbnew.ToMM(point.y)


def near(point: pcbnew.VECTOR2I, expected: tuple[float, float]) -> bool:
    x, y = mm(point)
    return abs(x - expected[0]) < 0.0005 and abs(y - expected[1]) < 0.0005


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("net")
    parser.add_argument("old", help="old via position as X,Y in millimetres")
    parser.add_argument("new", help="new via position as X,Y in millimetres")
    args = parser.parse_args()

    old = tuple(map(float, args.old.split(",")))
    new = tuple(map(float, args.new.split(",")))
    if len(old) != 2 or len(new) != 2:
        raise SystemExit("positions must be X,Y")

    board = pcbnew.LoadBoard(str(args.input))
    target = pcbnew.VECTOR2I_MM(*new)
    via_count = 0
    endpoint_count = 0

    for item in board.GetTracks():
        if item.GetNetname() != args.net:
            continue
        if isinstance(item, pcbnew.PCB_VIA):
            if near(item.GetPosition(), old):
                item.SetPosition(target)
                via_count += 1
            continue
        if near(item.GetStart(), old):
            item.SetStart(target)
            endpoint_count += 1
        if near(item.GetEnd(), old):
            item.SetEnd(target)
            endpoint_count += 1

    if via_count != 1:
        raise SystemExit(f"expected one via, found {via_count}")
    if endpoint_count < 2:
        raise SystemExit(f"expected at least two attached endpoints, found {endpoint_count}")
    if not pcbnew.SaveBoard(str(args.output), board):
        raise SystemExit("save failed")
    print(f"relocated 1 via and {endpoint_count} attached endpoints: {old} -> {new}")


if __name__ == "__main__":
    main()
