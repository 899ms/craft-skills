# recurring-character-diary-comic

[简体中文](README.md) | [English](README.en.md)

围绕已有且获授权的固定角色，创建、审核或局部修复 4–8 格个人日记漫画的
Agent Skill。

它不是一条“画成手绘漫画”的长 Prompt，而是一套可检查的制作流程：先锁定故事、
角色身份、跨格状态和逐字对白，再按风险选择生成路线；画面通过原始分辨率检查后，
才进入确定性拼版、中文加字和最终成品验收。

[![原创固定角色日记漫画不规则分镜案例](../../assets/examples/recurring-character-diary-comic/recurring-character-diary-comic-cover.png)](../../docs/recurring-character-diary-comic.zh-CN.md)

**状态：v0.1 实验版。** 技术验收、适合公开展示、用户认可和发布授权始终是四个
独立状态。Skill 不会因为生成命令成功就宣布漫画完成。

## 它解决什么问题

让 Agent 画一页漫画很容易，稳定续画同一个角色并证明细节正确则很难。常见失败包括：

- 角色跨格换脸、发型或服装漂移；
- 手、道具接触、纸张方向或物理因果关系错误；
- 对白被改写、错别字、说话人归属错误；
- 整页重画被包装成“局部修复”；
- 每格都做成相同圆角卡片，技术正确却没有漫画节奏；
- 只检查 Prompt 或缩略图，没有检查实际输出像素。

本 Skill 把这些风险变成显式合同、有限预算、分阶段产物和可复核的 QA 记录。

## 什么时候使用

同时满足以下条件时适合使用：

- 已有原创、公版或明确获授权的固定角色；
- 有可用的角色身份参考，而不是临时随机生成一张脸；
- 输入能压缩成 4–8 格完整短篇，例如生活趣事、对话、梦或个人观点；
- 角色身份、精确对白、跨格状态或物理关系需要被验证。

不要用于：

- 从零设计角色或只制作角色设定表；
- 科普解释漫画、信息图、单张插画或通用 Meme；
- 模仿某位在世艺术家的风格；
- 未经授权使用仍受版权保护的系列角色、品牌或专属标记；
- 水印、社交平台上传、提交或发布。

如果没有合格的固定角色参考，工作流会返回角色档案要求并停止，不会把第一次随机
生成的长相偷偷变成长期 IP。

## 三种模式

| 模式 | 适合的任务 | 主要交付 |
|---|---|---|
| `Create` | 把趣事、梦、对话或观点做成新短篇 | 故事合同、视觉合同、分格计划、候选格、合成页和双轴 QA |
| `Audit` | 只检查已有角色页、分格或最终漫画 | 逐格证据、缺陷等级、`pass` / `fail` / `not-verified`，不擅自修改 |
| `Repair` | 修复一个或多个已定位缺陷 | 先审核；优先替换失败分格，只有工具能证明区域外不变时才做像素级局部修复 |

## 安装

克隆仓库，然后只复制这个 Skill：

```sh
git clone https://github.com/ZSeven-W/craft-skills.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R craft-skills/skills/recurring-character-diary-comic \
  "${CODEX_HOME:-$HOME/.codex}/skills/"
```

如果安装后没有立即发现 Skill，请重启或重新加载 Agent 会话。

确定性合成器是可选运行组件，需要 Python 3.10 或更高版本，以及锁定的 Pillow：

```sh
python3 -m pip install -r \
  craft-skills/skills/recurring-character-diary-comic/scripts/requirements.txt

python3 \
  craft-skills/skills/recurring-character-diary-comic/scripts/self_test_compositor.py
```

中文加字还需要本机具备许可合适的 CJK 字体；仓库不分发字体。示例 manifest 只是
结构模板，不是无需填写即可运行的成品夹具。

## 30 秒开始使用

最稳定的方式是在请求里同时写出 Skill 名称、模式、权利状态和验收要求：

```text
使用 $recurring-character-diary-comic 的 Create 模式。

我拥有附件中固定原创角色的生成和编辑权。请把“她为了不忘带午饭，把饭盒放在
门口，出门时却顺手跨了过去”做成 5 格日记漫画。

先锁定故事、角色不变量和全部对白；无字逐格生成，通过原始分辨率检查后再确定性
拼版和加字。不要添加 Logo、水印或发布内容。
```

### Audit 示例

```text
使用 $recurring-character-diary-comic 的 Audit 模式审核附件中的最终漫画，不要修改
图片。请在原始分辨率下检查角色一致性、对白、手部、方向性物体、跨格状态和阅读
顺序；分别报告 contract_fidelity、editorial_layout 和 exposure。
```

### Repair 示例

```text
使用 $recurring-character-diary-comic 的 Repair 模式。

只处理第 4 格主角左手多出一根手指的问题。其他格、角色脸、服装、对白、气泡、
版式和颜色必须保持不变。如果编辑工具无法证明目标区域外保持不变，只返回修复
规格，不要用整页重生冒充局部修复。
```

## 建议提供的输入

```text
模式：[Create / Audit / Repair]
角色权利：[原创 / 公版 / 已获授权]
角色参考：[附件或路径]
故事或待检查成品：
必须保留：
精确对白与说话人：
目标格数和尺寸：
禁止元素：
希望检查或修复的具体字段：
```

字段不完整时，Agent 可以声明合理假设；但角色权利、身份参考、锁定对白和关键物理
关系不能靠猜测补齐。

## 核心工作流

1. **题材门**：选择可见行为、未说出口的心理和轻微揭示，拒绝只有口号的题材。
2. **角色档案**：锁定可识别身份、可变项、可选标记和禁止漂移。
3. **故事合同**：写清每格可观察事件、说话人、逐字对白、道具和状态变化。
4. **视觉合同**：把约束分成故事关键 `S0`、身份关键 `S1` 和可替换构图偏好 `S2`。
5. **风险路由**：按人物、方向物体、手物交互、接触与因果关系选择生成路线。
6. **版式预检**：先证明目标裁切能保住脸、手、动作、说话人锚点和保护区。
7. **先画后加字**：默认生成无字、无气泡画面；通过后再确定性拼版和加入中文。
8. **实际产物 QA**：分别检查原始单格、目标裁切、无字整页和加字最终页。

### 风险路线

| 路线 | 使用条件 |
|---|---|
| `whole-page` | 只有低风险短篇且全部资格门通过时才允许尝试一次；多格失败就切换逐格生成 |
| `panel-by-panel` | 多人物、方向性纸张或屏幕、手物交互、角色接触和跨格状态默认使用 |
| `key-panel-first` | 先验证决定性因果、插入、穿过、接触或高风险格；证明不了就尽早停止 |

随机生成有总预算、每格上限和连续无改善停止条件。换一个 run ID 不会重置预算。

## 技术通过，不等于适合展示

最终页必须分开记录两个审核轴：

- `contract_fidelity`：故事、身份、人体、关系、连续性、精确文字和最终文件 hash；
- `editorial_layout`：阅读路径、节拍层级、分格形状节奏、边框语言、反应格、留白
  意图、结尾强调和缩略图轮廓。

一页漫画可能技术合同全部通过，却因为统一卡片宫格、像误裁的反应条、没有叙事作用
的死白或结尾权重太弱，而不能作为公开案例。

## 确定性拼版与中文加字

可选合成器会验证源图 hash、裁切、frame、保护区和字体输入，拼接独立分格，再渲染
已批准的气泡与精确简体中文。它支持矩形和不规则分格、有限旋转、显式重叠、
z-order 与确定性纸张底纹；未知 manifest 字段会直接失败。

```sh
python3 \
  "${CODEX_HOME:-$HOME/.codex}/skills/recurring-character-diary-comic/scripts/compose_panels.py" \
  --manifest /path/to/compositor-manifest.json
```

只有在相同已记录的操作系统和运行时构建，以及相同 Python、Pillow、底层栅格库、
字体字节、manifest 和面板字节下，才主张字节级复现；不承诺跨平台得到
bit-identical 文件。

## 交付物与停止条件

Create 通常产生：

- 角色档案与授权状态；
- 锁定故事、分格计划和视觉任务合同；
- 被接受或拒绝的候选格与原图 QA；
- 合成 manifest、无字整页、加字最终页和 composition ledger；
- `contract_fidelity`、`editorial_layout` 与 `exposure` 结论。

遇到缺失身份参考、不可见的关键关系、预算耗尽、连续无改善、无法约束的局部编辑或
无法核实的最终像素时，Skill 会停止并报告阻塞项，而不是降低合同迎合图片。

## 验证

在仓库根目录运行：

```sh
python3 -m pip install -r \
  evals/recurring-character-diary-comic/requirements.txt

python3 evals/recurring-character-diary-comic/self_test_validate_cases.py
python3 evals/recurring-character-diary-comic/validate_cases.py \
  evals/recurring-character-diary-comic/cases.yaml
python3 skills/recurring-character-diary-comic/scripts/self_test_compositor.py
python3 scripts/check_release.py
```

公开 eval 中依赖内部图像的用例会标为 `deferred`。这表示公开包没有携带所需栅格
夹具，不表示测试已经通过或失败。

## 目录结构

```text
skills/recurring-character-diary-comic/
├── README.md                   # 中文默认入口
├── README.en.md                # English entry
├── SKILL.md                    # Agent 工作流与路由
├── agents/openai.yaml          # Skill 元数据
├── references/                 # 角色、故事、视觉合同、QA 与拼版规范
├── scripts/                    # 确定性合成器及自测
└── templates/                  # 合同和 manifest 模板

evals/recurring-character-diary-comic/
├── README.md
├── cases.yaml
├── self_test_validate_cases.py
└── validate_cases.py
```

## 权利与发布边界

仓库只包含方法文字、代码、模板、公开安全的行为测试和生成原创案例图，不包含用户
角色、内部 held-out 页面、教程生产素材、生图历史、下载的来源媒体或私人故事。

使用者必须确认输入角色、参考图、专属标记、字体和文字具备所需的生成、编辑与发布
权限。Apache-2.0 只覆盖仓库有权许可的原创材料，不自动覆盖用户输入、第三方字体、
人物肖像、品牌或模型输出。

## 继续阅读

- [Agent 工作流与触发边界](SKILL.md)
- [中文完整方法说明](../../docs/recurring-character-diary-comic.zh-CN.md)
- [English guide](../../docs/recurring-character-diary-comic.md)
- [公开 eval 说明](../../evals/recurring-character-diary-comic/README.md)
- [返回 Craft Skills 集合](../../README.md)
- [许可证](../../LICENSE) · [第三方声明](../../THIRD_PARTY_NOTICES.md)
