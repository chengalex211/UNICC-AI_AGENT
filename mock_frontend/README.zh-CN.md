# mock_frontend — 仅静态演示前端

本目录是 **非生产** 的 React + Vite + TypeScript 界面，用于 **版式、文案与流程原型**。**不会**调用评估后端 API。

## 行为说明

- **NewEvaluation**：提交用 `setTimeout`（约 2.2 秒）模拟等待，**无**对 `frontend_api` 的 `fetch`。
- **Dashboard / Report**：数据来自 `src/data/mockData.ts`，字段形态接近完整 `CouncilReport` JSON，**仅供视觉对齐**。

## 适用场景

- 无需启动 Python / API 时查看页面与交互。
- 与设计稿或文案对照。

## 生产环境应使用

请使用仓库根目录的 **real_frontend/**，并启动 **frontend_api/**（默认 **8100** 端口）。交接与能力说明见：

- `docs/system-overview.zh-CN.md`
- `docs/system-overview.en.md`

## 本地运行

```bash
cd mock_frontend
npm install
npm run dev
```

## 在 monorepo 中的位置

`mock_frontend/` 位于 **Capstone 仓库根目录**（与 `real_frontend/`、`UNICC-Project-2/` 同级）。原先 `UNICC-Project-2/frontend/` 已移除，**以本目录为唯一的 mock 前端副本**。
