#!/usr/bin/env python3
"""
Build script for luci-app-nvmestatus
Generates .ipk packages without requiring OpenWrt SDK

Usage:
    python3 build/build.py
"""

import tarfile, io, os, struct, sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR   = os.path.dirname(SCRIPT_DIR)
DIST_DIR   = os.path.join(ROOT_DIR, 'dist')

PKG_NAME    = 'luci-app-nvmestatus'
PKG_VERSION = '1.0.0-1'

# ── lmo builder ──────────────────────────────────────────────────────────────

def sfh_hash(data, init=None):
    if isinstance(data, str):
        data = data.encode('utf-8')
    length = len(data)
    if init is None:
        init = length
    h = init & 0xFFFFFFFF
    i = 0
    rem = length & 3
    main_len = length >> 2

    def get16(d, p):
        return d[p] | (d[p + 1] << 8)

    for _ in range(main_len):
        h = (h + get16(data, i)) & 0xFFFFFFFF
        tmp = ((get16(data, i + 2) << 11) ^ h) & 0xFFFFFFFF
        h = ((h << 16) ^ tmp) & 0xFFFFFFFF
        i += 4
        h = (h + (h >> 11)) & 0xFFFFFFFF

    if rem == 3:
        h = (h + get16(data, i)) & 0xFFFFFFFF
        h = (h ^ (h << 16)) & 0xFFFFFFFF
        h = (h ^ (data[i + 2] << 18)) & 0xFFFFFFFF
        h = (h + (h >> 11)) & 0xFFFFFFFF
    elif rem == 2:
        h = (h + get16(data, i)) & 0xFFFFFFFF
        h = (h ^ (h << 11)) & 0xFFFFFFFF
        h = (h + (h >> 17)) & 0xFFFFFFFF
    elif rem == 1:
        h = (h + data[i]) & 0xFFFFFFFF
        h = (h ^ (h << 10)) & 0xFFFFFFFF
        h = (h + (h >> 1)) & 0xFFFFFFFF

    h = (h ^ (h << 3)) & 0xFFFFFFFF
    h = (h + (h >> 5)) & 0xFFFFFFFF
    h = (h ^ (h << 4)) & 0xFFFFFFFF
    h = (h + (h >> 17)) & 0xFFFFFFFF
    h = (h ^ (h << 25)) & 0xFFFFFFFF
    h = (h + (h >> 6)) & 0xFFFFFFFF
    return h


def make_lmo(translations):
    entries = []
    data_buf = b''
    offset = 0

    plural_str = b'nplurals=1; plural=0;'
    key = b''
    key_id = sfh_hash(key, len(key))
    val_id = sfh_hash(plural_str, len(plural_str))
    if key_id != val_id:
        entries.append((key_id, val_id, offset, len(plural_str)))
        padded = plural_str + b'\x00' * ((4 - len(plural_str) % 4) % 4)
        data_buf += padded
        offset += len(padded)

    for msgid, msgstr in translations:
        if not msgid or not msgstr:
            continue
        key = msgid.encode('utf-8') if isinstance(msgid, str) else msgid
        val = msgstr.encode('utf-8') if isinstance(msgstr, str) else msgstr
        key_id = sfh_hash(key, len(key))
        val_id = sfh_hash(val, len(val))
        if key_id == val_id:
            continue
        entries.append((key_id, val_id, offset, len(val)))
        padded = val + b'\x00' * ((4 - len(val) % 4) % 4)
        data_buf += padded
        offset += len(padded)

    entries.sort(key=lambda e: e[0])
    index_buf = b''.join(struct.pack('>IIII', *e) for e in entries)
    return data_buf + index_buf + struct.pack('>I', len(data_buf))


def parse_po(po_path):
    translations = []
    msgid = msgstr = None
    with open(po_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('msgid "'):
                if msgid is not None and msgstr:
                    translations.append((msgid, msgstr))
                msgid = line[7:-1]
                msgstr = None
            elif line.startswith('msgstr "'):
                msgstr = line[8:-1]
            elif line.startswith('"') and msgstr is not None:
                msgstr += line[1:-1]
    if msgid is not None and msgstr:
        translations.append((msgid, msgstr))
    return [(k, v) for k, v in translations if k]


# ── ipk builder ───────────────────────────────────────────────────────────────

def make_tar_gz(file_map):
    """file_map: {arcname: bytes_or_filepath}"""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode='w:gz', format=tarfile.USTAR_FORMAT) as t:
        seen_dirs = set()
        for arcname in sorted(file_map.keys()):
            parts = arcname.lstrip('./').split('/')
            for i in range(1, len(parts)):
                dpath = './' + '/'.join(parts[:i]) + '/'
                if dpath not in seen_dirs:
                    dinfo = tarfile.TarInfo(name=dpath)
                    dinfo.type  = tarfile.DIRTYPE
                    dinfo.mode  = 0o755
                    dinfo.mtime = 0
                    dinfo.uid = dinfo.gid = 0
                    dinfo.uname = dinfo.gname = 'root'
                    t.addfile(dinfo)
                    seen_dirs.add(dpath)

            src = file_map[arcname]
            if isinstance(src, (bytes, bytearray)):
                content = bytes(src)
            else:
                with open(src, 'rb') as f:
                    content = f.read()

            info = tarfile.TarInfo(name=arcname)
            info.size  = len(content)
            info.mtime = 0
            info.uid = info.gid = 0
            info.uname = info.gname = 'root'
            info.type  = tarfile.REGTYPE
            if arcname.endswith('/rpcd/nvmestatus') or arcname.endswith('postinst') or arcname.endswith('prerm'):
                info.mode = 0o755
            else:
                info.mode = 0o644
            t.addfile(info, io.BytesIO(content))
    return buf.getvalue()


def build_ipk(output_path, control_map, data_map):
    ctrl_bytes = make_tar_gz(control_map)
    data_bytes = make_tar_gz(data_map)
    deb_bytes  = b'2.0\n'

    outer_buf = io.BytesIO()
    with tarfile.open(fileobj=outer_buf, mode='w:gz', format=tarfile.USTAR_FORMAT) as t:
        for name, content in [
            ('debian-binary',  deb_bytes),
            ('control.tar.gz', ctrl_bytes),
            ('data.tar.gz',    data_bytes),
        ]:
            info = tarfile.TarInfo(name=name)
            info.size  = len(content)
            info.mtime = 0
            info.mode  = 0o644
            info.uid = info.gid = 0
            info.uname = info.gname = 'root'
            info.type  = tarfile.REGTYPE
            t.addfile(info, io.BytesIO(content))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(outer_buf.getvalue())
    print(f'  Built: {os.path.basename(output_path)} ({os.path.getsize(output_path)} bytes)')


# ── main ──────────────────────────────────────────────────────────────────────

def read(path):
    return os.path.join(ROOT_DIR, path)


def text(path):
    with open(os.path.join(ROOT_DIR, path), 'rb') as f:
        return f.read()


def main():
    os.makedirs(DIST_DIR, exist_ok=True)

    print(f'Building {PKG_NAME} {PKG_VERSION}...')

    # ── main package ──
    main_control = {
        './control': (
            f'Package: {PKG_NAME}\n'
            f'Version: {PKG_VERSION}\n'
            f'Depends: luci-base, nvme-cli\n'
            f'Architecture: all\n'
            f'Maintainer: local\n'
            f'Section: luci\n'
            f'Priority: optional\n'
            f'Description: NVMe SSD health monitoring panel for LuCI\n'
        ).encode(),
        './conffiles': b'',
        './postinst': (
            '#!/bin/sh\n'
            '[ -x /etc/init.d/rpcd ] && /etc/init.d/rpcd restart\n'
            '[ -x /etc/init.d/uhttpd ] && /etc/init.d/uhttpd restart\n'
            'exit 0\n'
        ).encode(),
        './prerm': b'#!/bin/sh\nexit 0\n',
    }

    main_data = {
        './usr/share/luci/menu.d/luci-app-nvmestatus.json':
            read('root/usr/share/luci/menu.d/luci-app-nvmestatus.json'),
        './usr/share/rpcd/acl.d/luci-app-nvmestatus.json':
            read('root/usr/share/rpcd/acl.d/luci-app-nvmestatus.json'),
        './usr/libexec/rpcd/nvmestatus':
            read('root/usr/libexec/rpcd/nvmestatus'),
        './www/luci-static/resources/view/nvmestatus/status.js':
            read('htdocs/luci-static/resources/view/nvmestatus/status.js'),
    }

    build_ipk(
        os.path.join(DIST_DIR, f'{PKG_NAME}_{PKG_VERSION}_all.ipk'),
        main_control, main_data
    )

    # ── i18n package ──
    po_path = os.path.join(ROOT_DIR, 'po/zh_Hans/luci-app-nvmestatus.po')
    translations = parse_po(po_path)
    lmo_bytes = make_lmo(translations)

    i18n_control = {
        './control': (
            f'Package: luci-i18n-nvmestatus-zh-cn\n'
            f'Version: {PKG_VERSION}\n'
            f'Depends: {PKG_NAME}\n'
            f'Architecture: all\n'
            f'Maintainer: local\n'
            f'Section: luci\n'
            f'Priority: optional\n'
            f'Description: Chinese (Simplified) translation for {PKG_NAME}\n'
        ).encode(),
        './conffiles': b'',
        './postinst': (
            '#!/bin/sh\n'
            '[ -x /etc/init.d/uhttpd ] && /etc/init.d/uhttpd restart\n'
            'exit 0\n'
        ).encode(),
        './prerm': (
            '#!/bin/sh\n'
            'rm -f /www/luci-static/resources/locale/zh_Hans/luci-app-nvmestatus.js\n'
            'rmdir /www/luci-static/resources/locale/zh_Hans 2>/dev/null\n'
            'rmdir /www/luci-static/resources/locale 2>/dev/null\n'
            'exit 0\n'
        ).encode(),
    }

    i18n_data = {
        './www/luci-static/resources/locale/zh_Hans/luci-app-nvmestatus.js':
            read('i18n/zh_Hans/luci-app-nvmestatus.js'),
        './usr/lib/lua/luci/i18n/nvmestatus.zh-cn.lmo':
            lmo_bytes,
    }

    build_ipk(
        os.path.join(DIST_DIR, f'luci-i18n-nvmestatus-zh-cn_{PKG_VERSION}_all.ipk'),
        i18n_control, i18n_data
    )

    print('Done. Output in dist/')


if __name__ == '__main__':
    main()
