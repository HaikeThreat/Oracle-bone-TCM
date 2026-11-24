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

## Noto Serif SC（扉页中文字体子集）

- 文件：`index.html` 内嵌的 WOFF2 子集（仅收录扉页用字）
- 版权：Copyright © Google Inc. / Adobe
- 许可：SIL Open Font License 1.1 — <https://scripts.sil.org/OFL>
- 说明：用于保证 iPad / 电脑 / 手机 Safari 上扉页中文（馆名、欢迎您、展厅名等）字形一致。

## 三七写实模型 ⚠ 来源/授权待确认

- 文件：`libs/sanqi_model.glb`（约 9.2MB）及自动生成的 `libs/sanqi_model_fallback.js`
- 说明：中药展厅的三七写实模型（约 150k 三角面，2K PBR 贴图）。
- 状态：项目包未记录原始来源与许可信息；公开部署前需向模型提供方核实再分发授权。

## AYJGW 甲骨文字体 ⚠ 许可待确认

- 文件：`gesture3d.html` 内嵌子集；完整源字体 `libs/AYJGW.ttf` **不随仓库分发**
- 版权：Copyright © AYSY.JKX, 2003（字体名"乔老师甲骨字替换"）
- 状态：字体内嵌许可信息为空，正在与版权方确认再分发授权。
  为避免扩大分发范围，完整 TTF 已从公开仓库移除（页面仅保留必需的子集）；
  重建字库需自行获取该字体并放到 `libs/AYJGW.ttf`。

## 甲骨文字表数据 ⚠ 许可待确认

- 文件：`data/oracle_glyphs_full.json`、`data/curated_glyphs.json`
  （`curated_glyphs.json` 中部分条目的 tag/intro 与平台文案一致，视同继承该来源；
   原先单独存在的 `data/intros.json` 已被它完全覆盖，故合并删除，避免同一份数据两处维护）
- 来源：甲骨文AI协同平台（jgwlbq.org.cn）"甲骨文合并字表"已释字数据
- 状态：数据使用条款待与平台方核实。
