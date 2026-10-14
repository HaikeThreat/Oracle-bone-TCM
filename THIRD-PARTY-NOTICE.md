# 第三方组件声明 / Third-Party Notices

本仓库的代码按 [MIT License](LICENSE) 发布，但包含以下第三方组件，各自按其许可发布：

## Three.js（已确认可再分发）

- 文件：`libs/three.min.js`
- 版权：Copyright © 2010-2023 Three.js Authors
- 许可：MIT — <https://github.com/mrdoob/three.js/blob/dev/LICENSE>

## MediaPipe Hands（已确认可再分发）

- 文件：`libs/hands.js`、`libs/hands_solution_packed_assets*`、
  `libs/hands_solution_simd_wasm_bin.*`、`libs/hand_landmark_full.tflite`、
  `libs/hand_landmark_lite.tflite`、`libs/hands.binarypb`
- 版权：Google LLC
- 许可：Apache License 2.0 — <https://www.apache.org/licenses/LICENSE-2.0>

## AYJGW 甲骨文字体 ⚠ 许可待确认

- 文件：`libs/AYJGW.ttf`（完整源字体）及 `gesture3d.html` 内嵌子集
- 版权：Copyright © AYSY.JKX, 2003（字体名"乔老师甲骨字替换"）
- 状态：字体内嵌许可信息为空，正在与版权方确认再分发授权。
  若无法获得授权，后续版本将移除字体文件，改为提供下载指引 + 本地子集化脚本。

## 甲骨文字表数据 ⚠ 许可待确认

- 文件：`data/oracle_glyphs_full.json`、`data/curated_glyphs.json`
  （`curated_glyphs.json` 中部分条目的 tag/intro 与平台文案一致，视同继承该来源；
   原先单独存在的 `data/intros.json` 已被它完全覆盖，故合并删除，避免同一份数据两处维护）
- 来源：甲骨文AI协同平台（jgwlbq.org.cn）"甲骨文合并字表"已释字数据
- 状态：数据使用条款待与平台方核实。
