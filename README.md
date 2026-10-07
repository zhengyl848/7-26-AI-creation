# 西湖文脉图志

AI 驱动的杭州文化遗产数字化平台 —— 清华大学无穹书院实践支队

## 项目简介

**西湖文脉图志**以西湖周边人文景点为切入点，构建了集**交互式地图可视化**、**AI 智能文化导览**、**多用户协同管理**于一体的数字人文工具。平台采用 Streamlit 全栈框架，通过 DeepSeek 官方 API接入大语言模型。

## 快速开始

```bash
cd xihu_map_app
pip install -r requirements.txt
streamlit run xihu_map_app.py
```

浏览器访问 `http://localhost:8501`。

## 测试账户

| 用户名 | 密码 |
|--------|------|
| test | 123456 |

## 环境配置

打开项目自带的 `xihu_map_app/.env`，在等号后直接填入 DeepSeek 官方密钥：

```env
DEEPSEEK_API_KEY=你的真实密钥
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-flash
DEEPSEEK_TIMEOUT=120
```

保存后启动或重启项目即可。只保留一份 `.env`，地址、模型和超时已填好，直接填写密钥即可。
程序默认使用 `https://api.deepseek.com`、`deepseek-flash`，读取超时 120 秒。
密钥申请：https://platform.deepseek.com/api_keys
未填密钥时会明确提示并使用本地文化资料。不要把填有真实密钥的文件上传到 GitHub。

## 文件结构

```
xihu_map_app/
├── xihu_map_app.py      # 主程序
├── spots_data.json      # 景点数据（按用户存储为 spots_data_{用户名}.json）
├── users.json           # 用户账户（密码哈希存储）
├── requirements.txt     # Python 依赖
├── .env                 # API 密钥配置
└── images/
    ├── another.jpg      # 地图底图
    └── spot_*.png       # 景点图片（用户上传）
```

## 功能说明

### 🗺️ 交互地图
- 高精度西湖地图为底图，支持滚轮缩放和拖拽平移
- 鼠标悬停实时显示坐标
- 点击图片任意位置选址，添加标记
- 景点标记以红色圆点+编号展示，高亮景点呈金色脉动效果
- 也可手动输入精确坐标

### 🤖 AI 文脉对话
- 选择已添加的任一地点，与 AI 进行文化对话
- 默认使用 deepseek-flash，模型可配置，提供诗词鉴赏、历史解读、传说讲述等功能
- 内置 13 个经典景点（断桥残雪、苏堤、雷峰塔等）的结构化文化数据库
- 支持快捷提问和自由输入，API 不可用时自动回退到本地资料

### 👤 用户系统
- 注册/登录，密码 SHA-256 加密存储
- 每个用户独立数据文件，互不可见
- 支持添加、编辑、删除个人标注地点

### 📝 个人笔记
- 每个地点可添加笔记，记录个人见闻与思考
- 支持上传景点实拍图片

### ❓ 项目说明
- 侧边栏「项目说明」按钮查看完整项目文档
- 包含项目介绍、AI 使用披露、人员分工、GitHub 链接

## 成员分工

| 成员 | 职责 |
|------|------|
| 辛泽宇 | 整体框架搭建、系统设计 |
| 郑悦霖 | 项目开发、功能实现 |
| 黄麒文 | 外部素材收集、项目优化、展示 |
| 卢俞辰 | 外部素材收集、项目优化、展示 |

## 技术栈

- **Streamlit** — 全栈 Web 框架
- **Python** — 后端逻辑与 AI 接口
- **HTML/CSS/JS** — 自定义地图交互组件
- **DeepSeek V4** — 大语言模型
- **JSON** — 文件型数据存储
- **Pillow** — 图像处理

## GitHub

[https://github.com/zhengyl848/7-26-AI-creation](https://github.com/zhengyl848/7-26-AI-creation.git)

## DeepSeek 直连版运行说明

Windows 安装 Python 3.13 并加入 PATH 后，双击根目录 `start_xihu.cmd`。
脚本在项目内创建虚拟环境，联网安装锁定依赖并启动服务。
直接在项目自带的 `.env` 中填入密钥即可；地址、模型和超时已有默认值。
修改密钥后重启服务。系统环境变量优先于 `.env`。

网络连接超时 10 秒，读取等待默认 120 秒，可通过 `DEEPSEEK_TIMEOUT` 修改。
无自动重试。密钥无效、余额不足（HTTP 402）、权限、限流、网络故障、空回复或畸形回复均安全回退本地资料。
文脉对话仅使用 DeepSeek 配置，不再读取百炼的密钥和 endpoint。

回归测试：在 `xihu_map_app` 目录执行 `../.venv/Scripts/python.exe -m unittest test_chat_api test_chat_ui -v`。
未提供 DeepSeek 官方密钥，因此在线成功和失败路径通过模拟响应验证，尚未进行真实 DeepSeek 调用。
