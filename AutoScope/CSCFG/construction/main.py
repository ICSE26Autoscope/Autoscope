#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_icfgs.py
==============

1.  For every sub-folder (i.e., service) under  ``msapp-src``
    └── call **extractAPI.jar** to dump its Soot-style API list.

2.  For every <service>.txt produced in **APIList/**
    └── find the corresponding JAR in **msapp-bin/** and
        call **CSCFG.jar**  ➜  outputs  <service>.dot  into **CSCFGs/**.
"""
import os
import subprocess
from pathlib import Path
from shutil import rmtree

# ----------  Path layout (relative to project root) ----------
ROOT        = Path(__file__).resolve().parents[1]        # …/AutoScope/CSCFG
SRC_DIR     = ROOT / "msapp-src"
BIN_DIR     = ROOT / "msapp-bin"
API_DIR     = ROOT / "APIList"
ICFG_DIR    = ROOT / "CSCFGs"
JAR_DIR     = ROOT / "lib"
EXTRACT_JAR = JAR_DIR / "extractAPI.jar"
ICFG_JAR    = JAR_DIR / "CSCFG.jar"
JAVA        = os.getenv("JAVA", "java")                  # honour $JAVA if set

# ----------  Helper utilities ----------
def sh(cmd, cwd: Path = ROOT) -> None:
    """
    Run *cmd* inside *cwd* using os.system.
    Raises RuntimeError on non-zero exit code.
    """
    full_cmd = " ".join(map(str, cmd))
    exit_code = os.system(f'cd "{cwd}" && {full_cmd}')
    if exit_code != 0:
        raise RuntimeError(f"Command failed ({exit_code}): {full_cmd}")


def locate_service_jar(service:str) -> Path:
    """Heuristically locate the compiled JAR that belongs to *service*."""
    candidates = list(BIN_DIR.glob(f"{service}*.jar"))
    return None if not candidates else sorted(candidates)[0]   # shortest / first match


# ----------  Main workflow ----------
def main():
    # Fresh output folders
    API_DIR.mkdir(exist_ok=True)
    if ICFG_DIR.exists():
        rmtree(ICFG_DIR)      # start clean to avoid mixing old runs
    ICFG_DIR.mkdir()

    # 1) Generate API lists
    for svc_path in sorted(p for p in SRC_DIR.iterdir() if p.is_dir()):
        svc = svc_path.name
        print(f"[EXTRACT] {svc}")
        api_out = API_DIR / f"{svc}.txt"
        cmd = [JAVA, "-jar", str(EXTRACT_JAR), str(svc_path)]
        # extractAPI.jar writes <service>.txt into current working dir
        sh(cmd, cwd=API_DIR)
        if not api_out.exists():
            raise FileNotFoundError(f"{api_out} not produced by extractAPI")
    print("✓ API extraction complete.\n")

    # 2) Build CSCFGs
    for api_file in sorted(API_DIR.glob("*.txt")):
        svc = api_file.stem
        jar = locate_service_jar(svc)
        if jar is None:
            print(f"[WARN] No JAR found for {svc}, skip.")
            continue

        dot_out = ICFG_DIR / f"{svc}.dot"
        print(f"[CSCFG] {svc}  →  {dot_out.name}")
        cmd = [
            JAVA, "-jar", str(ICFG_JAR),
            str(jar), str(api_file), str(dot_out)
        ]
        sh(cmd)
    print("\n✓ All CSCFGs generated in:", ICFG_DIR)

if __name__ == "__main__":
    main()
