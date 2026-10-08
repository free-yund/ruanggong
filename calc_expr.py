#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ast
import operator


# 支持的运算符
OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,   # 一元负号
    ast.UAdd: operator.pos,   # 一元正号
}


def eval_expr(node):
    if isinstance(node, ast.Expression):
        return eval_expr(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"不支持的常量：{node.value!r}")
    if isinstance(node, ast.BinOp):
        op = OPS.get(type(node.op))
        if op is None:
            raise ValueError("不支持的运算符")
        left = eval_expr(node.left)
        right = eval_expr(node.right)
        if isinstance(node.op, ast.Div) and right == 0:
            raise ZeroDivisionError("除数不能为 0")
        return op(left, right)
    if isinstance(node, ast.UnaryOp):
        op = OPS.get(type(node.op))
        if op is None:
            raise ValueError("不支持的一元运算符")
        return op(eval_expr(node.operand))
    raise ValueError("表达式包含不支持的内容")


def safe_eval(expr):
    tree = ast.parse(expr, mode="eval")
    return eval_expr(tree)


def main():
    print("=== 四则运算计算器（支持括号和优先级）===")
    print("示例：1 + 2 * 3  或  (1 + 2) * 3")
    print("输入 q 退出\n")

    while True:
        expr = input("请输入表达式：").strip()

        if expr.lower() in ("q", "quit", "exit"):
            print("已退出。")
            break

        if not expr:
            continue

        try:
            result = safe_eval(expr)
        except ZeroDivisionError as e:
            print(f"错误：{e}\n")
            continue
        except Exception as e:
            print(f"表达式错误：{e}\n")
            continue

        if isinstance(result, float) and result == int(result):
            result = int(result)

        print(f"结果：{result}\n")


if __name__ == "__main__":
    main()