#!/usr/bin/env python3
"""
محاسبهٔ تعداد خانه‌های یکتای ملاقات‌شده هنگام حرکت پیاپی بین یک توالی از نقاط روی شبکهٔ مربعی.
(نسخهٔ بازبینی‌شده با تحمل بالاتر در ورودی و پیام خطای واضح.)
"""
from __future__ import annotations
import sys, ast, argparse, re
from typing import List, Tuple, Iterable, Set

def bresenham_cells(x0:int, y0:int, x1:int, y1:int) -> Iterable[Tuple[int,int]]:
    """بازگرداندن دنبالهٔ خانه‌های روی خط بین دو نقطه (شامل ابتدا و انتها)."""
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        yield (x0, y0)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy; x0 += sx
        if e2 < dx:
            err += dx; y0 += sy

def count_unique(points: List[Tuple[int,int]]) -> int:
    if len(points) < 2:
        return len(points)
    visited: Set[Tuple[int,int]] = set()
    first = True
    for (x0,y0),(x1,y1) in zip(points, points[1:]):
        for idx, cell in enumerate(bresenham_cells(x0,y0,x1,y1)):
            if not first and idx == 0:
                continue
            visited.add(cell)
        first = False
    return len(visited)

# --- Parsing Helpers -------------------------------------------------------
_BRACKET_STRIP_RE = re.compile(r'\s+')
_POINT_TOKEN_RE = re.compile(r'\[\s*(-?\d+)\s*,\s*(-?\d+)\s*\]')

def parse_points(text: str) -> List[Tuple[int,int]]:
    """Parse input text into list of (x,y).
    Accepts forms:
      [[0,0],[4,2],[6,6]]
      [0,0], [4,2], [6,6]
      (also with newlines / extra spaces)
    """
    text = text.strip()
    if not text:
        return []
    # Fast path: try literal_eval directly
    lit_candidate = text
    if not (text.startswith('[') and text.endswith(']')):
        # maybe form without outer brackets
        lit_candidate = f'[{text}]'
    try:
        obj = ast.literal_eval(lit_candidate)
        pts: List[Tuple[int,int]] = []
        for item in obj:
            if not (isinstance(item, (list, tuple)) and len(item) == 2):
                raise ValueError('هر عنصر باید جفت (x,y) باشد')
            x, y = item
            pts.append((int(x), int(y)))
        if pts:
            return pts
    except Exception:
        pass
    # Fallback regex extraction
    matches = _POINT_TOKEN_RE.findall(text)
    if not matches:
        raise ValueError('قالب نقاط شناسایی نشد. نمونه معتبر: [[0,0],[4,2],[6,6]]')
    return [(int(a), int(b)) for a,b in matches]

# --- CLI / Main ------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='شمارش خانه‌های یکتای ملاقات شده با مسیر خطی بین نقاط')
    parser.add_argument('--points', help='لیست نقاط: [[x1,y1],[x2,y2],...] یا بدون براکت بیرونی', default=None)
    parser.add_argument('--debug', action='store_true', help='نمایش جزئیات مسیر')
    args = parser.parse_args()

    default_points = [17, 4], [32, 19], [6, 39], [0, 33], [20, 34], [38, 8], [21, 18], [32, 35] ,[4, 16], [20, 11]

    # Determine source of input
    raw = None
    if args.points:
        raw = args.points
    else:
        if not sys.stdin.isatty():
            stdin_data = sys.stdin.read()
            if stdin_data.strip():
                raw = stdin_data
    if raw is None:
        points = default_points
    else:
        try:
            points = parse_points(raw)
        except Exception as e:
            print(f'INPUT_ERROR: {e}', file=sys.stderr)
            print(len(default_points))
            return
    if args.debug:
        print('Parsed points:', points, file=sys.stderr)
    try:
        result = count_unique(points)
    except Exception as e:
        print(f'RUNTIME_ERROR: {e}', file=sys.stderr)
        print('0')
        return
    print(result)
    if args.debug:
        # Optional: list visited cells when debug
        visited_cells = []
        first = True
        seen = set()
        for (a,b),(c,d) in zip(points, points[1:]):
            for idx, cell in enumerate(bresenham_cells(a,b,c,d)):
                if not first and idx == 0:
                    continue
                if cell not in seen:
                    seen.add(cell)
                    visited_cells.append(cell)
            first = False
        print('Visited cells count:', len(visited_cells), file=sys.stderr)
        print('Cells:', visited_cells, file=sys.stderr)

if __name__ == '__main__':
    main()
