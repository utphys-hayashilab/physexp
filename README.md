# 物理学実験II 「自動計測制御」 for Python （2023年度）
## はじめに

### 前提知識
- Pythonの基本的な言語仕様を理解しており，簡単なプログラムを書いたことがある

## 実験

## 実装方法
### 外部デバイスの制御
実験に使用する外部デバイス（ソースメータ・マルチメータ等）をPythonを用いて制御するには，[**PyVISA**](https://pypi.org/project/PyVISA/)パッケージを利用することができます．

PyVISAパッケージは，

```python
import pyvisa

rm = pyvisa.ResourceManager()
inst = rm.open_resource('ASRL1::INSTR')
print(inst.query("*IDN?"))
inst.close()
```

PyVISAパッケージの詳細な仕様については[PyVISAパッケージの公式ドキュメント(en)](https://pyvisa.readthedocs.io/en/latest/)を参照してください．

#### ソースメータ (6240A)
#### マルチメータ (34401A)
#### スペクトラムアナライザ (RSA306)

### 測定データの読み込み・書き出し

### 測定データのプロット

## サンプルプログラム
