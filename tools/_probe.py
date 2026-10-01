# -*- coding: utf-8 -*-
"""临时：查 Strippable 的 JSON 结构 + WoodType.OAK + LOGGER。用完删。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mc_source as M


def show(pat, ctx=8, limit=3):
    print("\n########", pat)
    M.grep_cli(pat, ctx, limit) if hasattr(M, "grep_cli") else None


print("=== Strippable ===")
print(M.show("net/neoforged/neoforge/registries/datamaps/builtin/Strippable")
      if hasattr(M, "show") else "no show()")
