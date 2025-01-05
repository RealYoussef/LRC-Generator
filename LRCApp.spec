# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['LRC generator 3.py'],  # Main script
    pathex=[],
    binaries=[],
    datas=[
        ('splash_screen.py', '.'),  # Include splash screen script
        ('Logo5.ico', '.'),         # Include icon file
        ('Logo5.png', '.'),         # Include logo image
	('romaji_converter.py', '.'),
	('lrc_cleaner.py', '.'),
	('lrc_timing_adjuster.py', '.'),
	('lrc_time_sync.py', '.'),
	('lrc_smart_sync.py', '.'),
	('C:\\Users\\srisr\\anaconda3\\Lib\\site-packages\\pykakasi\\data', 'pykakasi/data'),  # Include entire data folder
    ],
    hiddenimports=[],
    hookspath=['hooks'],  # Additional hooks directory
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LRCApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console output
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['Logo5.ico'],  # Use Logo5.ico as the icon
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LRCApp',
)
