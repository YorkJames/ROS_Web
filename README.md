# ROS Web

一个基于 **RouterOS REST API** 的轻量级 PPP 账号监控与 Script 控制的 Web 应用，适合部署在 RouterOS Container（Alpine）环境中，用于集中展示 PPP 在线状态并调用 Script 的运维操作。

---

## ✨ 项目背景

在实际运维中，直接让多人登录 RouterOS 进行 PPP 状态查看或调用 Script 存在以下问题：

* RouterOS 账号权限难以细分
* 日常查看 PPP 在线状态操作繁琐
* 针对 Script 调用风险系数高

**ROS Web** 通过 Web 化方式解决上述问题，实现 PPP 账号的统一监控与 Script 控制。

---

## 🧱 系统架构

```
浏览器
  ↓
Flask Web 应用（Alpine Container）
  ↓
RouterOS REST API
```

* **前端**：HTML + JavaScript（表格展示 + 自动刷新）
* **后端**：Python + Flask
* **设备侧**：RouterOS（REST API / Script）

---

## 🚀 核心功能

* Web 登录鉴权（避免直接暴露 RouterOS 账号）
* PPP 账号统一状态视图

  * name
  * online / offline
  * caller-id
  * uptime
* 配置态（`/ppp/secret`）与运行态（`/ppp/active`）聚合展示
* 基于 PPP 账号的远程运维操作（如禁用启用 ppp 账户）
* 自动刷新，无需手动操作

---

## 📂 项目结构

```text
/app
 ├── app.py              # Flask 主程序
 ├── templates/
 │    └── index.html     # 登录页 + 主页面
```

---

## 🔐 安全设计

* RouterOS REST API 凭据仅存在于后端
* 前端通过 Session 登录控制访问
* 不直接在浏览器中调用 Script
* 支持为 REST API 用户配置最小权限

---

## 🛠 部署方式（Alpine）

```sh
apk add python3 py3-flask py3-requests

python3 app.py
```

默认监听端口：`80`

---

## 🧩 适用场景

* 远程 CPE 通过 PPPoE / L2TP / PPTP 等 PPP 接入 RouterOS
* 需要对远程 CPE 进行重启操作
* 需要对 PPP 用户进行快速状态判断与操作的场景

---

## 📌 项目特点总结

* 轻量、无数据库依赖
* 容器化友好，适合 RouterOS Container
* 运维逻辑与设备逻辑解耦
* 易扩展

---

## 📄 License

Internal Use / Private Project
