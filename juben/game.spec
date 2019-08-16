# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['game.py'],
             pathex=['/Users/yibo/PycharmProjects/JuBenAI/juben'],
             binaries=[],
             datas=[],
             hiddenimports=['distutils.dist','numpy.random.common','numpy.random.bounded_integers','sklearn.tree._utils','sklearn.utils.sparsetools._graph_validation',
                 'sklearn.utils.sparsetools._graph_tools',
                 'sklearn.utils.lgamma',
                 'sklearn.utils.weight_vector',
 'sklearn.utils.fixes',
 'sklearn.utils.extmath',
 'sklearn.metrics.ranking',
 'sklearn.neighbors',
 'sklearn.neighbors.typedefs',
 'sklearn.neighbors.quad_tree'],
             hookspath=[],
             runtime_hooks=[],
             excludes=["tcl","tk","tkinter","_tkinter","Tkinter"],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='game',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='game')
