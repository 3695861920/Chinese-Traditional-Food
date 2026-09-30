# -*- coding: utf-8 -*-
"""
在反编译的 Minecraft / NeoForge 源码里查东西。

    python tools/mc_source.py find "GENERIC_EAT"                 # 全文搜
    python tools/mc_source.py show net/minecraft/sounds/SoundEvents   # 打印某个类
    python tools/mc_source.py grep "class SoundEvents" -C 2       # 带上下文

为什么需要它：本仓库一度无法编译，所有 API 只能靠官方文档 + GitHub 搜签名去猜。
现在 build/moddev/artifacts 下有反编译好的 *-sources.jar，
这里就是**权威依据**，能用就别猜。

数据来源（首次 `gradlew build` 后生成）：
    build/moddev/artifacts/minecraft-patched-<ver>-sources.jar
"""

import os
import re
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACTS = os.path.join(ROOT, "build", "moddev", "artifacts")


def project_neo_version():
    """从 gradle.properties 读本项目使用的 NeoForge 版本，避免查到别的版本的 API。"""
    props = os.path.join(ROOT, "gradle.properties")
    if os.path.isfile(props):
        for line in open(props, encoding="utf-8"):
            line = line.strip()
            if line.startswith("neo_version="):
                return line.split("=", 1)[1].strip()
    return None


def find_sources_jars():
    """返回要搜索的源码 jar 列表：Minecraft 已反编译源码 + NeoForge 源码。

    只取与 gradle.properties 中 neo_version 一致的那个 NeoForge 版本 ——
    缓存里往往同时存在 26.1.x / 26.2.x，查错版本会得到不存在的 API。
    """
    jars = []
    if os.path.isdir(ARTIFACTS):
        jars += [os.path.join(ARTIFACTS, f) for f in os.listdir(ARTIFACTS)
                 if f.endswith("-sources.jar")]

    wanted = project_neo_version()
    gradle_cache = os.path.join(os.path.expanduser("~"), ".gradle", "caches",
                               "modules-2", "files-2.1", "net.neoforged", "neoforge")
    if os.path.isdir(gradle_cache):
        versions = sorted(os.listdir(gradle_cache), reverse=True)
        if wanted and wanted in versions:
            versions = [wanted]
        for ver in versions:
            found = []
            for base, _dirs, files in os.walk(os.path.join(gradle_cache, ver)):
                for f in files:
                    if f.endswith("-sources.jar"):
                        found.append(os.path.join(base, f))
            if found:
                jars += found
                break

    if not jars:
        sys.exit("找不到源码 jar —— 请先跑一次 gradlew build")
    return jars


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    mode = sys.argv[1]
    needle = sys.argv[2]
    context = 2
    if "-C" in sys.argv:
        context = int(sys.argv[sys.argv.index("-C") + 1])

    jars = find_sources_jars()
    for j in jars:
        print("# source: %s" % os.path.relpath(j, ROOT) if j.startswith(ROOT) else "# source: %s" % j)
    hits = 0

    for jar in jars:
        with zipfile.ZipFile(jar) as zf:
            names = [n for n in zf.namelist() if n.endswith(".java")]

            if mode == "show":
                target = needle.strip("/")
                if not target.endswith(".java"):
                    target += ".java"
                match = [n for n in names if n.endswith(target)]
                if not match:
                    continue
                print("# file: %s" % match[0])
                print(zf.read(match[0]).decode("utf-8", "replace"))
                return

            if mode not in ("find", "grep"):
                sys.exit("未知模式: %s（可用 find / show / grep）" % mode)

            pattern = re.compile(needle if mode == "grep" else re.escape(needle))
            for name in names:
                try:
                    text = zf.read(name).decode("utf-8", "replace")
                except Exception:                 # noqa: BLE001
                    continue
                lines = text.splitlines()
                for i, line in enumerate(lines):
                    if not pattern.search(line):
                        continue
                    hits += 1
                    if hits > 40:
                        return
                    print("\n== %s:%d" % (name, i + 1))
                    lo = max(0, i - context)
                    hi = min(len(lines), i + context + 1)
                    for j in range(lo, hi):
                        mark = ">>" if j == i else "  "
                        print("%s %5d  %s" % (mark, j + 1, lines[j]))

    if mode == "show":
        sys.exit("找不到类: %s" % needle)


if __name__ == "__main__":
    main()
