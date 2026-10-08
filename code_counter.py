#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time

LANG_EXTS = {
    "C": {".c"},
    "C++": {".cpp", ".cc", ".cxx", ".c++", ".hpp", ".hh", ".hxx", ".h"},
    "Java": {".java"},
    "Python": {".py"},
}

LANG_ORDER = ["C", "C++", "Java", "Python"]

# 扫描时忽略的目录名
IGNORE_DIRS = {
    ".git", "node_modules", "__pycache__", "build", "dist",
    ".idea", ".vscode", ".venv", "venv", "env",
    "$Recycle.Bin", "System Volume Information",
    "Windows", "ProgramData", "Recovery",
    "WinSxS", "Installer", "assembly",
}


def classify(path):
    ext = os.path.splitext(path)[1].lower()
    for lang, exts in LANG_EXTS.items():
        if ext in exts:
            return lang
    return None


def read_lines(path):
    encodings = ["utf-8", "utf-8-sig", "gbk", "latin-1"]
    for enc in encodings:
        try:
            with open(path, "r", encoding=enc) as f:
                return f.readlines()
        except UnicodeDecodeError:
            continue
        except OSError:
            return []
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.readlines()
    except OSError:
        return []


def count_c_style(lines):
    blank = comment = code = 0
    in_block = False

    for raw in lines:
        line = raw.rstrip("\n\r")
        stripped = line.strip()

        if not stripped:
            blank += 1
            continue

        has_code = False
        i = 0
        n = len(line)
        in_string = None
        escaped = False

        while i < n:
            ch = line[i]

            if in_block:
                if ch == "*" and i + 1 < n and line[i + 1] == "/":
                    in_block = False
                    i += 2
                    continue
                i += 1
                continue

            if in_string:
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == in_string:
                    in_string = None
                i += 1
                continue

            if ch == "/" and i + 1 < n:
                nxt = line[i + 1]
                if nxt == "/":
                    break
                if nxt == "*":
                    in_block = True
                    i += 2
                    continue

            if ch in ('"', "'"):
                in_string = ch
                has_code = True
                i += 1
                continue

            if not ch.isspace():
                has_code = True

            i += 1

        if has_code:
            code += 1
        else:
            comment += 1

    return blank, comment, code


def count_python(lines):
    blank = comment = code = 0
    in_triple = False
    triple = None

    for raw in lines:
        line = raw.rstrip("\n\r")
        stripped = line.strip()

        if not stripped:
            blank += 1
            continue

        has_code = False
        i = 0
        n = len(line)
        in_string = None
        escaped = False

        while i < n:
            ch = line[i]

            if in_triple:
                if line.startswith(triple, i):
                    in_triple = False
                    i += 3
                    continue
                i += 1
                continue

            if in_string:
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == in_string:
                    in_string = None
                i += 1
                continue

            if ch == "#":
                break

            if line.startswith('"""', i) or line.startswith("'''", i):
                triple = line[i:i + 3]
                in_triple = True
                i += 3
                continue

            if ch in ('"', "'"):
                in_string = ch
                has_code = True
                i += 1
                continue

            if not ch.isspace():
                has_code = True

            i += 1

        if has_code:
            code += 1
        else:
            comment += 1

    return blank, comment, code


def main():
    start = time.time()

    root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    root = os.path.abspath(root)

    if not os.path.isdir(root):
        print(f"错误：目录不存在或不是目录：{root}")
        sys.exit(1)

    stats = {
        lang: {"files": 0, "blank": 0, "comment": 0, "code": 0}
        for lang in LANG_ORDER
    }

    total_files_scanned = 0
    total_dirs_scanned = 0

    for dirpath, dirnames, filenames in os.walk(root, onerror=lambda e: None):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        total_dirs_scanned += 1

        for name in filenames:
            total_files_scanned += 1
            full = os.path.join(dirpath, name)
            lang = classify(full)

            if not lang:
                continue

            try:
                lines = read_lines(full)
            except Exception:
                continue

            stats[lang]["files"] += 1

            if lang in ("C", "C++", "Java"):
                b, c, co = count_c_style(lines)
            else:
                b, c, co = count_python(lines)

            stats[lang]["blank"] += b
            stats[lang]["comment"] += c
            stats[lang]["code"] += co

    headers = ["Language", "files", "blank", "comment", "code"]
    rows = []
    total = {"files": 0, "blank": 0, "comment": 0, "code": 0}

    for lang in LANG_ORDER:
        s = stats[lang]
        rows.append([lang, s["files"], s["blank"], s["comment"], s["code"]])
        for k in total:
            total[k] += s[k]

    rows.append(["SUM", total["files"], total["blank"], total["comment"], total["code"]])

    widths = []
    for i in range(len(headers)):
        widths.append(max(len(str(r[i])) for r in [headers] + rows))

    fmt = "  ".join("{:<" + str(w) + "}" for w in widths)

    print(fmt.format(*headers))
    for r in rows:
        print(fmt.format(*[str(x) for x in r]))

    elapsed = time.time() - start
    print()
    print(f"扫描目录: {root}")
    print(f"扫描子目录数: {total_dirs_scanned}")
    print(f"扫描文件总数: {total_files_scanned}")
    print(f"查询耗时: {elapsed:.2f} 秒")


if __name__ == "__main__":
    main()