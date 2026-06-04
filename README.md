# luci-app-nvmestatus

**English** | [简体中文](README_ZH.md)

A LuCI plugin for monitoring NVMe SSD health on OpenWrt / iStoreOS.  
Compatible with [ArgonTheme](https://github.com/jerrykuku/luci-theme-argon).

## Features

- Real-time NVMe SMART data display
- Temperature, lifespan, spare blocks with color-coded status
- Health status, usage statistics, data throughput, temperature history
- Auto-refresh every 30 seconds
- Manual refresh button
- Mobile responsive layout
- Chinese (Simplified) translation via i18n package

## Screenshots

> System → NVMe Health Monitor

| Light Mode | Dark Mode |
|---|---|
| *(screenshot)* | *(screenshot)* |

## Installation

### Pre-built IPK (recommended)

Download the latest `.ipk` files from [Releases](../../releases).

```bash
# Upload to router, then:
opkg install luci-app-nvmestatus_1.0.0-1_all.ipk

# Optional: Chinese translation
opkg install luci-i18n-nvmestatus-zh-cn_1.0.0-1_all.ipk
```

### Build from source

**Requirements:** Python 3.6+, no other dependencies needed.

```bash
git clone https://github.com/YOUR_USERNAME/luci-app-nvmestatus.git
cd luci-app-nvmestatus
python3 build/build.py
# Output: dist/luci-app-nvmestatus_1.0.0-1_all.ipk
#         dist/luci-i18n-nvmestatus-zh-cn_1.0.0-1_all.ipk
```

### OpenWrt SDK

```bash
cp -r luci-app-nvmestatus /path/to/openwrt/package/feeds/luci/
make menuconfig  # Select LuCI → Applications → luci-app-nvmestatus
make package/luci-app-nvmestatus/compile
```

## Uninstallation

```bash
opkg remove luci-i18n-nvmestatus-zh-cn  # remove translation first if installed
opkg remove luci-app-nvmestatus
```

## File Structure

```
luci-app-nvmestatus/
├── Makefile                                  # OpenWrt SDK build file
├── build/
│   └── build.py                              # Standalone ipk build script
├── htdocs/
│   └── luci-static/resources/view/nvmestatus/
│       └── status.js                         # Frontend LuCI view
├── root/
│   ├── usr/libexec/rpcd/nvmestatus           # Backend rpcd shell script
│   ├── usr/share/luci/menu.d/
│   │   └── luci-app-nvmestatus.json          # Menu registration
│   └── usr/share/rpcd/acl.d/
│       └── luci-app-nvmestatus.json          # ACL permissions
├── i18n/
│   └── zh_Hans/
│       └── luci-app-nvmestatus.js            # JS translation (page content)
└── po/
    └── zh_Hans/
        └── luci-app-nvmestatus.po            # PO translation source (menu title)
```

## How i18n Works

This plugin uses two translation mechanisms:

| Mechanism | File | Covers |
|---|---|---|
| LuCI JS locale | `i18n/zh_Hans/*.js` | Page content (labels, buttons) |
| LuCI lmo catalog | `po/zh_Hans/*.po` → compiled to `.lmo` | Menu title in sidebar |

## Dependencies

- `luci-base` — LuCI framework
- `nvme-cli` — NVMe command-line tools

## Compatibility

Tested on:
- iStoreOS 24.10 (OpenWrt 24.10)
- LuCI istoreos-24.10 branch
- ArgonTheme v2.2.x

## License

MIT
