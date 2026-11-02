# -*- coding: utf-8 -*-
"""Windows 启动入口: 用 python-3.9.10-embed 运行本目录下的 PPOCRLabel。

用法:
    D:\\ocr\\OCRTrain\\python-3.9.10-embed\\python.exe run_ppocrlabel_win.py --lang ch --gpu false

说明:
    embed 版 Python 使用 python39._pth, 处于 isolated 模式, 不会把脚本所在目录加入
    sys.path, 因此这里手动插入, 否则 import PPOCRLabel 会失败。
"""
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from PPOCRLabel.PPOCRLabel import main

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
