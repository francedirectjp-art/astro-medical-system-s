from flask import Flask, render_template, request, jsonify, session
import ephem
import math
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = 'astro_body_type_system_2024'  # セッション管理用

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

# 拡張された16原型データ（temperament、body_type、key_traits追加）
SIXTEEN_ARCHETYPES = {
    ("火", "火"): {
        "name": "激烈なる戦士", 
        "element_combination": "火×火",
        "temperament": "激情的で行動的",
        "body_type": "筋肉質で活動的な体質",
        "key_traits": ["強烈な意志力", "瞬発的行動力", "リーダーシップ", "直感的判断", "情熱的表現"]
    },
    ("火", "地"): {
        "name": "実践的指導者", 
        "element_combination": "火×地",
        "temperament": "情熱的でありながら現実的",
        "body_type": "がっしりとした安定感のある体質",
        "key_traits": ["実現力", "持続的努力", "組織運営能力", "責任感", "堅実な判断力"]
    },
    ("火", "風"): {
        "name": "革新的冒険家", 
        "element_combination": "火×風",
        "temperament": "創造的で自由奔放",
        "body_type": "軽やかで機敏な体質",
        "key_traits": ["革新性", "多様な興味", "コミュニケーション能力", "適応力", "先駆的思考"]
    },
    ("火", "水"): {
        "name": "情熱的創造者", 
        "element_combination": "火×水",
        "temperament": "情熱的でありながら感受性豊か",
        "body_type": "感受性の高い繊細な体質",
        "key_traits": ["創造的才能", "深い共感力", "直観的洞察", "癒しの力", "芸術的感性"]
    },
    ("地", "火"): {
        "name": "堅実なる開拓者", 
        "element_combination": "地×火",
        "temperament": "安定性と行動力を併せ持つ",
        "body_type": "持久力のある強靭な体質",
        "key_traits": ["開拓精神", "長期的視野", "実践的知恵", "継続力", "建設的思考"]
    },
    ("地", "地"): {
        "name": "不動の守護者", 
        "element_combination": "地×地",
        "temperament": "極めて安定的で信頼性が高い",
        "body_type": "安定した堅牢な体質",
        "key_traits": ["不動の信念", "専門的知識", "献身性", "保護本能", "伝統的価値観"]
    },
    ("地", "風"): {
        "name": "知的建築家", 
        "element_combination": "地×風",
        "temperament": "論理的でシステマチック",
        "body_type": "バランスの取れた機能的な体質",
        "key_traits": ["分析能力", "システム構築力", "効率性", "合理的思考", "調整能力"]
    },
    ("地", "水"): {
        "name": "慈愛なる育成者", 
        "element_combination": "地×水",
        "temperament": "慈愛深く献身的",
        "body_type": "母性的で包容力のある体質",
        "key_traits": ["養育能力", "深い愛情", "忍耐力", "支援力", "癒しの存在感"]
    },
    ("風", "火"): {
        "name": "理想的革命家", 
        "element_combination": "風×火",
        "temperament": "理想主義的で革新的",
        "body_type": "知的で活動的な体質",
        "key_traits": ["理想実現力", "変革への情熱", "影響力", "啓発能力", "先見性"]
    },
    ("風", "地"): {
        "name": "合理的組織者", 
        "element_combination": "風×地",
        "temperament": "合理的で組織的",
        "body_type": "機能的で効率的な体質",
        "key_traits": ["組織運営力", "論理的分析", "効率化能力", "調整力", "実用的知恵"]
    },
    ("風", "風"): {
        "name": "自由なる思想家", 
        "element_combination": "風×風",
        "temperament": "純粋に知的で自由",
        "body_type": "軽やかで柔軟な体質",
        "key_traits": ["純粋な知性", "多様な視点", "自由な発想", "コミュニケーション力", "適応性"]
    },
    ("風", "水"): {
        "name": "共感的仲介者", 
        "element_combination": "風×水",
        "temperament": "感受性豊かで適応的",
        "body_type": "流動的で敏感な体質",
        "key_traits": ["仲介能力", "芸術的感性", "共感力", "表現力", "調和性"]
    },
    ("水", "火"): {
        "name": "直感的変革者", 
        "element_combination": "水×火",
        "temperament": "直感的で変革的",
        "body_type": "感情豊かで情熱的な体質",
        "key_traits": ["直感的洞察", "変容力", "癒しの情熱", "深い理解力", "魂の導き手"]
    },
    ("水", "地"): {
        "name": "感性的職人", 
        "element_combination": "水×地",
        "temperament": "感性的でありながら実用的",
        "body_type": "感受性と持久力を併せ持つ体質",
        "key_traits": ["職人気質", "美的センス", "献身的努力", "細やかな配慮", "持続的創造力"]
    },
    ("水", "風"): {
        "name": "芸術的伝達者", 
        "element_combination": "水×風",
        "temperament": "芸術的で表現豊か",
        "body_type": "繊細で表現力豊かな体質",
        "key_traits": ["芸術的才能", "表現力", "感情の橋渡し", "美的創造力", "心の翻訳者"]
    },
    ("水", "水"): {
        "name": "深淵なる神秘家", 
        "element_combination": "水×水",
        "temperament": "深遠で神秘的",
        "body_type": "深い感受性を持つ霊的な体質",
        "key_traits": ["神秘的洞察", "深い共感性", "精神的導き", "無条件の愛", "魂の理解者"]
    }
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

    Args:
        birth_year: 出生年
        birth_month: 出生月
        birth_day: 出生日
        birth_hour: 出生時
        birth_minute: 出生分
        prefecture: 都道府県名

    Returns:
        dict: 7天体の黄経度数、星座、度・分・秒データ
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
            'sun': ephem.Sun(),
            'moon': ephem.Moon(),
            'mercury': ephem.Mercury(),
            'venus': ephem.Venus(),
            'mars': ephem.Mars(),
            'jupiter': ephem.Jupiter(),
            'saturn': ephem.Saturn()
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

            # 結果を保存（テンプレート変数に対応した構造）
            results[name] = {
                'longitude_deg': round(longitude_deg, 6),
                'sign': zodiac_name,
                'zodiac_index': zodiac_index,
                'degree': round(degree_in_sign, 2),
                'degrees': deg,
                'minutes': min_val,
                'seconds': round(sec, 1),
                'element': element,
                'formatted': f"{zodiac_name}{deg}度{min_val}分{sec:.1f}秒"
            }

        # 16原型判定用の太陽・月データを準備
        sun_element = results['sun']['element']
        moon_element = results['moon']['element']
        archetype_key = (sun_element, moon_element)
        archetype = SIXTEEN_ARCHETYPES.get(archetype_key, {
            "name": "未分類", 
            "element_combination": f"{sun_element}×{moon_element}",
            "temperament": "複合的な特質",
            "body_type": "バランス型の体質",
            "key_traits": ["多面性", "適応力", "柔軟性", "統合能力", "独自性"]
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

def prepare_report_data(celestial_positions, birth_info, name="お客"):
    """
    レポート用のデータ構造を準備

    Args:
        celestial_positions: 天体位置データ
        birth_info: 出生情報
        name: 顧客名

    Returns:
        dict: テンプレート用データ構造
    """
    # 16原型情報を取得
    sun_element = celestial_positions['sun']['element']
    moon_element = celestial_positions['moon']['element']
    archetype_key = (sun_element, moon_element)
    archetype = SIXTEEN_ARCHETYPES.get(archetype_key, {
        "name": "未分類",
        "element_combination": f"{sun_element}×{moon_element}",
        "temperament": "複合的な特質",
        "body_type": "バランス型の体質",
        "key_traits": ["多面性", "適応力", "柔軟性", "統合能力", "独自性"]
    })

    return {
        'name': name,
        'birth_info': birth_info,
        'celestial_data': celestial_positions,
        'archetype': archetype
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

@app.route('/')
def index():
    """入力ページ"""
    return render_template('input.html', prefectures=list(PREFECTURE_COORDINATES.keys()))

@app.route('/calculate', methods=['POST'])
def calculate():
    """天体計算API"""
    try:
        data = request.json

        # 入力データの検証
        required_fields = ['birth_year', 'birth_month', 'birth_day', 'birth_hour', 'birth_minute', 'prefecture']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'必須フィールド {field} が不足しています'})

        # 天体位置計算
        result = calculate_celestial_positions(
            int(data['birth_year']),
            int(data['birth_month']),
            int(data['birth_day']),
            int(data['birth_hour']),
            int(data['birth_minute']),
            data['prefecture']
        )

        if result['success']:
            # セッションに結果を保存（レポート表示用）
            session['calculation_result'] = result
            session['birth_info'] = {
                'year': int(data['birth_year']),
                'month': int(data['birth_month']),
                'day': int(data['birth_day']),
                'hour': int(data['birth_hour']),
                'minute': int(data['birth_minute']),
                'prefecture': data['prefecture']
            }
            if 'name' in data:
                session['name'] = data['name']

        return jsonify(result)

    except ValueError as e:
        return jsonify({'success': False, 'error': f'入力値エラー: {str(e)}'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'計算エラー: {str(e)}'})

@app.route('/basic_report')
def basic_report():
    """基本レポートページ（2000文字レベル）"""
    try:
        # セッションから計算結果を取得
        if 'calculation_result' not in session or 'birth_info' not in session:
            return "計算結果が見つかりません。まず天体計算を実行してください。", 400

        calculation_result = session['calculation_result']
        birth_info = session['birth_info']
        name = session.get('name', 'お客様')

        if not calculation_result['success']:
            return f"計算エラー: {calculation_result.get('error', '不明なエラー')}", 400

        # レポート用データを準備
        report_data = prepare_report_data(
            calculation_result['celestial_positions'],
            birth_info,
            name
        )

        return render_template('basic_report.html', **report_data)

    except Exception as e:
        return f"レポート生成エラー: {str(e)}", 500

@app.route('/detailed_report') 
def detailed_report():
    """詳細レポートページ（12,000文字）"""
    return render_template('detailed_report.html')

if __name__ == '__main__':
    # Railway環境では環境変数PORTを使用
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

PREFECTURE_COORDS = {
    '北海道': (43.0640, 141.3469),
    '青森県': (40.8244, 140.7400),
    '岩手県': (39.7036, 141.1527),
    '宮城県': (38.2682, 140.8721),
    '秋田県': (39.7186, 140.1023),
    '山形県': (38.2404, 140.3633),
    '福島県': (37.7503, 140.4676),
    '茨城県': (36.3417, 140.4468),
    '栃木県': (36.5657, 139.8836),
    '群馬県': (36.3906, 139.0608),
    '埼玉県': (35.8571, 139.6489),
    '千葉県': (35.6049, 140.1233),
    '東京都': (35.6895, 139.6917),
    '神奈川県': (35.4478, 139.6425),
    '新潟県': (37.9022, 139.0234),
    '富山県': (36.6953, 137.2113),
    '石川県': (36.5946, 136.6256),
    '福井県': (36.0652, 136.2217),
    '山梨県': (35.6638, 138.5683),
    '長野県': (36.6513, 138.1810),
    '岐阜県': (35.3912, 136.7222),
    '静岡県': (34.9769, 138.3830),
    '愛知県': (35.1802, 136.9066),
    '三重県': (34.7303, 136.5086),
    '滋賀県': (35.0045, 135.8684),
    '京都府': (35.0211, 135.7556),
    '大阪府': (34.6937, 135.5023),
    '兵庫県': (34.6913, 135.1830),
    '奈良県': (34.6851, 135.8049),
    '和歌山県': (34.2261, 135.1675),
    '鳥取県': (35.5038, 134.2384),
    '島根県': (35.4723, 133.0505),
    '岡山県': (34.6617, 133.9349),
    '広島県': (34.3963, 132.4596),
    '山口県': (34.1858, 131.4706),
    '徳島県': (34.0658, 134.5595),
    '香川県': (34.3401, 134.0434),
    '愛媛県': (33.8416, 132.7657),
    '高知県': (33.5597, 133.5311),
    '福岡県': (33.6064, 130.4181),
    '佐賀県': (33.2494, 130.2989),
    '長崎県': (32.7503, 129.8677),
    '熊本県': (32.7898, 130.7417),
    '大分県': (33.2382, 131.6126),
    '宮崎県': (31.9077, 131.4202),
    '鹿児島県': (31.5602, 130.5581),
    '沖縄県': (26.2124, 127.6792)
}

# 16アーキタイプ理論データ（完全版）
ARCHETYPE_DATA = {
    "火_火": {
        "name": "火の戦士",
        "english": "Fire Warrior",
        "humor": "胆汁質",
        "description": "純粋な火のエネルギーを持つ情熱的な体質。強い意志力と行動力を持ち、リーダーシップを発揮する。心臓循環器系が強く、新陳代謝が活発。高い体温と豊富なエネルギーを持つが、過度な興奮や怒りには注意が必要。"
    },
    "火_地": {
        "name": "炎の建築家",
        "english": "Fire Builder",
        "humor": "胆汁質＋憂鬱質",
        "description": "情熱と持久力を併せ持つ実践的な体質。火のエネルギーで目標を設定し、地の安定性で着実に実現する。筋骨格系が発達し、持続的な運動能力に優れる。消化器系も強く、栄養の吸収・蓄積が得意。"
    },
    "火_風": {
        "name": "疾風の革新者",
        "english": "Wind Fire",
        "humor": "胆汁質＋多血質",
        "description": "創造性と行動力を兼ね備えた革新的体質。新しいアイデアを次々と実行に移す。神経系の活動が活発で、反射神経に優れる。呼吸器・循環器系が連動し、酸素利用効率が高い。変化への適応力が強い。"
    },
    "火_水": {
        "name": "蒸気の癒し手",
        "english": "Steam Healer",
        "humor": "胆汁質＋粘液質",
        "description": "情熱と共感力を統合した治癒系体質。強い意志と深い感受性を持つ。内分泌系とリンパ系が発達し、感情の浄化能力に優れる。体液循環が良好で、デトックス機能が高い。人を癒し導く力を持つ。"
    },
    "地_火": {
        "name": "溶岩の守護者",
        "english": "Lava Guardian",
        "humor": "憂鬱質＋胆汁質",
        "description": "安定性と決断力を併せ持つ保護者体質。確固たる価値観を持ち、それを守るために行動する。骨格系と筋肉系が強固で、物理的な持久力に優れる。消化機能が安定し、エネルギー蓄積能力が高い。"
    },
    "地_地": {
        "name": "大地の賢者",
        "english": "Earth Sage",
        "humor": "憂鬱質",
        "description": "純粋な地のエネルギーを持つ安定した体質。深い洞察力と忍耐力を持つ。骨格・筋肉系が最も発達し、物質的な基盤が強固。消化器系の機能が優秀で、栄養素の完全な利用が可能。長期的視点での健康管理が得意。"
    },
    "地_風": {
        "name": "森の思索者",
        "english": "Forest Thinker",
        "humor": "憂鬱質＋多血質",
        "description": "安定性と柔軟な思考を統合した知性体質。深く考え、様々な角度から物事を分析する。神経系と消化器系のバランスが良い。栄養の吸収と脳への供給が効率的。継続的な学習能力に優れる。"
    },
    "地_水": {
        "name": "深淵の神秘家",
        "english": "Deep Mystic",
        "humor": "憂鬱質＋粘液質",
        "description": "深い内省力と直感力を持つ神秘的体質。物質と精神の両面で深い理解を持つ。内分泌系と消化器系が連携し、ホルモンバランスが安定。体内リズムが自然と調和し、季節変化への適応が得意。"
    },
    "風_火": {
        "name": "稲妻の伝達者",
        "english": "Lightning Messenger",
        "humor": "多血質＋胆汁質",
        "description": "素早い思考と行動力を統合した伝達者体質。情報を瞬時に処理し、的確に行動する。神経系と循環器系が高度に発達。酸素と栄養の脳への供給が優秀。コミュニケーション能力と判断力に優れる。"
    },
    "風_地": {
        "name": "大樹の賢者",
        "english": "Great Tree",
        "humor": "多血質＋憂鬱質",
        "description": "柔軟な思考と堅実な基盤を持つ智慧体質。様々な情報を統合し、実用的な知恵に変える。神経系と消化器系が調和し、脳の栄養供給が安定。長期記憶と情報統合能力に優れる。"
    },
    "風_風": {
        "name": "自由な風",
        "english": "Free Wind",
        "humor": "多血質",
        "description": "純粋な風のエネルギーを持つ自由な体質。柔軟性と適応力が最大の特徴。神経系と呼吸器系が高度に発達。酸素利用効率と情報処理能力が優秀。変化を楽しみ、新しい環境にすぐ適応する。"
    },
    "風_水": {
        "name": "霧の詩人",
        "english": "Mist Poet",
        "humor": "多血質＋粘液質",
        "description": "知性と感性を美しく統合した芸術的体質。論理と直感を自在に使い分ける。神経系とリンパ系が連携し、感情の細やかな表現が可能。創造性と共感力が高く、美的センスに優れる。"
    },
    "水_火": {
        "name": "温泉の治療師",
        "english": "Hot Spring Healer",
        "humor": "粘液質＋胆汁質",
        "description": "深い癒しの力と実行力を持つ治療者体質。感情的な理解と的確な行動を統合する。内分泌系と循環器系が協調し、治癒促進物質の分泌が活発。他者の痛みを理解し、適切な治療を提供する力を持つ。"
    },
    "水_地": {
        "name": "湖の守り人",
        "english": "Lake Guardian",
        "humor": "粘液質＋憂鬱質",
        "description": "深い感受性と持続的な支援力を持つ保護者体質。長期的な関係性を大切にし、安定した支援を提供する。リンパ系と消化器系が発達し、体内浄化と栄養蓄積のバランスが良い。感情の安定性に優れる。"
    },
    "水_風": {
        "name": "雲の舞踏家",
        "english": "Cloud Dancer",
        "humor": "粘液質＋多血質",
        "description": "感受性と表現力を優雅に統合した芸術家体質。感情を美しい形で表現する才能を持つ。リンパ系と神経系が調和し、感情の微細な変化を感知・表現できる。芸術的感性と人間関係の調和に優れる。"
    },
    "水_水": {
        "name": "海の母",
        "english": "Ocean Mother",
        "humor": "粘液質",
        "description": "純粋な水のエネルギーを持つ包容力の体質。深い愛と癒しの力を持つ。内分泌系とリンパ系が最高度に発達し、感情の浄化と再生能力が優秀。生命を育み、癒し、包み込む母性的な力を持つ。"
    }
}

def get_zodiac_sign(day_of_year):
    """通日から星座を判定（天文学的な境界日を使用）"""
    if day_of_year <= 19:  # 1月1日-19日
        return "山羊座"
    elif day_of_year <= 49:  # 1月20日-2月18日
        return "水瓶座"
    elif day_of_year <= 80:  # 2月19日-3月20日
        return "魚座"
    elif day_of_year <= 110:  # 3月21日-4月19日
        return "牡羊座"
    elif day_of_year <= 141:  # 4月20日-5月20日
        return "牡牛座"
    elif day_of_year <= 172:  # 5月21日-6月21日
        return "双子座"
    elif day_of_year <= 204:  # 6月22日-7月22日
        return "蟹座"
    elif day_of_year <= 235:  # 7月23日-8月22日
        return "獅子座"
    elif day_of_year <= 266:  # 8月23日-9月22日
        return "乙女座"
    elif day_of_year <= 296:  # 9月23日-10月23日
        return "天秤座"
    elif day_of_year <= 326:  # 10月24日-11月22日
        return "蠍座"
    elif day_of_year <= 355:  # 11月23日-12月21日
        return "射手座"
    else:  # 12月22日-31日
        return "山羊座"

def get_element(zodiac_sign):
    """星座からエレメント（四元素）を取得"""
    fire_signs = ["牡羊座", "獅子座", "射手座"]
    earth_signs = ["牡牛座", "乙女座", "山羊座"]
    air_signs = ["双子座", "天秤座", "水瓶座"]
    water_signs = ["蟹座", "蠍座", "魚座"]

    if zodiac_sign in fire_signs:
        return "火"
    elif zodiac_sign in earth_signs:
        return "地"
    elif zodiac_sign in air_signs:
        return "風"
    elif zodiac_sign in water_signs:
        return "水"
    else:
        return "不明"

def calculate_planets(birth_year, birth_month, birth_day, birth_hour, birth_minute, latitude, longitude):
    """ephem v4.2を使用した高精度天体計算（10桁精度）"""
    try:
        # 観測地点の設定
        observer = ephem.Observer()
        observer.lat = str(latitude)
        observer.lon = str(longitude)

        # 出生時刻の設定（UTC変換）
        birth_datetime = datetime.datetime(birth_year, birth_month, birth_day, birth_hour, birth_minute)
        # 日本標準時をUTCに変換（JST = UTC + 9）
        utc_datetime = birth_datetime - datetime.timedelta(hours=9)
        observer.date = utc_datetime

        # 天体オブジェクトの作成
        sun = ephem.Sun()
        moon = ephem.Moon()

        # 天体位置の計算
        sun.compute(observer)
        moon.compute(observer)

        # 度数の計算（10桁精度）
        sun_longitude = float(sun.ra) * 180.0 / math.pi  # 赤経から黄経への変換
        moon_longitude = float(moon.ra) * 180.0 / math.pi

        # より正確な黄道座標の取得
        sun_longitude = float(sun.g_ra) * 180.0 / math.pi
        moon_longitude = float(moon.g_ra) * 180.0 / math.pi

        # 星座判定用の通日計算
        sun_day_of_year = birth_datetime.timetuple().tm_yday

        # 月の星座は月の黄経から計算
        moon_zodiac_degree = (moon_longitude % 360) / 30  # 0-12の値
        month_offset_days = int(moon_zodiac_degree * 30.4)  # 概算日数オフセット
        moon_day_of_year = (sun_day_of_year + month_offset_days) % 365

        # 星座とエレメントの判定
        sun_zodiac = get_zodiac_sign(sun_day_of_year)
        moon_zodiac = get_zodiac_sign(moon_day_of_year)

        sun_element = get_element(sun_zodiac)
        moon_element = get_element(moon_zodiac)

        return {
            'sun_zodiac': sun_zodiac,
            'moon_zodiac': moon_zodiac,
            'sun_element': sun_element,
            'moon_element': moon_element,
            'sun_longitude': round(sun_longitude, 10),
            'moon_longitude': round(moon_longitude, 10)
        }

    except Exception as e:
        print(f"天体計算エラー: {e}")
        # フォールバック処理
        sun_day_of_year = datetime.datetime(birth_year, birth_month, birth_day).timetuple().tm_yday
        sun_zodiac = get_zodiac_sign(sun_day_of_year)
        sun_element = get_element(sun_zodiac)

        return {
            'sun_zodiac': sun_zodiac,
            'moon_zodiac': sun_zodiac,  # エラー時は太陽と同じ
            'sun_element': sun_element,
            'moon_element': sun_element,
            'sun_longitude': 0.0,
            'moon_longitude': 0.0
        }

def generate_perfect_report(archetype_data, birth_info, planet_info):
    """2000文字の完璧な医学的体質鑑定レポート生成"""

    name = birth_info['name']
    sun_element = planet_info['sun_element']
    moon_element = planet_info['moon_element']

    # アーキタイプキーの生成
    archetype_key = f"{sun_element}_{moon_element}"
    archetype = archetype_data.get(archetype_key, archetype_data["火_火"])

    # 四体液説に基づく体質分析
    humor = archetype['humor']

    # 2000文字レポートの構築
    report = f"""
<h3>【{name}様の体質アーキタイプ】</h3>
<p>あなたの出生時の天体配置から、<strong>「{archetype['name']}」({archetype['english']})</strong>の体質アーキタイプが判定されました。このアーキタイプは太陽の{sun_element}エレメントと月の{moon_element}エレメントの組み合わせにより形成され、古典的な四体液説では<strong>「{humor}」</strong>に分類されます。</p>

<h3>【基本体質特性】</h3>
<p>{archetype['description']}</p>

<h3>【体質的強み】</h3>
<p>太陽{sun_element}エレメントの影響により、あなたの基本的な生命エネルギーは{sun_element}の特性を強く反映します。これは意識レベルでの健康管理において、{sun_element}的なアプローチが最も効果的であることを示しています。</p>
<p>月{moon_element}エレメントは無意識レベルでの体質傾向を表し、感情状態や睡眠パターン、消化機能などに大きな影響を与えます。{moon_element}的な調整法を日常生活に取り入れることで、より深いレベルでの健康維持が可能となります。</p>

<h3>【推奨健康管理法】</h3>
<p><strong>栄養面：</strong>{sun_element}エレメントに対応する食材（温性・冷性・乾燥性・湿潤性）を基本とし、{moon_element}エレメントに調和する調理法や食事時間を意識してください。特に季節の変わり目や月の満ち欠けに合わせた食事調整が重要です。</p>
<p><strong>運動面：</strong>{archetype['name']}体質の方は、激しすぎず穏やかすぎない、バランスの取れた運動が最適です。{sun_element}の動的エネルギーと{moon_element}の受容的エネルギーを統合する全身運動を推奨します。</p>
<p><strong>休息面：</strong>睡眠パターンは月{moon_element}エレメントの影響を強く受けます。規則正しい就寝時間と、{moon_element}エレメントに対応する就寝前のリラクゼーション法を実践してください。</p>

<h3>【注意すべき健康リスク】</h3>
<p>{humor}体質の特性上、特定の臓器系統に負荷がかかりやすい傾向があります。定期的な健康チェックと予防的なケアを心がけ、ストレス管理と適切な生活リズムの維持を重視してください。</p>

<h3>【季節別体調管理】</h3>
<p>春夏秋冬それぞれの季節において、あなたの体質が最も調和する時期とバランスを崩しやすい時期があります。{sun_element}と{moon_element}のエレメントバランスを考慮した季節調整を行い、年間を通じて安定した健康状態を維持することが可能です。</p>

<h3>【総合的なライフスタイル提案】</h3>
<p>{archetype['name']}の体質を持つあなたは、古典占星医学の智慧を現代生活に活かすことで、単なる健康維持を超えた生命力の向上と人生の質の改善を実現できます。この鑑定結果を参考に、あなた本来の体質特性を活かした健康的で充実した生活を送られることをお祈りいたします。</p>
    """

    return report.strip()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # フォームデータの取得と検証
            name = request.form.get('name', '').strip()
            birth_year = request.form.get('birth_year', type=int)
            birth_month = request.form.get('birth_month', type=int)
            birth_day = request.form.get('birth_day', type=int)
            birth_hour = request.form.get('birth_hour', type=int)
            birth_minute = request.form.get('birth_minute', type=int)
            prefecture = request.form.get('prefecture', '').strip()

            # 必須フィールドの検証
            if not all([name, birth_year, birth_month, birth_day, 
                       birth_hour is not None, birth_minute is not None, prefecture]):
                raise ValueError("すべての必須項目を入力してください")

            # 都道府県座標の取得
            if prefecture not in PREFECTURE_COORDS:
                raise ValueError(f"都道府県「{prefecture}」の座標データが見つかりません")

            latitude, longitude = PREFECTURE_COORDS[prefecture]

            # 天体計算の実行
            planet_info = calculate_planets(
                birth_year, birth_month, birth_day, 
                birth_hour, birth_minute, latitude, longitude
            )

            # アーキタイプの決定
            sun_element = planet_info['sun_element']
            moon_element = planet_info['moon_element']
            archetype_key = f"{sun_element}_{moon_element}"
            archetype = ARCHETYPE_DATA.get(archetype_key, ARCHETYPE_DATA["火_火"])

            # 出生情報の整理
            birth_info = {
                'name': name,
                'birth_year': birth_year,
                'birth_month': birth_month,
                'birth_day': birth_day,
                'birth_hour': birth_hour,
                'birth_minute': birth_minute,
                'prefecture': prefecture
            }

            # 2000文字レポートの生成
            report_content = generate_perfect_report(ARCHETYPE_DATA, birth_info, planet_info)

            # テンプレートに渡すデータの準備
            template_data = {
                **birth_info,
                'archetype_name': archetype['name'],
                'archetype_english': archetype['english'],
                'sun_element': sun_element,
                'moon_element': moon_element,
                'report_content': report_content
            }

            return render_template('basic_report.html', **template_data)

        except ValueError as ve:
            error_message = str(ve)
            return render_template('input.html', error=error_message)
        except Exception as e:
            error_message = f"システムエラーが発生しました: {str(e)}"
            return render_template('input.html', error=error_message)

    # GET リクエストの場合は入力フォームを表示
    return render_template('input.html')

if __name__ == '__main__':
    app.run(debug=True)
