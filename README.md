# 片刻 (Pianke)

> **让 AI 协助初筛与分组，把最终的审美决定权留给自己。**
>
> **Let AI handle the first pass of grouping and filtering, while you keep the final creative decision.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows-lightgrey.svg)](#一键启动推荐)
[![License: Pianke v2](https://img.shields.io/badge/license-Pianke%20v2-cc785c.svg)](LICENSE)

## 项目主页介绍

片刻是一个本地优先的 AI 辅助选片工具，面向摄影师、摄影工作室和需要整理大量照片的摄影爱好者。它解决的不是“替你决定审美”，而是把最耗时间的第一轮机械工作交给程序：扫描照片文件夹、读取 JPG/RAW/HEIC、生成缩略图、识别明显废片、把相似连拍归成同一组，再用左右 A/B 擂台让人快速决定哪一张更好。

日常摄影工作里，一次活动、婚礼、写真或旅行可能有几百到几千张照片。人工从头翻到尾很容易疲劳，也容易在相似连拍里反复犹豫。片刻的价值是先把“明显不值得看的”和“应该放在一起比较的”整理好，让你集中精力做最后的审美判断。这样能更快交付成片，也能减少漏选、重复比对和临时中断带来的混乱。

本仓库是基于原作者 [zhaoyue4810/pianke](https://github.com/zhaoyue4810/pianke) 的公开 fork。保留原项目名称、作者署名和 Pianke Software License Agreement v2，不改成 MIT。本 fork 主要补充大工程断点继续、前端流程和本地启动集成相关改动。

## 技术框架和实现思路

片刻是一个“本地 Web 应用”：

- **Python + Flask**：提供本地 Web 服务和照片处理 API，默认打开 `http://localhost:5057`。
- **Pillow / pillow-heif / rawpy**：读取 JPG、PNG、HEIC 和 RAW 预览，生成缩略图和水印输出。
- **imagehash / numpy / scipy / OpenCV**：计算相似度、质量特征和基础图像分析。
- **PyTorch / torchvision / transformers**：专家模式下用于视觉语义特征和更强的相似图分组。
- **InsightFace / ONNX Runtime**：用于人像场景的人脸检测和特征提取。
- **pyiqa / timm**：用于图像质量和美学评分辅助。
- **OpenAI 兼容接口**：土豪模式可接入火山 Ark 等视觉模型服务，用于生成更接近人话的退片理由。
- **原生 HTML/CSS/JavaScript 前端**：提供导入、进度、复核、分组、A/B 擂台、撤销、导出和水印界面。

核心效果是把照片处理拆成几个可中断的阶段：扫描、初筛、分组、人工擂台、导出。状态写入照片目录下的 `.pic_selecter_state.json`，缩略图和日志写入 `_pic_selecter/`，因此大工程可以中途停止，下次继续。

## 用户需要提供什么

最少只需要：

- 一个本地照片文件夹的绝对路径。
- 选择处理模式：极速、专家或土豪。
- 选择归档方式：移动或复制。

根据场景可能还需要：

- **土豪模式 API Key**：在网页弹窗填写，或通过 `ARK_API_KEY` 环境变量提供。
- **端口**：默认 `5057`，可用 `PIC_SELECTER_PORT` 或 `python app.py --port 8080` 调整。
- **工作区路径**：可用 `PIC_SELECTER_WORKSPACE` 指定运行缓存根目录。
- **修图/接入工作区路径**：可用 `PIANKE_RETOUCH_WORKSPACE` 指定外部工作流目录。
- **脚本访问 token**：如果要让脚本或 curl 调接口，可设置 `PIC_SELECTER_TOKEN`。
- **运行设备选择**：可用 `PIC_SELECTER_RUNTIME=auto|cpu|gpu` 指定推理运行偏好。
- **禁用国内镜像**：一键启动器默认适配国内镜像；如需禁用可设置 `PIANKE_NO_MIRROR=1`。

这些变量都在启动前设置。示例：

```bash
export PIC_SELECTER_PORT=8080
export PIC_SELECTER_RUNTIME=auto
export ARK_API_KEY="your_ark_api_key"
python app.py --port "$PIC_SELECTER_PORT"
```

## 给 OpenClaw / Agent 的快速开始

把下面这段交给 OpenClaw、Codex、Claude Code 或小模型 agent，就能让它快速跑起来：

```text
这是一个 Python + Flask 的本地照片 AI 选片工具。请先确认仓库里有 LICENSE，不要改许可证；这是 Pianke Software License Agreement v2，不是 MIT。运行前创建虚拟环境，安装 requirements.txt。国内网络请优先使用阿里云或清华 PyPI 镜像。安装后如 cv2.saliency 缺失，卸载 opencv-python / opencv-python-headless，再安装 opencv-contrib-python。启动命令是 `python app.py --port 5057`，浏览器访问 `http://localhost:5057`。让用户在网页里填写照片文件夹绝对路径，选择极速/专家/土豪模式和移动/复制归档方式。土豪模式需要 ARK_API_KEY 或网页内填写 API Key。不要上传用户照片、模型缓存、workspace、.venv、日志或 .pic_selecter_state.json。
```

更完整的 agent 操作清单见 [docs/AGENT_QUICKSTART.md](docs/AGENT_QUICKSTART.md)。

---

## Project Overview

Pianke is a local-first AI-assisted photo culling tool for photographers, studios, and anyone who needs to sort large photo sets. It does not try to replace creative taste. Instead, it automates the repetitive first pass: scan a folder, read JPG/RAW/HEIC files, build thumbnails, reject obvious failed shots, group visually similar burst photos, and present candidates in a fast left-vs-right A/B arena so the human can make the final selection.

In real photography work, a wedding, event, portrait session, or trip can produce hundreds or thousands of images. Reviewing everything manually is slow and tiring. Pianke makes life easier by preparing the review surface: failed shots are separated, similar shots are grouped, and progress can resume after interruption. You spend more time choosing and less time fighting folders.

This repository is a public fork of [zhaoyue4810/pianke](https://github.com/zhaoyue4810/pianke). It keeps the upstream name, attribution, and Pianke Software License Agreement v2. It is not relicensed as MIT. This fork focuses on large-project resume behavior, front-end workflow improvements, and local launch integration.

## Technical Stack

Pianke is a local web app:

- **Python + Flask** for the local service and photo-processing API.
- **Pillow / pillow-heif / rawpy** for JPG, PNG, HEIC, RAW previews, thumbnails, and watermark export.
- **imagehash / numpy / scipy / OpenCV** for similarity, quality signals, and image analysis.
- **PyTorch / torchvision / transformers** for expert-mode visual features.
- **InsightFace / ONNX Runtime** for face detection and embeddings in portrait workflows.
- **pyiqa / timm** for image-quality and aesthetic scoring.
- **OpenAI-compatible API clients** for Tycoon mode, such as Volcengine Ark vision models.
- **Native HTML/CSS/JavaScript front end** for import, progress, review, grouping, A/B selection, undo, export, and watermark UI.

The workflow is staged and resumable: scan, pre-screen, group, manual A/B culling, and export. State is stored in `.pic_selecter_state.json` inside the photo folder; thumbnails and logs live under `_pic_selecter/`.

## User Inputs And Environment Variables

Minimum user input:

- Absolute path to a local photo folder.
- Mode: Fast, Expert, or Tycoon.
- Archive behavior: move or copy.

Optional configuration:

- `ARK_API_KEY`: vision model key for Tycoon mode.
- `PIC_SELECTER_PORT`: local web port, default `5057`.
- `PIC_SELECTER_WORKSPACE`: runtime workspace root.
- `PIANKE_RETOUCH_WORKSPACE`: external retouch/integration workspace.
- `PIC_SELECTER_TOKEN`: optional token for script/API access.
- `PIC_SELECTER_RUNTIME=auto|cpu|gpu`: runtime preference.
- `PIANKE_NO_MIRROR=1`: disable launcher mirror defaults.

Example:

```bash
export PIC_SELECTER_PORT=8080
export PIC_SELECTER_RUNTIME=auto
export ARK_API_KEY="your_ark_api_key"
python app.py --port "$PIC_SELECTER_PORT"
```

## Agent Quickstart

Give this to OpenClaw, Codex, Claude Code, or a smaller model agent:

```text
This is a Python + Flask local AI photo-culling tool. First verify that LICENSE remains Pianke Software License Agreement v2; do not convert it to MIT. Create a venv and install requirements.txt. On China mainland networks, use an Aliyun or Tsinghua PyPI mirror. If cv2.saliency is missing, uninstall opencv-python and opencv-python-headless, then install opencv-contrib-python. Start with `python app.py --port 5057` and open `http://localhost:5057`. Ask the user for an absolute photo-folder path, choose Fast/Expert/Tycoon mode, and choose move/copy archive mode. Tycoon mode needs ARK_API_KEY or an API key entered in the web UI. Never upload user photos, model caches, workspace data, .venv, logs, or .pic_selecter_state.json.
```

See [docs/AGENT_QUICKSTART.md](docs/AGENT_QUICKSTART.md) for a fuller agent checklist.

---

**片刻** 是一款专为摄影师和摄影爱好者设计的**本地照片双语/擂台式选片工具**。它能够将一次拍摄中相似的几十甚至上百张照片自动归入“同一个瞬间”的组中，然后通过直观的 **左右 A/B 擂台 PK** 方式，让你快速挑出最满意的一张。

**Pianke** is a local-first bilingual photo culling tool for photographers and photo enthusiasts. It groups visually similar shots from the same moment, filters out obvious failed images, and lets you make the final choice through a fast left-vs-right A/B selection workflow.

---

## Bilingual overview / 中英文说明

### 中文

片刻的目标不是替代摄影师的审美，而是把重复、耗时、机械的第一轮筛选交给 AI：扫描照片文件夹、识别明显废片、把相似连拍自动分组，并在后续擂台式对比中保留人工判断。极速和专家模式以本地处理为主，照片不会上传；土豪模式会把缩略图发送到你配置的大模型服务商，用于生成更接近人话的退片理由。

本 fork 在原作者项目基础上，重点补充了适合大工程/大批量照片处理的断点继续能力和更完整的前端 UI 工作流。除这些本地增强外，项目仍保留原作者的产品定位、授权限制和免费使用原则。

### English

Pianke does not try to replace a photographer's taste. Instead, it gives AI the repetitive first pass: scan a photo folder, reject obvious failed shots, group burst or near-duplicate photos, and then present the remaining candidates in a fast A/B comparison flow where the human still makes the final call. Fast and Expert modes are designed for local processing, so photos stay on your machine. Tycoon mode can send thumbnails to the configured vision model provider to generate more human-readable rejection reasons.

This fork keeps the original project's positioning, license restrictions, and free-use principle, while adding local improvements for large photo sets: resumable sessions for long-running projects and a more complete front-end UI workflow.

---

## 📣 关于授权（请在使用前阅读）

> **本项目完全免费！不收一分钱！**
>
> **摄影师可以用它处理付费拍摄的客户照片；但绝对禁止把软件本身拿去卖钱。**

### ✅ 允许
- 个人使用——爱好者、学生、个人摄影师整理自己的照片
- **摄影师 / 工作室在日常拍摄业务中使用，包括处理付费客户的照片**（拍摄服务是你卖的，软件只是你用的工具）
- 自由修改源码自用、提交 PR
- 在保留原始版权与许可的前提下，免费分享给朋友、同事、摄影社群

### ❌ 禁止
- **销售本软件**（原版、改名、汉化、二次打包、上架商店——一律不行）
- **把本软件作为付费服务对外提供**（付费 SaaS / 在线选片网站 / 收费小程序等）
- 转售、转授权、再许可
- 移除或隐藏"片刻"品牌、版权、作者联系方式
- 用"片刻"或近似名称分发改版软件

### 🤝 商业合作 / 二次开发授权

如果你想做的事情超出上面"允许"范围（比如把片刻嵌入你的付费产品、做付费 SaaS 等），请联系作者协商单独授权：

**微信 `15828377122`**

> 完整条款见 [LICENSE](LICENSE)（中文为准、附英文摘要）。
>
> 如果你发现有人在卖片刻 / 把它包装成付费服务，欢迎私信举报。

---

## 核心特性

## Core features / 核心特性

- 🔒 **照片不出本地**：除"土豪模式"外，所有分析、初筛、分组都在你自己的电脑里完成，不上传任何云端。
- 🔒 **Local-first processing**: except for Tycoon mode, analysis, pre-screening, and grouping run on your own computer without uploading photos.
- 🤖 **自动剔除明显废片**：模糊、过曝、欠曝、闭眼，自动识别并归到一边，担心错杀可一键复核召回。
- 🤖 **Automatic rejection of obvious failed shots**: blur, exposure issues, closed eyes, and similar problems can be pre-screened before manual review.
- 📁 **把同一瞬间的连拍归到一组**：理解"这几张是同一个画面"——同一个人、同一个场景、同一段时间，自动放在一起对比。
- 📁 **Moment-based grouping**: similar shots from the same person, scene, or time window are grouped together for faster comparison.
- ⚔️ **左右擂台两两对决**：按 `←` / `→` 选哪边更好，一组里只留一张（或几张），节奏极快。
- ⚔️ **A/B culling arena**: compare two photos at a time and use the keyboard to keep the stronger candidate.
- 📸 **原生支持 RAW**：
  - **RAW+JPG 同名双拍**：以 JPG 显示与分析，归档时 RAW 跟着自动一起搬走（含 `.xmp` 伴随文件）。
  - **纯 RAW**：从 RAW 文件里直接取出预览图，秒级读图，不卡。
- 🔄 **随时反悔、随时续做**：
  - **多级撤销**：单步撤销、整组重选、全局回头都可以。
  - **进度自动保存**：随时关掉，下次启动接着上次继续。
- 🔄 **Resume anytime**: progress is saved locally so long-running selection projects can be paused and continued later.

---

## 三种工作模式

你可以在首页自由切换三种模式，按你的电脑性能和照片类型选：

| 模式 | 适合谁 | 上手成本 | 联网要求 |
| :--- | :--- | :--- | :--- |
| **极速** | 拍物 / 风景 / 低配电脑 | 装一次约 200 MB | **完全不需要** |
| **专家** | 拍人像 / 婚礼 / 活动 / 主流性能电脑 | 装一次约 2-3 GB | 仅第一次联网下载，之后纯离线 |
| **土豪** | 想看到"为什么退这张"的人话解释 | 装一次约 5 MB + 配一个 API Key | 每张图都要联网（图片会发到大模型服务商） |

> 💡 **选择建议**：
> - **拍物 / 风景 / 旧电脑** ➔ 选 **极速**，对静物、产品、多角度连拍非常稳。
> - **拍人 / 婚礼 / 活动** ➔ 选 **专家**，能识别"同一个人不同姿势不同背景"并归为一组。
> - **需要"人话退片理由"** ➔ 选 **土豪**，会用大白话告诉你"左边小孩闭眼了"这种原因。

---

## 快速开始

> 💡 **强烈推荐小白用户使用 [Trae](https://www.trae.com.cn/)（或 Qoder）**：装好 Trae 后用它打开本项目文件夹，直接告诉 AI：
>
> > **"先把 pip 换成阿里云源（`https://mirrors.aliyun.com/pypi/simple/`）或清华源（`https://pypi.tuna.tsinghua.edu.cn/simple`），再安装相关依赖并运行这个项目。"**
>
> 国内默认走的 PyPI 官方源在没有梯子的情况下经常卡到超时，专家模式光依赖就有 2GB 多，不换源基本装不下来。换成阿里 / 清华镜像后整套依赖几分钟就能装完，剩下的交给 Trae 就行。

### 方式一：一键启动（推荐非开发者）

适合未安装 Python 环境或不熟悉命令行的用户。

1. [下载项目 ZIP 压缩包](https://github.com/zhaoyue4810/pianke/archive/refs/heads/main.zip) 并解压到本地。
2. 双击运行对应的启动器脚本：

| 系统 | 启动脚本 | 首次运行安全提示过白方式 |
| :--- | :--- | :--- |
| **macOS** | `启动_macOS.command` | 若提示“身份不明的开发者”：**按住 Control 键**点击脚本 ➔ 选择 **打开** ➔ 弹窗中再次点击 **打开**。 |
| **Windows** | `启动_Windows.bat` | 若弹出“Windows 已保护你的电脑”：点击 **更多信息** ➔ 选择 **仍要运行**。 |

*注：启动器会自动在项目独立目录下下载并构建 Python 环境，不污染你的系统环境。国内用户默认启用 PyPI 和模型镜像，可以使用环境变量 `PIANKE_NO_MIRROR=1` 禁用镜像走官方源。*

### 方式二：手动启动（适合开发者）

如果你已安装 Python 环境并希望手动控制：

```bash
# 1. 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. 安装项目依赖（包含所有模式的并集）
pip install -r requirements.txt

# 3. 运行服务（默认端口 5057，自动打开浏览器）
python app.py

# 常用参数：
python app.py --port 8080 --no-browser
```

> ⚠️ **开发模式提示**：若手动安装依赖，可能因传递依赖导致 `opencv-python` 冲突。可运行以下命令修复：
> ```bash
> pip uninstall -y opencv-python opencv-python-headless
> pip install --force-reinstall --no-deps "opencv-contrib-python>=4.9"
> ```

---

## 选片工作流

1. **导入与配置**：在首页选择工作模式，输入或拖入照片文件夹的绝对路径，点击 **开始整理**。
2. **分析与进度**：系统流式显示扫描进度和预估剩余时间。
3. **初筛复核**：平铺展示被自动淘汰的废片及原因。**点击任意照片即可直接将其放回待分组列表**。未点击的将直接归入淘汰区。
4. **分组预览与调参**：预览分组效果。如果分组过细或过粗，可实时拖动滑块调节阈值并点击 **重新分组** 即时更新。
5. **左右擂台 PK**：在相似组内进行两两对比。
   - `←` / `→`：保留左侧 / 保留右侧 (对侧淘汰)
   - `↑` / `↓`：全要 / 全不要
   - `[` / `]`：仅淘汰左侧 / 仅淘汰右侧 (处理单张图像损坏)
   - `S`：跳过本组 (暂存至队尾最后处理)
   - `Z`：切换缩放等级 (1x ➔ 2x ➔ 4x)，两图同步平移
   - `Shift + Z`：撤销当前组的上一步操作
6. **完成与导出**：展示所有 Winner 照片，支持一键打开结果文件夹。

---

## 输出与目录策略

本工具采用**单文件夹、单会话**策略，会在你指定的**照片目录**下生成以下结构：

```text
📂 你的照片文件夹/
├── 📂 winners/                # 最终胜出保留的照片 (你的成片)
├── 📂 losers/                 # 被淘汰的照片
├── 📄 .pic_selecter_state.json # 进度持久化文件 (可随时中断并继续)
└── 📂 _pic_selecter/          # 缓存与日志目录
    ├── 📂 thumbs/             # 缩略图缓存 (重复加载近乎瞬时)
    ├── 📄 log.txt             # 详细处理日志
    └── 📄 skipped.log         # 坏图/无法读取文件清单
```

### 归档模式

你可以在首页的”更多选项”中选择以下归档模式：
- **移动模式（默认，推荐）**：将原片直接移动到 `winners/` 或 `losers/` 目录。最省磁盘空间，符合一次性选片直觉。反悔时文件会无损搬回原位。
- **复制模式**：原片保持不动，在 `winners/` 和 `losers/` 中创建副本。需要双倍磁盘空间。

### 初筛强度

在”更多选项”里还可以选择初筛强度：
- **标准**：阈值较宽，只剔除明显废片，适合不放心 AI 判断时使用。
- **进阶（默认推荐）**：阈值更严，能多拒一些疑似废片，进入擂台的图片更少。所有被淘汰的图都可以在复核页或完成页召回。

---

## 相机水印

选片完成后，在 Winner 总览页点击 **相机水印** 可以为胜出的照片批量添加 EXIF 信息水印。
水印会读取照片的相机品牌、机型、镜头、焦距、光圈、快门、ISO、拍摄时间并合成在画面上，
也会自动匹配品牌 Logo（富士、佳能、尼康、索尼、徕卡、哈苏、奥林巴斯等）。

共 11 个样式 ID。详尽程度直接编码在样式名里（**-详尽** 带镜头·参数·时间；
**-极简** 仅品牌 Logo + 机型）：

| ID | 名称 | 风格 |
| :--- | :--- | :--- |
| **A** | 标准底栏 | 白色信息条，左机型/镜头 ｜ 中品牌 Logo ｜ 右参数/时间 |
| **B_full / B_clean** | 极简底栏-详尽 / 极简底栏-极简 | 顶/左/右贴边窄白 + 底部居中 Logo + 信息 |
| **C_full / C_clean** | 毛玻璃悬浮-详尽 / 毛玻璃悬浮-极简 | 原图模糊作背景 + 缩小照片悬浮居中带阴影 |
| **D_full / D_clean** | 经典白边相框-详尽 / 经典白边相框-极简 | 顶/左/右窄白 + 底大白边居中放品牌 |
| **F_full / F_clean** | 杂志风-详尽 / 杂志风-极简 | 左下色卡（从图自动提取）+ 右下品牌信息 |
| **G** | 极简白边 | 照片四周均匀窄白边，无任何文字 |
| **H** | 相机回放 | 上原图 + 下模糊版 + 居中富士 X-T5，LCD 与取景器都显示画面 |

输出到 `winners/watermarked_<时间戳>/` 子目录，保留原 EXIF（旋转标志归位），JPEG 92 质量、progressive。

---

## 常见问题 (FAQ)

<details>
<summary><b>1. 启动后浏览器没有自动打开？</b></summary>
手动在浏览器中访问 <code>http://localhost:5057</code> 即可。
</details>

<details>
<summary><b>2. 默认的 5057 端口被占用怎么办？</b></summary>
一键启动器读环境变量 <code>PIC_SELECTER_PORT</code>。在启动前设置后再运行启动器：
<ul>
  <li>macOS: <code>export PIC_SELECTER_PORT=8080</code></li>
  <li>Windows: <code>set PIC_SELECTER_PORT=8080</code></li>
</ul>
手动启动（<code>python app.py</code>）则直接传 <code>--port 8080</code>。
</details>

<details>
<summary><b>3. 专家模式首次启动卡在“加载中”？</b></summary>
专家模式第一次启动需要从网络下载几百兆的辅助数据，视网速 1-3 分钟。装完之后下次启动是秒开的。如果长时间无响应，请检查终端窗口日志或网络连接。
</details>

<details>
<summary><b>4. 土豪模式如何配置 API Key？</b></summary>
启动后在网页端弹窗里贴入 Key 即可，Key 仅本地保存在 <code>~/.config/pic_selecter/ark_key</code>（仅你可读）。也可以在启动前设置环境变量 <code>ARK_API_KEY=你的key</code>。
</details>

<details>
<summary><b>5. 极速模式和专家模式在"剔除废片"上有什么区别？</b></summary>
两者擅长的废片类型不同：
<ul>
  <li><b>极速模式</b>：擅长抓"整张糊掉/手抖/失焦"这类全图都模糊的废片。</li>
  <li><b>专家模式</b>：擅长抓"背景清楚但人脸糊了/眼睛闭了"这类人像废片。</li>
</ul>
</details>

<details>
<summary><b>6. 如何彻底卸载和清理缓存？</b></summary>
<ul>
  <li><b>清理照片缓存</b>：直接删除对应照片目录下的 <code>winners/</code>、<code>losers/</code>、<code>.pic_selecter_state.json</code> 及 <code>_pic_selecter/</code> 文件夹（移动模式下请先移回照片）。</li>
  <li><b>完全卸载程序</b>：删除解压出的项目文件夹，并清理本地全局工具缓存：
    <ul>
      <li>macOS: <code>rm -rf ~/.local/bin/uv ~/.local/share/uv/</code></li>
      <li>Windows: 删除 <code>%USERPROFILE%\.local\bin\uv.exe</code> 和 <code>%USERPROFILE%\.local\share\uv\</code></li>
    </ul>
  </li>
</ul>
</details>

<details>
<summary><b>7. HEIC 格式图片在网页上无法预览？</b></summary>
Windows 系统可能需要安装微软官方的 HEIF 扩展才能正常在浏览器中预览该格式；片刻工具在后端能够正常分析处理该格式。
</details>

---

## 隐私与安全说明

1. 极速与专家模式下，所有照片**完全在你的电脑里处理**，没有任何照片或数据发往外部。
2. 程序起的服务**只在你自己的电脑回环地址（127.0.0.1）上监听**，局域网和外网设备都访问不到。
3. 接口做了严格的来源校验，防止任何外部网站偷偷调用。需要给脚本开启额外鉴权，可在启动前设置环境变量 `PIC_SELECTER_TOKEN=你的口令`。
4. ⚠️ **土豪模式例外**：该模式下，照片的缩略图会被发到你配置的大模型服务商接口（按 token 计费）。对隐私要求极高的场景请只用**极速**或**专家**模式。

---

## 反馈与贡献

欢迎通过 [GitHub Issues](https://github.com/zhaoyue4810/pianke/issues) 提交反馈或建议。

# 个人微信
15828377122
