import math
import random
import statistics


def parse_rr_input(text):
    values = []
    text = text.strip()
    if not text:
        raise ValueError("至少需要10个盈亏比数据")
    tokens = [t for t in text.replace("，", ",").split() if t]
    simple_ok = True
    for token in tokens:
        parts = token.split(",")
        for p in parts:
            p = p.strip()
            if not p:
                continue
            try:
                values.append(float(p))
            except ValueError:
                simple_ok = False
    if simple_ok and len(values) >= 10:
        return values
    values = []
    lines = text.splitlines()
    for raw_line in lines:
        line = raw_line.replace("，", ",").strip()
        if not line:
            continue
        pieces = []
        for segment in line.split(","):
            segment = segment.replace("\t", " ")
            for chunk in segment.split():
                if chunk:
                    pieces.append(chunk)
        numeric_in_line = []
        for item in pieces:
            try:
                numeric_in_line.append(float(item))
            except ValueError:
                continue
        if numeric_in_line:
            values.append(numeric_in_line[-1])
    if len(values) < 10:
        raise ValueError("至少需要10个盈亏比数据")
    return values


def percentile_from_sorted(sorted_values, p):
    if not 0 <= p <= 1:
        raise ValueError("百分位必须在0到1之间")
    if len(sorted_values) == 1:
        return sorted_values[0]
    k = (len(sorted_values) - 1) * p
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_values[int(k)]
    d0 = sorted_values[f] * (c - k)
    d1 = sorted_values[c] * (k - f)
    return d0 + d1


def run_monte_carlo(rr_list, trades_per_run, num_runs):
    if trades_per_run <= 0:
        raise ValueError("交易笔数必须大于0")
    if num_runs <= 0:
        raise ValueError("模拟次数必须大于0")
    totals = []
    max_drawdowns = []
    for _ in range(num_runs):
        total = 0.0
        peak = 0.0
        max_dd = 0.0
        for _ in range(trades_per_run):
            r = random.choice(rr_list)
            total += r
            if total > peak:
                peak = total
            dd = total - peak
            if dd < max_dd:
                max_dd = dd
        totals.append(total)
        max_drawdowns.append(max_dd)
    return totals, max_drawdowns


def describe_distribution(values):
    if not values:
        raise ValueError("没有可用结果")
    sorted_values = sorted(values)
    mean = statistics.mean(sorted_values)
    median = statistics.median(sorted_values)
    worst = sorted_values[0]
    best = sorted_values[-1]
    p05 = percentile_from_sorted(sorted_values, 0.05)
    p25 = percentile_from_sorted(sorted_values, 0.25)
    p75 = percentile_from_sorted(sorted_values, 0.75)
    p95 = percentile_from_sorted(sorted_values, 0.95)
    lines = []
    lines.append(f"模拟结果数量: {len(sorted_values)}")
    lines.append(f"平均最终盈亏R: {mean:.2f}")
    lines.append(f"中位数最终盈亏R: {median:.2f}")
    lines.append(f"最差情景最终盈亏R: {worst:.2f}")
    lines.append(f"最佳情景最终盈亏R: {best:.2f}")
    lines.append(f"5%分位数最终盈亏R: {p05:.2f}")
    lines.append(f"25%分位数最终盈亏R: {p25:.2f}")
    lines.append(f"75%分位数最终盈亏R: {p75:.2f}")
    lines.append(f"95%分位数最终盈亏R: {p95:.2f}")
    return "\n".join(lines)


def describe_drawdown_distribution(drawdowns):
    if not drawdowns:
        raise ValueError("没有可用结果")
    sorted_values = sorted(drawdowns)
    mean = statistics.mean(sorted_values)
    median = statistics.median(sorted_values)
    worst = sorted_values[0]
    best = sorted_values[-1]
    p05 = percentile_from_sorted(sorted_values, 0.05)
    p25 = percentile_from_sorted(sorted_values, 0.25)
    p75 = percentile_from_sorted(sorted_values, 0.75)
    p95 = percentile_from_sorted(sorted_values, 0.95)
    lines = []
    lines.append("")
    lines.append("最大回撤统计（单位R，负值代表从峰值回撤）")
    lines.append(f"平均最大回撤: {mean:.2f}")
    lines.append(f"中位数最大回撤: {median:.2f}")
    lines.append(f"最糟糕的最大回撤: {worst:.2f}")
    lines.append(f"最轻的最大回撤: {best:.2f}")
    lines.append(f"5%分位最大回撤: {p05:.2f}")
    lines.append(f"25%分位最大回撤: {p25:.2f}")
    lines.append(f"75%分位最大回撤: {p75:.2f}")
    lines.append(f"95%分位最大回撤: {p95:.2f}")
    return "\n".join(lines)
