# 微缩剧场评测

cases.yaml 使用 JSON 编码（合法 YAML 子集），包含三个正常成图题、三个生成前边界题，以及审图、非触发各一题。验证器只验证字段、唯一 ID、路由覆盖和非空断言，不运行生图或证明断言成立。

同题材的三个正常案例与三个边界案例的历史结果见 [验证摘要](../../skills/single-path-process-diorama/evals/VALIDATION.md)。实际历史输入分别见随包 [成图题](../../skills/single-path-process-diorama/evals/evals.json) 和 [边界题](../../skills/single-path-process-diorama/evals/boundary-evals.json)。本目录 cases.yaml 是简化路由规格，不把重述的题目视为再次执行；新增审图与非触发题也尚未做行为运行。原始私人研究工作区不在此仓库中。

```sh
python3 -B evals/single-path-process-diorama/validate_cases.py evals/single-path-process-diorama/cases.yaml
python3 -B evals/single-path-process-diorama/self_test_validate_cases.py
python3 -B -m unittest discover -s skills/single-path-process-diorama/tests -p 'test_verify_delivery.py'
```
