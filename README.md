# research-project-management · 科研项目管理 skill

**版本** 1.1（2026-11-18） · **作者** Xiayin Lou（TUM） · **适用** Claude Code（终端 / 桌面 app / IDE） · **许可证** [MIT](LICENSE)

让 GeoAI 及相关科研项目在长期使用 Claude Code 的过程中**始终保持精简、一致、可追溯**：
代码、实验、数据、作图、参考文献、稿件版本、开源代码都有固定的位置、命名和检查。

---

## 目录

1. [它解决什么问题](#1-它解决什么问题)
2. [包内容](#2-包内容)
3. [安装](#3-安装)
4. [快速上手：按科研流程使用](#4-快速上手按科研流程使用)
5. [规范速查](#5-规范速查)
6. [四个检查脚本](#6-四个检查脚本)
7. [个性化设置](#7-个性化设置)
8. [与其他 skill 的配合](#8-与其他-skill-的配合)
9. [常见问题](#9-常见问题)
10. [版本记录](#10-版本记录)

---

## 1. 它解决什么问题

| 痛点 | 机制 |
|---|---|
| 做得越久结果越多，项目越来越臃肿 | **三层信息结构**：`PROJECT.md` 定容 150 行，超出部分降级进实验卡或归档索引，而不是删掉 |
| 结果太多，需要时间才能看懂 | 每个实验一页**实验卡**，必须写一句话结论（带关键数字）和决策 adopt / discard / follow-up |
| 记忆堆积、token 消耗变大 | 每次会话只读 150 行的 `PROJECT.md`；实验卡和归档按需才读 |
| 文件夹越来越乱 | 固定目录结构 + 边界规则（一次性脚本不进 `src/`，大数据不进项目，只登记） |
| 作图标准、图注格式每个项目都不一样 | 统一作图规范（Aptos，AAG 印刷尺寸）+ 图注模式 + 自动检查脚本 |
| 稿件多轮修改、中途换期刊 | 唯一活稿 `01_main_vN.tex` + 不可变里程碑快照 + 审稿轮次配对 + 期刊清单 `VENUE.md` |
| AI 编造或记错参考文献 | 参考文献只从数据库生成 + 自动核查（Crossref / arXiv / OpenAlex）+ 引用内容核对 |
| 开源代码和私有材料混在一起，容易误传；双盲期间泄露身份 | 独立的 `code/` 文件夹 = GitHub 仓库，里面全部公开、私有的一律不进；推送前用脚本检查私有文件、密钥、个人路径和身份信息 |

核心思想：**在写入时压缩，而不是事后清理。**

## 2. 包内容

```
research-project-management-v1.1/
├── README.md                      ← 本说明
├── LICENSE                        ← MIT
├── install.sh                     ← 一键安装 + 依赖检查
├── research-project-management.skill   ← claude.ai 网页版用的安装包
└── research-project-management/   ← skill 本体（安装时整个复制到 ~/.claude/skills/）
    ├── SKILL.md                   Claude 读的主文件：模式、流程、规则
    ├── references/                详细规范（Claude 按需读取）
    │   ├── figure-standard.md       作图、图文件命名、图注
    │   ├── manuscript-versioning.md 稿件命名、版本、审稿轮次、换期刊、Overleaf
    │   ├── reference-audit.md       参考文献的添加与核查
    │   └── code-release.md          code/ 文件夹、git 设置、路径、README、匿名审稿、tag
    ├── scripts/                   可直接运行的检查工具
    │   ├── check_figures.py         图件按印刷尺寸检查字号、字体、dpi、命名
    │   ├── export_submission_figures.sh  导出投稿用 CMYK 600 dpi TIFF
    │   ├── check_references.py      参考文献核查 + --lookup 生成可靠的 BibTeX
    │   └── check_release.py         推送 GitHub 前检查 code/（私有文件、密钥、路径、身份）
    └── assets/                    初始化新项目时用的模板
        ├── PROJECT / CARD / CLAUDE / MANIFEST / INDEX / VERSIONS-INDEX / VENUE 模板
        ├── manuscript/              01_main_v1.tex, 01_supplementary_v1.tex,
        │                            02_references.bib, sync_figures.sh
        └── code/                    公开仓库模板：README、gitignore、pyproject、
                                     paths.py、plotstyle.py；私有的 env.sh
```

## 3. 安装

**方式 A：脚本安装（推荐）**

```bash
cd research-project-management-v1.1
sh install.sh
```

脚本会：
- 把 skill 复制到 `~/.claude/skills/research-project-management/`；
- 已有旧版本时，先移到 `~/.claude/skill-backups/`；
- 检查依赖，缺什么就告诉你怎么装。

**方式 B：手动安装**：把 `research-project-management/` 整个文件夹复制到 `~/.claude/skills/`。
如果只想在某一个项目里用，可以改放到项目根目录的 `.claude/skills/` 下。

**方式 C：claude.ai 网页版**：使用随附的 `research-project-management.skill` 文件上传。

安装后**新开一个 Claude Code 会话**才会加载。

**依赖**

| 依赖 | 用途 | 必需？ | 安装 |
|---|---|---|---|
| Python 3 | 所有脚本（只用标准库） | 必需 | macOS 自带 |
| Ghostscript | 图件检查、TIFF 导出 | 用到作图检查时必需 | `brew install ghostscript` |
| Poppler（pdfinfo/pdffonts） | TIFF 导出；检查未嵌入字体 | 推荐 | `brew install poppler` |
| Aptos 字体 | 统一作图字体 | 推荐 | Microsoft 365 自带，或从微软官网下载 |
| matplotlib、Pillow | `plotstyle.py`；位图 dpi 检查 | 可选 | `pip install matplotlib pillow` |
| 网络 | 参考文献核查（访问公共 API，无需账号） | 用到核查时必需 | — |
| git | `code/` 仓库；`check_release.py` 读取将要发布的文件 | 开源代码时必需 | macOS 自带（Xcode 命令行工具） |

## 4. 快速上手：按科研流程使用

直接用自然语言说就行，不需要记命令。中英文都可以。

| 时机 | 你说 | Claude 会做 |
|---|---|---|
| **开新项目** | "帮我初始化一个研究项目，课题是……，数据在……，目标期刊是……" | 建好目录；生成 PROJECT.md、CLAUDE.md、数据登记表、稿件模板、VENUE.md、`code/` 仓库骨架和 env.sh；可选初始化 git（仓库数据放在同步盘之外） |
| **日常工作** | （什么都不用说） | 项目里的 CLAUDE.md 每次会话自动生效：先读 PROJECT.md；脚本放进 `code/`，结果写回私有实验目录；加文献要查数据库；作图按规范 |
| **一次工作结束** | "收尾" / "checkpoint" | 写或更新实验卡；登记新数据；检查改过的图和文献；PROJECT.md 瘦身；清理游离文件 |
| **作图 / 写图注** | "画一张 xx 的图" / "检查一下图" | 调用 nature-figure（Python）并套用本规范；用脚本按印刷尺寸检查 |
| **加参考文献** | "把这篇加进参考文献：<DOI 或标题>" | 用 `--lookup` 从数据库生成条目，不凭记忆写 |
| **核查引用** | "核查一下参考文献" | 跑核查脚本，列出 FAIL / WARN |
| **开源代码** | "准备把代码传到 GitHub" / "要匿名镜像" | 完善 README 复现表；跑 `check_release.py`（双盲期间加 `--anonymous`）；推送和建仓库**等你明确同意**才做 |
| **一轮修改结束 / 投稿 / 审稿回来** | "打个快照" / "我今天投稿了" / "审稿意见回来了" | 检查图、文献和代码；冻结快照到 `versions/`；代码打同名 tag 并记下 commit 号；版本号 +1；建立意见 ↔ 回复配对文件 |
| **换期刊** | "被拒了，改投 XX" | 快照；记录投稿历史和经验；版本号 +1；换新 VENUE.md 并逐项核对 |
| **定期体检** | "audit 一下这个项目" | 只诊断不动手，按"三个月后造成多大困惑"排序列出问题 |
| **整理旧项目** | "adopt 这个项目，整理成规范结构" | 盘点；补写实验卡；给出迁移方案，**经你确认后**才移动文件 |

原则：涉及移动或删除文件时，Claude 总是**先提方案、等你确认**；不会悄悄删除任何东西。

## 5. 规范速查

### 5.1 项目结构

```
<project>/
├── PROJECT.md          项目当前状态，≤150 行，每次会话先读
├── CLAUDE.md           常驻规则（init 生成）
├── env.sh              本机的数据、输出、图片路径（私有）
├── data/MANIFEST.md    所有数据的登记表（位置、格式、CRS、分辨率、时间范围、来源、大小）
├── data/processed/     只放小文件（<~50 MB）
├── experiments/EXP-001-name/   私有：CARD.md、结果、scratch/
├── code/               公开 = GitHub 仓库（见 5.8）
├── figures/            稿件用图（脚本输出到这里）
├── manuscript/         稿件（见 5.3）
└── archive/INDEX.md    归档索引，一行一条
```

- 遥感影像、点云、模型权重等**大文件不放进项目**，只在 `MANIFEST.md` 里登记路径和元数据。项目通常在同步盘上。
- 所有代码都在 `code/` 里；项目根目录不放脚本。随手试的探索代码放私有的 `experiments/EXP-…/scratch/`。

### 5.2 实验卡（一页）

Question / Setup / **Result（一句话 + 关键数字）** / Evidence（图表及其生成脚本） / **Decision（adopt / discard / follow-up）**。
写不出一句话结论，说明这个实验还没分析完。

### 5.3 稿件与版本

```
manuscript/
├── 01_main_vN.tex  01_supplementary_vN.tex  02_references.bib
├── figures/  tables/  sync_figures.sh
├── VENUE.md                当前目标期刊及其要求清单
├── versions/INDEX.md       快照表 + 投稿历史
│   └── vNN-<期刊>-<事件>-<日期>/     例：v03-IJGIS-submitted-2026-11-02
└── reviews/
    ├── R1-comments.md ↔ R1-response.md               内审轮次（导师、合作者）
    └── IJGIS-R1-comments.md ↔ IJGIS-R1-response.md   期刊返修轮次
```

- **vN 表示"正在改的第 N 版"**。到里程碑时把 vN 冻结成快照，活稿改名为 v(N+1)。永远只有一份活稿，不出现 `_final`、`_old` 这类副本。
- **哪些算里程碑**：完整初稿、一轮修改结束（回复写完）、投稿、重投、接收。不按会话打快照；被拒本身也不打快照，只记进投稿历史。
- **换期刊**：版本号不重置。新期刊的要求逐项写进 VENUE.md，包括模板、字数、匿名、引用格式、各类声明、图件要求。

### 5.4 作图规范（以印刷尺寸为准）

| 项目 | 规定 |
|---|---|
| 宽度 | 单栏 84 mm，通栏 180 mm；高度连图注不超过 240 mm（AAG Annals） |
| 字体 | **全部 Aptos**，包括 λ、α 等数学符号 |
| 字号 | 面板标题 9 pt · 正文 / 图例 7 pt · 最小 6.5 pt（AAG 要求 >6 pt） |
| 面板标题 | **a** Pecos River basin：粗体小写字母 + 常规体标题，同一行；结果面板直接写结论 |
| 线宽 | ≥0.3 pt |
| 分辨率 | 600 dpi；LaTeX 用矢量 PDF；投稿用 CMYK TIFF |
| 颜色 | 每个项目在 `plotstyle.PALETTE` 定义一次，含义全文固定；转灰度后仍能区分 |
| Affinity 作图 | 文档宽度直接设成 84 或 180 mm，**不要在大画布上画完再缩小** |

### 5.5 图文件命名

- `fig_<主题>` 是正文图，`figS_<主题>` 是补充材料图；表格同理用 `tab_` / `tabS_`。
- 全小写，多个词用连字符连接，例如 `fig_flood-results.pdf`、`figS_alpha-sweep.pdf`。
- 同一张图的 .pdf、.png、`src/*.afdesign` 和 LaTeX 标签（`fig:flood-results`）都用同一个名字。
- **文件名里不带图号、版本或日期**。图号由 LaTeX 编，调整顺序不用改名；旧版本的图在快照里。
- 投稿文件 `LouFigure1.tif` 由脚本按正文顺序自动生成，不用手动命名。

### 5.6 图注

```latex
% source: figures/fig_flood-results.pdf <- experiments/EXP-012-flood/plot.py (CARD: EXP-012)
\caption{Standard CRC misses floods in flash-flood regions; GeoCRC evens out the misses.
\panel{a}Share of floods not warned per region, 2007--2018, $\alpha=0.3$ (grey, at $\alpha$; red, above).
\panel{b}Days on alert per basin-year.}
\label{fig:flood-results}
```

- 第一句写这张图的结论。
- 每个面板用 `\panel{x}` 开头，换期刊时只需改这一个宏。
- 图例说明写成"颜色或线型, 含义"，并给出时段、区域、参数。
- 每张图上方加一行 `% source:` 注释，写明生成脚本和对应实验卡。

### 5.7 参考文献

- **不凭记忆写 bib 条目**，统一用 `--lookup` 从数据库生成。
- 查不到的条目加 `unverified = {原因}`，正文对应句子用 `\pending{}` 标成橙色。
- 投稿和返修前必须通过核查，并做一次引用内容核对。

### 5.8 开源代码：`code/` 文件夹

```
code/                         = GitHub 仓库，里面全部公开
├── src/<package>/            核心方法（可 pip install，不依赖具体实验）
├── src/paperfigs/            论文辅助：plotstyle.py（作图样式）、paths.py（路径）
├── experiments/EXP-003-flood/  该实验的脚本，与私有的 experiments/EXP-003-flood/ 同名
├── examples/                 quickstart.py + 小示例数据（<~1 MB）
├── docs/                     项目页 index.html（+ supplement.html）、.nojekyll
└── README.md LICENSE pyproject.toml requirements.txt .gitignore
```

- **规则**：`code/` 里全部公开，私有的一律不进。实验卡、PROJECT/CLAUDE/MANIFEST、tex/bib、审稿意见、草稿、幻灯片、数据和结果都不放进来。
- **脚本放哪里**：结果会写进实验卡、图、表或论文的脚本，都放 `code/experiments/`；随手试的探索代码放私有的 `scratch/`，有结果依赖它时再挪进 `code/`。
- **路径**：脚本不写死路径，统一用 `paperfigs.paths`（`data_dir`、`out_dir`、`fig_dir`）。别人 clone 下来直接能跑，结果写到 `code/out/`；你先 `source env.sh`，结果就写回私有的 `experiments/EXP-…/`，和实验卡放在一起。
- **git**：用 `git init --separate-git-dir=<本地非同步路径>`，仓库数据不放在同步盘上（同步盘会损坏 `.git`）；`code/.git` 只是一个指针文件。
- **README**：按模板写，其中"复现论文"表要把每张图、每张表对应到一条命令，并列出每个 `code/experiments/` 目录。
- **与稿件版本对齐**：每个对外快照给代码打同名 tag，并在 `versions/INDEX.md` 记下 commit 号。
- **双盲审稿**：只给匿名镜像链接，不给 GitHub 或 GitHub Pages 链接（都含用户名）；推送前用 `check_release.py --anonymous` 检查。
- **接收后**：恢复作者信息，从 camera-ready 的 tag 发 GitHub release，存档到 Zenodo 拿 DOI，加 `CITATION.cff`。
- **推送需要你同意**：本地 commit 可以照常做；推送、新建 GitHub 仓库、公开仓库、更新匿名镜像，都等你明确说了才做。

## 6. 四个检查脚本

以下 `$S` 代表 `~/.claude/skills/research-project-management/scripts`。

**图件检查**：按印刷尺寸检查字号、字体、dpi、命名；有不达标就返回退出码 1。

```bash
python3 $S/check_figures.py manuscript/01_main_v2.tex
```

```bash
python3 $S/check_figures.py --single fig_concept manuscript/01_main_v2.tex
```

第二条把 `fig_concept` 按单栏 84 mm 检查。

**投稿图导出**：按正文中的出现顺序生成 `LouFigure1.tif`、`LouFigureS1.tif`……（CMYK，600 dpi）。

```bash
sh $S/export_submission_figures.sh Lou submission/figures manuscript/01_main_v2.tex
```

**参考文献核查**：

```bash
python3 $S/check_references.py manuscript/01_main_v2.tex manuscript/01_supplementary_v2.tex
```

```bash
python3 $S/check_references.py --report manuscript/REFERENCES_AUDIT.md manuscript/01_main_v2.tex
```

```bash
python3 $S/check_references.py --lookup 10.1038/s41586-019-0912-1
```

`--lookup` 也接受 arXiv 号或论文标题。

| 结果 | 含义 | 怎么办 |
|---|---|---|
| **FAIL** | 正文引用了但 bib 里没有；DOI 不存在；DOI 指向别的论文；arXiv 号错误；数据库里找不到（疑似编造）；已撤稿 | 投稿前必须修好 |
| **WARN** | 作者或年份与记录不符；预印本已正式发表；书或报告查不到；标了 unverified | 人工核对 |
| **ERROR** | 数据库没响应（限流或网络问题） | 不是结论，稍后重跑 |

- 结果缓存 30 天。第一次跑几十条约 1–2 分钟，之后几秒。
- 只访问 Crossref、DataCite、arXiv、OpenAlex 的公共接口，不需要账号，也不会发送你的邮箱。

**开源前检查**：检查 git 将要发布的所有文件，只读，不改动任何东西。

```bash
python3 $S/check_release.py code/
```

```bash
python3 $S/check_release.py code/ --anonymous --names "姓氏,单位缩写,单位全称"
```

| 结果 | 含义 |
|---|---|
| **FAIL** | 私有文件进了 `code/`；文件超过 25 MB；密钥或令牌；个人机器路径（`/Users/<名字>`、同步盘路径）；Python 语法错误；匿名模式下出现身份信息（自动从 git 配置和 GitHub 用户名收集，再加上 `--names`） |
| **WARN** | 文件超过 5 MB；超过 1 MB 的数据或模型文件；个人默认路径（`Path.home() / "…"`）；跳出仓库的 `../../`；带输出的 notebook；草稿或备份命名；`docs/` 里的非网页文件；README 复现表漏写的实验；邮箱地址 |

## 7. 个性化设置

这些默认值反映作者本人的习惯。分享给他人或换环境时，改下面这些地方即可：

| 内容 | 位置 |
|---|---|
| 作者信息（姓名、邮箱、单位） | `assets/manuscript/01_main_v1.tex` 的 author block |
| LaTeX 版式（默认 elsarticle） | 同上；换期刊时按 VENUE.md 更换 |
| 字体（Aptos）、字号、宽度、配色 | `assets/code/plotstyle.py` 顶部常量；同步修改 `references/figure-standard.md` |
| 本机数据和输出路径 | 每个项目根目录的 `env.sh`（init 时生成） |
| 代码许可证 | init 时会问，默认 MIT |
| 检查标准 | `check_figures.py` 参数：`--font`、`--min-pt`、`--width-mm`、`--dpi` |
| 投稿文件名中的姓氏 | `export_submission_figures.sh` 的第一个参数 |
| Crossref 礼貌池（可选，限流更宽松） | 设环境变量 `CROSSREF_MAILTO=你的邮箱` |

修改 skill 后要重新安装（`sh install.sh`），或直接改 `~/.claude/skills/research-project-management/` 里的文件。

## 8. 与其他 skill 的配合

| skill / 插件 | 分工 |
|---|---|
| **nature-figure**（nature-skills） | 负责画图（Python）；本 skill 提供尺寸、字体、命名规范和检查 |
| **ARS `/ars-revision-coach`** | 解析审稿意见、起草回复内容；本 skill 管文件配对和版本 |
| **ARS `/ars-disclosure`** | 生成 AI 使用声明；VENUE.md 清单会提醒你做这一项 |
| **ARS `/ars-citation-check`** | 检查引用格式和一致性；本 skill 的脚本负责查数据库，确认文献真实存在 |

都不是必需的。没装时，本 skill 的其他功能照常可用。

## 9. 常见问题

**Q：说了"收尾"，但 skill 没有被调用？**
新开一个会话再试，或直接说 "use the research-project-management skill to checkpoint"。另外，日常规则写在项目的 CLAUDE.md 里，即使 skill 没触发也会生效。

**Q：matplotlib 找不到 Aptos？**
安装字体后，删除 matplotlib 的字体缓存再重开 Python。用这条命令查看缓存目录：

```bash
python3 -c "import matplotlib; print(matplotlib.get_cachedir())"
```

删掉该目录里的 `fontlist-*.json` 即可。

**Q：参考文献核查出现很多 ERROR（HTTP 429）？**
这是 Crossref 限流，短时间内连续跑多次就会出现。等几分钟重跑即可，已查过的条目走缓存，不会重复请求。

**Q：投 AAG 必须用 Arial 吗？**
AAG 原文写的是 "a standard font such as Arial or Times New Roman"。Aptos 不在其中，投稿前建议向编辑确认。如需改用 Arial，在 `plotstyle.py` 里把 `FONT` 改掉，检查时加 `--font Arial`。

**Q：稿件写在 Overleaf 上怎么办？**
本地放一个 `manuscript/POINTER.md`，记录 Overleaf 链接和当前版本号。到里程碑时从 Overleaf 下载源码 zip 和 PDF，存成快照。详见 `references/manuscript-versioning.md` §6。

**Q：旧项目能用吗？**
可以，说 "adopt 这个项目"。Claude 会先盘点、给出迁移方案，确认后才动文件。
如果旧项目整个根目录就是 git 仓库、用白名单 `.gitignore` 挑公开文件，迁移时会建议把工作区移到 `code/`，并保留提交历史。

**Q：换了一台电脑，`code/` 里的 git 不能用了？**
`code/.git` 是指向本机仓库数据的指针文件。在新电脑上用 `--separate-git-dir` 重新 clone 一份到本地非同步目录，或者把 `code/.git` 改成指向新的本地克隆。详见 `references/code-release.md` §2。

**Q：脚本找不到数据，或者结果写到了 `code/out/`？**
运行前没有 `source env.sh`。这时脚本用的是仓库内的默认路径，也就是别人 clone 下来后的行为。

## 10. 版本记录

**1.1（2026-11-18）**
- 新增公开的 `code/` 文件夹（= GitHub 仓库）：方法、复现脚本、示例、项目页；实验脚本与私有的实验卡、结果分开放，同名对应
- 新增 `paths.py` + 私有 `env.sh`：公开代码里不再有机器路径，clone 下来直接能跑
- git 数据放在同步盘之外（`--separate-git-dir`）
- 新增 `check_release.py`：检查私有文件、超大文件、密钥、个人路径、语法错误，以及双盲期间的身份信息
- 稿件快照给代码打同名 tag，INDEX 里记录 commit 号；VENUE.md 加入代码可用性检查项
- 新增 release 模式；init、checkpoint、audit、adopt、snapshot 都接入 `code/` 规则
- `plotstyle.py` 移到 `code/src/paperfigs/`
- 已测试：埋入的 11 种发布问题全部检出；按模板搭的干净仓库 0 条问题；在一个真实项目上没有误报 FAIL，并检出一处代码注释泄露单位信息

**1.0（2026-10-28）**
- 项目结构、定容 PROJECT.md、实验卡、数据登记、归档索引
- init / checkpoint / audit / adopt / snapshot / venue switch / figures / references 八种模式
- 作图规范（Aptos，AAG 印刷尺寸）、图文件命名、图注模式、`plotstyle.py`
- `check_figures.py`、`export_submission_figures.sh`
- 稿件命名 `01_main_vN`、快照后版本号 +1、审稿轮次配对、VENUE.md、投稿历史
- `check_references.py`：tex 与 bib 一致性、存在性、元数据、撤稿、预印本、引用内容核对（`--abstracts`）、`--lookup`
- 已测试：故意埋入的 7 类伪造或错误引用全部检出；一个真实项目的 62 条引用没有误报 FAIL
