# PPOCRLabel Windows / embed 环境运行说明

本目录原为 Jetson（Linux + Python 3.8 系统 PyQt5 + Python 3.10 PaddleOCR 子进程）上的
定制版备份。现已在 **Windows + `python-3.9.10-embed`** 下跑通，并且**不再安装 PaddlePaddle**：
OCR 改用 PP-OCRv5 的 **ONNX 模型 + onnxruntime**，与 GUI 共用同一个解释器。

## 1. 怎么启动

双击**上层目录的 `1-启动PPOCRLabel标注工具.bat`**（启动器与程序本体分开放置；脚本会自动查找同层/上层的
`python-3.9.10-embed`，整包拷到别的机器也能直接用），或在本目录命令行：

```
python-3.9.10-embed\python.exe run_ppocrlabel_win.py --lang ch --gpu false
```

| 文件 | 位置 | 作用 |
| --- | --- | --- |
| `1-启动PPOCRLabel标注工具.bat` | **上一层目录** | 日常启动（`pythonw.exe`，无控制台；日志写到它同目录的 `ppocrlabel.log`） |
| `run_ppocrlabel_win.py` | 本目录 | 真正的入口脚本（embed 版 Python 是 isolated 模式，需手动加 `sys.path`） |
| `tools/fetch_ppocrv5_onnx_models.py` | 本目录 | 重新下载/校验 ONNX 模型（含 IR 版本修正） |
| `PPOCRLabel/models/ppocrv5/` | 本目录 | 3 个模型文件，共约 13 MB |

> 启动器会把工作目录切到本目录再拉起进程，所以模型/资源仍按工具目录解析。

依赖（已安装在 `python-3.9.10-embed`）：`PyQt5 5.15.10`、`xlrd 2.0.1`、`rapidocr 3.10.0`、
`pyclipper`、`omegaconf`、`colorlog`、`antlr4-python3-runtime`，其余用环境里原有的
`onnxruntime 1.17.1` / `opencv 4.9.0` / `numpy 1.24.3`。

> 安装 `rapidocr` 时用了 `--no-deps`，避免它把环境里的 `opencv-python` 换成
> `opencv-python-headless`（会顶掉 `cv2`，影响同环境下的 ultralytics 等工具）。

## 1.1 便携部署（拷贝到其它机器）

推荐目录结构（`python-3.9.10-embed` 与工具同层，两个启动器都在外层）：

```
<任意目录>\
├─ python-3.9.10-embed\          环境（约 1.05 GB）
├─ 1-启动PPOCRLabel标注工具.bat    启动器
├─ PPOCRLabel_2026\              程序本体（PPOCRLabel\、models\、tools\、run_ppocrlabel_win.py）
├─ 2-启动样本字符裁剪工具.bat      启动器
└─ CropCharRegion_2026\          裁剪工具本体（cropCharRegionByOcrLabel_v3_ui.py、crop_core.py）
```

两个启动脚本的查找顺序一致（**全相对路径，不写死盘符、不回退 PATH**）：
工具同级 → 上一级 → 上两级 的 `python-3.9.10-embed`；都找不到时打印提示并暂停，
强制要求随附环境在位。

要点：
- 两套工具都只用 **PyQt5**（不再需要 PySide6，已卸载）
- 环境内所有路径都是相对的，`python39._pth` 也是相对写法，可整体搬移
- 若换机器后 Qt 报缺少平台插件，检查 `python-3.9.10-embed\Lib\site-packages\PyQt5\Qt5\plugins\platforms\qwindows.dll` 是否存在
- YOLO 训练需要的 `ultralytics / torch / ncnn / onnx` 也在这个环境里，一并拷走即可


## 2. 相对原 Linux 版改了哪些代码

| 文件 | 改动 |
| --- | --- |
| `PPOCRLabel/libs/ocr_v5_onnx_backend.py` | **新增**。ONNX 推理后端，与 `ocr_v5_backend.py` 的 stdin/stdout JSON 协议完全一致 |
| `PPOCRLabel/libs/ocrV5Bridge.py` | 后端可切换：`PPOCRLABEL_OCR_BACKEND=onnx`（默认）/ `paddle`；onnx 时用 `sys.executable`，不必再找 `python3.10` |
| `PPOCRLabel/PPOCRLabel.py` | `from paddleocr import PPStructure` 改为可选导入；表格识别缺失时弹提示而不是启动崩溃 |

原有 `libs/ocr_v5_backend.py`（Paddle 版）保留，未修改，可用环境变量切回去。

## 3. 环境变量

| 变量 | 默认 | 说明 |
| --- | --- | --- |
| `PPOCRLABEL_OCR_BACKEND` | `onnx` | `onnx` = onnxruntime；`paddle` = 原来的 Python 3.10 子进程 |
| `PPOCRLABEL_OCR_PYTHON` | 当前解释器 | 仅 `paddle` 模式需要，指向带 PaddlePaddle 的 python |
| `PPOCRLABEL_V5_MODEL_DIR` | `PPOCRLabel/models/ppocrv5` | 模型目录 |
| `PPOCRLABEL_V5_USE_CLS` | `1` | 文本行方向分类；`0` 关闭（原 Paddle 版是关闭的） |
| `PPOCRLABEL_V5_CPU_THREADS` | 0（auto） | onnxruntime 线程数 |

## 4. 实测结果（本机，i7 级 CPU）

| 项目 | 结果 |
| --- | --- |
| 启动到窗口可见 | < 2 s |
| 模型加载（后端首次请求） | 约 2.5 s |
| 2448×2048 图，4 行文字 | 约 1.9–2.2 s / 张 |
| 450×170 小图 | 约 0.6 s / 张 |
| 识别示例 | `806501-7` (0.998)、`Coord: (647.83, 867.98)` (0.991)、`Angle: 0.69` (1.000)、`PASS` (0.986) |

自动标注全流程（`autoRecognition` → `AutoDialog` → `Cache.cach`）已用离屏方式验证通过，
两行/多行文本的框与文本均正确落盘。

## 5. 为什么用 ONNX，不用 Paddle / ncnn

| 方案 | 可行性 | 结论 |
| --- | --- | --- |
| **PaddlePaddle 3.x（原方案）** | cp39 Windows 轮子存在（`paddlepaddle-3.0.0-cp39-cp39-win_amd64.whl`，97 MB） | 需要另建/复制一套环境，装完约 1 GB；PaddleOCR 3.x 的 PP-OCRv5 权重还要在首次运行时联网拉取。可用但重 |
| **ONNX + onnxruntime（当前）** | ✅ 已跑通 | 模型仅 13 MB，复用环境里已有的 `onnxruntime`，与 GUI 同解释器；PP-OCRv5 的 det/en-rec 与 Paddle 版同名同源（RapidAI 官方转换） |
| ncnn | ⚠️ 不推荐 | 环境里有 `ncnn 1.0.20240102` Python 绑定，但 PP-OCRv5 没有官方 ncnn 权重，需要 `pnnx`/`onnx2ncnn` 自行转换，且 DB 检测后处理、CTC 解码要自己实现；收益仅是可能快一些，工程量与风险都高于 ONNX |

**关键坑**：ModelScope 上的 PP-OCRv5 ONNX 模型标注 `ir_version=10`，而 Python 3.9 能装的
onnxruntime 最高 1.19（只支持 IR ≤ 9），直接加载会报
`Unsupported model IR version: 10`。模型实际只用了 opset 14，把 `ir_version` 改成 9
即可，数值不变（脚本里已自动处理并 `onnx.checker` 校验）。

## 5.1 为什么保留 v5、不换 v6（2026-10-26 实测）

试过 `PP-OCRv6`（RapidOCR v3.10 自带 det/rec small，另下载过 medium），在本项目的
机器视觉截图上**识别质量反而下降**，因此继续用 v5：

| 模型 | `PASS` | 其他文本 | 误检 |
| --- | --- | --- | --- |
| v5（det mobile + **en** rec mobile） | `PASS` 0.986 | `806501-7` 0.998、`Coord: (647.83, 867.98)` 0.991、`Angle: 0.69` 1.000 | 无 |
| v6 small（det/rec small，多语种） | `Ps` 0.65（100.jpg 为 `PAS` 0.65） | 上述三项仍正确 | 多出 3–4 个 `+` / `_` / `D0` 假框 |

原因分析：
- v6 rec 是**多语种大字典**（输出 18710 类，v5 en 只有 438 类），对短全大写单词（PASS）
  容易混淆；v6 det 对小划痕/标记更敏感，产生了 v5 没有的假框
- v6 唯一的优势在中文：同一张中文样图 v5 输出 `it`（乱码），v6 正确得到 `中文识别` (1.000) /
  `测试 ABC 123` (0.991)

结论：**当前数据是英文/数字标签，v5 更准**。若以后要标注中文，再切 v6；
两种模型都需把 `ir_version` 从 10 降到 9 才能在本机 onnxruntime 1.17 上加载。
v6 模型文件已删除，需要时可从 ModelScope `RapidAI/RapidOCR` v3.10.0 重新下载：
`onnx/PP-OCRv6/det/PP-OCRv6_det_small.onnx`、`onnx/PP-OCRv6/rec/PP-OCRv6_rec_small.onnx`
（无需字典文件，字典内嵌）。

## 6. 已知限制

- **表格识别**（`TableRecognition`）依赖旧版 PaddleOCR 2.x 的 `PPStructure`，本环境未安装，
  点击会弹出提示。该功能与自动标注无关。
- 模型只带**英文识别**（`en_PP-OCRv5_rec_mobile`），与原 Linux 定制版一致；需要中文识别时，
  把 `ch_PP-OCRv5_rec_mobile.onnx` + `ppocrv5_dict.txt` 放进模型目录，并在
  `ocr_v5_onnx_backend.py` 里把 `Rec.lang_type` 改成 `LangRec.CH`、模型文件名改成对应值。
- 恢复回 Linux/Jetson 时，把 `PPOCRLabel/` 覆盖回 site-packages 即可；新增的
  `ocr_v5_onnx_backend.py` 与 `models/` 不会被 Paddle 版逻辑调用。
