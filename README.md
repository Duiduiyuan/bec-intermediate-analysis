# BEC 中级分析 / BEC Intermediate Analysis

将英文文章制作成含中文翻译、重点词汇与搭配注释的 A4 学习图。

Create A4 English–Chinese study sheets with translations, vocabulary notes, and business collocations.

[中文](#中文) · [English](#english)

## 中文

### 功能

这是一个面向 BEC 中级（BEC Vantage）学习的 AI Skill，支持输入英文文本或文章图片。

- 根据英文重新翻译中文，并选择有学习价值的商务词汇、搭配和语境义。
- 输出 `2480 × 3508 px` 的 A4 竖版 PNG，支持 5 套配色，同次任务配色统一。
- 重点词组带下划线和居中注释，按完整段落分页。
- 内附 Outfit 和思源黑体 Light，无需安装到系统。

文章图片识别、翻译和选词由所用 AI 工具完成；Python 脚本将准备好的分析 JSON 排版为 PNG。脚本本身不提供 OCR 或自动翻译。安装依赖后，渲染脚本无需联网；AI 工具的数据处理方式取决于所用服务。

### 安装与使用

下载本仓库，或使用 Git 克隆：

```bash
git clone https://github.com/Duiduiyuan/BEC-bec-intermediate-analysis.git bec-intermediate-analysis
```

保留整个文件夹及内部目录结构，将它安装到所用 AI 工具的 Skills 目录。若下载的是仓库 ZIP，解压后将文件夹命名为 `bec-intermediate-analysis`。安装位置和调用方式以所用工具为准。

提供英文文章或图片，并说明：

> 使用 bec中级分析处理这篇文章，选用 4 号配色，输出名称为“客户反馈”。

完整的配色、固定排版规范和分析 JSON 格式见 [SKILL.md](SKILL.md)。

### 依赖与示例渲染

需要 Python 3.10+ 和 Pillow；已验证版本固定在 [requirements.txt](requirements.txt)。在本仓库文件夹内打开终端，运行以下命令。环境和输出会放在相邻目录。

macOS / Linux：

```bash
python3 -m venv ../bec-venv
../bec-venv/bin/python -m pip install -r requirements.txt
../bec-venv/bin/python scripts/render_bec.py examples/example.json --output-dir ../bec-example --style 4
```

Windows PowerShell（已安装 Python Launcher）：

```powershell
py -3 -m venv ..\bec-venv
..\bec-venv\Scripts\python.exe -m pip install -r requirements.txt
..\bec-venv\Scripts\python.exe scripts/render_bec.py examples/example.json --output-dir ..\bec-example --style 4
```

示例输出为相邻目录中的 `bec-example/bec-example-01.png`。将输入路径换为自己的分析 JSON，将输出目录换为文章名称即可。`--style` 可选 `1`—`5`，省略时随机选择一次。也可使用 `--english-font` 和 `--chinese-font` 显式指定符合规范的字体文件。

### 文件与授权

- [SKILL.md](SKILL.md)：Skill 规则、配色和输入格式。
- [scripts/render_bec.py](scripts/render_bec.py)：精确排版与 PNG 渲染脚本。
- [assets/fonts/](assets/fonts/)：字体、各自的授权原文及[来源说明](assets/fonts/SOURCES.md)。
- [examples/example.json](examples/example.json)：可直接渲染的原创示例。
- [agents/openai.yaml](agents/openai.yaml)：Skill 展示信息。

两款字体分别采用 SIL Open Font License 1.1，再发布时须保留字体版权声明及完整授权。字体许可仅覆盖字体文件；本仓库尚未为 Skill 说明和 Python 脚本指定单独的开源许可证。

## English

### Features

An AI Skill for BEC Intermediate (BEC Vantage) study, accepting English text or article images.

- Prepare fresh Chinese translations and useful business vocabulary, collocations, and contextual meanings from the English source.
- Export portrait A4 PNGs at `2480 × 3508 px`, with five color presets and one consistent preset per task.
- Underline selected phrases, center notes beneath them, and keep each paragraph together when paginating.
- Use the bundled Outfit and Source Han Sans SC Light fonts without installing them on the system.

The AI tool handles article-image recognition, translation, and annotation selection. The Python script renders prepared analysis JSON into PNGs; it does not perform OCR or automatic translation. Rendering requires no network access after dependencies are installed. The AI service's handling of your input depends on the tool you use.

### Installation and use

Download this repository or clone it with Git:

```bash
git clone https://github.com/Duiduiyuan/BEC-bec-intermediate-analysis.git bec-intermediate-analysis
```

Install the complete folder in your AI tool's Skills directory, preserving the internal structure. If you downloaded the repository ZIP, rename the extracted folder to `bec-intermediate-analysis`. Follow your tool's instructions for the installation location and invocation method.

Provide an English article or image and ask:

> Use bec-intermediate-analysis to turn this article into BEC study sheets. Choose color preset 4 and name the output “Customer Feedback”.

See [SKILL.md](SKILL.md) for the full task instructions, color presets, fixed layout rules, and analysis JSON format. The Skill instructions are currently written in Chinese.

### Dependencies and sample rendering

Requires Python 3.10+ and Pillow. The tested Pillow version is pinned in [requirements.txt](requirements.txt). Open a terminal in this repository folder and run the commands below. They place the virtual environment and output in adjacent directories.

macOS / Linux:

```bash
python3 -m venv ../bec-venv
../bec-venv/bin/python -m pip install -r requirements.txt
../bec-venv/bin/python scripts/render_bec.py examples/example.json --output-dir ../bec-example --style 4
```

Windows PowerShell, with Python Launcher installed:

```powershell
py -3 -m venv ..\bec-venv
..\bec-venv\Scripts\python.exe -m pip install -r requirements.txt
..\bec-venv\Scripts\python.exe scripts/render_bec.py examples/example.json --output-dir ..\bec-example --style 4
```

The sample creates `bec-example/bec-example-01.png` in the adjacent output directory. Replace the input path with your own analysis JSON and choose an output directory named after the article. Select `--style 1` through `--style 5`, or omit the option to choose a random preset once. Use `--english-font` and `--chinese-font` to explicitly provide font files that meet the Skill's requirements.

### Files and licensing

- [SKILL.md](SKILL.md): Skill instructions, color presets, and input format.
- [scripts/render_bec.py](scripts/render_bec.py): precise layout and PNG renderer.
- [assets/fonts/](assets/fonts/): bundled fonts, their full license texts, and [source information](assets/fonts/SOURCES.md).
- [examples/example.json](examples/example.json): an original, ready-to-render sample.
- [agents/openai.yaml](agents/openai.yaml): Skill display metadata.

Both fonts are distributed under their respective SIL Open Font License 1.1 terms. Retain their copyright notices and full license texts when redistributing. These font licenses cover the font files only; no separate open-source license has been specified for the Skill instructions or Python script in this repository.
