#!/usr/bin/env python3
"""GitHub 个人主页生成器：改下面的 CONFIG，然后运行 `python3 build.py`。

生成：
  README.md            —— 放到 <用户名>/<用户名> 仓库根目录
  assets/*.svg         —— 动画 SVG（横幅 / 终端 / Agent 循环 / 分隔线）
  .github/workflows/   —— 贡献图贪吃蛇动画（GitHub Actions 自动生成）
"""
from pathlib import Path
from xml.sax.saxutils import escape

# ============================== CONFIG ==============================
CONFIG = {
    "name": "Aohancool",               # 显示名
    "github": "Aohancool",              # GitHub 用户名（统计卡片、贪吃蛇都依赖它）
    "city": "Beijing, China",
    "roles": [                          # 横幅里循环打字的头衔（建议英文，等宽字体）
        "AI Agent Developer",
        "LLM Application Engineer",
        "MCP & Tool-Use Builder",
        "Multi-Agent Orchestrator",
    ],
    "focus": ["LLM Agents", "Tool Use", "MCP", "Multi-Agent", "RAG", "Evals"],
    "motto": "Let agents do the boring parts.",
    "email": "",                        # 留空则不显示
    "blog": "",                         # 个人站点 / 博客，留空则不显示
}
# ===================================================================

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
MONO = "'SF Mono','JetBrains Mono',Menlo,Consolas,'Liberation Mono',monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Helvetica,Arial,sans-serif"


def keytimes(points):
    """[(t, v), ...] -> (keyTimes, values)，去掉重复时间点，保证 0..1 单调。"""
    out = []
    for t, v in points:
        t = round(min(max(t, 0.0), 1.0), 4)
        if out and t <= out[-1][0]:
            out[-1] = (out[-1][0], v) if t == out[-1][0] else out[-1]
            continue
        out.append((t, v))
    if out[0][0] != 0:
        out.insert(0, (0.0, out[0][1]))
    if out[-1][0] != 1:
        out.append((1.0, out[-1][1]))
    return ";".join(f"{t:g}" for t, _ in out), ";".join(str(v) for _, v in out)


# ------------------------------------------------------------------ banner
def banner(cfg):
    W, H = 1200, 340
    name = escape(cfg["name"])
    roles = cfg["roles"]
    fs, cw = 26, 26 * 0.602          # 等宽字体字符宽度估算
    x0, y0 = 64, 222
    slot = 3.2
    T = slot * len(roles)

    typing = []
    for i, r in enumerate(roles):
        w = round(len(r) * cw + 4, 1)
        s, d = i / len(roles), 1 / len(roles)
        kt, wv = keytimes([(0, 0), (s, 0), (s + .35 * d, w), (s + .8 * d, w), (s + .97 * d, 0), (1, 0)])
        _, xv = keytimes([(0, x0), (s, x0), (s + .35 * d, x0 + w), (s + .8 * d, x0 + w), (s + .97 * d, x0), (1, x0)])
        okt, ov = keytimes([(0, 0), (s, 1), (s + d, 0), (1, 0)]) if i else keytimes([(0, 1), (d, 0), (1, 0)])
        typing.append(f'''
    <clipPath id="c{i}"><rect x="{x0}" y="{y0-30}" height="40" width="0">
      <animate attributeName="width" dur="{T}s" repeatCount="indefinite" keyTimes="{kt}" values="{wv}"/></rect></clipPath>
    <text x="{x0}" y="{y0}" clip-path="url(#c{i})" class="role">{escape(r)}</text>
    <rect y="{y0-24}" width="3" height="30" fill="#22d3ee" x="{x0}">
      <animate attributeName="x" dur="{T}s" repeatCount="indefinite" keyTimes="{kt}" values="{xv}"/>
      <animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{okt}" values="{ov}"/>
    </rect>''')

    # 右侧 agent 网络
    cx, cy = 930, 170
    nodes = [("LLM", cx, cy, 34), ("Plan", 820, 78, 20), ("Tools", 1050, 70, 20), ("MCP", 1110, 175, 20),
             ("Memory", 1040, 275, 20), ("RAG", 840, 272, 20), ("Eval", 760, 178, 18)]
    edges = [(0, i) for i in range(1, len(nodes))] + [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 1)]
    lines = []
    for k, (a, b) in enumerate(edges):
        _, ax, ay, _ = nodes[a]
        _, bx, by, _ = nodes[b]
        hub = a == 0
        lines.append(f'<line x1="{ax}" y1="{ay}" x2="{bx}" y2="{by}" class="{"e" if hub else "e2"}"/>')
        if hub:
            lines.append(f'<line x1="{ax}" y1="{ay}" x2="{bx}" y2="{by}" class="flow" style="animation-delay:-{k*0.37:.2f}s"/>')
    circles = []
    for k, (label, x, y, r) in enumerate(nodes):
        main = k == 0
        r = max(r, len(label) * 3.6 + 6)
        circles.append(f'''<g class="node" style="animation-delay:-{k*0.5}s">
      <circle cx="{x}" cy="{y}" r="{r+10}" fill="url(#halo)" opacity="{0.9 if main else 0.5}"/>
      <circle cx="{x}" cy="{y}" r="{r}" fill="#0b1220" stroke="url(#gname)" stroke-width="{2.5 if main else 1.6}"/>
      <text x="{x}" y="{y+4}" text-anchor="middle" class="{"nl" if main else "ns"}">{label}</text></g>''')

    chips = [("🤖 Agent Builder", "#22d3ee"), ("🌙 Night-owl Coder", "#a78bfa"), ("☕ Coffee → Code", "#f472b6"), ("🐛 Bug Hunter", "#fbbf24")]
    chip_svg, cxp = [], x0
    for text, col in chips:
        w = len(text) * 7.6 + 26
        chip_svg.append(f'<g transform="translate({cxp:.0f},262)"><rect width="{w:.0f}" height="30" rx="15" fill="{col}" fill-opacity=".1" stroke="{col}" stroke-opacity=".55"/>'
                        f'<text x="{w/2:.0f}" y="20" text-anchor="middle" class="chip" fill="{col}">{escape(text)}</text></g>')
        cxp += w + 12

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#070b14"/><stop offset=".55" stop-color="#0c1428"/><stop offset="1" stop-color="#160c2e"/>
    </linearGradient>
    <linearGradient id="gname" x1="0" y1="0" x2="1" y2="0" gradientUnits="objectBoundingBox" spreadMethod="reflect">
      <stop offset="0" stop-color="#22d3ee"/><stop offset=".5" stop-color="#a78bfa"/><stop offset="1" stop-color="#f472b6"/>
      <animateTransform attributeName="gradientTransform" type="translate" values="-1 0;1 0;-1 0" dur="8s" repeatCount="indefinite"/>
    </linearGradient>
    <radialGradient id="halo"><stop offset="0" stop-color="#7c3aed" stop-opacity=".55"/><stop offset="1" stop-color="#7c3aed" stop-opacity="0"/></radialGradient>
    <radialGradient id="blob1"><stop offset="0" stop-color="#06b6d4" stop-opacity=".35"/><stop offset="1" stop-color="#06b6d4" stop-opacity="0"/></radialGradient>
    <radialGradient id="blob2"><stop offset="0" stop-color="#8b5cf6" stop-opacity=".35"/><stop offset="1" stop-color="#8b5cf6" stop-opacity="0"/></radialGradient>
    <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#94a3b8" stroke-opacity=".07"/></pattern>
    <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff" stop-opacity=".1"/></linearGradient>
    <mask id="gm"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
    <clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  </defs>
  <style>
    .hello{{font:500 18px {MONO};fill:#64748b}}
    .name{{font:800 66px {SANS};letter-spacing:-1.5px}}
    .role{{font:600 {fs}px {MONO};fill:#e2e8f0}}
    .chip{{font:600 13px {SANS}}}
    .nl{{font:800 15px {MONO};fill:#f8fafc}}
    .ns{{font:600 11px {MONO};fill:#cbd5e1}}
    .e{{stroke:#334155;stroke-width:1.4}}
    .e2{{stroke:#1e293b;stroke-width:1;stroke-dasharray:3 5}}
    .flow{{stroke:#22d3ee;stroke-width:2.2;stroke-linecap:round;stroke-dasharray:6 120;animation:flow 2.6s linear infinite}}
    .node{{animation:pulse 3s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
    .b1{{animation:drift1 14s ease-in-out infinite}}
    .b2{{animation:drift2 18s ease-in-out infinite}}
    .scan{{animation:scan 6s linear infinite}}
    @keyframes flow{{to{{stroke-dashoffset:-126}}}}
    @keyframes pulse{{50%{{transform:scale(1.06)}}}}
    @keyframes drift1{{50%{{transform:translate(120px,40px)}}}}
    @keyframes drift2{{50%{{transform:translate(-140px,-30px)}}}}
    @keyframes scan{{from{{transform:translateY(-40px)}}to{{transform:translateY({H+40}px)}}}}
  </style>
  <g clip-path="url(#frame)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    <rect width="{W}" height="{H}" fill="url(#grid)" mask="url(#gm)"/>
    <circle class="b1" cx="180" cy="60" r="260" fill="url(#blob1)"/>
    <circle class="b2" cx="1000" cy="300" r="300" fill="url(#blob2)"/>
    <rect class="scan" width="{W}" height="2" fill="#22d3ee" opacity=".08"/>
    {"".join(lines)}
    {"".join(circles)}
    <text x="{x0}" y="92" class="hello">~/dev $ echo "hello, world 👋 I'm"</text>
    <text x="{x0-3}" y="160" class="name" fill="url(#gname)">{name}</text>
    <text x="{x0}" y="{y0}" class="role" fill="#475569" opacity="0">.</text>
    <text x="{x0-22}" y="{y0}" style="font:700 {fs}px {MONO};fill:#22d3ee">›</text>
    {"".join(typing)}
    {"".join(chip_svg)}
  </g>
  <rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="url(#gname)" stroke-opacity=".5"/>
</svg>'''


# ---------------------------------------------------------------- terminal
def terminal(cfg):
    W = 900
    focus = ", ".join(cfg["focus"])
    # (延迟秒, 行内容[(文本, 颜色类)])
    P, K, V, S, D, G, Y, M = "p", "k", "v", "s", "d", "g", "y", "m"
    rows = [
        [("~ ", P), ("$ ", D), ("cat about.yaml", V)],
        [("name", K), (":     ", D), (cfg["name"], S)],
        [("role", K), (":     ", D), ("AI Agent Developer", S)],
        [("based", K), (":    ", D), (cfg["city"], S)],
        [("editor", K), (":   ", D), ("neovim + cursor  ", S), ("# yes, both", D)],
        [("focus", K), (":    ", D), (f"[{focus}]", Y)],
        [("habits", K), (":   ", D), ("[night-owl, rubber-duck debugging, automate everything twice]", Y)],
        [("motto", K), (":    ", D), (f'"{cfg["motto"]}"', S)],
        [],
        [("~ ", P), ("$ ", D), ('agent run --goal "build something cool"', V)],
        [("  ◆ perceive ", M), ("reading context, memory & repo ......... ", D), ("ok", G)],
        [("  ◆ plan     ", M), ("decomposed into 4 sub-tasks ............ ", D), ("ok", G)],
        [("  ◆ act      ", M), ("12 tool calls · 3 MCP servers ......... ", D), ("ok", G)],
        [("  ◆ reflect  ", M), ("self-check passed, evals 98.6% ......... ", D), ("ok", G)],
        [("  ✨ shipped. ", G), ("next task?", V)],
    ]
    lh, top = 26, 70
    H = top + lh * len(rows) + 46
    T = 16.0
    step = 0.55
    out = []
    t = 0.4
    for i, row in enumerate(rows):
        if not row:
            t += 0.2
            continue
        typed = row[0][1] == P
        start = t
        t += 1.1 if typed else step
        p0 = start / T * 100
        p1 = (start + (0.9 if typed else 0.15)) / T * 100
        y = top + i * lh
        tspans = "".join(f'<tspan class="{c}">{escape(s)}</tspan>' for s, c in row)
        if typed:
            # 命令行：用裁剪模拟逐字输入
            chars = sum(len(s) for s, _ in row)
            w = chars * 8.43 + 6
            out.append(f'''<style>@keyframes w{i}{{0%,{p0:.2f}%{{width:0}}{p1:.2f}%,96%{{width:{w:.0f}px}}100%{{width:0}}}}</style>
    <clipPath id="t{i}"><rect x="28" y="{y-18}" height="26" style="animation:w{i} {T}s steps({chars}) infinite"/></clipPath>
    <text x="30" y="{y}" clip-path="url(#t{i})">{tspans}</text>''')
        else:
            out.append(f'''<style>@keyframes o{i}{{0%,{p0:.2f}%{{opacity:0}}{p1:.2f}%,96%{{opacity:1}}100%{{opacity:0}}}}</style>
    <text x="30" y="{y}" style="opacity:0;animation:o{i} {T}s infinite">{tspans}</text>''')
    cy = top + len(rows) * lh
    pe = t / T * 100
    out.append(f'''<style>@keyframes cur{{0%,{pe:.2f}%{{opacity:0}}{pe+0.1:.2f}%,96%{{opacity:1}}100%{{opacity:0}}}}@keyframes blink{{50%{{fill-opacity:0}}}}</style>
    <g style="opacity:0;animation:cur {T}s infinite"><text x="30" y="{cy}"><tspan class="p">~ </tspan><tspan class="d">$ </tspan></text>
    <rect x="59" y="{cy-16}" width="10" height="20" fill="#22d3ee" style="animation:blink 1s step-end infinite"/></g>''')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="tb" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b1020"/><stop offset="1" stop-color="#111827"/></linearGradient>
    <linearGradient id="bd" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#22d3ee"/><stop offset=".5" stop-color="#a78bfa"/><stop offset="1" stop-color="#f472b6"/></linearGradient>
  </defs>
  <style>
    text{{font:500 14px {MONO};white-space:pre}}
    .p{{fill:#22d3ee}} .d{{fill:#475569}} .v{{fill:#e2e8f0}} .k{{fill:#a78bfa}} .s{{fill:#86efac}}
    .y{{fill:#fcd34d}} .g{{fill:#4ade80;font-weight:700}} .m{{fill:#f472b6;font-weight:700}}
    .ttl{{font:600 13px {SANS};fill:#94a3b8}}
  </style>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="url(#tb)" stroke="url(#bd)" stroke-opacity=".6"/>
  <path d="M1 44H{W-1}" stroke="#1f2937"/>
  <circle cx="26" cy="23" r="6.5" fill="#ff5f57"/><circle cx="48" cy="23" r="6.5" fill="#febc2e"/><circle cx="70" cy="23" r="6.5" fill="#28c840"/>
  <text x="{W/2}" y="27" text-anchor="middle" class="ttl">{escape(cfg["github"])}@dev-box — zsh — 90×{len(rows)+2}</text>
  {"".join(out)}
</svg>'''


# -------------------------------------------------------------- agent loop
def agent_loop():
    W, H = 900, 500
    cx, cy, R = 450, 262, 140
    steps = [("Perceive", "感知上下文", -90, "#22d3ee"), ("Plan", "拆解与规划", 0, "#a78bfa"),
             ("Act", "调用工具 / MCP", 90, "#f472b6"), ("Reflect", "反思与评估", 180, "#fbbf24")]
    import math
    nodes = []
    for k, (en, zh, deg, col) in enumerate(steps):
        a = math.radians(deg)
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        # 所有标签放在节点右侧（Reflect 放左侧），避免与标题/页脚重叠
        lx, ly = (x - 34, y + 4) if k == 3 else (x + 34, y - 10 if k == 0 else y + 4)
        anchor = "end" if k == 3 else "start"
        delay = k * 1.5
        nodes.append(f'''<g>
      <circle cx="{x:.1f}" cy="{y:.1f}" r="22" fill="{col}" opacity=".12" class="ring" style="animation-delay:{delay}s"/>
      <circle cx="{x:.1f}" cy="{y:.1f}" r="22" fill="#0b1220" stroke="{col}" stroke-width="2"/>
      <circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{col}" class="lit" style="animation-delay:{delay}s"/>
      <text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" class="en" fill="{col}">{en}</text>
      <text x="{lx:.1f}" y="{ly+18:.1f}" text-anchor="{anchor}" class="zh">{zh}</text></g>''')

    tools = ["Browser", "Code", "Search", "Memory", "MCP", "SQL", "Files", "APIs"]
    orbit = []
    for k, t in enumerate(tools):
        a = math.radians(k * 360 / len(tools) + 22)
        x, y = cx + 76 * math.cos(a), cy + 76 * math.sin(a)
        orbit.append(f'<g transform="translate({x:.1f},{y:.1f})"><g class="counter"><rect x="-25" y="-10" width="50" height="20" rx="10" fill="#111827" stroke="#334155"/>'
                     f'<text y="4" text-anchor="middle" class="tool">{t}</text></g></g>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="lb" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#070b14"/><stop offset="1" stop-color="#140c2a"/></linearGradient>
    <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#22d3ee"/><stop offset=".33" stop-color="#a78bfa"/><stop offset=".66" stop-color="#f472b6"/><stop offset="1" stop-color="#fbbf24"/></linearGradient>
    <radialGradient id="core"><stop offset="0" stop-color="#a78bfa" stop-opacity=".6"/><stop offset="1" stop-color="#a78bfa" stop-opacity="0"/></radialGradient>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <path id="loop" d="M{cx} {cy-R} A{R} {R} 0 1 1 {cx-0.01} {cy-R}"/>
  </defs>
  <style>
    .title{{font:800 20px {SANS};fill:#f1f5f9}}
    .sub{{font:500 12px {MONO};fill:#64748b}}
    .en{{font:800 17px {SANS}}}
    .zh{{font:500 12.5px {SANS};fill:#94a3b8}}
    .tool{{font:600 10px {MONO};fill:#cbd5e1}}
    .core{{font:900 22px {MONO};fill:#fff}}
    .ring{{animation:ping 6s ease-out infinite;transform-box:fill-box;transform-origin:center}}
    .lit{{animation:lit 6s ease-in-out infinite;opacity:.25}}
    .spin{{animation:spin 24s linear infinite;transform-origin:{cx}px {cy}px}}
    .counter{{animation:spin 24s linear infinite reverse}}
    .dash{{animation:dash 1.5s linear infinite}}
    @keyframes ping{{0%{{transform:scale(1);opacity:.5}}20%{{transform:scale(2.4);opacity:0}}100%{{opacity:0}}}}
    @keyframes lit{{0%,22%{{opacity:1}}30%,100%{{opacity:.25}}}}
    @keyframes spin{{to{{transform:rotate(360deg)}}}}
    @keyframes dash{{to{{stroke-dashoffset:-24}}}}
  </style>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="16" fill="url(#lb)" stroke="#1e293b"/>
  <text x="32" y="44" class="title">How my agents think</text>
  <text x="32" y="66" class="sub">while (!done) {{ perceive(); plan(); act(); reflect(); }}</text>
  <text x="32" y="{H-24}" class="sub">tools orbit the model · context flows around the loop</text>
  <circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="url(#ring)" stroke-opacity=".35" stroke-width="2"/>
  <circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="url(#ring)" stroke-width="2" stroke-dasharray="4 8" class="dash"/>
  <circle cx="{cx}" cy="{cy}" r="96" fill="none" stroke="#1e293b" stroke-dasharray="2 6"/>
  <circle cx="{cx}" cy="{cy}" r="60" fill="url(#core)"/>
  <g class="spin">{"".join(orbit)}</g>
  <circle cx="{cx}" cy="{cy}" r="30" fill="#0b1220" stroke="url(#ring)" stroke-width="2.5"/>
  <text x="{cx}" y="{cy+8}" text-anchor="middle" class="core">LLM</text>
  {"".join(nodes)}
  <g filter="url(#glow)">
    <circle r="7" fill="#fff"><animateMotion dur="6s" repeatCount="indefinite" rotate="auto"><mpath href="#loop"/></animateMotion></circle>
    <circle r="4" fill="#22d3ee" opacity=".6"><animateMotion dur="6s" begin="-0.12s" repeatCount="indefinite"><mpath href="#loop"/></animateMotion></circle>
    <circle r="2.5" fill="#a78bfa" opacity=".4"><animateMotion dur="6s" begin="-0.24s" repeatCount="indefinite"><mpath href="#loop"/></animateMotion></circle>
  </g>
</svg>'''


# -------------------------------------------------------------------- htop
def htop(cfg):
    W = 900
    user = escape(cfg["github"].lower()[:9])
    procs = [  # pid, cpu 数值序列(%), mem, 时间, 命令, 颜色
        (1,    [97, 92, 99, 95, 97],  "∞",    "24/7",   "coffee.exe --refill --no-limit", "#f472b6"),
        (42,   [78, 88, 70, 84, 78],  "3.1G", "∞:∞",    "agent-runtime --mcp --tools=all", "#22d3ee"),
        (1337, [55, 72, 61, 80, 55],  "1.2G", "02:47",  "debug --method=rubber-duck 🦆", "#a78bfa"),
        (2077, [30, 46, 38, 52, 30],  "640M", "88:00",  "side-project-17 --status=wip", "#fbbf24"),
        (8080, [22, 35, 28, 18, 22],  "512M", "12:34",  "learn --topic=llm-evals,long-horizon", "#4ade80"),
        (404,  [2, 1, 3, 1, 2],       "8K",   "00:00",  "sleep  # process not found", "#64748b"),
    ]
    top, lh = 196, 30
    H = top + lh * len(procs) + 70
    bx, bw = 210, 120  # CPU 条形图位置/宽度

    rows = []
    for k, (pid, cpu, mem, tm, cmd, col) in enumerate(procs):
        y = top + k * lh
        widths = ";".join(f"{bw * c / 100:.0f}" for c in cpu)
        dur = 3 + k * 0.7
        sel = k == 1
        rows.append(f"""
    {'<rect x="14" y="%d" width="%d" height="%d" fill="#22d3ee" fill-opacity=".1"/>' % (y - 20, W - 28, lh - 2) if sel else ''}
    <text x="30" y="{y}" class="pid">{pid:>5}</text><text x="92" y="{y}" class="usr">{user}</text>
    <rect x="{bx}" y="{y-13}" width="{bw}" height="12" rx="3" fill="#1e293b"/>
    <rect x="{bx}" y="{y-13}" height="12" rx="3" fill="{col}" width="{bw*cpu[0]/100:.0f}">
      <animate attributeName="width" values="{widths}" dur="{dur:.1f}s" repeatCount="indefinite" calcMode="spline" keySplines="{';'.join(['.4 0 .6 1']*(len(cpu)-1))}"/></rect>
    <text x="{bx+bw+14}" y="{y}" class="num" fill="{col}">{max(cpu)}%</text>
    <text x="440" y="{y}" class="dim" text-anchor="end">{escape(mem)}</text>
    <text x="462" y="{y}" class="dim">{tm}</text>
    <text x="530" y="{y}" class="cmd" fill="{'#f8fafc' if sel else '#cbd5e1'}">{escape(cmd)}</text>""")

    # 顶部 CPU 核心条（htop 风格的 [|||||   ] ）
    meters = []
    for k in range(4):
        x, y = 30 + (k % 2) * 245, 76 + (k // 2) * 26
        seq = [[60, 85, 70, 95, 60], [40, 75, 55, 65, 40], [80, 60, 90, 70, 80], [25, 55, 35, 60, 25]][k]
        vals = ";".join(f"{180 * v / 100:.0f}" for v in seq)
        meters.append(f"""<text x="{x}" y="{y}" class="lbl">{k}</text><text x="{x+16}" y="{y}" class="br">[</text>
    <rect x="{x+28}" y="{y-11}" width="180" height="12" fill="#1e293b"/>
    <rect x="{x+28}" y="{y-11}" height="12" fill="url(#bars)" width="{180*seq[0]/100:.0f}">
      <animate attributeName="width" values="{vals}" dur="{2.4 + k*0.6:.1f}s" repeatCount="indefinite"/></rect>
    <rect x="{x+28}" y="{y-11}" width="180" height="12" fill="url(#tick)"/>
    <text x="{x+212}" y="{y}" class="br">]</text>""")
    info = [("Tasks:", "17 side projects · ", "3 shipped"), ("Load avg:", "☕ ☕ ☕", ""), ("Uptime:", "02:47 AM, ", "still coding")]
    info_svg = "".join(
        f'<text x="560" y="{76 + i*26}"><tspan class="lbl">{a}</tspan><tspan dx="8" class="v">{escape(b)}</tspan><tspan class="hl">{escape(c)}</tspan></text>'
        for i, (a, b, c) in enumerate(info))

    keys = [("F1", "Help"), ("F2", "Refactor"), ("F3", "Search"), ("F5", "Tree"), ("F6", "SortBy☕"), ("F9", "Kill bugs"), ("F10", "Ship")]
    kx, ksvg = 20, []
    for k, lbl in keys:
        ksvg.append(f'<text x="{kx}" y="{H-22}" class="fk">{k}</text>'
                    f'<rect x="{kx+len(k)*8.4+2}" y="{H-37}" width="{len(lbl)*8.4+10}" height="20" fill="#22d3ee" fill-opacity=".85"/>'
                    f'<text x="{kx+len(k)*8.4+7}" y="{H-22}" class="fl">{escape(lbl)}</text>')
        kx += len(k) * 8.4 + len(lbl) * 8.4 + 22

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="hb" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b1020"/><stop offset="1" stop-color="#111827"/></linearGradient>
    <linearGradient id="bars" x1="0" x2="1"><stop offset="0" stop-color="#4ade80"/><stop offset=".6" stop-color="#fbbf24"/><stop offset="1" stop-color="#f43f5e"/></linearGradient>
    <pattern id="tick" width="5" height="12" patternUnits="userSpaceOnUse"><rect width="3" height="12" fill="#000" fill-opacity=".45"/></pattern>
    <linearGradient id="hbd" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#22d3ee"/><stop offset=".5" stop-color="#a78bfa"/><stop offset="1" stop-color="#f472b6"/></linearGradient>
  </defs>
  <style>
    text{{font:500 14px {MONO};white-space:pre}}
    .ttl{{font:600 13px {SANS};fill:#94a3b8}}
    .lbl{{fill:#22d3ee;font-weight:700}} .br{{fill:#64748b;font-weight:700}} .v{{fill:#e2e8f0}} .hl{{fill:#4ade80;font-weight:700}}
    .hdr{{fill:#0b1020;font-weight:800}} .pid{{fill:#94a3b8}} .usr{{fill:#a78bfa}} .num{{font-weight:700}} .dim{{fill:#64748b}}
    .cmd{{font-weight:600}} .fk{{fill:#e2e8f0;font-weight:700}} .fl{{fill:#0b1020;font-weight:700}}
  </style>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="url(#hb)" stroke="url(#hbd)" stroke-opacity=".6"/>
  <path d="M1 44H{W-1}" stroke="#1f2937"/>
  <circle cx="26" cy="23" r="6.5" fill="#ff5f57"/><circle cx="48" cy="23" r="6.5" fill="#febc2e"/><circle cx="70" cy="23" r="6.5" fill="#28c840"/>
  <text x="{W/2}" y="27" text-anchor="middle" class="ttl">htop — {user}@brain</text>
  {"".join(meters)}
  {info_svg}
  <text x="30" y="128"><tspan class="lbl">Mem</tspan><tspan dx="4" class="br">[</tspan><tspan fill="#4ade80">||||||||||||||||||</tspan><tspan fill="#a78bfa">||||||||</tspan><tspan fill="#334155">||||||||</tspan><tspan class="br">]</tspan><tspan dx="10" class="dim">ctx 76%</tspan></text>
  <rect x="14" y="{top-42}" width="{W-28}" height="24" fill="#4ade80"/>
  <text x="30" y="{top-25}" class="hdr">  PID</text><text x="92" y="{top-25}" class="hdr">USER</text><text x="{bx}" y="{top-25}" class="hdr">CPU%</text><text x="440" y="{top-25}" class="hdr" text-anchor="end">MEM</text><text x="462" y="{top-25}" class="hdr">TIME+</text><text x="530" y="{top-25}" class="hdr">COMMAND</text>
  {"".join(rows)}
  {"".join(ksvg)}
</svg>"""


# ----------------------------------------------------------------- divider
def divider():
    W, H = 1200, 24
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs><linearGradient id="g" x1="0" x2="1" spreadMethod="reflect">
    <stop offset="0" stop-color="#22d3ee" stop-opacity="0"/><stop offset=".3" stop-color="#22d3ee"/><stop offset=".6" stop-color="#a78bfa"/><stop offset=".85" stop-color="#f472b6"/><stop offset="1" stop-color="#f472b6" stop-opacity="0"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="-0.5 0;0.5 0;-0.5 0" dur="6s" repeatCount="indefinite"/></linearGradient></defs>
  <rect x="0" y="11" width="{W}" height="2" rx="1" fill="url(#g)"/>
  <circle cy="12" r="3.5" fill="#fff"><animate attributeName="cx" values="0;{W};0" dur="6s" repeatCount="indefinite"/></circle>
</svg>'''


# ------------------------------------------------------------------ README
def readme(cfg):
    u = cfg["github"]
    contact = []
    if cfg["email"]:
        contact.append(f'<a href="mailto:{cfg["email"]}"><img src="https://img.shields.io/badge/Email-Say%20hi-22d3ee?style=for-the-badge&logo=gmail&logoColor=white&labelColor=0d1117"/></a>')
    if cfg["blog"]:
        contact.append(f'<a href="{cfg["blog"]}"><img src="https://img.shields.io/badge/Blog-Read-a78bfa?style=for-the-badge&logo=hashnode&logoColor=white&labelColor=0d1117"/></a>')
    contact_html = ("\n  " + "\n  ".join(contact)) if contact else ""

    def badge(label, color, logo, logo_color="white"):
        return f'<img src="https://img.shields.io/badge/{label}-{color}?style=flat-square&logo={logo}&logoColor={logo_color}&labelColor=0d1117"/>'

    ai_badges = " ".join([
        badge("Claude", "D97757", "anthropic"), badge("OpenAI", "412991", "openai"),
        badge("MCP", "22d3ee", "modelcontextprotocol"), badge("LangGraph", "1C3C3C", "langchain"),
        badge("LlamaIndex", "a78bfa", "llamaindex"), badge("vLLM", "f472b6", "vllm"),
        badge("Ollama", "334155", "ollama"), badge("Hugging%20Face", "FFD21E", "huggingface", "black"),
    ])

    return f'''<!-- Generated by build.py — 修改 CONFIG 后重新运行即可 -->

<p align="center">
  <img src="./assets/banner.svg" width="100%" alt="{cfg["name"]} · AI Agent Developer"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/☕_Powered_by-Coffee-22d3ee?style=for-the-badge&labelColor=0d1117"/>
  <img src="https://img.shields.io/badge/🤖_Building-AI_Agents-a78bfa?style=for-the-badge&labelColor=0d1117"/>
  <img src="https://komarev.com/ghpvc/?username={u}&label=Profile%20views&color=f472b6&style=for-the-badge&labelColor=0d1117"/>{contact_html}
</p>

<img src="./assets/divider.svg" width="100%"/>

## 🧑‍💻 About Me

<p align="center">
  <img src="./assets/terminal.svg" width="88%" alt="whoami"/>
</p>

- 🤖 全职 **AI Agent** 开发 —— 让大模型不只会聊天，还能真正把事情办完
- 🧠 关注 **Tool Use / MCP / Multi-Agent 协作 / RAG / Agent 评测**，喜欢把复杂流程拆成可靠的自动化
- 🛠️ 从原型到生产：Prompt 与上下文工程、工具编排、记忆系统、可观测性与 Evals 全链路
- 🌱 正在探索：长程任务规划、Agent 自我反思与纠错、人机协作的工作流
- 🌙 夜猫子型选手：最好的代码写于凌晨两点，最难查的 bug 也是
- 🦆 信奉小黄鸭调试法；同一件事手动做第二遍之前，一定先写个脚本
- ⌨️ 键盘党 · 终端重度用户 · 坚信 *"It works on my machine"* 不是终点
- 💬 想聊 Agent、LLM 应用落地，或者一起做点酷东西？随时找我 👋

<img src="./assets/divider.svg" width="100%"/>

## 🔄 How I Build Agents

<p align="center">
  <img src="./assets/agent-loop.svg" width="88%" alt="perceive → plan → act → reflect"/>
</p>

<table>
<tr>
<td width="50%" valign="top">

### 🧩 Agent Engineering
- 单 Agent / 多 Agent 编排与任务拆解
- Function Calling · MCP Server 开发
- 长短期记忆、上下文压缩与检索

</td>
<td width="50%" valign="top">

### 🚀 Production Ready
- Agent 评测体系 & 回归测试
- Tracing / 可观测性 / 成本控制
- 安全护栏、人工审批与兜底策略

</td>
</tr>
</table>

<img src="./assets/divider.svg" width="100%"/>

## ⚙️ Currently Running

<p align="center">
  <img src="./assets/htop.svg" width="88%" alt="htop — what's running in my head"/>
</p>

<img src="./assets/divider.svg" width="100%"/>

## 🛠️ Tech Stack

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,ts,go,rust,react,nextjs,tailwind,fastapi,nodejs&theme=dark&perline=9"/>
  <br/>
  <img src="https://skillicons.dev/icons?i=postgres,redis,mongodb,docker,kubernetes,linux,git,githubactions,vscode&theme=dark&perline=9"/>
</p>

<p align="center">
  {ai_badges}
</p>

<img src="./assets/divider.svg" width="100%"/>

## 📊 GitHub Stats

<p align="center">
  <img height="170" src="https://github-readme-stats.vercel.app/api?username={u}&show_icons=true&theme=tokyonight&hide_border=true&bg_color=0d1117&title_color=22d3ee&icon_color=a78bfa&text_color=cbd5e1&include_all_commits=true&count_private=true"/>
  <img height="170" src="https://github-readme-stats.vercel.app/api/top-langs/?username={u}&layout=compact&theme=tokyonight&hide_border=true&bg_color=0d1117&title_color=22d3ee&text_color=cbd5e1&langs_count=8"/>
</p>

<p align="center">
  <img width="88%" src="https://streak-stats.demolab.com?user={u}&theme=tokyonight&hide_border=true&background=0d1117&ring=a78bfa&fire=f472b6&currStreakLabel=22d3ee"/>
</p>

<p align="center">
  <img width="100%" src="https://github-readme-activity-graph.vercel.app/graph?username={u}&bg_color=0d1117&color=a78bfa&line=22d3ee&point=f472b6&area=true&area_color=22d3ee&hide_border=true&custom_title=Contribution%20Graph"/>
</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/{u}/{u}/output/github-snake-dark.svg"/>
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/{u}/{u}/output/github-snake.svg"/>
    <img alt="snake eating my contributions" src="https://raw.githubusercontent.com/{u}/{u}/output/github-snake-dark.svg"/>
  </picture>
</p>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=600&size=18&duration=3500&pause=800&color=A78BFA&center=true&vCenter=true&width=600&lines=Thanks+for+stopping+by+%F0%9F%91%8B;Let+agents+do+the+boring+parts.;git+commit+-m+%22see+you+in+the+next+PR+%F0%9F%9A%80%22" alt="footer"/>
</p>
'''


SNAKE = '''name: Generate snake animation

on:
  schedule:
    - cron: "0 */12 * * *"
  workflow_dispatch:
  push:
    branches: [main]

permissions:
  contents: write

jobs:
  generate:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: Platane/snk@v3
        with:
          github_user_name: ${{ github.repository_owner }}
          outputs: |
            dist/github-snake.svg
            dist/github-snake-dark.svg?palette=github-dark&color_snake=#a78bfa&color_dots=#161b22,#0e4429,#006d32,#26a641,#39d353
      - uses: crazy-max/ghaction-github-pages@v4
        with:
          target_branch: output
          build_dir: dist
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
'''


def main():
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "banner.svg").write_text(banner(CONFIG), encoding="utf-8")
    (ASSETS / "terminal.svg").write_text(terminal(CONFIG), encoding="utf-8")
    (ASSETS / "agent-loop.svg").write_text(agent_loop(), encoding="utf-8")
    (ASSETS / "htop.svg").write_text(htop(CONFIG), encoding="utf-8")
    (ASSETS / "divider.svg").write_text(divider(), encoding="utf-8")
    (ROOT / "README.md").write_text(readme(CONFIG), encoding="utf-8")
    wf = ROOT / ".github" / "workflows"
    wf.mkdir(parents=True, exist_ok=True)
    (wf / "snake.yml").write_text(SNAKE, encoding="utf-8")
    print("✓ README.md + assets/ + .github/workflows/snake.yml 已生成")


if __name__ == "__main__":
    main()
