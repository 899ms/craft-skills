# native-transparent-imagegen

[简体中文](README.md) | [English](README.en.md)

Generate and verify PNG or WebP assets with native alpha transparency. The skill targets
stickers, sprites, character assets, product cutouts, and fine-edged subjects such as fur,
hair, or glass where post-generation background removal is unacceptable.

This is not a magic transparency prompt and it never treats a checkerboard as proof. It
generates one asset at a time, validates the untouched original, retries within a fixed limit,
and fails clearly when the file remains RGB. It does not use matting, chroma key, segmentation,
or locally synthesized alpha to manufacture success.

- [Agent workflow and trigger boundaries](SKILL.md)
- [Full English guide](../../docs/native-transparent-imagegen.md)
- [中文使用指南](../../docs/native-transparent-imagegen.zh-CN.md)
- [First-version Tuanzi and Hutao fur case](../../examples/native-transparent-imagegen-tuanzi-hutao.md)
- [Back to Craft Skills](../../README.en.md)

**Status: v0.1 experimental.** Native transparency and its host toolchain may change. Passing
alpha metadata does not prove clean fur edges or visual acceptance.
