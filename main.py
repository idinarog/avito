#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Точка входа в приложение Avito Commander
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.app import Application


def main():
    """Главная функция"""
    print("""
    ╔═══════════════════════════════════════════╗
    ║     Avito Commander v0.2.0              ║
    ║     Управление объявлениями Avito       ║
    ╚═══════════════════════════════════════════╝
    """)
    
    app = Application()
    app.init_app()
    sys.exit(app.start())


if __name__ == "__main__":
    main()
