import sys

from cx_Freeze import Executable, setup

VERSION = "1.0.0.0"
TITLE = "GSMdtTools"

if __name__ == "__main__":
    # base = "Win32GUI" if sys.platform == "win32" else "gui"

    executables = [
        Executable(
            script="main.py",
            base="console",
            target_name=TITLE.replace(" ", "-"),
            copyright="Copyright (C) 2026 veydzh3r",
            # icon="assets/icon.ico",
            # shortcut_name=TITLE,
            # shortcut_dir="ProgramMenuFolder",
        )
    ]

    build_exe_options = {
        "packages": ["src"],
        "includes": [
            "src.gs",
            "src.utils",
        ],
        "excludes": ["tkinter", "unittest", "zoneinfo"],
        "include_files": [
            ("scripts", "")
        ],
        "zip_filename": "lib/library.zip",
        "zip_include_packages": ["encodings", "PySide6", "shiboken6"],
    }

    setup(
        name=TITLE.replace(" ", "-"),
        version=VERSION,
        options={"build_exe": build_exe_options},
        executables=executables,
        # url="https://github.com/Veydzher/i2loc-manager",
    )
