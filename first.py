#!/usr/bin/env python3
"""
تعیین نقش ها در ماتریس گزارش مافیا

مقدارها در ماتریس n×n:
  1  => بازیکن i و j یک نقش (هر دو شهروند یا هر دو مافیا)
 -1  => بازیکن i و j نقش متفاوت
  0  => بدون اطلاعات

هدف: تولید رشته ای از 0/1 به طول n
 1 = شهروند (سفید)
 0 = مافیا (سیاه)

اگر تناقض (عدم دو رنگی یا تساوی و تضاد همزمان) وجود داشته باشد چاپ IMPOSSIBLE.
سیاست رفع چند پاسخ ممکن: کامپوننت شامل بازیکن 0 رنگ 1 می گیرد؛ رنگ های دیگر در پیمایش BFS تعیین می شوند؛
اگر هنوز چند پاسخ (انعکاس کلی) ممکن باشد همان حالتِ به دست آمده چاپ می شود.

ورودی (یکی از دو فرمت):
1) n سپس n خط شامل n مقدار از بین {-1,0,1}
2) یک لیست پایتونی قابل literal_eval مانند: [[1,1,0], [0,1,-1], ...]

خروجی: رشته 0/1 یا IMPOSSIBLE

نمونه:
Input:
6\n1 1 0 -1 1 1\n0 1 0 0 1 0\n0 -1 1 1 -1 0\n0 0 1 1 -1 -1\n1 1 0 0 1 1\n1 1 -1 -1 1 1
Output:
110011
"""
from __future__ import annotations
from collections import deque, defaultdict
import sys, ast

class DSU:
    __slots__ = ("p","r")
    def __init__(self, n:int):
        self.p = list(range(n))
        self.r = [0]*n
    def find(self, x:int) -> int:
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x
    def union(self, a:int, b:int):
        a = self.find(a); b = self.find(b)
        if a == b: return
        if self.r[a] < self.r[b]:
            a, b = b, a
        self.p[b] = a
        if self.r[a] == self.r[b]:
            self.r[a] += 1

class InferenceError(Exception):
    pass

def infer_roles(matrix:list[list[int]]) -> str:
    n = len(matrix)
    if n == 0:
        return ""
    for row in matrix:
        if len(row) != n:
            raise InferenceError("ماتریس باید مربعی باشد")
    dsu = DSU(n)
    # 1) Union for equalities (1)
    for i in range(n):
        mi = matrix[i]
        for j in range(n):
            v = mi[j]
            if v == 1:
                dsu.union(i, j)
    # 2) Build inequality graph between component roots
    adj: dict[int,set[int]] = defaultdict(set)
    for i in range(n):
        for j in range(n):
            if matrix[i][j] == -1:
                a = dsu.find(i); b = dsu.find(j)
                if a == b:
                    raise InferenceError("تناقض: تساوی و تضاد همزمان")
                adj[a].add(b); adj[b].add(a)
    # 3) Bipartite coloring of component graph
    color: dict[int,int] = {}
    roots = {dsu.find(i) for i in range(n)}
    # Ensure root of player 0 visited first, color=1 (citizen)
    ordered = sorted(roots, key=lambda r: (r != dsu.find(0), r))
    for r in ordered:
        if r in color: continue
        # First component containing player 0 -> color 1, others also start with 1 (arbitrary) for determinism
        start_color = 1
        color[r] = start_color
        q = deque([r])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if v not in color:
                    color[v] = 1 - color[u]
                    q.append(v)
                elif color[v] == color[u]:
                    raise InferenceError("تناقض: گراف دو رنگ نیست")
    # 4) Map each original node to its component's color
    return ''.join(str(color[dsu.find(i)]) for i in range(n))

def parse_input(text:str) -> list[list[int]]:
    text = text.strip()
    if not text:
        return []
    # Try literal list
    if text[0] in '[(':
        try:
            obj = ast.literal_eval(text)
            # Normalize to list of lists
            matrix = [list(map(int, row)) for row in obj]
            return matrix
        except Exception:
            pass
    # Otherwise assume first token n then n lines or flat tokens
    tokens = text.split()
    n = int(tokens[0])
    nums = list(map(int, tokens[1:]))
    if len(nums) != n*n:
        # Maybe lines separated by newlines (already split). If mismatch raise.
        raise ValueError("تعداد اعداد با n*n تطابق ندارد")
    matrix = [nums[i*n:(i+1)*n] for i in range(n)]
    return matrix

def main():
    import argparse, os
    parser = argparse.ArgumentParser(description="استنتاج نقش ها از ماتریس گزارش مافیا")
    parser.add_argument("--matrix", help="لیست ماتریس به صورت literal مثلا '[[1,1,0],[0,1,-1],[0,-1,1]]'", default=None)
    parser.add_argument("--file", help="مسیر فایل حاوی ماتریس", default=None)
    args = parser.parse_args()

    sample = [
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

    try:
        if args.matrix:
            matrix = parse_input(args.matrix)
        elif args.file:
            with open(args.file, 'r', encoding='utf-8') as f:
                matrix = parse_input(f.read())
        else:
            # If stdin has data and is not a TTY, read it; else use sample
            if not sys.stdin.isatty():
                data = sys.stdin.read()
                if data.strip():
                    matrix = parse_input(data)
                else:
                    matrix = sample
            else:
                matrix = sample
        ans = infer_roles(matrix)
        print(ans)
    except InferenceError:
        print("IMPOSSIBLE")
    except Exception as e:
        print(f"INPUT_ERROR: {e}")

if __name__ == "__main__":
    main()
