#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =========================
# تنظیم نگاشت و سیاست مؤلفه
# =========================
OUTPUT_MAPPING   = "1=mafia"   # یا "1=mafia"
COMPONENT_POLICY = "start=1"     # "start=1" | "start=0" | "minlex"

# =========================
# ورودی‌ها (به‌صورت متغیّر)
# =========================
A = [
[1, 0, 0, 0, 0, 1, -1, -1, 0],
[-1, 1, 1, 1, -1, -1, 0, 1, 1],
[0, 0, 1, 1, 0, 0, 1, 1, 1],
[-1, 0, 0, 1, -1, -1, 1, 1, 0],
[0, 0, 0, -1, 1, 0, -1, -1, 0],
[0, -1, 0, 0, 1, 1, -1, 0, -1],
[0, 1, 0, 1, 0, -1, 1, 1, 0],
[-1, 0, 1, 1, 0, -1, 1, 1, 0],
[-1, 1, 0, 1, 0, 0, 0, 1, 1]
]

points = [(0,0), (4,2), (6,6), (0,5), (9,9)]  # برای مسئلهٔ فیل

# =========================
# حل‌گر «صبح مافیا»
# =========================
from collections import deque

def _apply_mapping(sign_list):
    """
    sign_list: لیست مقادیر +1 (citizen) یا -1 (mafia) برای هر نفر.
    OUTPUT_MAPPING: "1=citizen" یا "1=mafia"
    """
    if OUTPUT_MAPPING == "1=citizen":
        return ''.join('1' if s == +1 else '0' for s in sign_list)
    elif OUTPUT_MAPPING == "1=mafia":
        return ''.join('1' if s == -1 else '0' for s in sign_list)
    else:
        raise ValueError("OUTPUT_MAPPING must be '1=citizen' or '1=mafia'")

def mafia_solver(A):
    n = len(A)
    # تناقض فوری روی قطر
    for i in range(n):
        if A[i][i] == -1:
            return None

    # گراف علامت‌دار: x[j] = w * x[i]
    g = [[] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j and A[i][j] != 0:
                g[i].append((j, A[i][j]))

    x = [None]*n  # +1 = citizen, -1 = mafia

    def solve_component(start_node):
        # سیاست مؤلفه: شروع ثابت یا minlex
        if COMPONENT_POLICY == "minlex":
            start_candidates = [+1, -1]
        elif COMPONENT_POLICY == "start=1":
            start_candidates = [+1]
        elif COMPONENT_POLICY == "start=0":
            start_candidates = [-1]
        else:
            raise ValueError("COMPONENT_POLICY must be 'start=1', 'start=0', or 'minlex'")

        best = None  # (binary_string_for_component, nodes, vals)

        for start_val in start_candidates:
            ok = True
            vals = {start_node: start_val}
            nodes = []
            q = deque([start_node])

            while q and ok:
                u = q.popleft()
                nodes.append(u)
                for v, w in g[u]:
                    need = w * vals[u]
                    if v not in vals:
                        vals[v] = need
                        q.append(v)
                    elif vals[v] != need:
                        ok = False
                        break

            if not ok:
                best = None
                # اگر یکی از کاندیداها تناقض داد، ممکن است دیگری جواب بدهد (فقط در minlex مهم است)
                if COMPONENT_POLICY != "minlex":
                    return None
                else:
                    continue

            if COMPONENT_POLICY == "minlex":
                # نگاشت باینری مؤلفه را بر اساس OUTPUT_MAPPING بساز و کمینه‌ی لغت‌نامه‌ای را نگه‌دار
                signs_comp = [vals[i] for i in nodes]
                bits_comp = _apply_mapping(signs_comp)
                if best is None or bits_comp < best[0]:
                    best = (bits_comp, nodes, vals)
            else:
                best = ("", nodes, vals)
                break

        return best

    for s in range(n):
        if x[s] is not None:
            continue
        result = solve_component(s)
        if result is None:
            return None
        _, nodes, vals = result
        for i in nodes:
            x[i] = vals[i]

    return _apply_mapping(x)

# =========================
# حل‌گر «مسیر فیل» 10×10
# =========================
SIZE = 10
def _inb(x,y): return 0 <= x < SIZE and 0 <= y < SIZE

def _bishop_segment(p, q):
    (x1,y1),(x2,y2) = p, q
    if (x1,y1) == (x2,y2):
        return [p]
    dx, dy = abs(x1-x2), abs(y1-y2)
    if dx == dy:  # روی یک قطر
        return [p, q]
    if (x1+y1) % 2 != (x2+y2) % 2:
        return None  # غیرهم‌رنگ، ناممکن
    s1, d1 = x1+y1, x1-y1
    s2, d2 = x2+y2, x2-y2
    cand = [
        ((s1+d2)//2, (s1-d2)//2),
        ((s2+d1)//2, (s2-d1)//2),
    ]
    for cx, cy in cand:
        if 2*cx in (s1+d2, s2+d1) and 2*cy in (s1-d2, s2-d1) and _inb(cx,cy):
            return [p, (cx,cy), q]
    return None

def bishop_chain(points):
    if not points:
        return []
    path = [points[0]]
    for a, b in zip(points, points[1:]):
        seg = _bishop_segment(a, b)
        if seg is None:
            return None
        path.extend(seg[1:])  # حذف تکرارِ نقطهٔ اتصال
    return path

# =========================
# اجرای نمونه‌ها
# =========================
if __name__ == "__main__":
    ans_mafia = mafia_solver(A)
    print("Mafia:", ans_mafia if ans_mafia is not None else "inconsistent")

    bp = bishop_chain(points)
    print("Bishop:", "impossible" if bp is None else bp)
