# Recurring Character Diary Comic Skill 中文使用指南

[English](recurring-character-diary-comic.md) | [简体中文](recurring-character-diary-comic.zh-CN.md)

[返回 Craft Skills 集合](../README.md)

这是一个实验性的 Codex Skill，用于围绕已有且获授权的固定角色，创建、审核和
局部修复 4–8 格个人日记漫画。

它不是一条漫画风格 Prompt，也不是从零设计角色、模仿某位在世艺术家或自动发布内容
的工具。它把故事事实、角色身份、跨格状态、方向关系和精确对白变成可检查的
合同，比较三种故事驱动的页面骨架，并默认把选中的完整页面一次生成。

**状态：v0.2 实验版。** 结构化工作流、合成器和行为测试不保证黑盒图像模型
一定生成正确画面，也不代表任何成品已经获得发布授权。

## 什么时候使用

同时满足这些条件时使用：

- 已有原创、公版或明确获授权的固定角色，以及可用的身份参考；
- 输入是可以压缩成 4–8 格完整短篇的生活趣事、对话、梦或个人观点；
- 角色身份、精确对白、跨格状态或物理关系需要被验证，而不能只交给一条长 Prompt。

不要用于单独设计角色、科普解释漫画、信息图、单张插画、通用 Meme、未经授权使用仍受
版权保护的系列 IP 角色、模仿某位在世艺术家、水印或社交平台发布。公版角色、有明确
许可的系列角色，以及合法的历史艺术家参考并不被一概排除。若没有可用的固定角色身份，
工作流会停下来返回角色档案要求，而不是把第一次随机生成的长相偷偷变成长期 IP。

## 三种模式

| 模式 | 目标结果 |
|---|---|
| `Create` | 锁定故事与视觉合同，比较三种页面骨架，整页原生生成并对最终成品做双轴检查。 |
| `Audit` | 只审核已有页面的身份、人体、文字、关系、连续性和版式证据，不擅自修改。 |
| `Repair` | 先审核，优先做一次可验证的整页局部修复；只有通过降级门后才重构独立分格。 |

## 安装

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

中文加字还需要本机具备许可合适的 CJK 字体；仓库不分发字体。示例 manifest
只是结构模板，不是无需填写即可运行的成品夹具。

## 如何调用

需要稳定路由时，建议明确写出 Skill 名称和模式。

### Create

```text
使用 $recurring-character-diary-comic 的 Create 模式。

我拥有附件中固定原创角色的生成和编辑权。请把“她为了不忘带午饭，把饭盒放在
门口，出门时却顺手跨了过去”做成 5 格日记漫画。

先锁定故事、角色不变量和全部对白；画出三种结构不同的页面骨架，在工作尺寸和 25%
下比较后选择一种，再把完整页面一次生成。高风险手部、方向关系和状态变化只增加
提示词与放大检查，不要静默切成逐格拼版。不要添加 Logo、水印或发布内容。
```

### Audit

```text
使用 $recurring-character-diary-comic 的 Audit 模式审核附件中的最终漫画，不要修改
图片。请在原始分辨率下检查角色一致性、对白、手部、方向性物体、跨格状态和阅读
顺序；分别报告 contract_fidelity、editorial_layout 和 exposure。
```

### Repair

```text
使用 $recurring-character-diary-comic 的 Repair 模式。

只处理第 4 格主角左手多出一根手指的问题。其他格、角色脸、服装、对白、气泡、
版式和颜色必须保持不变。如果编辑工具无法证明目标区域外保持不变，只返回修复
规格，不要用整页重生冒充局部修复。
```

## 工作流会强制什么

1. **题材门。** 优先选择可见行为、未说出口的心理和轻微揭示，而不是抽象口号。
2. **故事合同。** 生图前锁定可观察节拍、角色、道具、状态变化、说话人、标点和
   逐字对白。
3. **视觉合同。** 为关键角色、物体、状态和关系设置稳定 ID，并分为故事关键
   `S0`、身份关键 `S1` 和可替换构图偏好 `S2`。
4. **页面结构选择。** 比较三种结构不同的页面骨架，在工作尺寸和 25% 下选择故事最合适的一种。
5. **风险聚焦。** 风险决定提示词、放大 QA 和停止条件，不自动拆格。
6. **整页原生默认。** 分格、场景、人物、道具、气泡、逐字对白、纸张、色彩和留白一起生成。
7. **实际产物 QA。** 对同一最终 hash 在原始分辨率和 25% 下分别检查合同与艺术编排。
8. **有限兜底。** 优先一次局部修复；只有文字失败才做全页确定性加字，只有满足公开降级门才重构面板。

## 技术通过，不等于适合展示

Skill 把两个审核轴分开：

- `contract_fidelity` 检查故事、身份、人体、关系、连续性、精确文字和最终文件
  hash；
- `editorial_layout` 检查阅读路径、节拍层级、分格形状节奏、边框语言、反应格、
  留白意图、结尾强调和缩略图轮廓。

一页漫画可能技术合同全部通过，但因为统一卡片宫格、像误裁的反应条、没有叙事
作用的死白或结尾权重太弱，而不能作为公开案例。`accepted`、`showcase-ready`、
用户认可和发布授权始终是四个独立状态。

## 确定性合成

可选合成器默认只在一张已接受的完整无字页上渲染闭合软尾气泡与精确简体中文。
只有明确接受重构降级后才拼接独立分格。它验证源图 hash、几何、保护区和字体；
未知 manifest 字段直接失败。

```sh
python3 \
  "${CODEX_HOME:-$HOME/.codex}/skills/recurring-character-diary-comic/scripts/compose_panels.py" \
  --manifest /path/to/compositor-manifest.json
```

合成器会记录输入、字体快照、运行环境版本、几何参数和输出 hash。只有在相同已
记录的操作系统与运行时构建，以及相同 Python、Pillow、底层栅格库、字体字节、
manifest 和面板字节下，才主张字节级复现；不承诺不同平台或底层库之间得到
bit-identical 文件。

## 公开评测

公开测试说明位于
[`evals/recurring-character-diary-comic`](../evals/recurring-character-diary-comic/README.md)。
它覆盖路由、Create/Audit/Repair 边界、权利安全、故事与视觉合同、整页原生路线、
关系证据、页面结构选择和双轴发布门。

```sh
python3 -m pip install -r \
  evals/recurring-character-diary-comic/requirements.txt

python3 evals/recurring-character-diary-comic/self_test_validate_cases.py
python3 evals/recurring-character-diary-comic/validate_cases.py \
  evals/recurring-character-diary-comic/cases.yaml
python3 scripts/check_release.py
```

依赖实际图像的用例被有意标为 `deferred`，因为公开包不分发内部栅格夹具。
`deferred` 既不是通过也不是失败，不能被描述成已经完成视觉测试。

## 来源、权利和媒体边界

本次发布只包含方法文字、代码、模板与公开安全的行为测试，不包含用户角色、内部
held-out 页面、教程生产素材、生图历史、下载的来源媒体或私人故事。

生产账本在完成审阅与脱敏前应视为私有构建证据。即使漫画成品可以公开，账本中
仍可能包含本地来源文件、字体与输出路径。

使用者必须确认输入角色、参考图、专属标记和文字具备所需的生成、编辑及发布权限。
Apache-2.0 只覆盖仓库有权许可的原创材料，不自动覆盖用户输入、第三方字体、人物
肖像、品牌、模型输出或链接内容。详见
[THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md)。

## 包结构

```text
skills/recurring-character-diary-comic/
├── SKILL.md
├── agents/openai.yaml
├── references/
├── scripts/
└── templates/

evals/recurring-character-diary-comic/
├── README.md
├── cases.yaml
├── requirements.txt
├── self_test_validate_cases.py
└── validate_cases.py
```

## 许可证

仓库原创材料采用 [Apache License 2.0](../LICENSE)，并受上述权利边界约束。
