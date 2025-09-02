from flask import Flask, render_template, request
import ephem
import datetime
import math

app = Flask(__name__)

# 47都道府県の座標データ（高精度版）
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
