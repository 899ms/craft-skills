# Logo Semantic Fusion Skill 中文使用指南

[English](logo-semantic-fusion.md) | [简体中文](logo-semantic-fusion.zh-CN.md)

[返回 Craft Skills 集合](../README.md)

这是一个实验性的 Codex Skill，适合处理 Logo 构思与评审中的“语义共形”问题：
当两个或更多品牌含义需要共享同一条轮廓、笔画、负空间、字形骨架或模块系统时，
它会帮助 Agent 判断这条路线是否成立，并把概念推进到可验证的结果。

**状态：v0.1 实验版。** 它是一套结构化的概念开发与评审工作流，不能替代品牌
战略、专业品牌设计师、母语文字审核、生产制图、受众测试或商标法律意见。

## 什么时候使用

只在“语义共形”本身就是设计问题时使用。例如：

- 把品牌首字母与产品动作做成同一个不可拆分的标记；
- 判断两个含义是否真的共享结构，而不是把两枚完整图标叠在一起；
- 比较多个候选方向的融合质量、品牌契合度和小尺寸表现；
- 为后续图像或矢量生成写出带验收条件的生产提示词。

不要因为任务提到了 Logo 就自动使用。进入创意前，下面三个条件必须同时成立：

1. 至少有两个值得编码的独立品牌信号；
2. 它们之间存在可信的共享几何结构；
3. 共形不会破坏必要文字的可读性、品类信任或目标尺寸识别。

如果条件不成立，Skill 会明确退出语义共形路线，并建议纯字标、单一符号、抽象
标志或更完整的品牌识别流程。它不适合通用 Logo 生成、完整 VI、插画、包装、
单纯字体选择，以及没有语义共形要求的格式转换或导出任务。

## 四种工作模式

| 模式 | 适合的结果 |
|---|---|
| `design` / `redesign` | 建立并筛选多个共形概念家族；工具允许时，渲染并检查入选方向的实际产物。改版会先锁定必须保留的设计不变量。 |
| `critique` | 评审用户提供的实际标记，报告证据、缺陷、风险与最小必要修改；除非用户要求，不擅自重做。 |
| `compare` | 使用同一 brief、尺寸和硬门槛比较所有候选；允许结论为 `reject all`，不会自行补做新方案。 |
| `prompt-only` | 只输出生产提示词、负向约束与未来验收项；不会生成产物，也不能声称已经完成视觉 QA、相似性筛查或达到生产就绪。 |

## 安装

克隆或下载本仓库，然后把 Skill 文件夹复制到 Codex 的个人 Skill 目录：

```sh
git clone https://github.com/ZSeven-W/craft-skills.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R craft-skills/skills/logo-semantic-fusion \
  "${CODEX_HOME:-$HOME/.codex}/skills/"
```

开发时可以在仓库根目录建立软链接，目标目录必须尚不存在：

```sh
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -s "$PWD/skills/logo-semantic-fusion" \
  "${CODEX_HOME:-$HOME/.codex}/skills/logo-semantic-fusion"
```

如果其他兼容 Agent 使用不同的发现目录，请按该 Agent 的文档放置
`skills/logo-semantic-fusion`。安装后的文件夹名称应保持为
`logo-semantic-fusion`，以匹配 Skill 元数据。

如果安装后没有立即显示，请重启或重新加载 Agent 会话。

## 如何调用

为了让路由更稳定，建议在请求中同时写出 Skill 名称和模式。

### 1. 设计一个新 Logo

```text
使用 $logo-semantic-fusion 的 design 模式，为一个安全交接工具设计单色
App Icon，把字母 N 与 handoff 动作共形。目标尺寸为 16–128 px，禁止使用
握手、链条和盾牌。
```

### 2. 只评审，不重做

```text
使用 $logo-semantic-fusion 的 critique 模式检查我附上的 SVG，判断叶片和
对话气泡是否真正共享结构。只报告问题和最小修改，不要重新设计。
```

### 3. 比较多个候选

```text
使用 $logo-semantic-fusion 的 compare 模式，按同一 brief、品牌契合度、
融合完整性、差异性和小尺寸识别比较 A、B、C。允许 reject all，不要生成
第四个方案。
```

### 4. 只生成生产提示词

```text
使用 $logo-semantic-fusion 的 prompt-only 模式，为「山行」生成“山势 +
路径”共形的中文品牌标志生产提示词。不要修改汉字，并明确说明没有检查实际
产物、视觉 QA 尚未执行。
```

## 建议提供的 brief

信息越明确，Skill 越容易判断语义共形是否适合。可以直接复制下面的模板：

```text
使用 $logo-semantic-fusion 的 [design / critique / compare / prompt-only] 模式。

品牌名与读音：
受众与品类：
品牌承诺与个性：
希望融合的含义：
载体与最小尺寸：
必须保留：
禁止元素：
文字系统：
颜色、背景与无障碍：
交付物：
```

字段不完整时，Agent 可以作合理推断，但必须明确说明会影响结果的假设。对于不
熟悉的文字系统，不能臆造字符、读音或文化含义；生产批准仍需要母语者或文字
专家复核。

## 工作流会强制执行什么

- 先判断语义共形是否适用，再生成概念；
- 建立紧凑的语义清单，核心信号不超过三个，优先保留两个；
- 至少探索 6 个缩略方向、3 个真正不同的概念家族和 3 种融合方法；
- 概念家族必须同时改变语义解释和主轮廓，换颜色或圆角不算新家族；
- 至少一条轮廓、笔画、负空间或模块同时承担两个语义角色；完整图标仍可移动、
  分离，通常说明它只是拼贴；
- 先在黑白条件下解决结构，再考虑颜色；
- 在润色前检查常见品类俗套和方向相似性；这些检查不等于商标法律核查；
- 对实际渲染产物进行目标尺寸、单色、反白、灰度和轮廓检查；
- 允许语义共形是错误策略，并诚实退出。

设计模式使用六项标准评分：品牌契合、融合完整性、经筛查的差异性、小尺寸识别、
单色复现，以及文化与品类安全。任何单项低于 3 分都不能通过；融合完整性和
文化与品类安全至少为 4 分，平均分至少为 3.8。硬门槛始终优先于平均分；没有
完成当前同类标志及结构相似标志筛查时，经筛查的差异性最高只能记 3 分。

## 各模式的交付结构

### `design` / `redesign`

1. 规范化 brief；
2. 适用性结论；
3. 语义清单；
4. 避用清单（avoid map）；
5. 概念家族矩阵；
6. 统一评分；
7. 选中方案的结构原则；
8. 实际产物；若未生成或无法检查，明确记录缺失；
9. QA 结果；未检查实际渲染产物时必须标记 `visual QA not run`；
10. 交付状态与待完成事项。

### `critique`

- 与可见证据对应的发现；
- 各项硬门槛状态；
- `pass`、`revise` 或 `reject`；
- 最小必要修改。

### `compare`

- 使用统一维度的评分表；
- 各候选的硬门槛状态；
- 胜者，或 `reject all`。

### `prompt-only`

- 生产提示词；
- 负向约束；
- 后续验收测试；
- 明确声明未检查实际产物，视觉 QA 和生产就绪均未验证。

## 原创案例

### 主案例：Handoff

[![六个原创 Handoff 语义共形概念家族](../assets/examples/handoff/handoff-concept-sheet.png)](../examples/handoff-hero.md)

入选方向 `Relay Joint H` 让两条分别属于协作者的竖笔共享一个发送—接收横向
连接，从同一结构中读出 `H + transfer + collaboration`。案例包含可编辑 SVG、
响应式微型标记（micro mark）和实际 QA 板。

它目前只能称为“概念阶段的几何暂定通过”；尚未完成当前市场相似性筛查、识别
测试或商标法律核查。

| 中文与陌生文字安全案例 | 缩小回归夹具 |
|---|---|
| [![岫页 Sheltered Page 案例板](../assets/examples/xiuyue/xiuyue-case-board.png)](../examples/chinese-brand-native-review.md) | [![D tool 语义共形 QA 板](../assets/examples/d-tool/d-tool-qa-board.png)](../examples/d-tool-regression.md) |
| 图标让纸页与山体共享几何，但没有修改「岫页」两个汉字。 | D tool 展示基于实际产物的缩小测试；它是回归夹具，不是主品牌案例。 |

仓库还包含两个纯文字演练案例：

- [Rillnote 英文 App Icon 设计案例](../examples/english-app-icon.md)：展示六个概念
  家族，但没有渲染实际产物，因此视觉 QA 必须标记为 `not run`；
- [Trailnest critique-only 案例](../examples/critique-only.md)：在没有实际附件时保持
  结论为暂定判断，并严格遵守“不重做”的范围。

## 已知边界与限制

### 商标与原创性

工作流可以识别明显的品类俗套并要求竞品研究，但不会执行完整商标检索、自由
实施（FTO）分析或法律核准。正式采用标记前，应按相关类别与地区完成检索，并在
需要时咨询具备资质的专业人士。

### 非母语文字与文化

不要因为几何看起来合理，就接受模型生成的汉字、偏旁、阿拉伯连写、Indic 文字
塑形或其他陌生文字系统。母语者或文字专家必须复核可读性、读音、含义、笔画
逻辑和文化适配。如果无法完成复核，应把结果标记为“暂定”，并避免投入生产。

### 生产级品牌工作

通过概念评审不等于完成整套品牌识别。响应式 Logo 变体、字体、留白规则、色彩
规范、无障碍、印刷表现、App Store 蒙版、标牌、文件制备与治理仍需针对具体
场景设计和测试。

### 证据纪律

只有实际渲染并检查过的产物，才能声称完成视觉 QA。提示词、SVG 源码或成功的
渲染命令本身都不是视觉证据。在 `prompt-only` 模式或附件无法打开时，必须报告
缺失的证据，不能从指令反推已经通过缩小、反白、灰度或相似性检查。

## 包结构

```text
.
├── skills/logo-semantic-fusion/
│   ├── SKILL.md                 # Agent 工作流与路由
│   ├── agents/openai.yaml       # Skill 列表元数据
│   └── references/              # 方法、评审门槛与溯源说明
├── assets/examples/
│   ├── handoff/                 # 原创主标、概念板与渲染结果
│   ├── xiuyue/                  # 原创文字安全符号与案例板
│   └── d-tool/                  # 哈希锁定的视觉回归夹具
├── examples/
│   ├── handoff-hero.md          # 从概念到 QA 的视觉演练
│   ├── english-app-icon.md      # 新设计演练
│   ├── chinese-brand-native-review.md
│   ├── critique-only.md         # 不擅自重做
│   └── d-tool-regression.md     # 回归案例，不是主品牌身份
├── evals/logo-semantic-fusion/
│   └── cases.yaml               # 10 个行为与边界测试用例
├── scripts/check_release.py     # 确定性发布卫生检查
├── THIRD_PARTY_NOTICES.md
└── LICENSE
```

`examples/` 与 `assets/examples/` 中的文件都是虚构教学演示，不是已批准的品牌
资产，也不代表完成商标法律核查。

## 验证

在仓库根目录运行：

```sh
python3 scripts/check_release.py
```

检查器会验证必要包结构、Skill 元数据、Markdown 链接、常见密钥模式、本机路径、
Agent 元数据，以及已批准视觉资产的精确哈希、大小、尺寸和 SVG 安全结构。未列入
白名单的媒体文件仍会使发布失败。这些确定性检查不证明设计质量。

当路由、模式行为或验收门槛发生变化时，还需要在目标 Agent 上实际运行
`evals/logo-semantic-fusion/cases.yaml`。这里的 10 个用例是行为测试契约，不能在
尚未运行时描述成“10 项模型评测全部通过”。

视觉前向测试应使用内置案例没有覆盖的新 brief，在请求尺寸下检查真实输出，记录
失败模式，以及是否决定退出语义共形路线。

## 来源与媒体政策

这套方法的研究过程部分受到 BIGFISH 公开教育视频启发。署名和来源链接列在
[THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) 中。

**本仓库不包含下载的视频、音频、封面、截图、字幕或转录文本、平台元数据或
第三方 Logo 素材。** `assets/examples/` 中的视觉内容是项目原创教学资产，其公开
路径与哈希由发布检查器锁定。不要把本地来源媒体档案加入 fork 或发布包；
`.gitignore` 会额外阻止常见原始媒体目录和格式。

## 许可证

项目原创内容采用 [Apache License 2.0](../LICENSE) 许可。该许可证不授予第三方
内容、名称、商标、链接材料或平台品牌的相关权利；详见
[THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md)。
