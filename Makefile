include $(TOPDIR)/rules.mk

PKG_NAME:=luci-app-nvmestatus
PKG_VERSION:=1.0.0
PKG_RELEASE:=1

PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)

include $(INCLUDE_DIR)/package.mk

define Package/luci-app-nvmestatus
	SECTION:=luci
	CATEGORY:=LuCI
	SUBMENU:=3. Applications
	TITLE:=LuCI NVMe Health Monitor
	DEPENDS:=+luci-base +nvme-cli
	PKGARCH:=all
endef

define Package/luci-app-nvmestatus/description
  NVMe SSD health monitoring panel for LuCI.
  Displays SMART data including temperature, lifespan,
  errors and I/O statistics. Compatible with Argon theme.
endef

define Package/luci-i18n-nvmestatus-zh-cn
	SECTION:=luci
	CATEGORY:=LuCI
	SUBMENU:=6. Translations
	TITLE:=Chinese (Simplified) - luci-app-nvmestatus
	DEPENDS:=+luci-app-nvmestatus
	PKGARCH:=all
endef

define Package/luci-i18n-nvmestatus-zh-cn/description
  Chinese (Simplified) translation for luci-app-nvmestatus.
endef

define Build/Prepare
endef

define Build/Compile
endef

define Package/luci-app-nvmestatus/install
	$(INSTALL_DIR) $(1)/usr/share/luci/menu.d
	$(INSTALL_DATA) ./root/usr/share/luci/menu.d/luci-app-nvmestatus.json \
		$(1)/usr/share/luci/menu.d/

	$(INSTALL_DIR) $(1)/usr/share/rpcd/acl.d
	$(INSTALL_DATA) ./root/usr/share/rpcd/acl.d/luci-app-nvmestatus.json \
		$(1)/usr/share/rpcd/acl.d/

	$(INSTALL_DIR) $(1)/usr/libexec/rpcd
	$(INSTALL_BIN) ./root/usr/libexec/rpcd/nvmestatus \
		$(1)/usr/libexec/rpcd/

	$(INSTALL_DIR) $(1)/www/luci-static/resources/view/nvmestatus
	$(INSTALL_DATA) ./htdocs/luci-static/resources/view/nvmestatus/status.js \
		$(1)/www/luci-static/resources/view/nvmestatus/
endef

define Package/luci-i18n-nvmestatus-zh-cn/install
	$(INSTALL_DIR) $(1)/www/luci-static/resources/locale/zh_Hans
	$(INSTALL_DATA) ./i18n/zh_Hans/luci-app-nvmestatus.js \
		$(1)/www/luci-static/resources/locale/zh_Hans/

	$(INSTALL_DIR) $(1)/usr/lib/lua/luci/i18n
	$(call PO2LMO,./po/zh_Hans/luci-app-nvmestatus.po,\
		$(1)/usr/lib/lua/luci/i18n/nvmestatus.zh-cn.lmo)
endef

$(eval $(call BuildPackage,luci-app-nvmestatus))
$(eval $(call BuildPackage,luci-i18n-nvmestatus-zh-cn))
