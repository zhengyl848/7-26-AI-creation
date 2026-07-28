# 西湖文脉图志

AI 驱动的杭州文化遗产数字化平台 —— 清华大学无穹书院实践支队

## 项目简介

**西湖文脉图志**以西湖周边人文景点为切入点，构建了集**交互式地图可视化**、**AI 智能文化导览**、**多用户协同管理**于一体的数字人文工具。平台采用 Streamlit 全栈框架，接入 DeepSeek V4 大语言模型。

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

编辑 `.env` 文件，将 `DASHSCOPE_API_KEY` 替换为你的真实 API 密钥：

```env
DASHSCOPE_API_KEY = "在此填入你的 DashScope API 密钥"
DASHSCOPE_BASE_URL = "https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
DASHSCOPE_MODEL = "deepseek-v4-flash"
```

> ⚠️ **必须补全密钥**：`.env` 中 `DASHSCOPE_API_KEY` 为占位符。可前往 [阿里云百炼平台](https://bailian.console.aliyun.com/) 申请 DashScope API Key。
>
> 不配置密钥也可正常使用，AI 对话会自动回退到内置文化资料库。

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
- 基于 DeepSeek V4 大模型，提供诗词鉴赏、历史解读、传说讲述等功能
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
