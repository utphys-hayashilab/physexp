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
ソースメータ (6240A) を使用する際に必要なコマンドを以下に示します．これ以外のコマンドについては実験室に用意された取扱説明書を参照してください．

**初期化**：接続時に以下のコマンドを実行してください．
```
*RST; MD0; VF; F2; R0; SVR5; SOV 0; E
```

**電圧の印加**：`SOV`コマンドを利用することで，設定した値の電圧を発生させることができます．例えば，$`2.5\, {\rm V}`$の電圧を発生させるには以下のコマンドを実行してください．
```
SOV 2.5
```

#### マルチメータ (34401A)
マルチメータ (34401A) を使用する際に必要なコマンドを以下に示します．これ以外のコマンドについては実験室に用意された取扱説明書を参照してください．

**初期化**：接続時に以下のコマンドを実行してください．
```
TRIG:SOUR BUS
INIT
*TRG
```

**電圧の印加**：`FETC?`コマンドを利用することで，マルチメータの読み取り値を取得することができます．PyVISAパッケージの`query()`メソッドを利用して値を取得する際，返値は空白を含んだ文字列になることに注意してください．

#### スペクトラムアナライザ (RSA306)
スペクトラムアナライザ(RSA306)については，実装が複雑であるため，事前に用意されたプログラムである`/lib/rsa306b_spec.py`を利用してかまいません．

`import`文で`rsa306b_spec.py`ファイルを読み込んだ後，以下の`getPeakSpectrum()`関数を利用することで，スペクトル（周波数に対するパワー）とピークの位置を取得することができます．

```python
# スペクトルの取得
freq, trace, peakPower, peakFreq = rsa306b_spec.getPeakSpectrum(startFreq= 4800e6, endFreq = 6000e6, refLevel=-10)
```

返値は次の通りです．
- `freq`：周波数（単位：Hz）の配列．`numpy`の`NDArray`形式で格納されています．
- `trace`：パワー（単位：dBm）の配列．`numpy`の`NDArray`形式で格納されています．
- `peakPower`：パワーの極大値（単位：dBm）です．
- `peakFreq`：パワーが極大となるような周波数（単位：Hz）です．

### 測定データの読み込み・書き出し
Pythonで測定データをファイルに書き出したり，測定データが記録されたファイルを読み込んだりするには，`open(), read(), write()`などの組み込み関数を利用します．

実験で要求されている測定データの出力形式は任意ですが，カンマ区切り形式（拡張子`.csv`）などを用いると，データを効率的に取り扱うことができて便利です．

### 測定データのプロット
測定データをプロットするには，以下の方法があります．

- Pythonのライブラリ[matplotlib](https://matplotlib.org/)を利用する
- gnuplotやMATLABなどのソフトウェアを利用する
