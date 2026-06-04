# luci-app-nvmestatus

[English](README.md) | **简体中文**

适用于 OpenWrt / iStoreOS 的 NVMe SSD 健康监控 LuCI 插件。  
兼容 [ArgonTheme](https://github.com/jerrykuku/luci-theme-argon) 主题。

## 功能特性

- 实时显示 NVMe SMART 数据
- 温度、寿命、备用块状态颜色预警
- 健康状态、使用统计、数据吞吐、温度历史四大模块
- 每 30 秒自动刷新
- 手动立即刷新按钮
- 移动端自适应布局
- 支持简体中文翻译（通过 i18n 包）

## 截图

> 系统 → NVMe 健康监控

| 亮色模式 | 暗色模式 |
|---|---|
| *(截图)* | *(截图)* |

## 安装方法

### 使用预编译 IPK（推荐）

从 [Releases](../../releases) 页面下载最新的 `.ipk` 文件。

```bash
# 上传到路由器后执行：
opkg install luci-app-nvmestatus_1.0.0-1_all.ipk

# 可选：安装中文翻译包
opkg install luci-i18n-nvmestatus-zh-cn_1.0.0-1_all.ipk
```

### 从源码构建

**依赖：** Python 3.6+，无需其他依赖。

```bash
git clone https://github.com/YOUR_USERNAME/luci-app-nvmestatus.git
cd luci-app-nvmestatus
python3 build/build.py
# 输出：dist/luci-app-nvmestatus_1.0.0-1_all.ipk
#       dist/luci-i18n-nvmestatus-zh-cn_1.0.0-1_all.ipk
```

### OpenWrt SDK

```bash
cp -r luci-app-nvmestatus /path/to/openwrt/package/feeds/luci/
make menuconfig  # 选择 LuCI → Applications → luci-app-nvmestatus
make package/luci-app-nvmestatus/compile
```

## 卸载

```bash
opkg remove luci-i18n-nvmestatus-zh-cn  # 如已安装中文包，先卸载
opkg remove luci-app-nvmestatus
```

## 文件结构

```
luci-app-nvmestatus/
├── Makefile                                  # OpenWrt SDK 构建文件
├── build/
│   └── build.py                              # 独立 ipk 构建脚本
├── htdocs/
│   └── luci-static/resources/view/nvmestatus/
│       └── status.js                         # 前端 LuCI 视图
├── root/
│   ├── usr/libexec/rpcd/nvmestatus           # 后端 rpcd Shell 脚本
│   ├── usr/share/luci/menu.d/
│   │   └── luci-app-nvmestatus.json          # 菜单注册
│   └── usr/share/rpcd/acl.d/
│       └── luci-app-nvmestatus.json          # 权限配置
├── i18n/
│   └── zh_Hans/
│       └── luci-app-nvmestatus.js            # JS 翻译（界面内容）
└── po/
    └── zh_Hans/
        └── luci-app-nvmestatus.po            # PO 翻译源文件（菜单标题）
```

## i18n 翻译机制

本插件使用两套翻译机制：

| 机制 | 文件 | 覆盖范围 |
|---|---|---|
| LuCI JS 本地化 | `i18n/zh_Hans/*.js` | 界面内容（标签、按钮等） |
| LuCI lmo 目录 | `po/zh_Hans/*.po` → 编译为 `.lmo` | 侧边栏菜单标题 |

## 依赖

- `luci-base` — LuCI 框架
- `nvme-cli` — NVMe 命令行工具

## 兼容性

已在以下环境测试：
- iStoreOS 24.10（OpenWrt 24.10）
- LuCI istoreos-24.10 分支
- ArgonTheme v2.2.x

## 开源协议

MIT
