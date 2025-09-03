from flask import Flask, render_template, request, jsonify, session
import ephem
import math
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-for-session-management-change-in-production'

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
    ("火", "火"): {
        "name": "超新星",
        "name_en": "The Supernova",
        "element_combination": "火×火",
        "tagline": "純粋で混じり気のない情熱の化身。内外のベクトルが一つの目的に完全一致する。",
        "temperament": "純粋な情熱",
        "body_type": "胆汁質の極致",
        "core": "純粋で混じり気のない情熱の化身。彼らの内なる世界と外に向かう表現は、燃え盛る炎のような一つの目的に向かって完全に一致しています。",
        "talents": "圧倒的な行動力と決断の速さ。困難を前にしても怯まず、直感に従って突き進む勇気。",
        "challenges": "地の「現実感覚」と水の「共感性」の欠如。忍耐を学び、結果への配慮と感情の機微への感受性を育むことが課題。"
    },
    ("火", "地"): {
        "name": "マグマ",
        "name_en": "The Magma",
        "element_combination": "火×地",
        "tagline": "熱血のリアリスト。燃えるビジョンを現実的な忍耐で形にする建設者。",
        "temperament": "熱血のリアリスト",
        "body_type": "胆汁質と憂鬱質の統合",
        "core": "燃えるようなビジョンを抱きながらも、その情熱を現実的で忍耐強い、地に足のついた感情の性質を通して表現します。",
        "talents": "壮大なビジョンと実行力を兼備。目標設定後の粘り強さと集中力に優れる。",
        "challenges": "風の「代替案」や水の「感情配慮」を見落としがち。柔軟性と協力の価値を学ぶことが課題。"
    },
    ("火", "風"): {
        "name": "伝道師",
        "name_en": "The Evangelist",
        "element_combination": "火×風",
        "tagline": "熱狂のカリスマ。情熱×知性でムーブメントを起こすストーリーテラー。",
        "temperament": "熱狂のカリスマ",
        "body_type": "胆汁質と多血質の結合",
        "core": "情熱は知性によって磨かれ、伝染性の高い熱意で語られる。卓越したストーリーテラー／リーダー／プレゼンター。",
        "talents": "斬新な発想力と魅力的な伝達力。社交性も高く、多様なネットワークを構築。",
        "challenges": "地の「質実剛健さ」が不足。アイデアが絵に描いた餅に終わるリスク。"
    },
    ("火", "水"): {
        "name": "間欠泉",
        "name_en": "The Geyser",
        "element_combination": "火×水",
        "tagline": "激情の共感者。深い感情を熱して行動へ昇華するダイナモ。",
        "temperament": "激情の共感者",
        "body_type": "胆汁質と粘液質の調和",
        "core": "行動は深く強力な感情の流れに突き動かされる。猛烈に守り、強烈に忠実。",
        "talents": "並外れた共感力と爆発的行動力。豊かな感情は創造の源泉。",
        "challenges": "感情の波に飲み込まれ客観性を失いやすい。地の現実感と風の論理を学ぶ。"
    },
    ("地", "火"): {
        "name": "火山",
        "name_en": "The Volcano",
        "element_combination": "地×火",
        "tagline": "現実的なる情熱家。静かな構造に熱源を秘め、決定的一手で噴火する。",
        "temperament": "現実的な情熱家",
        "body_type": "憂鬱質と胆汁質の統合",
        "core": "穏やかで有能な外面の奥に、野心と情熱のマグマ。忍耐強い建設者だが、好機には決定的で力強い行動力で噴火する。",
        "talents": "壮大な夢を現実にする計画力と実行力。リスク判断と大胆な行動を兼備。",
        "challenges": "推進力が他者のアイデア（風）や感情（水）を軽視して見えることがある。"
    },
    ("地", "地"): {
        "name": "岩盤",
        "name_en": "The Bedrock",
        "element_combination": "地×地",
        "tagline": "揺るぎなき現実主義者。安定・忍耐・実用の究極形。",
        "temperament": "揺るぎなき現実主義",
        "body_type": "憂鬱質の完成形",
        "core": "安定、忍耐、実用性の究極的体現者。内外の目的は測定可能な達成に完全調和。",
        "talents": "具体化、計画、粘り強い実現力に他の追随を許さない。五感に根差した生活力。",
        "challenges": "安定性が頑固さや視野の狭さになりうる。火の自発性と風の好奇心を意識的に取り入れる。"
    },
    ("地", "風"): {
        "name": "サバンナ",
        "name_en": "The Savannah",
        "element_combination": "地×風",
        "tagline": "現実的な設計者。理にかなう美しい構造を現実へ落とし込む。",
        "temperament": "現実的な設計者",
        "body_type": "憂鬱質と多血質の調和",
        "core": "知的な青写真を現実へ落とし込む達人。合理と効率、エレガントな理論と実用を両立。",
        "talents": "冷静客観で状況把握、科学的思考で判断。交渉や根回しも涼やかに。",
        "challenges": "合理と効率の優先で情熱（火）や感情（水）を見失いがち。"
    },
    ("地", "水"): {
        "name": "庭園",
        "name_en": "The Garden",
        "element_combination": "地×水",
        "tagline": "育む供給者。愛と実務で安心と豊かさをつくる肥沃な大地。",
        "temperament": "育む供給者",
        "body_type": "憂鬱質と粘液質の融合",
        "core": "深い共感と愛情を、具体的な安定と快適さの創造で表す。究極の世話役。",
        "talents": "思いやりと繊細さ、現実的たくましさを兼備。役立つ喜びに尽くす。",
        "challenges": "身近なサークルに集中しすぎ、個人的輝き（火）や広い視点（風）を忘れがち。"
    },
    ("風", "火"): {
        "name": "山火事",
        "name_en": "The Wildfire",
        "element_combination": "風×火",
        "tagline": "情熱のメッセンジャー。言葉で熱を点火し、理想へ駆け上がる。",
        "temperament": "情熱のメッセンジャー",
        "body_type": "多血質と胆汁質の結合",
        "core": "アイデアは火花となって他者に熱意を点火。ダイナミックなコミュニケーター、社会的触媒。",
        "talents": "発想力と社交性。積極的に外へ出て交流し、チャンスを嗅ぎ取る能力。",
        "challenges": "地の基盤と水の深みが欠けやすい。アウトプット過多でエネルギー切れ。"
    },
    ("風", "地"): {
        "name": "砂岩の彫刻家",
        "name_en": "The Sandstone Carver",
        "element_combination": "風×地",
        "tagline": "合理的な現実主義者。抽象に形を与え、思考をシステムへ刻む。",
        "temperament": "合理的な現実主義",
        "body_type": "多血質と憂鬱質の調和",
        "core": "抽象を取り上げ構造と形を与える達人。明晰で論理的、社交的でありながら地に足がついた能力。",
        "talents": "高いコミュ力で誰とでも合わせられる。最終判断は肌感覚に基づく。",
        "challenges": "合理と現実性の融合が火の情熱や水の感情を欠いた冷徹さに映ることがある。"
    },
    ("風", "風"): {
        "name": "サイクロン",
        "name_en": "The Cyclone",
        "element_combination": "風×風",
        "tagline": "純粋な知性体。情報と会話の渦を生み、世界を横断する。",
        "temperament": "純粋な知性体",
        "body_type": "多血質の純粋形",
        "core": "アイデア、コミュニケーション、社会的ネットワークの世界で呼吸。客観的・合理的・好奇心旺盛。",
        "talents": "豊かな教養と洗練で議論の場でも存在感。独立心が強く自由な交流を好む。",
        "challenges": "「頭でっかち」で肉体から遊離しやすい。非論理的な感情や日常の現実が苦手。"
    },
    ("風", "水"): {
        "name": "霧",
        "name_en": "The Mist",
        "element_combination": "風×水",
        "tagline": "共感する知性。論理と感情を溶かし、言葉で潤いをもたらす。",
        "temperament": "共感する知性",
        "body_type": "多血質と粘液質の統合",
        "core": "感情の機微を理解し言葉で表現する稀有な才能。論理と直感を融合。",
        "talents": "卓越したユーモアとオリジナルな想像力。人の気持ちを察し、計画を立て実行。",
        "challenges": "思考と感情に没入し行動（火）や現実対処（地）が遅れがち。"
    },
    ("水", "火"): {
        "name": "温泉",
        "name_en": "The Hot Spring",
        "element_combination": "水×火",
        "tagline": "行動する共感者。守るべきもののために、温もりと勇気で動く。",
        "temperament": "行動する共感者",
        "body_type": "粘液質と胆汁質の調和",
        "core": "癒しに満ちた水の太陽の性質は、情熱的で直接的な火の月の行動力を通して表現。",
        "talents": "深い愛情と実行情熱の兼備。困っている人を見過ごせず即行動。",
        "challenges": "主観的・衝動的に傾き、地の見通しや風の論理を欠く。"
    },
    ("水", "地"): {
        "name": "粘土",
        "name_en": "The Clay",
        "element_combination": "水×地",
        "tagline": "形ある癒し手。混沌に器を与え、安心を持続する。",
        "temperament": "形ある癒し手",
        "body_type": "粘液質と憂鬱質の融合",
        "core": "深い感情的目的は、現実的・具体的・永続的な安心の提供。魂の陶芸家。",
        "talents": "共感力と実務能力の兼備。情に厚い職人肌で、最後まで責任を持つ。",
        "challenges": "過度に慎重で慣習に固執しやすい。火の個人リスクや風の抽象に抵抗。"
    },
    ("水", "風"): {
        "name": "雨雲",
        "name_en": "The Raincloud",
        "element_combination": "水×風",
        "tagline": "詩的な魂。感情を言語と芸術へ翻訳するストーリーテラー。",
        "temperament": "詩的な魂",
        "body_type": "粘液質と多血質の統合",
        "core": "感情の世界を深く見つめ、それを言語・芸術・アイデアに翻訳する非凡な能力。",
        "talents": "細やかで鋭い洞察。人を見て気質を見抜く。表現語彙が豊富。",
        "challenges": "内なる美しい非現実に没入し憂鬱や無気力へ。火の行動と地の現実が欠けがち。"
    },
    ("水", "水"): {
        "name": "大洋",
        "name_en": "The Ocean",
        "element_combination": "水×水",
        "tagline": "無限の共感体。境界を越え、すべてを包む深い水域。",
        "temperament": "無限の共感体",
        "body_type": "粘液質の深化形",
        "core": "純粋で希釈されていない感情・直感・霊的感受性。集合的無意識と深く繋がる。",
        "talents": "驚異的な共感能力と思いやり。芸術感受性が高く、存在自体が安らぎと潤いを与える。",
        "challenges": "個人的境界線の維持と現実世界での機能が課題。同調しすぎて圧倒され自己喪失の危険。"
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
            # セッションに天体データを保存（後でレポートで使用）
            import json
            from flask import session
            session['celestial_data'] = json.dumps(result['celestial_positions'])
            session['name'] = name
            
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
    import json
    
    # URLパラメータから情報を取得
    name = request.args.get('name', session.get('name', 'お客様'))
    archetype_name = request.args.get('archetype', '未分類')
    
    # セッションから天体データを取得
    celestial_data_raw = session.get('celestial_data')
    if celestial_data_raw:
        try:
            celestial_positions = json.loads(celestial_data_raw)
            # データ形式を変換
            celestial_data = {}
            planet_mapping = {
                '太陽': 'sun', '月': 'moon', '水星': 'mercury',
                '金星': 'venus', '火星': 'mars', '木星': 'jupiter', '土星': 'saturn'
            }
            for jp_name, en_name in planet_mapping.items():
                if jp_name in celestial_positions:
                    celestial_data[en_name] = {
                        'sign': celestial_positions[jp_name]['zodiac'],
                        'element': celestial_positions[jp_name]['element'],
                        'degree': celestial_positions[jp_name]['degree_in_sign']
                    }
        except:
            # デフォルトデータ
            celestial_data = {
                'sun': {'sign': '牡羊座', 'element': '火', 'degree': 15.5},
                'moon': {'sign': '蟹座', 'element': '水', 'degree': 22.3},
                'mercury': {'sign': '双子座', 'element': '風', 'degree': 8.7},
                'venus': {'sign': '牡牛座', 'element': '地', 'degree': 18.2},
                'mars': {'sign': '獅子座', 'element': '火', 'degree': 25.8},
                'jupiter': {'sign': '射手座', 'element': '火', 'degree': 12.4},
                'saturn': {'sign': '山羊座', 'element': '地', 'degree': 5.9}
            }
    else:
        # デフォルトデータ
        celestial_data = {
            'sun': {'sign': '牡羊座', 'element': '火', 'degree': 15.5},
            'moon': {'sign': '蟹座', 'element': '水', 'degree': 22.3},
            'mercury': {'sign': '双子座', 'element': '風', 'degree': 8.7},
            'venus': {'sign': '牡牛座', 'element': '地', 'degree': 18.2},
            'mars': {'sign': '獅子座', 'element': '火', 'degree': 25.8},
            'jupiter': {'sign': '射手座', 'element': '火', 'degree': 12.4},
            'saturn': {'sign': '山羊座', 'element': '地', 'degree': 5.9}
        }
    
    # アーキタイプ情報を取得
    archetype = None
    for key, value in SIXTEEN_ARCHETYPES.items():
        if value['name'] == archetype_name:
            archetype = value
            archetype['key_traits'] = ['直感的', '情熱的', '創造的', '独立心が強い']
            break
    
    if not archetype:
        archetype = {
            "name": archetype_name,
            "element_combination": "火×水",
            "temperament": "複合的",
            "body_type": "混合型",
            "key_traits": ['適応力が高い', '柔軟性がある', '創造的', '直感的']
        }
    
    return render_template('basic_report.html', 
                         name=name,
                         archetype=archetype,
                         celestial_data=celestial_data)

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
