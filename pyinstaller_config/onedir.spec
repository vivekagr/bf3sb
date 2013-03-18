# -*- mode: python -*-

# Path to PyInstaller files
pyinstaller_path = 'C:\\Users\\VivekPC\\Desktop\\pyinstaller-2.0'

# Path to the BF3 browser source files
source_path = 'C:\\Users\\VivekPC\\Desktop\\bf3'

a = Analysis([source_path + '\\gui.py'],
             pathex=[pyinstaller_path],
             hiddenimports=[],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build\\pyi.win32\\gui', 'BF3 Server Browser.exe'),
          debug=False,
          strip=None,
          upx=True,
		  icon=source_path + '\\icon\\icon.ico',
          console=False )
coll = COLLECT(exe,
               [('layout.html', source_path + '\\layout.html', 'DATA')],
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name=os.path.join('dist', 'gui'))
