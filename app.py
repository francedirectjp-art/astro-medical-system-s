from flask import Flask, render_template, request, jsonify
import ephem
import math
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# 47都道府県の座標データ
PREFECTURE_COORDINATES = {
    "北海道": {"lat": 43.0642, "lon": 141.3469},
    "青森県": {"lat": 40.8244, "lon": 140.74},
    "岩手県": {"lat": 39.7036, "lon": 141.1527},
    "宮城県": {"lat": 38.2688, "lon": 140.8721},
    "秋田県": {"lat": 39.7186, "lon": 140.1024},
    "山形県": {"lat": 38.2404, "lon": 140.3633},
    "福島県": {"lat": 37.7503, "lon": 140.4676},
    "茨城県": {"lat": 36.3414, "lon": 140.4467},
    "栃木県": {"lat": 36.5658, "lon": 139.8836},
    "群馬県": {"lat": 36.3911, "lon": 139.0608},
    "埼玉県": {"lat": 35.8617, "lon": 139.6455},
    "千葉県": {"lat": 35.6074, "lon": 140.1233},
    "東京都": {"lat": 35.6762, "lon": 139.6503},
    "神奈川県": {"lat": 35.4478, "lon": 139.6425},
    "新潟県": {"lat": 37.9026, "lon": 139.0234},
    "富山県": {"lat": 36.6953, "lon": 137.2113},
    "石川県": {"lat": 36.5946, "lon": 136.6256},
    "福井県": {"lat": 36.0652, "lon": 136.2217},
    "山梨県": {"lat": 35.6638, "lon": 138.5683},
    "長野県": {"lat": 36.6513, "lon": 138.1811},
    "岐阜県": {"lat": 35.3911, "lon": 136.7221},
    "静岡県": {"lat": 34.9769, "lon": 138.3831},
    "愛知県": {"lat": 35.1802, "lon": 136.9066},
    "三重県": {"lat": 34.7303, "lon": 136.5086},
    "滋賀県": {"lat": 35.0045, "lon": 135.8687},
    "京都府": {"lat": 35.0211, "lon": 135.7556},
    "大阪府": {"lat": 34.6862, "lon": 135.5200},
    "兵庫県": {"lat": 34.6913, "lon": 135.1830},
    "奈良県": {"lat": 34.6851, "lon": 135.8332},
    "和歌山県": {"lat": 34.2261, "lon": 135.1675},
    "鳥取県": {"lat": 35.5038, "lon": 134.2382},
    "島根県": {"lat": 35.4721, "lon": 133.0506},
    "岡山県": {"lat": 34.6617, "lon": 133.9349},
    "広島県": {"lat": 34.3965, "lon": 132.4596},
    "山口県": {"lat": 34.1858, "lon": 131.4707},
    "徳島県": {"lat": 34.0658, "lon": 134.5593},
    "香川県": {"lat": 34.3401, "lon": 134.0435},
    "愛媛県": {"lat": 33.8416, "lon": 132.7660},
    "高知県": {"lat": 33.5597, "lon": 133.5311},
    "福岡県": {"lat": 33.6064, "lon": 130.4181},
    "佐賀県": {"lat": 33.2494, "lon": 130.2989},
    "長崎県": {"lat": 32.7503, "lon": 129.8677},
    "熊本県": {"lat": 32.7898, "lon": 130.7417},
    "大分県": {"lat": 33.2382, "lon": 131.6126},
    "宮崎県": {"lat": 31.9077, "lon": 131.4202},
    "鹿児島県": {"lat": 31.5601, "lon": 130.5581},
    "沖縄県": {"lat": 26.2124, "lon": 127.6792}
}

# 星座名の定義（黄経0度から30度区切り）
ZODIAC_SIGNS = [
    '牡羊座', '牡牛座', '双子座', '蟹座', '獅子座', '乙女座',
    '天秤座', '蠍座', '射手座', '山羊座', '水瓶座', '魚座'
]

# 16原型データ
SIXTEEN_ARCHETYPES = {
    ("火", "火"): {"name": "激烈なる戦士", "element_combination": "火×火", "temperament": "情熱的", "body_type": "胆汁質の極致"},
    ("火", "地"): {"name": "実践的指導者", "element_combination": "火×地", "temperament": "力強い", "body_type": "胆汁質と憂鬱質の統合"},
    ("火", "風"): {"name": "革新的冒険家", "element_combination": "火×風", "temperament": "創造的", "body_type": "胆汁質と多血質の結合"},
    ("火", "水"): {"name": "情熱的創造者", "element_combination": "火×水", "temperament": "感情豊か", "body_type": "胆汁質と粘液質の調和"},
    ("地", "火"): {"name": "堅実なる開拓者", "element_combination": "地×火", "temperament": "実行力のある", "body_type": "憂鬱質と胆汁質の統合"},
    ("地", "地"): {"name": "不動の守護者", "element_combination": "地×地", "temperament": "安定した", "body_type": "憂鬱質の完成形"},
    ("地", "風"): {"name": "知的建築家", "element_combination": "地×風", "temperament": "論理的", "body_type": "憂鬱質と多血質の調和"},
    ("地", "水"): {"name": "慈愛なる育成者", "element_combination": "地×水", "temperament": "献身的", "body_type": "憂鬱質と粘液質の融合"},
    ("風", "火"): {"name": "理想的革命家", "element_combination": "風×火", "temperament": "革新的", "body_type": "多血質と胆汁質の結合"},
    ("風", "地"): {"name": "合理的組織者", "element_combination": "風×地", "temperament": "効率的", "body_type": "多血質と憂鬱質の調和"},
    ("風", "風"): {"name": "自由なる思想家", "element_combination": "風×風", "temperament": "知的", "body_type": "多血質の純粋形"},
    ("風", "水"): {"name": "共感的仲介者", "element_combination": "風×水", "temperament": "調和的", "body_type": "多血質と粘液質の統合"},
    ("水", "火"): {"name": "直感的変革者", "element_combination": "水×火", "temperament": "変容をもたらす", "body_type": "粘液質と胆汁質の調和"},
    ("水", "地"): {"name": "感性的職人", "element_combination": "水×地", "temperament": "繊細な", "body_type": "粘液質と憂鬱質の融合"},
    ("水", "風"): {"name": "芸術的伝達者", "element_combination": "水×風", "temperament": "表現豊か", "body_type": "粘液質と多血質の統合"},
    ("水", "水"): {"name": "深淵なる神秘家", "element_combination": "水×水", "temperament": "神秘的", "body_type": "粘液質の深化形"}
}

def rad_to_deg(rad):
    """ラジアンを度に変換"""
    return rad * 180.0 / math.pi

def deg_to_dms(degrees):
    """度を度・分・秒に変換"""
    deg = int(degrees)
    minutes_float = (degrees - deg) * 60
    min_val = int(minutes_float)
    sec = (minutes_float - min_val) * 60
    return deg, min_val, sec

def get_zodiac_info(longitude_deg):
    """黄経度数から星座と星座内度数を取得"""
    # 黄経度数を0-360度に正規化
    longitude_deg = longitude_deg % 360

    # 星座番号（0-11）
    zodiac_index = int(longitude_deg / 30)

    # 星座内での度数
    degree_in_sign = longitude_deg - (zodiac_index * 30)

    return ZODIAC_SIGNS[zodiac_index], degree_in_sign, zodiac_index

def get_element(zodiac_name):
    """星座から四元素を取得"""
    elements = {
        '牡羊座': '火', '獅子座': '火', '射手座': '火',
        '牡牛座': '地', '乙女座': '地', '山羊座': '地', 
        '双子座': '風', '天秤座': '風', '水瓶座': '風',
        '蟹座': '水', '蠍座': '水', '魚座': '水'
    }
    return elements.get(zodiac_name, '不明')

def calculate_celestial_positions(birth_year, birth_month, birth_day, birth_hour, birth_minute, prefecture):
    """
    天体位置を計算（地球中心黄道座標系を使用）
    """
    try:
        # 都道府県座標を取得
        coords = PREFECTURE_COORDINATES.get(prefecture)
        if not coords:
            raise ValueError(f"都道府県 '{prefecture}' の座標データが見つかりません")

        lat = coords['lat']
        lon = coords['lon']

        # 観測地点の設定
        observer = ephem.Observer()
        observer.lat = str(lat)
        observer.lon = str(lon)
        observer.elevation = 0

        # JST時刻をUTCに変換（JST = UTC + 9時間）
        jst = datetime(birth_year, birth_month, birth_day, birth_hour, birth_minute, 0)
        utc = jst - timedelta(hours=9)
        observer.date = utc.strftime('%Y/%m/%d %H:%M:%S')

        # 7天体の定義
        planets = {
            '太陽': ephem.Sun(),
            '月': ephem.Moon(),
            '水星': ephem.Mercury(),
            '金星': ephem.Venus(),
            '火星': ephem.Mars(),
            '木星': ephem.Jupiter(),
            '土星': ephem.Saturn()
        }

        results = {}

        for name, planet in planets.items():
            # 天体位置を計算
            planet.compute(observer)

            # 地球中心黄道座標を取得（占星術で使用する正しい座標系）
            ecliptic = ephem.Ecliptic(planet)
            longitude_deg = rad_to_deg(ecliptic.lon)

            # 星座情報を取得
            zodiac_name, degree_in_sign, zodiac_index = get_zodiac_info(longitude_deg)

            # 度・分・秒に変換
            deg, min_val, sec = deg_to_dms(degree_in_sign)

            # 四元素を取得
            element = get_element(zodiac_name)

            # 結果を保存
            results[name] = {
                'longitude_deg': round(longitude_deg, 6),
                'zodiac': zodiac_name,
                'zodiac_index': zodiac_index,
                'degree_in_sign': round(degree_in_sign, 2),
                'degrees': deg,
                'minutes': min_val,
                'seconds': round(sec, 1),
                'element': element,
                'formatted': f"{zodiac_name}{deg}度{min_val}分{sec:.1f}秒"
            }

        # 16原型判定用の太陽・月データを準備
        sun_element = results['太陽']['element']
        moon_element = results['月']['element']
        archetype_key = (sun_element, moon_element)
        archetype = SIXTEEN_ARCHETYPES.get(archetype_key, {
            "name": "未分類", 
            "element_combination": f"{sun_element}×{moon_element}",
            "temperament": "複合的",
            "body_type": "混合型"
        })

        # 計算情報を追加
        calculation_info = {
            'jst_datetime': jst.strftime('%Y年%m月%d日 %H時%M分'),
            'utc_datetime': utc.strftime('%Y/%m/%d %H:%M:%S'),
            'location': prefecture,
            'coordinates': {'lat': lat, 'lon': lon},
            'coordinate_system': '地球中心黄道座標系 (Geocentric Ecliptic)',
            'archetype': archetype
        }

        return {
            'success': True,
            'celestial_positions': results,
            'calculation_info': calculation_info
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def translate_to_japanese(text):
    """英語の占星術用語を日本語に変換"""
    translations = {
        # 星座名
        'Aries': '牡羊座', 'Taurus': '牡牛座', 'Gemini': '双子座', 'Cancer': '蟹座',
        'Leo': '獅子座', 'Virgo': '乙女座', 'Libra': '天秤座', 'Scorpio': '蠍座',
        'Sagittarius': '射手座', 'Capricorn': '山羊座', 'Aquarius': '水瓶座', 'Pisces': '魚座',

        # 四元素
        'Fire': '火', 'Earth': '地', 'Air': '風', 'Water': '水',

        # 天体名
        'Sun': '太陽', 'Moon': '月', 'Mercury': '水星', 'Venus': '金星',
        'Mars': '火星', 'Jupiter': '木星', 'Saturn': '土星'
    }

    result = text
    for eng, jpn in translations.items():
        result = result.replace(eng, jpn)
    return result

# Flaskルート定義（重複を排除）

@app.route('/')
def input_form():
    """入力ページ"""
    return render_template('input.html', prefectures=list(PREFECTURE_COORDINATES.keys()))

@app.route('/result', methods=['POST'])
def show_result():
    """パーソナライズされた鑑定結果ページ"""
    try:
        # フォームデータを取得
        name = request.form.get('name', '').strip()
        if not name:
            name = "お客様"
        
        birth_year = int(request.form.get('birth_year'))
        birth_month = int(request.form.get('birth_month'))
        birth_day = int(request.form.get('birth_day'))
        birth_hour = int(request.form.get('birth_hour'))
        birth_minute = int(request.form.get('birth_minute'))
        prefecture = request.form.get('prefecture')
        
        # 天体位置を計算
        result = calculate_celestial_positions(
            birth_year, birth_month, birth_day, 
            birth_hour, birth_minute, prefecture
        )
        
        if result['success']:
            # 成功時は結果ページへ
            return render_template('result.html', 
                                 name=name,
                                 data=result['celestial_positions'],
                                 info=result['calculation_info'])
        else:
            # エラー時は入力ページへ戻る
            return render_template('input.html', 
                                 prefectures=list(PREFECTURE_COORDINATES.keys()),
                                 error=result.get('error', '計算エラーが発生しました'))
    
    except Exception as e:
        return render_template('input.html', 
                             prefectures=list(PREFECTURE_COORDINATES.keys()),
                             error=f'エラーが発生しました: {str(e)}')

@app.route('/calculate', methods=['POST'])
def calculate_api():
    """天体計算API"""
    try:
        data = request.json

        # 入力データの検証
        required_fields = ['birth_year', 'birth_month', 'birth_day', 'birth_hour', 'birth_minute', 'prefecture']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'必須フィールド {field} が不足しています'})

        # 名前を取得（オプション）
        name = data.get('name', 'お客様')

        # 天体位置計算
        result = calculate_celestial_positions(
            int(data['birth_year']),
            int(data['birth_month']),
            int(data['birth_day']),
            int(data['birth_hour']),
            int(data['birth_minute']),
            data['prefecture']
        )
        
        # 名前を結果に追加
        if result['success']:
            result['name'] = name

        return jsonify(result)

    except ValueError as e:
        return jsonify({'success': False, 'error': f'入力値エラー: {str(e)}'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'計算エラー: {str(e)}'})

@app.route('/basic_report')
def basic_report_page():
    """基本レポートページ（2000文字）"""
    # URLパラメータから情報を取得
    name = request.args.get('name', 'お客様')
    archetype_name = request.args.get('archetype', '未分類')
    
    # アーキタイプ情報を取得（簡易的に再構築）
    archetype = None
    for key, value in SIXTEEN_ARCHETYPES.items():
        if value['name'] == archetype_name:
            archetype = value
            break
    
    # デフォルトのアーキタイプ情報
    if not archetype:
        archetype = {
            "name": archetype_name,
            "element_combination": "未定",
            "temperament": "複合的",
            "body_type": "混合型"
        }
    
    return render_template('basic_report.html', 
                         name=name,
                         archetype=archetype)

@app.route('/detailed_report') 
def detailed_report_page():
    """詳細レポートページ（12,000文字）"""
    # URLパラメータから情報を取得
    name = request.args.get('name', 'お客様')
    archetype_name = request.args.get('archetype', '未分類')
    
    # アーキタイプ情報を取得（簡易的に再構築）
    archetype = None
    for key, value in SIXTEEN_ARCHETYPES.items():
        if value['name'] == archetype_name:
            archetype = value
            break
    
    # デフォルトのアーキタイプ情報
    if not archetype:
        archetype = {
            "name": archetype_name,
            "element_combination": "未定",
            "temperament": "複合的",
            "body_type": "混合型"
        }
    
    return render_template('detailed_report.html', 
                         name=name,
                         archetype=archetype)

if __name__ == '__main__':
    # Railway環境では環境変数PORTを使用
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
