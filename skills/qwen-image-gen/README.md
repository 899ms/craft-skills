# Qwen Image Gen

面向已有 Qwen-Image 部署的生图与图片编辑 Skill。把需求拆成提示词、参考图关系、画幅参数和验收标准。

**v0.1.0 实验版候选。** 当前 Agent 负责改写；不需要再下载提示词增强模型。自动生成仍需用户已有可用的 Qwen 连接。

## 使用

```text
使用 $qwen-image-gen，把我的柠檬茶海报需求整理成提示词。
只出现“夏日柠檬茶”“¥19”两行文字，3:4。先给提示词，不生成。
```

```text
使用 $qwen-image-gen，先看参考图，把人物转成正面站姿。
保留人物身份、服装和环境，允许肩部、手臂和褶皱随动作变化。
```

- [完整中文指南](../../docs/qwen-image-gen.zh-CN.md)
- [Agent 工作流](SKILL.md)
- [研究 A/B 原图与参数](assets/examples/ab/README.md)
- [人像原图与提示词](assets/examples/portraits/README.md)
- [测试与边界](../../evals/qwen-image-gen/VALIDATION.md)
- [可选应用集成：共享运行模块](references/shared-runtime.md)（Node.js 18+，不联网）

可选脚本 `scripts/prepare_workbench_request.py` 只在本地构造一种工作台协议的请求，不联网、不改写、不生成。其单参考图、约1MP编辑和2048像素上限属于适配器，不能推导为 Qwen 模型的上限。

官方 PE 权重和系统提示词全文不在包内。复杂肢体、人物一致性和工作流参数仍要实际看图验收。
