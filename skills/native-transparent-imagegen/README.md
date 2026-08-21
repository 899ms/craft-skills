# native-transparent-imagegen

[简体中文](README.md) | [English](README.en.md)

原生生成并验证带 Alpha 通道的透明 PNG/WebP。它面向贴纸、Sprite、角色素材、商品
素材，以及毛发、头发、玻璃等不应依赖事后抠图的细边缘对象。

这个 Skill 不提供“万能透明提示词”，也不把棋盘格当成透明。它逐张生成、检查原始
文件、最多有限重试，并在仍为 RGB 时明确失败；不会调用抠图、色键、分割或本地写入
Alpha 来伪造成功。

- [Agent 工作流与触发边界](SKILL.md)
- [中文完整使用指南](../../docs/native-transparent-imagegen.zh-CN.md)
- [English guide](../../docs/native-transparent-imagegen.md)
- [团子与胡桃第一版毛发案例记录](../../examples/native-transparent-imagegen-tuanzi-hutao.md)
- [返回 Craft Skills 集合](../../README.md)

**状态：v0.1 实验版。** 原生透明能力与宿主工具链仍可能变化；通过 Alpha 元数据
检查也不等于毛发边缘或视觉成品已经通过检查。
