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
          a.binaries,
		  [('layout.html', source_path + '\\layout.html', 'DATA')],
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'Battlefield 3 Server Browser.exe'),
          debug=False,
          strip=None,
          upx=True,
          console=False,
		  icon=source_path + '\\icon\\icon.ico')
