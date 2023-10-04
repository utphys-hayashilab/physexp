# 物理学実験II 「自動計測制御」 for Python （2023年度）
## はじめに

### 前提知識
- Pythonの基本的な言語仕様を理解しており，簡単なプログラムを書いたことがある

## 実験

## 実装方法
### 外部デバイスの制御
実験に使用する外部デバイス（ソースメータ・マルチメータ等）をPythonを用いて制御するには，[**PyVISA**](https://pypi.org/project/PyVISA/)パッケージを利用することができます．

PyVISAパッケージは，実験に使用する測定機器との通信を行う際のの共通規格であるVISA (Virtual Instrument Software Architecture)を，Pythonから利用できるようにしたものです．

本実験で使用する外部デバイスには，それぞれ専用の**コマンド**と呼ばれる命令が設定されています．PyVISAパッケージを用いて外部デバイスにコマンドを送信することで，デバイスの操作を行ったり，デバイスから値を取得したりすることができます．

PyVISAパッケージの詳細な仕様については[PyVISAパッケージの公式ドキュメント(en)](https://pyvisa.readthedocs.io/en/latest/)を参照してください．

#### 利用例
以下は，PyVISAパッケージを利用して外部デバイスとの通信を行うPythonプログラムの例です．

```python
import pyvisa

rm = pyvisa.ResourceManager()
inst = rm.open_resource('ASRL1::INSTR')
print(inst.query("*IDN?"))
inst.close()
rm.close()
```

まず，`import`文を利用して`pyvisa`パッケージを読み込みます（1行目）．続いて，`pyvisa.ResourceManager`クラスを初期化し，インスタンスを変数`rm`に代入します（3行目）．

`open_resource()`メソッドを利用すると，引数に指定した**アドレス**をもつ外部デバイスを取得することができます（4行目）．アドレスとは，外部デバイスを識別するための文字列のことです（実験で使用する各デバイスのアドレスについては後述）．

`query()`メソッドは，引数に指定した**コマンド**を外部デバイスに送信し，デバイスからの返値を返します．5行目では，`inst`変数に格納されたデバイスに対して`*IDN?`というコマンドを送信し，その結果を`print`関数で表示しています（`*IDN?`はデバイスのID番号と呼ばれる識別子を取得するコマンドです）．

プログラムの最後では，`close()`メソッドを利用して必ず使用したデバイスとの通信を終了してください．

#### ソースメータ (6240A)
#### マルチメータ (34401A)
#### スペクトラムアナライザ (RSA306)

### 測定データの読み込み・書き出し

### 測定データのプロット

## サンプルプログラム
