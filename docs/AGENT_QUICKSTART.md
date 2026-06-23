# Agent 快速开始 / Agent Quickstart

## 中文

这是一个 Python + Flask 的本地照片 AI 选片工具，适合让 OpenClaw、Codex、Claude Code 或小模型 agent 快速接手运行。

### 许可边界

- 保留原作者和原项目链接：[zhaoyue4810/pianke](https://github.com/zhaoyue4810/pianke)。
- 保留 `LICENSE`，许可证是 Pianke Software License Agreement v2。
- 不要改成 MIT、Apache、GPL 等通用开源协议。
- 不要移除“片刻 / Pianke”品牌、版权和作者联系方式。

### 最小启动步骤

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py --port 5057
```

打开：

```text
http://localhost:5057
```

让用户在网页里填写照片文件夹绝对路径，然后选择：

- `极速`：适合静物、风景、产品图和低配电脑。
- `专家`：适合人像、婚礼、活动，依赖更重。
- `土豪`：需要视觉大模型 API Key，用于生成更自然的退片理由。

归档方式：

- `移动`：节省磁盘空间，直接把照片移动到 `winners/` 或 `losers/`。
- `复制`：保留原片位置，但需要更多磁盘空间。

### 国内网络建议

如果安装依赖很慢，优先使用镜像源：

```bash
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

或：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

如果 `cv2.saliency` 缺失：

```bash
pip uninstall -y opencv-python opencv-python-headless
pip install --force-reinstall --no-deps "opencv-contrib-python>=4.9"
```

### 环境变量

| 变量 | 作用 |
| --- | --- |
| `PIC_SELECTER_PORT` | 本地服务端口，默认 `5057` |
| `PIC_SELECTER_WORKSPACE` | 运行工作区根目录 |
| `PIANKE_RETOUCH_WORKSPACE` | 外部修图/接入工作区 |
| `PIC_SELECTER_TOKEN` | 脚本/API 访问 token，默认不开启 |
| `PIC_SELECTER_RUNTIME` | `auto`、`cpu` 或 `gpu` |
| `ARK_API_KEY` | 土豪模式视觉模型 API Key |
| `PIANKE_NO_MIRROR` | 设置为 `1` 时禁用启动器镜像源 |

示例：

```bash
export PIC_SELECTER_PORT=8080
export PIC_SELECTER_RUNTIME=auto
export ARK_API_KEY="your_ark_api_key"
python app.py --port "$PIC_SELECTER_PORT"
```

### 不要提交或上传

- 用户照片
- `.venv/`
- `models/`
- `workspace/`
- `_pic_selecter/`
- `.pic_selecter_state.json`
- `winners/`
- `losers/`
- `*.log`
- `*.pid`
- 模型缓存和照片缓存

## English

This is a Python + Flask local AI-assisted photo-culling tool. It is suitable for OpenClaw, Codex, Claude Code, or smaller agents that need a direct operational checklist.

### License Boundary

- Preserve upstream attribution: [zhaoyue4810/pianke](https://github.com/zhaoyue4810/pianke).
- Keep `LICENSE` as Pianke Software License Agreement v2.
- Do not relicense as MIT, Apache, GPL, or another generic open-source license.
- Do not remove the Pianke brand, copyright, or author contact.

### Minimal Startup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py --port 5057
```

Open:

```text
http://localhost:5057
```

Ask the user for an absolute photo-folder path, then choose:

- `Fast`: objects, landscapes, product photos, and lower-end machines.
- `Expert`: portraits, weddings, and events. Heavier dependencies.
- `Tycoon`: requires a vision-model API key for more natural rejection reasons.

Archive mode:

- `Move`: saves disk space and moves photos into `winners/` or `losers/`.
- `Copy`: preserves originals in place, but uses more disk space.

### China Mainland Network Tip

If dependency installation is slow, use a mirror:

```bash
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

or:

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

If `cv2.saliency` is missing:

```bash
pip uninstall -y opencv-python opencv-python-headless
pip install --force-reinstall --no-deps "opencv-contrib-python>=4.9"
```

### Environment Variables

| Variable | Purpose |
| --- | --- |
| `PIC_SELECTER_PORT` | Local service port, default `5057` |
| `PIC_SELECTER_WORKSPACE` | Runtime workspace root |
| `PIANKE_RETOUCH_WORKSPACE` | External retouch/integration workspace |
| `PIC_SELECTER_TOKEN` | Optional script/API token |
| `PIC_SELECTER_RUNTIME` | `auto`, `cpu`, or `gpu` |
| `ARK_API_KEY` | Vision-model API key for Tycoon mode |
| `PIANKE_NO_MIRROR` | Set to `1` to disable launcher mirror defaults |

Example:

```bash
export PIC_SELECTER_PORT=8080
export PIC_SELECTER_RUNTIME=auto
export ARK_API_KEY="your_ark_api_key"
python app.py --port "$PIC_SELECTER_PORT"
```

### Never Commit Or Upload

- User photos
- `.venv/`
- `models/`
- `workspace/`
- `_pic_selecter/`
- `.pic_selecter_state.json`
- `winners/`
- `losers/`
- `*.log`
- `*.pid`
- model caches and photo caches
