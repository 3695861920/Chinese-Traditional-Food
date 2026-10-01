# -*- coding: utf-8 -*-
"""扫 MC 日志，看有没有资源/注册类报错。仅开发期用。

    python tools/_logcheck.py                 # 自动取 run/logs 下最新的日志
    python tools/_logcheck.py <path>          # 指定日志

为什么不看 `--console=plain | Out-File` 那份：Gradle 的控制台输出被削过，
只有几百行；真正的全量日志在 `run/logs/latest.log`（上万行），
"Missing model""Couldn't parse"这类关键行只在那边有。
"""

import glob
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PATTERNS = [
    "Missing model", "Missing texture", "Unable to load model",
    "Couldn't parse", "Unknown registry", "Missing item model",
    "texture does not exist", "Failed to load", "recipe", "Recipes",
    "Exception", "Caused by", "ERROR",
]


def newest_log():
    logs = glob.glob(os.path.join(ROOT, "run", "logs", "*.log"))
    if not logs:
        return None
    return max(logs, key=os.path.getmtime)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else newest_log()
    if path is None or not os.path.exists(path):
        print("找不到日志")
        return 1
    print("日志:", os.path.basename(path))
    lines = io.open(path, encoding="utf-8",
                    errors="replace").read().splitlines()
    print("行数:", len(lines))
    for pat in PATTERNS:
        hits = [l.strip() for l in lines if pat in l]
        if hits:
            print("\n=== [%s] %d 处 ===" % (pat, len(hits)))
            for h in hits[-6:]:
                print("   ", h[:230])
    print("\n--- 末尾 ---")
    for l in lines[-6:]:
        print(l[:230])
    return 0


if __name__ == "__main__":
    sys.exit(main())
