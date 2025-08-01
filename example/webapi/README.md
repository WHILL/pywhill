
# WebAPI 仕様書 <!-- omit in toc -->
- [1. 概要](#1-概要)
  - [1.1. API バージョン](#11-api-バージョン)
  - [1.2. ベースURL](#12-ベースurl)
  - [1.3. 認証](#13-認証)
- [2. 共通仕様](#2-共通仕様)
  - [2.1. リクエスト形式](#21-リクエスト形式)
  - [2.2. レスポンス形式](#22-レスポンス形式)
    - [2.2.1. 成功レスポンス](#221-成功レスポンス)
    - [2.2.2. エラーレスポンス](#222-エラーレスポンス)
  - [2.3. HTTPステータスコード](#23-httpステータスコード)
  - [2.4. データ型](#24-データ型)
- [3. エンドポイント仕様](#3-エンドポイント仕様)
  - [3.1. 電源制御](#31-電源制御)
    - [3.1.1. 電源制御](#311-電源制御)
  - [3.2. モーション制御](#32-モーション制御)
    - [3.2.1. ジョイスティック制御](#321-ジョイスティック制御)
    - [3.2.2. 速度制御](#322-速度制御)
    - [3.2.3. 制御解除](#323-制御解除)
  - [3.3. データストリーミング](#33-データストリーミング)
    - [3.3.1. データストリーム開始](#331-データストリーム開始)
    - [3.3.2. データストリーム停止](#332-データストリーム停止)
  - [3.4. ステータス監視](#34-ステータス監視)
    - [3.4.1. ステータス取得](#341-ステータス取得)
    - [3.4.2. バッテリー情報取得](#342-バッテリー情報取得)
    - [3.4.3. モーター情報取得](#343-モーター情報取得)
  - [3.5. 設定](#35-設定)
    - [3.5.1. スピードプロファイル設定](#351-スピードプロファイル設定)
    - [3.5.2. スピードプロファイル取得](#352-スピードプロファイル取得)
    - [3.5.3. バッテリー節約設定](#353-バッテリー節約設定)
  - [3.6. 診断](#36-診断)
    - [3.6.1. 接続テスト](#361-接続テスト)
- [4. エラーコード詳細](#4-エラーコード詳細)
  - [4.1. 400 Bad Request](#41-400-bad-request)
  - [4.2. 500 Internal Server Error](#42-500-internal-server-error)
- [5. 使用例](#5-使用例)
  - [5.1. curl を使用した基本的な操作](#51-curl-を使用した基本的な操作)
    - [5.1.1. 電源ON](#511-電源on)
    - [5.1.2. データストリーミング開始](#512-データストリーミング開始)
    - [5.1.3. 前進（2秒間持続）](#513-前進2秒間持続)
    - [5.1.4. 状態取得](#514-状態取得)
    - [5.1.5. 制御解除](#515-制御解除)
    - [5.1.6. 電源OFF](#516-電源off)
- [6. 依存ライブラリのライセンス](#6-依存ライブラリのライセンス)
  - [6.1. メインアプリケーション依存関係](#61-メインアプリケーション依存関係)
  - [6.2. 開発ツール依存関係](#62-開発ツール依存関係)
- [7. ライセンス](#7-ライセンス)
- [8. 免責事項](#8-免責事項)

---

## 1. 概要

本書は、WHILL Mobile Robot Platform WebAPI の仕様に関するドキュメントです。
WHILL Mobile Robot Platform WebAPI は、WHILL電動モビリティプラットフォーム（WHILL Model CR/CR2, ロボット台車, 電装系キット）（※以降、WHILLと記す）を制御・監視するためのRESTful APIです。HTTP経由でWHILLの電源制御、モーション制御、ステータス監視などの機能を提供します。

### 1.1. API バージョン

| 項目 | 値 |
|------|-----|
| **バージョン** | v1 |
| **最終更新** | 2025/08/01 |

### 1.2. ベースURL
```
http://localhost:5000
```
※デフォルトの値。必要に応じて環境変数を設定するかリバースプロキシなどを用いて任意のホストアドレス・ポート番号に変更してください


### 1.3. 認証
認証機能は実装されていません。必要に応じて適切な認証機能を実装してください。

## 2. 共通仕様

### 2.1. リクエスト形式

| 項目 | 値 |
|------|-----|
| **Content-Type** | `application/json` |
| **文字コード** | UTF-8 |

### 2.2. レスポンス形式

#### 2.2.1. 成功レスポンス
```json
{
  "success": true,
  "message": "成功メッセージ",
  "data": {
    // エンドポイント固有のデータ
  },
  "timestamp": "2025-01-15T10:30:00.000Z"
}
```

#### 2.2.2. エラーレスポンス
```json
{
  "success": false,
  "error": "エラーメッセージ",
  "timestamp": "2025-01-15T10:30:00.000Z"
}
```

### 2.3. HTTPステータスコード
- `200 OK`: 成功
- `400 Bad Request`: パラメータエラー
- `500 Internal Server Error`: サーバーエラー

### 2.4. データ型
- **boolean**: `true` または `false`
- **integer**: 整数値
- **number**: 数値（整数または小数）

---

## 3. エンドポイント仕様

**エンドポイント一覧**

| カテゴリ | メソッド | エンドポイント | 説明 |
|----------|----------|----------------|------|
| 電源制御 | POST | `/api/v1/whill/power` | WHILL電源のON/OFF制御 |
| モーション制御 | POST | `/api/v1/whill/motion/joystick` | ジョイスティック制御 |
| モーション制御 | POST | `/api/v1/whill/motion/velocity` | 速度制御 |
| モーション制御 | POST | `/api/v1/whill/motion/release` | アクティブな持続制御の解除 |
| データストリーミング | POST | `/api/v1/whill/data-streams/start` | データストリーミング開始 |
| データストリーミング | POST | `/api/v1/whill/data-streams/stop` | データストリーミング停止 |
| ステータス監視 | GET | `/api/v1/whill/status` | 包括的なステータス情報取得 |
| ステータス監視 | GET | `/api/v1/whill/battery` | バッテリー情報取得 |
| ステータス監視 | GET | `/api/v1/whill/motors` | モーター情報取得 |
| 設定 | POST | `/api/v1/whill/speed-profiles` | スピードプロファイル設定 |
| 設定 | GET | `/api/v1/whill/speed-profiles` | スピードプロファイル取得 |
| 設定 | POST | `/api/v1/whill/battery/saving` | バッテリー節約設定 |
| 診断 | GET | `/api/v1/whill/diagnostics/connection` | 接続テスト |

---

### 3.1. 電源制御

#### 3.1.1. 電源制御
WHILLの電源をON/OFFします。

- **エンドポイント**: `POST /api/v1/whill/power`
- **説明**: WHILL電源の制御

**リクエストパラメータ:**
```json
{
  "power_on": boolean  // 必須: true=電源ON, false=電源OFF
}
```

**レスポンス例:**
```json
{
  "success": true,
  "message": "Power turned ON",
  "data": {
    "power_on": true
  },
  "timestamp": "2025-01-15T10:30:00.000Z"
}
```

**エラー例:**
```json
{
  "success": false,
  "error": "power_on parameter is required",
  "timestamp": "2025-01-15T10:30:00.000Z"
}
```

---

### 3.2. モーション制御
**※注意** 以下のジョイスティック制御および速度制御の"シングルショット"を使用してWHILLを連続動作させる場合には、200ms以内に後続の制御コマンドを送信する必要があります。

#### 3.2.1. ジョイスティック制御
ジョイスティック値による移動制御を行います。

- **エンドポイント**: `POST /api/v1/whill/motion/joystick`
- **説明**: ジョイスティック制御（シングルショットまたは持続制御）

**リクエストパラメータ:**
```json
{
  "front": number,   // 必須: 前後方向制御値 (-100 〜 100)
  "side": number,    // 必須: 左右方向制御値 (-100 〜 100)
  "timeout": number  // オプション: 持続時間(ms)、0または未指定でシングルショット
}
```

**パラメータ詳細:**
- `front`: 正の値で前進、負の値で後退
- `side`: 正の値で右旋回、負の値で左旋回
- `timeout`: 0または未指定の場合はシングルショット制御、指定した場合は持続制御

**レスポンス例:**
```json
{
  "success": true,
  "message": "Joystick control command sent",
  "data": {
    "front": 50,
    "side": 0,
    "timeout": 0,
    "control_type": "single_shot"
  },
  "timestamp": "2025-01-15T10:30:00.000Z"
}
```

#### 3.2.2. 速度制御
速度値による移動制御を行います。

- **エンドポイント**: `POST /api/v1/whill/motion/velocity`
- **説明**: 速度制御（シングルショットまたは持続制御）

**リクエストパラメータ:**
```json
{
  "front": number,   // 必須: 前後方向速度 (-500 〜 1500)
  "side": number,    // 必須: 左右旋回速度 (-750 〜 750)
  "timeout": number  // オプション: 持続時間(ms)、0または未指定でシングルショット
}
```

**パラメータ詳細:**
- `front`: 前後方向の速度値（単位：0.004[km/h]相当）
- `side`: 左右旋回の速度値（単位：0.004[km/h]相当）

**レスポンス例:**
```json
{
  "success": true,
  "message": "Velocity control command sent",
  "data": {
    "front": 1000,
    "side": 0,
    "timeout": 1500,
    "control_type": "hold"
  },
  "timestamp": "2025-01-15T10:30:00.000Z"
}
```

#### 3.2.3. 制御解除
アクティブな持続制御を解除します。

- **エンドポイント**: `POST /api/v1/whill/motion/release`
- **説明**: アクティブなジョイスティックまたは速度持続制御を解除

**リクエストパラメータ:**
なし

**レスポンス例:**
```json
{
  "success": true,
  "message": "Joystick control released",
  "data": {
    "released_control_type": "joystick"
  },
  "timestamp": "2025-01-15T10:30:00.000Z"
}
```

---

### 3.3. データストリーミング

#### 3.3.1. データストリーム開始
WHILLからのデータストリーミングを開始します。

- **エンドポイント**: `POST /api/v1/whill/data-streams/start`
- **説明**: リアルタイムデータストリーミングの開始
  - `data_set_number`: 0 => `speed_mode`に該当するスピードプロファイルのストリーミング
  - `data_set_number`: 1 => motor/batteryなど動的に変化するステータスのストリーミング

**リクエストパラメータ:**
```json
{
  "interval_msec": integer,    // 必須: 送信間隔(ms) デフォルト:1000, 最小:10
  "data_set_number": integer,  // 必須: データセット番号(0または1) デフォルト:1
  "speed_mode": integer       // オプション: スピードモード(0-5) デフォルト:4
}
```

**レスポンス例:**
```json
{
  "success": true,
  "message": "Data stream started",
  "data": {
    "interval_msec": 1000,
    "data_set_number": 1,
    "speed_mode": 4
  },
  "timestamp": "2025-01-15T10:30:00.000Z"
}
```

#### 3.3.2. データストリーム停止
アクティブなデータストリーミングを停止します。

- **エンドポイント**: `POST /api/v1/whill/data-streams/stop`
- **説明**: データストリーミングの停止

**リクエストパラメータ:**
なし

**レスポンス例:**
```json
{
  "success": true,
  "message": "Data stream stopped",
  "timestamp": "2025-01-15T10:30:00.000Z"
}
```

---

### 3.4. ステータス監視

#### 3.4.1. ステータス取得
WHILLの包括的なステータス情報を取得します。

- **エンドポイント**: `GET /api/v1/whill/status`
- **説明**: 基本ステータス、バッテリー、モーター情報を含む包括的なステータス

**リクエストパラメータ:**
なし

**レスポンス例:**
```json
{
  "success": true,
  "message": "Comprehensive status retrieved",
  "data": {
    "basic_status": {
      "power_status": 1,
      "speed_mode_indicator": 2,
      "error_code": 0
    },
    "battery": {
      "current": 88,
      "level": 75
    },
    "motors": {
      "left_motor": {
        "angle": -0.807,
        "speed": 4.096
      },
      "right_motor": {
        "angle": 0.807,
        "speed": -4.096
      }
    }
  },
  "timestamp": "2025-01-15T10:30:00.000Z"
}
```

#### 3.4.2. バッテリー情報取得
バッテリー関連の情報を取得します。

- **エンドポイント**: `GET /api/v1/whill/battery`
- **説明**: バッテリー電流・残量の情報

**レスポンス例:**
```json
{
  "success": true,
  "message": "Battery information retrieved",
  "data": {
    "current": 0,
    "level": 75
  },
  "timestamp": "2025-01-15T10:30:00.000Z"
}
```

#### 3.4.3. モーター情報取得
左右モーターの詳細情報を取得します。

- **エンドポイント**: `GET /api/v1/whill/motors`
- **説明**: 左右モーターの角度・速度の情報

**レスポンス例:**
```json
{
  "success": true,
  "message": "Motor information retrieved",
  "data": {
    "left_motor": {
      "angle": -0.807,
      "speed": 4.096
    },
    "right_motor": {
      "angle": 0.807,
      "speed": -4.096
    }
  },
  "timestamp": "2025-01-15T10:30:00.000Z"
}
```

---

### 3.5. 設定

#### 3.5.1. スピードプロファイル設定
WHILLのスピードプロファイルを設定します。

- **エンドポイント**: `POST /api/v1/whill/speed-profiles`
- **説明**: 指定したスピードモードのプロファイル設定

**リクエストパラメータ:**
```json
{
  "speed_mode": integer,  // 必須: スピードモード(0-5)
  "profile": {
    "forward_speed": number,        // 必須: 最大前進速度(8-60)
    "forward_acceleration": number, // 必須: 前進加速度(10-64)
    "forward_deceleration": number, // 必須: 前進減速度(40-160)
    "reverse_speed": number,        // 必須: 最大後退速度(8-30)
    "reverse_acceleration": number, // 必須: 後退加速度(10-50)
    "reverse_deceleration": number, // 必須: 後退減速度(40-80)
    "turn_speed": number,           // 必須: 最大旋回速度(8-35)
    "turn_acceleration": number,    // 必須: 旋回加速度(10-60)
    "turn_deceleration": number     // 必須: 旋回減速度(40-160)
  }
}
```

**レスポンス例:**
```json
{
  "success": true,
  "message": "Speed profile configured",
  "data": {
    "speed_mode": 4,
    "profile": {
      "forward_speed": 60,
      "forward_acceleration": 56,
      "forward_deceleration": 125,
      "reverse_speed": 20,
      "reverse_acceleration": 24,
      "reverse_deceleration": 56,
      "turn_speed": 25,
      "turn_acceleration": 56,
      "turn_deceleration": 72
    }
  },
  "timestamp": "2025-01-15T10:30:00.000Z"
}
```

#### 3.5.2. スピードプロファイル取得
WHILLに設定されている全てのスピードプロファイルを取得します。

- **エンドポイント**: `GET /api/v1/whill/speed-profiles`
- **説明**: 全スピードモードのプロファイル設定取得

**リクエストパラメータ:**
なし

**レスポンス例:**
```json
{
  "success": true,
  "message": "Speed profiles retrieved",
  "data": [
    {
      "mode": 0,
      "profile": {
        "forward_speed": 30,
        "forward_acceleration": 30,
        "forward_deceleration": 80,
        "reverse_speed": 15,
        "reverse_acceleration": 20,
        "reverse_deceleration": 50,
        "turn_speed": 15,
        "turn_acceleration": 30,
        "turn_deceleration": 60
      }
    },
    {
      "mode": 1,
      "profile": {
        "forward_speed": 40,
        "forward_acceleration": 40,
        "forward_deceleration": 100,
        "reverse_speed": 18,
        "reverse_acceleration": 22,
        "reverse_deceleration": 55,
        "turn_speed": 20,
        "turn_acceleration": 40,
        "turn_deceleration": 70
      }
    }
  ],
  "timestamp": "2025-01-15T10:30:00.000Z"
}
```

#### 3.5.3. バッテリー節約設定
WHILLのバッテリー節約機能を設定します。

- **エンドポイント**: `POST /api/v1/whill/battery/saving`
- **説明**: バッテリー残量が低い場合の動作設定

**リクエストパラメータ:**
```json
{
  "low_battery_level": integer,  // 必須: 節約モード開始レベル(1-90) デフォルト:19
  "sounds_buzzer": boolean       // 必須: 低バッテリー時のブザー音 デフォルト:true
}
```

**レスポンス例:**
```json
{
  "success": true,
  "message": "Battery saving settings applied",
  "data": {
    "low_battery_level": 20,
    "sounds_buzzer": true
  },
  "timestamp": "2025-01-15T10:30:00.000Z"
}
```

---

### 3.6. 診断

#### 3.6.1. 接続テスト
WHILLとの接続状態をテストします。

- **エンドポイント**: `GET /api/v1/whill/diagnostics/connection`
- **説明**: WHILLデバイスとの接続状態確認

**リクエストパラメータ:**
なし

**レスポンス例:**
```json
{
  "success": true,
  "message": "Connection test completed",
  "data": {
    "connected": true,
    "port": "COM3"
  },
  "timestamp": "2025-01-15T10:30:00.000Z"
}
```

---

## 4. エラーコード詳細

### 4.1. 400 Bad Request
- **原因**: パラメータエラー、値の範囲外、必須パラメータ未指定
- **対処**: リクエストパラメータを確認し、正しい値で再送信

### 4.2. 500 Internal Server Error
- **原因**: デバイス未接続、内部処理エラー
- **対処**: デバイス接続を確認し、しばらく待ってから再試行

---

## 5. 使用例

### 5.1. curl を使用した基本的な操作

#### 5.1.1. 電源ON

```bash
curl -X POST "http://localhost:5000/api/v1/whill/power" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d "{ \"power_on\": true }"
```

#### 5.1.2. データストリーミング開始
```bash
curl -X POST "http://localhost:5000/api/v1/whill/data-streams/start" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d "{ 
    \"data_set_number\": 1, 
    \"interval_msec\": 1000, 
    \"speed_mode\": 4 
  }"
```

#### 5.1.3. 前進（2秒間持続）
```bash
curl -X POST "http://localhost:5000/api/v1/whill/motion/joystick" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d "{ 
    \"front\": 20, 
    \"side\": 0, 
    \"timeout\": 2000 
  }"
```

#### 5.1.4. 状態取得
```bash
curl -X GET "http://localhost:5000/api/v1/whill/status" \
  -H "accept: application/json"
```

#### 5.1.5. 制御解除
```bash
curl -X POST "http://localhost:5000/api/v1/whill/motion/release" \
  -H "accept: application/json"
```

#### 5.1.6. 電源OFF
```bash
curl -X POST "http://localhost:5000/api/v1/whill/power" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d "{ \"power_on\": false }"
```

---

## 6. 依存ライブラリのライセンス

### 6.1. メインアプリケーション依存関係
このプロジェクトは以下のオープンソースライブラリを使用しています：

| ライブラリ | バージョン | ライセンス | 説明 |
|-----------|-----------|-----------|------|
| pywhill | >=1.5.0 | MIT | WHILLデバイス制御ライブラリ |
| Flask | >=2.0.0 | BSD-3-Clause | Webフレームワーク |
| flasgger | >=0.9.5 | MIT | Swagger UI統合 |
| waitress | >=2.1.0 | ZPL-2.1 | WSGIサーバー |

各ライブラリのライセンス全文は以下のURLで確認できます：
- [pywhill](https://github.com/WHILL/pywhill/blob/master/LICENSE)
- [Flask](https://github.com/pallets/flask/blob/main/LICENSE.txt)
- [flasgger](https://github.com/flasgger/flasgger/blob/master/LICENSE)
- [waitress](https://github.com/Pylons/waitress/blob/main/LICENSE.txt)

### 6.2. 開発ツール依存関係
開発用ツール（Swaggerドキュメント生成など）では以下のライブラリを使用しています：

| ライブラリ | バージョン | ライセンス | 説明 |
|-----------|-----------|-----------|------|
| requests | >=2.25.0 | Apache-2.0 | HTTPライブラリ（開発ツール用） |
| pyyaml | >=5.0 | MIT | YAML処理ライブラリ（開発ツール用） |

開発ツール用ライブラリのライセンス全文：
- [requests](https://github.com/psf/requests/blob/main/LICENSE)
- [pyyaml](https://github.com/yaml/pyyaml/blob/master/LICENSE)

---

## 7. ライセンス
このプロジェクトはMITライセンスの下で公開されています。詳細は`LICENSE`ファイルを参照してください。

---

## 8. 免責事項
このソフトウェアは「現状のまま」提供され、明示的または暗黙的な保証は一切ありません。WHILLデバイスの使用に関連するリスクは、ユーザーが自己責任で負うものとします。


以上//
