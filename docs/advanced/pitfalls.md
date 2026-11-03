# 坑点（都踩过）

## 1. stdout 只放 JSON
`--json` 时进度条走 stderr；`> file.json` 前别混 `echo`。

## 2. 中文路径
`aigc.cmd` 已 `chcp 65001`，PowerShell 里传中文路径用单引号更稳。

## 3. `-t` 不能带换行
Windows 命令行会吞掉换行后的参数，多段请用 `-f`。

## 4. 阈值不是 0.5
默认 0.56（`settings.json` → `detect.threshold`）。

## 5. `--gpu` 需要真 CUDA
本机 `torch+cpu`，先 `aigc.cmd gpu` 确认。

## 6. 改完一定复检
规则改写会让部分段分数**反升**（72.8% → 73.4%）；LLM 改写也会（v21 有 5 段反升到 0.99）。

## 7. 别把困惑度类当分类器
`zh_perplexity` 的 prob 近恒值，只能当参考。

## 8. P1.5 的服务器别用 `start` / `Start-Process` 拉
会继承调用方的 Job Object，脚本一结束就被连带杀掉（表现为"刚 [ok] 就没了"）。

`start-local.cmd` 内部走 WMI（`local-ai\_spawn.ps1`），进程挂在 `WmiPrvSE` 下才活得久。

## 9. 端口会漂
GUI 那个离线版每次启动都换端口和 key（实测 11103 → 39676）。

- 要走 GUI 就让它自动发现
- 要稳定就用 `start-local.cmd` + `paper auth set --local-fixed` 钉死 11103
