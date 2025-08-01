
# WebAPI 仕様書 <!-- omit in toc -->
- [1. 概要](#1-概要)
  - [1.1. API バージョン](#11-api-バージョン)
  - [1.2. ベースURL](#12-ベースurl)
  - [1.3. 認証](#13-認証)
- [2. セットアップ](#2-セットアップ)
  - [2.1. 環境変数の設定](#21-環境変数の設定)
  - [2.2. 環境変数の詳細](#22-環境変数の詳細)
- [3. 共通仕様](#3-共通仕様)
  - [3.1. リクエスト形式](#31-リクエスト形式)
  - [3.2. レスポンス形式](#32-レスポンス形式)
    - [3.2.1. 成功レスポンス](#321-成功レスポンス)
    - [3.2.2. エラーレスポンス](#322-エラーレスポンス)
  - [3.3. HTTPステータスコード](#33-httpステータスコード)
  - [3.4. データ型](#34-データ型)
- [4. エンドポイント仕様](#4-エンドポイント仕様)
  - [4.1. 電源制御](#41-電源制御)
    - [4.1.1. 電源制御](#411-電源制御)
  - [4.2. モーション制御](#42-モーション制御)
    - [4.2.1. ジョイスティック制御](#421-ジョイスティック制御)
    - [4.2.2. 速度制御](#422-速度制御)
    - [4.2.3. 制御解除](#423-制御解除)
  - [4.3. データストリーミング](#43-データストリーミング)
    - [4.3.1. データストリーム開始](#431-データストリーム開始)
    - [4.3.2. データストリーム停止](#432-データストリーム停止)
  - [4.4. ステータス監視](#44-ステータス監視)
    - [4.4.1. ステータス取得](#441-ステータス取得)
    - [4.4.2. バッテリー情報取得](#442-バッテリー情報取得)
    - [4.4.3. モーター情報取得](#443-モーター情報取得)
  - [4.5. 設定](#45-設定)
    - [4.5.1. スピードプロファイル設定](#451-スピードプロファイル設定)
    - [4.5.2. スピードプロファイル取得](#452-スピードプロファイル取得)
    - [4.5.3. バッテリー節約設定](#453-バッテリー節約設定)
  - [4.6. 診断](#46-診断)
    - [4.6.1. 接続テスト](#461-接続テスト)
- [5. エラーコード詳細](#5-エラーコード詳細)
  - [5.1. 400 Bad Request](#51-400-bad-request)
  - [5.2. 500 Internal Server Error](#52-500-internal-server-error)
- [6. 使用例](#6-使用例)
  - [6.1. 基本的な操作](#61-基本的な操作)
  - [6.2. curl を使用した基本的な操作](#62-curl-を使用した基本的な操作)
    - [6.2.1. 電源ON](#621-電源on)
    - [6.2.2. データストリーミング開始](#622-データストリーミング開始)
    - [6.2.3. 前進（2秒間持続）](#623-前進2秒間持続)
    - [6.2.4. 状態取得](#624-状態取得)
    - [6.2.5. 制御解除](#625-制御解除)
    - [6.2.6. 電源OFF](#626-電源off)
- [7. 依存ライブラリのライセンス](#7-依存ライブラリのライセンス)
  - [7.1. メインアプリケーション依存関係](#71-メインアプリケーション依存関係)
  - [7.2. 開発ツール依存関係](#72-開発ツール依存関係)
- [8. ライセンス](#8-ライセンス)
- [9. 免責事項](#9-免責事項)

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

---

## 2. セットアップ

### 2.1. 環境変数の設定

1. 必要なライブラリをインストール：
```bash
pip install -r requirements.txt
```

2. WHILLデバイスをUSBで接続

3. 環境変数の設定（オプション）：
```bash
# Windows (PowerShell)
$env:WHILL_PORT="COM3"
$env:WHILL_HOST="0.0.0.0"
$env:WHILL_PORT_NUMBER="5000"

# Windows (Command Prompt)
set WHILL_PORT=COM3
set WHILL_HOST=0.0.0.0
set WHILL_PORT_NUMBER=5000

# Linux/macOS
export WHILL_PORT="/dev/ttyUSB0"
export WHILL_HOST="0.0.0.0"
export WHILL_PORT_NUMBER="5000"
```

4. WebAPIサーバーを起動：
```bash
python app.py
```

5. ブラウザでの確認（オプション）：
- Swagger UI: `http://localhost:5000/apidocs/`

### 2.2. 環境変数の詳細

| 環境変数名 | デフォルト値 | 説明 |
|-----------|-------------|------|
| `WHILL_PORT` | `COM3` (Windows) / `/dev/ttyUSB0` (Linux/macOS) | WHILLデバイスのシリアルポート |
| `WHILL_HOST` | `127.0.0.1` | WebAPIサーバーのホストアドレス |
| `WHILL_PORT_NUMBER` | `5000` | WebAPIサーバーのポート番号 |

**注意事項:**
- シリアルポート名は接続されているデバイスによって異なります
- Windowsでは通常 `COM1`, `COM2`, `COM3` など
- Linux/macOSでは通常 `/dev/ttyUSB0`, `/dev/ttyACM0` など
- デバイスマネージャー（Windows）または `ls /dev/tty*`（Linux/macOS）で確認できます

---

## 3. 共通仕様

### 3.1. リクエスト形式

| 項目 | 値 |
|------|-----|
| **Content-Type** | `application/json` |
| **文字コード** | UTF-8 |

### 3.2. レスポンス形式

#### 3.2.1. 成功レスポンス
```json
{
  "success": true,
  "message": "成功メッセージ",
  "data": {
    "エンドポイント固有のデータ"
  },
  "timestamp": "2025-01-15T10:30:00.000Z"
}
```

#### 3.2.2. エラーレスポンス
```json
{
  "success": false,
  "error": "エラーメッセージ",
  "timestamp": "2025-01-15T10:30:00.000Z"
}
```

### 3.3. HTTPステータスコード
- `200 OK`: 成功
- `400 Bad Request`: パラメータエラー
- `500 Internal Server Error`: サーバーエラー

### 3.4. データ型
- **boolean**: `true` または `false`
- **integer**: 整数値
- **number**: 数値（整数または小数）

---

## 4. エンドポイント仕様

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

### 4.1. 電源制御

#### 4.1.1. 電源制御
WHILLの電源をON/OFFします。

- **エンドポイント**: `POST /api/v1/whill/power`
- **説明**: WHILL電源の制御

**リクエストパラメータ:**

**JSON Schema:**
```json
{
  "type": "object",
  "required": ["power_on"],
  "properties": {
    "power_on": {
      "type": "boolean",
      "description": "true=電源ON, false=電源OFF"
    }
  }
}
```

**パラメータ詳細:**
- `power_on`: 必須。true=電源ON, false=電源OFF

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

### 4.2. モーション制御
**※注意** 以下のジョイスティック制御および速度制御の"シングルショット"を使用してWHILLを連続動作させる場合には、200ms以内に後続の制御コマンドを送信する必要があります。

#### 4.2.1. ジョイスティック制御
ジョイスティック値による移動制御を行います。

- **エンドポイント**: `POST /api/v1/whill/motion/joystick`
- **説明**: ジョイスティック制御（シングルショットまたは持続制御）

**リクエストパラメータ:**

**JSON Schema:**
```json
{
  "type": "object",
  "required": ["front", "side"],
  "properties": {
    "front": {
      "type": "number",
      "minimum": -100,
      "maximum": 100,
      "description": "前後方向制御値。正の値で前進、負の値で後退"
    },
    "side": {
      "type": "number",
      "minimum": -100,
      "maximum": 100,
      "description": "左右方向制御値。正の値で右旋回、負の値で左旋回"
    },
    "timeout": {
      "type": "number",
      "minimum": 0,
      "description": "持続時間(ms)。0または未指定でシングルショット制御"
    }
  }
}
```

**パラメータ詳細:**
- `front`: 必須。前後方向制御値 (-100 〜 100)。正の値で前進、負の値で後退
- `side`: 必須。左右方向制御値 (-100 〜 100)。正の値で右旋回、負の値で左旋回
- `timeout`: オプション。持続時間(ms)、0または未指定でシングルショット制御、指定した場合は持続制御

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

#### 4.2.2. 速度制御
速度値による移動制御を行います。

- **エンドポイント**: `POST /api/v1/whill/motion/velocity`
- **説明**: 速度制御（シングルショットまたは持続制御）

**リクエストパラメータ:**

**JSON Schema:**
```json
{
  "type": "object",
  "required": ["front", "side"],
  "properties": {
    "front": {
      "type": "number",
      "minimum": -500,
      "maximum": 1500,
      "description": "前後方向速度。単位：0.004[km/h]相当"
    },
    "side": {
      "type": "number",
      "minimum": -750,
      "maximum": 750,
      "description": "左右旋回速度。単位：0.004[km/h]相当"
    },
    "timeout": {
      "type": "number",
      "minimum": 0,
      "description": "持続時間(ms)。0または未指定でシングルショット制御"
    }
  }
}
```

**パラメータ詳細:**
- `front`: 必須。前後方向速度 (-500 〜 1500)。単位：0.004[km/h]相当
- `side`: 必須。左右旋回速度 (-750 〜 750)。単位：0.004[km/h]相当
- `timeout`: オプション。持続時間(ms)、0または未指定でシングルショット制御、指定した場合は持続制御

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

#### 4.2.3. 制御解除
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

### 4.3. データストリーミング

#### 4.3.1. データストリーム開始
WHILLからのデータストリーミングを開始します。

- **エンドポイント**: `POST /api/v1/whill/data-streams/start`
- **説明**: リアルタイムデータストリーミングの開始
  - `data_set_number`: 0 => `speed_mode`に該当するスピードプロファイルのストリーミング
  - `data_set_number`: 1 => motor/batteryなど動的に変化するステータスのストリーミング

**リクエストパラメータ:**

**JSON Schema:**
```json
{
  "type": "object",
  "required": ["interval_msec", "data_set_number"],
  "properties": {
    "interval_msec": {
      "type": "integer",
      "minimum": 10,
      "default": 1000,
      "description": "送信間隔(ms)"
    },
    "data_set_number": {
      "type": "integer",
      "enum": [0, 1],
      "default": 1,
      "description": "データセット番号(0または1)"
    },
    "speed_mode": {
      "type": "integer",
      "minimum": 0,
      "maximum": 5,
      "default": 4,
      "description": "スピードモード(0-5)"
    }
  }
}
```

**パラメータ詳細:**
- `interval_msec`: 必須。送信間隔(ms) デフォルト:1000, 最小:10
- `data_set_number`: 必須。データセット番号(0または1) デフォルト:1
- `speed_mode`: オプション。スピードモード(0-5) デフォルト:4

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

#### 4.3.2. データストリーム停止
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

### 4.4. ステータス監視

#### 4.4.1. ステータス取得
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

#### 4.4.2. バッテリー情報取得
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

#### 4.4.3. モーター情報取得
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

### 4.5. 設定

#### 4.5.1. スピードプロファイル設定
WHILLのスピードプロファイルを設定します。

- **エンドポイント**: `POST /api/v1/whill/speed-profiles`
- **説明**: 指定したスピードモードのプロファイル設定

**リクエストパラメータ:**

**JSON Schema:**
```json
{
  "type": "object",
  "required": ["speed_mode", "profile"],
  "properties": {
    "speed_mode": {
      "type": "integer",
      "minimum": 0,
      "maximum": 5,
      "description": "スピードモード(0-5)"
    },
    "profile": {
      "type": "object",
      "required": [
        "forward_speed", "forward_acceleration", "forward_deceleration",
        "reverse_speed", "reverse_acceleration", "reverse_deceleration",
        "turn_speed", "turn_acceleration", "turn_deceleration"
      ],
      "properties": {
        "forward_speed": {
          "type": "number",
          "minimum": 8,
          "maximum": 60,
          "description": "最大前進速度"
        },
        "forward_acceleration": {
          "type": "number",
          "minimum": 10,
          "maximum": 64,
          "description": "前進加速度"
        },
        "forward_deceleration": {
          "type": "number",
          "minimum": 40,
          "maximum": 160,
          "description": "前進減速度"
        },
        "reverse_speed": {
          "type": "number",
          "minimum": 8,
          "maximum": 30,
          "description": "最大後退速度"
        },
        "reverse_acceleration": {
          "type": "number",
          "minimum": 10,
          "maximum": 50,
          "description": "後退加速度"
        },
        "reverse_deceleration": {
          "type": "number",
          "minimum": 40,
          "maximum": 80,
          "description": "後退減速度"
        },
        "turn_speed": {
          "type": "number",
          "minimum": 8,
          "maximum": 35,
          "description": "最大旋回速度"
        },
        "turn_acceleration": {
          "type": "number",
          "minimum": 10,
          "maximum": 60,
          "description": "旋回加速度"
        },
        "turn_deceleration": {
          "type": "number",
          "minimum": 40,
          "maximum": 160,
          "description": "旋回減速度"
        }
      }
    }
  }
}
```

**パラメータ詳細:**
- `speed_mode`: 必須。スピードモード(0-5)
- `profile.forward_speed`: 必須。最大前進速度(8-60)
- `profile.forward_acceleration`: 必須。前進加速度(10-64)
- `profile.forward_deceleration`: 必須。前進減速度(40-160)
- `profile.reverse_speed`: 必須。最大後退速度(8-30)
- `profile.reverse_acceleration`: 必須。後退加速度(10-50)
- `profile.reverse_deceleration`: 必須。後退減速度(40-80)
- `profile.turn_speed`: 必須。最大旋回速度(8-35)
- `profile.turn_acceleration`: 必須。旋回加速度(10-60)
- `profile.turn_deceleration`: 必須。旋回減速度(40-160)

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

#### 4.5.2. スピードプロファイル取得
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

#### 4.5.3. バッテリー節約設定
WHILLのバッテリー節約機能を設定します。

- **エンドポイント**: `POST /api/v1/whill/battery/saving`
- **説明**: バッテリー残量が低い場合の動作設定

**リクエストパラメータ:**

**JSON Schema:**
```json
{
  "type": "object",
  "required": ["low_battery_level", "sounds_buzzer"],
  "properties": {
    "low_battery_level": {
      "type": "integer",
      "minimum": 1,
      "maximum": 90,
      "default": 19,
      "description": "節約モード開始レベル"
    },
    "sounds_buzzer": {
      "type": "boolean",
      "default": true,
      "description": "低バッテリー時のブザー音"
    }
  }
}
```

**パラメータ詳細:**
- `low_battery_level`: 必須。節約モード開始レベル(1-90) デフォルト:19
- `sounds_buzzer`: 必須。低バッテリー時のブザー音 デフォルト:true

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

### 4.6. 診断

#### 4.6.1. 接続テスト
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

## 5. エラーコード詳細

### 5.1. 400 Bad Request
- **原因**: パラメータエラー、値の範囲外、必須パラメータ未指定
- **対処**: リクエストパラメータを確認し、正しい値で再送信

### 5.2. 500 Internal Server Error
- **原因**: デバイス未接続、内部処理エラー
- **対処**: デバイス接続を確認し、しばらく待ってから再試行

---

## 6. 使用例

### 6.1. 基本的な操作
- **電源ON**: `POST /api/v1/whill/power` に `{"power_on": true}` を送信
- **データストリーミング開始**: `POST /api/v1/whill/data-streams/start` を送信
- **前進**: `POST /api/v1/whill/motion/joystick` に `{"front": 20, "side": 0, "timeout": 2000}` を送信
- **状態確認**: `GET /api/v1/whill/status` で現在の状態を取得
- **停止**: `POST /api/v1/whill/motion/release` を送信
- **電源OFF**: `POST /api/v1/whill/power` に `{"power_on": false}` を送信

### 6.2. curl を使用した基本的な操作

#### 6.2.1. 電源ON

```bash
curl -X POST "http://localhost:5000/api/v1/whill/power" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d "{ \"power_on\": true }"
```

#### 6.2.2. データストリーミング開始
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

#### 6.2.3. 前進（2秒間持続）
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

#### 6.2.4. 状態取得
```bash
curl -X GET "http://localhost:5000/api/v1/whill/status" \
  -H "accept: application/json"
```

#### 6.2.5. 制御解除
```bash
curl -X POST "http://localhost:5000/api/v1/whill/motion/release" \
  -H "accept: application/json"
```

#### 6.2.6. 電源OFF
```bash
curl -X POST "http://localhost:5000/api/v1/whill/power" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d "{ \"power_on\": false }"
```

---

## 7. 依存ライブラリのライセンス

### 7.1. メインアプリケーション依存関係
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

### 7.2. 開発ツール依存関係
開発用ツール（Swaggerドキュメント生成など）では以下のライブラリを使用しています：

| ライブラリ | バージョン | ライセンス | 説明 |
|-----------|-----------|-----------|------|
| requests | >=2.25.0 | Apache-2.0 | HTTPライブラリ（開発ツール用） |
| pyyaml | >=5.0 | MIT | YAML処理ライブラリ（開発ツール用） |

開発ツール用ライブラリのライセンス全文：
- [requests](https://github.com/psf/requests/blob/main/LICENSE)
- [pyyaml](https://github.com/yaml/pyyaml/blob/master/LICENSE)

---

## 8. ライセンス
このプロジェクトはMITライセンスの下で公開されています。詳細は`LICENSE`ファイルを参照してください。

---

## 9. 免責事項
このソフトウェアは「現状のまま」提供され、明示的または暗黙的な保証は一切ありません。WHILLデバイスの使用に関連するリスクは、ユーザーが自己責任で負うものとします。


以上//
