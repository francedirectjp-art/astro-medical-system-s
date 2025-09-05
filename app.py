from flask import Flask, render_template, request, jsonify, session
import ephem
import math
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-for-session-management-change-in-production'

# サビアンシンボルデータのグローバル変数
SABIAN_SYMBOLS = None

def load_sabian_symbols():
    """サビアンシンボルをJSONファイルから読み込む"""
    global SABIAN_SYMBOLS
    if SABIAN_SYMBOLS is None:
        try:
            import os
            # スクリプトのディレクトリを基準にパスを構築
            base_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(base_dir, 'sabian_symbols.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                SABIAN_SYMBOLS = json.load(f)
        except FileNotFoundError:
            print("サビアンシンボルファイルが見つかりません")
            SABIAN_SYMBOLS = []
        except Exception as e:
            print(f"サビアンシンボル読み込みエラー: {e}")
            SABIAN_SYMBOLS = []
    return SABIAN_SYMBOLS

def get_sabian_for_position(sign, degree):
    """特定の星座と度数に対応するサビアンシンボルを取得"""
    symbols = load_sabian_symbols()
    
    # 星座名を英語に変換
    sign_mapping = {
        '牡羊座': 'aries', '牡牛座': 'taurus', '双子座': 'gemini',
        '蟹座': 'cancer', '獅子座': 'leo', '乙女座': 'virgo',
        '天秤座': 'libra', '蠍座': 'scorpio', '射手座': 'sagittarius',
        '山羊座': 'capricorn', '水瓶座': 'aquarius', '魚座': 'pisces'
    }
    
    sign_id = sign_mapping.get(sign)
    if not sign_id:
        return None
    
    # サビアンシンボルは切り上げ度数を使用（例：0.1度→1度、15.7度→16度）
    sabian_degree = math.ceil(degree) if degree > 0 else 1
    sabian_degree = min(30, max(1, sabian_degree))  # 1-30の範囲に制限
    
    # 該当する星座のシンボルを検索
    for sign_data in symbols:
        if sign_data['sign_id'] == sign_id:
            for symbol in sign_data['degrees']:
                if symbol['degree'] == sabian_degree:
                    return {
                        'sign': sign_data['sign_ja'],
                        'degree': sabian_degree,
                        'title': symbol['title_ja'],
                        'keyword': symbol['keyword']
                    }
    return None

def generate_sabian_talent_interpretation(planet_name, sabian_symbol, element):
    """サビアンシンボルから才能の解釈を生成（霊的な表現を避け、実践的な才能にフォーカス）"""
    
    if not sabian_symbol:
        return ""
    
    # 惑星別の才能領域
    planet_talents = {
        '太陽': '核心的な才能と人生の目的',
        '月': '感情的知性と適応能力', 
        '水星': '知的能力とコミュニケーション',
        '金星': '審美眼と人間関係の才能',
        '火星': '実行力と達成能力',
        '木星': '成長と発展の可能性',
        '土星': '専門性と持続力'
    }
    
    talent_domain = planet_talents.get(planet_name, '潜在能力')
    
    # エレメント別の表現スタイル
    element_styles = {
        '火': '直感的で創造的な',
        '地': '実践的で具体的な',
        '風': '知的で革新的な',
        '水': '感受性豊かで洞察力のある'
    }
    
    style = element_styles.get(element, '独特な')
    
    interpretation = f"""
{sabian_symbol['sign']}{sabian_symbol['degree']}度のサビアンシンボル「{sabian_symbol['title']}」は、
{planet_name}が司る{talent_domain}において、「{sabian_symbol['keyword']}」という特別な才能を示しています。

これは{style}方法で発揮され、以下のような具体的な能力として現れます：

• 職業的には、{get_vocational_talent(sabian_symbol['keyword'], planet_name)}
• 対人関係では、{get_interpersonal_talent(sabian_symbol['keyword'], element)}
• 創造活動では、{get_creative_talent(sabian_symbol['keyword'], style)}

この才能は訓練と経験によってさらに洗練され、専門的なスキルへと発展する可能性を秘めています。
"""
    
    return interpretation

def get_vocational_talent(keyword, planet):
    """職業的才能の具体例を生成"""
    # キーワードに基づいて職業的才能を推定
    if '新' in keyword or '誕生' in keyword:
        return "革新的なプロジェクトの立ち上げや、新しい分野の開拓に優れた能力"
    elif '統合' in keyword or '調和' in keyword:
        return "チームをまとめ、異なる要素を統合する管理能力やコーディネート力"
    elif '変容' in keyword or '変化' in keyword:
        return "組織改革や事業転換を導くチェンジマネジメントの才能"
    elif '達成' in keyword or '完成' in keyword:
        return "プロジェクトを完遂させる実行力と、目標達成への強いコミットメント"
    else:
        return "独自の視点から価値を創造し、新たな可能性を開く能力"

def get_interpersonal_talent(keyword, element):
    """対人関係の才能を生成"""
    element_approach = {
        '火': '情熱的で励ましに満ちたアプローチ',
        '地': '信頼と安定を提供する堅実なサポート',
        '風': '知的な刺激と新鮮な視点の提供',
        '水': '深い共感と感情的な理解'
    }
    
    return f"{element_approach.get(element, '独自の方法')}により、{keyword}に関連した人間関係の構築力"

def get_creative_talent(keyword, style):
    """創造的才能を生成"""
    return f"{keyword}をテーマとした{style}表現により、独創的な作品や解決策を生み出す力"

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

def _get_archetype_details(archetype_name):
    """体質原型に基づく詳細な特徴を生成"""
    archetype_features = {
        "火のカリスマ": {
            "strength": "強力なリーダーシップ、決断力、行動力",
            "physical": "高い基礎代謝、筋肉質な体質、熱産生が活発",
            "caution": "過労、ストレス性疾患、炎症性疾患への注意",
            "lifestyle": "定期的なクールダウン、瞑想、十分な水分補給"
        },
        "マグマ": {
            "strength": "爆発的な創造力、情熱、カリスマ性",
            "physical": "非常に高い体温、活発な循環系、強い消化力",
            "caution": "怒りのコントロール、血圧管理、熱性疾患",
            "lifestyle": "冷却食品の摂取、水泳、定期的な休息"
        },
        "聖火": {
            "strength": "持続的な情熱、理想主義、インスピレーション",
            "physical": "安定した熱産生、良好な代謝、強い免疫力",
            "caution": "理想と現実のギャップによるストレス",
            "lifestyle": "創造的活動、芸術療法、自然との触れ合い"
        },
        "野火": {
            "strength": "瞬発力、適応力、直感的判断力",
            "physical": "変動しやすい体温、敏感な神経系",
            "caution": "エネルギーの浪費、神経過敏",
            "lifestyle": "規則的な生活リズム、グラウンディング"
        },
        "竈の火": {
            "strength": "忍耐力、実務能力、安定性",
            "physical": "安定した消化機能、堅実な体格",
            "caution": "柔軟性の欠如、関節の硬化",
            "lifestyle": "ストレッチ、ヨガ、柔軟性を高める運動"
        },
        "鉱床": {
            "strength": "分析力、計画性、持久力",
            "physical": "強固な骨格、ゆっくりとした代謝",
            "caution": "循環不良、冷え性、消化不良",
            "lifestyle": "有酸素運動、温かい食事、マッサージ"
        },
        "山": {
            "strength": "安定性、信頼性、保守力",
            "physical": "強靭な体格、ゆったりとした動作",
            "caution": "変化への抵抗、頑固さ",
            "lifestyle": "新しい経験、旅行、社交活動"
        },
        "流砂": {
            "strength": "柔軟性、適応力、受容力",
            "physical": "変化しやすい体調、敏感な消化器",
            "caution": "境界の曖昧さ、依存傾向",
            "lifestyle": "境界設定の練習、自己主張トレーニング"
        },
        "山火事": {
            "strength": "コミュニケーション力、情熱、発信力",
            "physical": "活発な代謝、敏感な呼吸器系",
            "caution": "オーバーワーク、呼吸器疾患",
            "lifestyle": "呼吸法、休息、森林浴"
        },
        "砂岩の彫刻家": {
            "strength": "論理性、創造性、実用性の融合",
            "physical": "バランスの取れた体質、安定した神経系",
            "caution": "感情表現の抑制、緊張性頭痛",
            "lifestyle": "感情解放、アート活動、音楽療法"
        },
        "サイクロン": {
            "strength": "知的好奇心、多才、社交性",
            "physical": "敏感な神経系、変動しやすいエネルギー",
            "caution": "散漫、不眠、神経疲労",
            "lifestyle": "瞑想、集中力トレーニング、十分な睡眠"
        },
        "霧": {
            "strength": "共感力、想像力、柔軟な思考",
            "physical": "繊細な体質、敏感な感覚器官",
            "caution": "境界の喪失、エネルギー枯渇",
            "lifestyle": "エネルギー管理、境界設定、グラウンディング"
        },
        "温泉": {
            "strength": "癒しの力、情熱的な共感、行動力",
            "physical": "温かい体質、活発な循環",
            "caution": "感情の起伏、エネルギーの消耗",
            "lifestyle": "感情調整、定期的な休息、水分補給"
        },
        "粘土": {
            "strength": "創造性、実用性、育成力",
            "physical": "しっとりとした体質、ゆったりとした代謝",
            "caution": "停滞、むくみ、消化不良",
            "lifestyle": "定期的な運動、リンパマッサージ、軽い食事"
        },
        "霧雨": {
            "strength": "繊細さ、直感力、芸術性",
            "physical": "敏感な体質、変動しやすい体調",
            "caution": "過敏性、不安、エネルギー不足",
            "lifestyle": "規則正しい生活、栄養管理、創作活動"
        },
        "海": {
            "strength": "深い感受性、包容力、直感",
            "physical": "流動的な体質、リンパ系が活発",
            "caution": "感情の波、水分代謝の問題",
            "lifestyle": "感情日記、水中運動、月のリズムに合わせた生活"
        }
    }
    
    # デフォルト値
    default_features = {
        "strength": "バランスの取れた資質、適応力",
        "physical": "標準的な体質、安定した健康状態",
        "caution": "ストレス管理、生活習慣の維持",
        "lifestyle": "規則正しい生活、適度な運動、バランスの取れた食事"
    }
    
    return archetype_features.get(archetype_name, default_features)

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
            
            # 元素バランスを計算
            elements = {'火': 0, '地': 0, '風': 0, '水': 0}
            for planet_data in result['celestial_positions'].values():
                element = planet_data.get('element', '')
                if element in elements:
                    elements[element] += 1
            
            # 最も多い元素を特定
            dominant_element = max(elements, key=elements.get)
            total_planets = sum(elements.values())
            
            # パーセンテージ計算
            element_percents = {
                'fire': int((elements['火'] / total_planets * 100)) if total_planets > 0 else 0,
                'earth': int((elements['地'] / total_planets * 100)) if total_planets > 0 else 0,
                'air': int((elements['風'] / total_planets * 100)) if total_planets > 0 else 0,
                'water': int((elements['水'] / total_planets * 100)) if total_planets > 0 else 0,
                'fire_count': elements['火'],
                'earth_count': elements['地'],
                'air_count': elements['風'],
                'water_count': elements['水']
            }
            
            # 元素の意味を設定
            element_meanings = {
                '火': '活動的でエネルギッシュな体質',
                '地': '安定性と持続力のある体質',
                '風': '柔軟性と適応力の高い体質',
                '水': '感受性と直感力に優れた体質'
            }
            
            # 体質原型の詳細情報を生成
            archetype_info = result['calculation_info']['archetype']
            
            # 体質原型に基づく詳細な特徴を設定
            archetype_details = _get_archetype_details(archetype_info.get('name', ''))
            archetype_info.update(archetype_details)
            
            # calculation_infoに元素情報を追加
            result['calculation_info']['elements'] = element_percents
            result['calculation_info']['dominant_element'] = dominant_element
            result['calculation_info']['element_meaning'] = element_meanings.get(dominant_element, '')
            
            # レポート用の追加情報を生成
            info = result['calculation_info']
            
            # 太陽と月の性質を設定
            sun_qualities = {
                '牡羊座': '積極的で率直な', '牡牛座': '堅実で忍耐強い',
                '双子座': '知的で社交的な', '蟹座': '感受性豊かで保護的な',
                '獅子座': '創造的で自信のある', '乙女座': '分析的で実践的な',
                '天秤座': '調和的でバランスの取れた', '蠍座': '深遠で変容力のある',
                '射手座': '楽観的で冒険心のある', '山羊座': '責任感が強く野心的な',
                '水瓶座': '革新的で独立心のある', '魚座': '直感的で共感性の高い'
            }
            
            moon_qualities = {
                '牡羊座': '即座の感情反応と独立心', '牡牛座': '安定した感情と持続性',
                '双子座': '柔軟で適応力のある', '蟹座': '深い感情と養育的な本能',
                '獅子座': '温かく寛大な感情表現', '乙女座': '慎重で分析的な感情処理',
                '天秤座': '調和を求め客観的な視点を保持', '蠍座': '深い感情と強い直感',
                '射手座': '楽観的で自由を求める感情', '山羊座': '抑制的で実践的な感情管理',
                '水瓶座': '独立的で理性的な感情処理', '魚座': '共感的で境界の曖昧な感情'
            }
            
            sun_identities = {
                '牡羊座': '先駆者精神とリーダーシップに優れ', '牡牛座': '安定性と美的感覚に優れ',
                '双子座': '知的でコミュニケーション能力に優れ', '蟹座': '育成力と感情的知性に優れ',
                '獅子座': '創造性とカリスマ性に優れ', '乙女座': '実践力と分析力に優れ',
                '天秤座': '協調性と美的センスに優れ', '蠍座': '洞察力と変容力に優れ',
                '射手座': '探求心と楽観性に優れ', '山羊座': '組織力と達成力に優れ',
                '水瓶座': '革新性と独創性に優れ', '魚座': '直感力と創造性に優れ'
            }
            
            info['sun_quality'] = sun_qualities.get(result['celestial_positions']['太陽']['zodiac'], '独特な')
            info['moon_quality'] = moon_qualities.get(result['celestial_positions']['月']['zodiac'], '独特な')
            info['sun_identity'] = sun_identities.get(result['celestial_positions']['太陽']['zodiac'], '多面的な才能を持ち')
            info['moon_emotion'] = moon_qualities.get(result['celestial_positions']['月']['zodiac'], '感情を独自の方法で処理')
            
            # 元素ごとの天体リストを作成
            element_planets = {'火': [], '地': [], '風': [], '水': []}
            planet_names = {
                '太陽': 'sun', '月': 'moon', '水星': 'mercury',
                '金星': 'venus', '火星': 'mars', '木星': 'jupiter', '土星': 'saturn'
            }
            
            for planet_jp, planet_en in planet_names.items():
                element = result['celestial_positions'][planet_jp]['element']
                if element in element_planets:
                    element_planets[element].append(planet_en)
            
            info['fire_planets'] = ', '.join(element_planets['火']) if element_planets['火'] else 'なし'
            info['earth_planets'] = ', '.join(element_planets['地']) if element_planets['地'] else 'なし'
            info['air_planets'] = ', '.join(element_planets['風']) if element_planets['風'] else 'なし'
            info['water_planets'] = ', '.join(element_planets['水']) if element_planets['水'] else 'なし'
            
            # 最も多い元素の詳細情報
            dominant = info['dominant_element']
            info['dominant_count'] = max(elements.values())
            info['dominant_planets'] = ', '.join(element_planets[dominant]) if element_planets[dominant] else ''
            
            # 人生のテーマと特別な才能
            life_themes = {
                '火のカリスマ': '情熱的なリーダーシップと創造',
                'マグマ': '爆発的な創造力の発揮',
                '聖火': '理想の実現と持続的な情熱',
                '野火': '直感と冒険による成長',
                '竈の火': '実践的な創造と安定',
                '鉱床': '知識の蓄積と分析',
                '山': '不動の信頼性と保護',
                '流砂': '柔軟な適応と受容',
                '山火事': '情熱的なコミュニケーション',
                '砂岩の彫刻家': '論理と創造の統合',
                'サイクロン': '多様な視点と知的な探求',
                '霧': '想像力と共感の深化',
                '温泉': '癒しと情熱の融合',
                '粘土': '創造と実践の統合',
                '霧雨': '繊細な感受性と芸術',
                '海': '深い感情と包容力'
            }
            
            special_talents = {
                '火のカリスマ': '強力な影響力とリーダーシップ',
                'マグマ': '変革を起こす創造力',
                '聖火': '持続的な情熱と献身',
                '野火': '瞬発的な適応力',
                '竈の火': '実践的な問題解決力',
                '鉱床': '深い分析力と計画性',
                '山': '揺るぎない信頼性',
                '流砂': '無限の適応力',
                '山火事': '熱意あるコミュニケーション',
                '砂岩の彫刻家': '知的な創造性',
                'サイクロン': '知的な革新性',
                '霧': '深い共感力と想像力',
                '温泉': '癒しの力と行動力',
                '粘土': '形を与える創造力',
                '霧雨': '繊細な芸術性',
                '海': '無限の包容力'
            }
            
            archetype_name = info['archetype']['name']
            info['life_theme'] = life_themes.get(archetype_name, '自己実現と成長')
            info['special_talent'] = special_talents.get(archetype_name, '独自の才能')
            
            # 火星と土星のコンビネーション解釈
            mars_sign = result['celestial_positions']['火星']['zodiac']
            saturn_sign = result['celestial_positions']['土星']['zodiac']
            info['mars_saturn_combo'] = f"{mars_sign}の行動力と{saturn_sign}の構造化"
            
            # 元素による洞察
            if info['dominant_element'] == '火':
                info['element_insight'] = '情熱的な創造と自己表現'
            elif info['dominant_element'] == '地':
                info['element_insight'] = '実践的な達成と安定'
            elif info['dominant_element'] == '風':
                info['element_insight'] = '知的な探求と交流'
            else:
                info['element_insight'] = '感情的な深まりと直感'
            
            # セッションに追加情報も保存
            session['archetype_name'] = info['archetype']['name']
            session['archetype_name_en'] = info['archetype'].get('name_en', '')
            
            # 成功時は詳細レポートページへ
            return render_template('result_summary_enhanced.html', 
                                 name=name,
                                 data=result['celestial_positions'],
                                 info=info)
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
    """詳細レポートページ（12,000文字以上の包括的医学レポート）"""
    import json
    from datetime import datetime
    from flask import redirect
    
    # セッションチェック - データがない場合はトップページへ
    if 'celestial_data' not in session:
        return redirect('/')
    
    # URLパラメータとセッションから情報を取得
    name = request.args.get('name', session.get('name', 'お客様'))
    archetype_name = request.args.get('archetype', '未分類')
    
    # セッションから天体データを取得
    celestial_data_raw = session.get('celestial_data')
    celestial_data = {}
    
    if celestial_data_raw:
        try:
            celestial_positions = json.loads(celestial_data_raw)
            planet_mapping = {
                '太陽': 'sun', '月': 'moon', '水星': 'mercury',
                '金星': 'venus', '火星': 'mars', '木星': 'jupiter', '土星': 'saturn'
            }
            for jp_name, en_name in planet_mapping.items():
                if jp_name in celestial_positions:
                    planet_info = {
                        'sign': celestial_positions[jp_name]['zodiac'],
                        'element': celestial_positions[jp_name]['element'],
                        'degree': celestial_positions[jp_name]['degree_in_sign'],
                        'quality': get_sign_quality(celestial_positions[jp_name]['zodiac'])
                    }
                    # サビアンシンボルを追加
                    sabian = get_sabian_for_position(
                        celestial_positions[jp_name]['zodiac'],
                        celestial_positions[jp_name]['degree_in_sign']
                    )
                    if sabian:
                        planet_info['sabian'] = sabian
                    celestial_data[en_name] = planet_info
        except:
            celestial_data = get_default_celestial_data()
    else:
        celestial_data = get_default_celestial_data()
    
    # アーキタイプ情報を取得
    archetype = None
    sun_element = celestial_data.get('sun', {}).get('element', '火')
    moon_element = celestial_data.get('moon', {}).get('element', '水')
    archetype_key = (sun_element, moon_element)
    
    if archetype_key in SIXTEEN_ARCHETYPES:
        archetype = SIXTEEN_ARCHETYPES[archetype_key].copy()
    else:
        # アーキタイプ名から検索
        for key, value in SIXTEEN_ARCHETYPES.items():
            if value['name'] == archetype_name:
                archetype = value.copy()
                break
    
    if not archetype:
        archetype = {
            "name": "調和の探究者",
            "name_en": "The Harmony Seeker",
            "element_combination": f"{sun_element}×{moon_element}",
            "temperament": "複合型気質",
            "body_type": "混合体質",
            "tagline": "多様な要素を統合し、独自のバランスを見出す者",
            "core": "複数の要素が織りなす独特な個性を持つ存在",
            "talents": "適応力と柔軟性、多角的な視点",
            "challenges": "方向性の模索と統合への道"
        }
    
    # 包括的な12,000文字レポートの生成
    report_content = generate_comprehensive_report(
        name=name,
        archetype=archetype,
        celestial_data=celestial_data,
        sun_element=sun_element,
        moon_element=moon_element
    )
    
    # 統計情報の計算
    element_distribution = calculate_element_distribution(celestial_data)
    quality_distribution = calculate_quality_distribution(celestial_data)
    
    # レポート生成日時
    report_date = datetime.now().strftime('%Y年%m月%d日')
    
    # アーキタイプ名を取得
    archetype_name = session.get('archetype_name', '未分類')
    archetype_name_en = session.get('archetype_name_en', '')
    
    return render_template('detailed_report_complete.html',
                         name=name,
                         archetype=archetype,
                         celestial_data=celestial_data,
                         report_content=report_content,
                         element_distribution=element_distribution,
                         quality_distribution=quality_distribution,
                         report_date=report_date,
                         total_characters=len(report_content['full_text']))

def get_sign_quality(sign):
    """星座のクオリティを返す"""
    cardinal = ['牡羊座', '蟹座', '天秤座', '山羊座']
    fixed = ['牡牛座', '獅子座', '蠍座', '水瓶座']
    mutable = ['双子座', '乙女座', '射手座', '魚座']
    
    if sign in cardinal:
        return '活動宮'
    elif sign in fixed:
        return '固定宮'
    elif sign in mutable:
        return '柔軟宮'
    return '不明'

def get_default_celestial_data():
    """デフォルトの天体データを返す"""
    return {
        'sun': {'sign': '牡羊座', 'element': '火', 'degree': 15.5, 'quality': '活動宮'},
        'moon': {'sign': '蟹座', 'element': '水', 'degree': 22.3, 'quality': '活動宮'},
        'mercury': {'sign': '双子座', 'element': '風', 'degree': 8.7, 'quality': '柔軟宮'},
        'venus': {'sign': '牡牛座', 'element': '地', 'degree': 18.2, 'quality': '固定宮'},
        'mars': {'sign': '獅子座', 'element': '火', 'degree': 25.8, 'quality': '固定宮'},
        'jupiter': {'sign': '射手座', 'element': '火', 'degree': 12.4, 'quality': '柔軟宮'},
        'saturn': {'sign': '山羊座', 'element': '地', 'degree': 5.9, 'quality': '活動宮'}
    }

def calculate_element_distribution(celestial_data):
    """惑星の元素分布を計算"""
    elements = {'火': 0, '地': 0, '風': 0, '水': 0}
    for planet, data in celestial_data.items():
        element = data.get('element')
        if element in elements:
            elements[element] += 1
    return elements

def calculate_quality_distribution(celestial_data):
    """惑星のクオリティ分布を計算"""
    qualities = {'活動宮': 0, '固定宮': 0, '柔軟宮': 0}
    for planet, data in celestial_data.items():
        quality = data.get('quality')
        if quality in qualities:
            qualities[quality] += 1
    return qualities

def generate_comprehensive_report(name, archetype, celestial_data, sun_element, moon_element):
    """12,000文字以上の包括的レポートを生成"""
    
    # 第1章：アーキタイプの深層分析（サビアンシンボルを含む、2,500文字以上）
    chapter1 = generate_archetype_analysis(name, archetype, sun_element, moon_element, celestial_data)
    
    # 第2章：惑星配置の詳細解釈（2,500文字）
    chapter2 = generate_planetary_interpretation(name, celestial_data)
    
    # 第3章：医学的体質分析（2,500文字）
    chapter3 = generate_medical_constitution(name, archetype, celestial_data)
    
    # 第4章：ホリスティック処方箋（2,500文字）
    chapter4 = generate_holistic_prescriptions(name, archetype, celestial_data)
    
    # 第5章：人生設計とライフプランニング（2,500文字）
    chapter5 = generate_life_planning(name, archetype, celestial_data)
    
    # エピローグ（500文字）
    epilogue = generate_epilogue(name, archetype)
    
    full_text = chapter1 + chapter2 + chapter3 + chapter4 + chapter5 + epilogue
    
    return {
        'chapter1': chapter1,
        'chapter2': chapter2,
        'chapter3': chapter3,
        'chapter4': chapter4,
        'chapter5': chapter5,
        'epilogue': epilogue,
        'full_text': full_text
    }

def generate_archetype_analysis(name, archetype, sun_element, moon_element, celestial_data=None):
    """第1章：アーキタイプの深層分析を生成（2,500文字）"""
    
    element_meanings = {
        '火': '情熱と創造性、直感的な行動力、開拓精神',
        '地': '現実性と安定感、着実な成長力、物質的豊かさ',
        '風': '知性と社交性、柔軟な思考力、コミュニケーション能力',
        '水': '感情と共感性、深い洞察力、癒しの力'
    }
    
    text = f"""
【第1章：{archetype['name']}というアーキタイプの深層分析】

{name}様の本質を形作る「{archetype['name']}」というアーキタイプは、太陽の{sun_element}エレメントと月の{moon_element}エレメントが織りなす、極めて独特な存在様式を表しています。このアーキタイプは、織田先生の16原型論において、{archetype['tagline']}

■ 原型の核心的性質

{archetype['name']}の本質は、{archetype['core']}このような性質を持つ{name}様は、人生において独自の道を切り開いていく運命にあります。太陽が示す意識的な自己表現は{element_meanings.get(sun_element, '独特な個性')}を通じて現れ、月が示す無意識的な感情反応は{element_meanings.get(moon_element, '深い内面性')}として内在しています。

この二つのエレメントの組み合わせ「{archetype['element_combination']}」は、単なる性格的特徴を超えて、{name}様の生命エネルギーの根本的な流れ方を規定しています。古代ギリシャの四体液説に基づく{archetype['body_type']}という体質分類は、現代医学における心身相関の観点からも重要な示唆を与えています。

■ 才能と可能性の展開

{archetype['name']}が持つ主要な才能：{archetype['talents']}

これらの才能は、{name}様が生まれながらに持っている宝物です。しかし、これらの才能が完全に開花するためには、意識的な育成と適切な環境が必要となります。特に、{sun_element}の要素が強く現れる場面では、驚くほどの能力を発揮することができるでしょう。

日常生活において、これらの才能は以下のような形で現れることが多いです：

1. 仕事や創造活動において：{sun_element}の性質が前面に出て、革新的なアイデアや独創的な解決策を生み出します。特にプレッシャーがかかる状況では、通常では考えられないような突破力を示すことがあります。

2. 人間関係において：{moon_element}の要素が対人関係の質を決定づけます。親密な関係では特にこの傾向が強く現れ、深い理解と共感を基盤とした関係性を築くことができます。

3. 自己実現の過程において：{archetype['element_combination']}という組み合わせは、一般的な成功の定義にとらわれない、独自の価値観と生き方を追求する力を与えています。

■ 成長への課題と超越の道

{archetype['name']}が直面する主な課題：{archetype['challenges']}

これらの課題は、{name}様の成長にとって避けては通れない重要なテーマです。しかし、これらは決して弱点ではなく、むしろ人生を通じて磨き上げていくべき「成長の種」なのです。

特に注意すべきは、{sun_element}と{moon_element}のバランスが崩れやすい状況です。ストレスが高まると、どちらか一方の要素が過剰に働き、もう一方が抑圧される傾向があります。このアンバランスは、身体的には{archetype['body_type']}特有の症状として現れ、精神的には内的葛藤や決断の困難さとして表面化することがあります。

■ アーキタイプの進化段階

{archetype['name']}というアーキタイプは、人生の各段階で異なる表現をします：

- 若年期（〜30歳）：{sun_element}の要素が強く、外向的で挑戦的な姿勢が目立ちます。この時期は多くの経験を積み、自己の可能性を探求する重要な時期です。

- 中年期（30〜50歳）：{moon_element}の要素が成熟し、内面的な充実と外的活動のバランスを見出し始めます。キャリアと個人生活の統合が主要テーマとなります。

- 円熟期（50歳〜）：両方の要素が統合され、独自の wisdom（知恵）を獲得します。他者への貢献と自己実現が自然に一致する境地に至ります。

■ 太陽と月のサビアンシンボルが示す核心的才能

{name}様の太陽と月の正確な位置が示すサビアンシンボルは、最も重要な才能の指標です：
"""
    
    # 太陽と月のサビアンシンボルを取得して追加
    if celestial_data:
        sun_data = celestial_data.get('sun', {})
        moon_data = celestial_data.get('moon', {})
        
        if sun_data:
            sun_sabian = get_sabian_for_position(sun_data.get('sign'), sun_data.get('degree', 0))
            if sun_sabian:
                text += f"""

★ 太陽のサビアンシンボル：{sun_sabian['sign']}{sun_sabian['degree']}度
「{sun_sabian['title']}」
キーワード：{sun_sabian['keyword']}

このシンボルは、{name}様の意識的な自己表現と人生の目的において、「{sun_sabian['keyword']}」という特別な才能を示しています。
これは{sun_element}のエネルギーを通して、特にキャリアや社会的活動において顕著に現れます。
"""
        
        if moon_data:
            moon_sabian = get_sabian_for_position(moon_data.get('sign'), moon_data.get('degree', 0))
            if moon_sabian:
                text += f"""

★ 月のサビアンシンボル：{moon_sabian['sign']}{moon_sabian['degree']}度
「{moon_sabian['title']}」
キーワード：{moon_sabian['keyword']}

このシンボルは、{name}様の無意識的な感情パターンと内的才能において、「{moon_sabian['keyword']}」という潜在力を示しています。
これは{moon_element}の性質を通して、特に対人関係や内的な創造活動において発揮されます。
"""
        
        text += f"""

これらのサビアンシンボルが示す才能は、{archetype['name']}というアーキタイプを通して統合され、
{name}様独自の才能プロフィールを形成しています。これらは訓練と経験によってさらに洗練され、
専門的なスキルや独創的な表現へと発展する可能性を秘めています。
"""
    
    text += f"""

■ 同じアーキタイプを持つ歴史的人物との共鳴

歴史上、{archetype['name']}的な資質を持つとされる人物たちは、それぞれの時代において革新的な貢献をしてきました。
彼らに共通するのは、既存の枠組みにとらわれない独創性と、深い内的確信に基づく行動力です。

{name}様もまた、この系譜に連なる存在として、独自の方法で世界に貢献する可能性を秘めています。
それは必ずしも歴史に名を残すような大きな功績である必要はありません。
日々の生活の中で、{archetype['name']}としての本質を生きることそのものが、周囲に大きな影響を与えているのです。
"""
    
    return text

def generate_planetary_interpretation(name, celestial_data):
    """第2章：惑星配置の詳細解釈を生成（サビアンシンボルを含む、2,500文字以上）"""
    
    planet_meanings = {
        'sun': {'name': '太陽', 'domain': '本質的自己、生命力、創造性', 'medical': '心臓、背骨、目'},
        'moon': {'name': '月', 'domain': '感情、無意識、養育', 'medical': '胃、乳房、体液'},
        'mercury': {'name': '水星', 'domain': '知性、コミュニケーション、学習', 'medical': '神経系、呼吸器、手'},
        'venus': {'name': '金星', 'domain': '愛情、美、価値観', 'medical': '腎臓、喉、皮膚'},
        'mars': {'name': '火星', 'domain': '行動力、情熱、闘争', 'medical': '筋肉、血液、頭部'},
        'jupiter': {'name': '木星', 'domain': '拡大、幸運、哲学', 'medical': '肝臓、大腿部、成長'},
        'saturn': {'name': '土星', 'domain': '制限、責任、成熟', 'medical': '骨格、歯、関節'}
    }
    
    text = f"""
【第2章：天体配置とサビアンシンボルが示す才能の宝庫】

{name}様の出生時の天体配置は、宇宙的な観点から見た個性の青写真です。各惑星が特定の星座の特定の度数に位置することで、それぞれ固有のエネルギーパターンと特別な才能を形成しています。特に注目すべきは、各惑星の正確な度数が示すサビアンシンボルです。これらは{name}様の隠された才能と可能性を具体的に示しています。

■ 7惑星の詳細分析とサビアンシンボルが示す才能
"""
    
    for planet_key, planet_data in celestial_data.items():
        if planet_key in planet_meanings:
            pm = planet_meanings[planet_key]
            sign = planet_data.get('sign', '不明')
            element = planet_data.get('element', '不明')
            degree = planet_data.get('degree', 0)
            quality = planet_data.get('quality', '不明')
            
            # サビアンシンボルを取得
            sabian = get_sabian_for_position(sign, degree)
            
            text += f"""

◆ {pm['name']}（{sign} {degree:.1f}度）
支配領域：{pm['domain']}
医学的対応：{pm['medical']}
エレメント：{element}／クオリティ：{quality}

{pm['name']}が{sign}に位置していることは、{name}様の{pm['domain']}に関して、{element}の性質が強く現れることを示しています。{sign}の{degree:.1f}度という具体的な位置は、この星座の{get_degree_interpretation(degree)}を強調しています。

医学的観点から見ると、{pm['name']}は{pm['medical']}と関連しており、これらの器官や機能に{element}的な特徴が現れやすいことを示唆しています。例えば、{get_medical_tendency(element, pm['medical'])}といった傾向が考えられます。
"""
            
            # サビアンシンボルの才能解釈を追加
            if sabian:
                sabian_interpretation = generate_sabian_talent_interpretation(pm['name'], sabian, element)
                text += f"""
★ サビアンシンボルが示す特別な才能：
{sabian_interpretation}
"""
            
            text += f"""
日常生活では、この配置は{get_daily_manifestation(pm['name'], sign, element)}として現れることが多いでしょう。
"""
    
    text += f"""

■ エレメントバランスの総合評価

{name}様の7惑星のエレメント分布を分析すると、独特なエネルギーパターンが浮かび上がります。このバランスは、単なる性格分析を超えて、生命エネルギーの流れ方そのものを示しています。

最も強調されているエレメントは、{name}様の人生において主導的な役割を果たし、逆に不足しているエレメントは、意識的に補う必要がある領域を示しています。このアンバランスは弱点ではなく、むしろ{name}様の個性を際立たせる特徴なのです。

■ アスペクトパターンが創る独自の才能

惑星同士の角度関係（アスペクト）は、異なるエネルギーがどのように相互作用するかを示しています。{name}様の場合、特に注目すべきは太陽と月の関係性で、これが意識と無意識の統合度を表しています。

これらの天体配置は、静的なものではなく、人生の各段階で異なる形で活性化されます。現在の天体の動き（トランジット）と出生図の関係を理解することで、最適なタイミングでの行動が可能になります。
"""
    
    return text

def get_degree_interpretation(degree):
    """度数の解釈を返す"""
    if degree < 10:
        return "初期段階のエネルギー"
    elif degree < 20:
        return "中期の安定したエネルギー"
    else:
        return "成熟した完成段階のエネルギー"

def get_medical_tendency(element, medical_area):
    """医学的傾向を返す"""
    tendencies = {
        '火': '炎症や熱性の症状が出やすく、エネルギーの燃焼が激しい',
        '地': '慢性的な症状や構造的な問題が生じやすく、回復に時間がかかる',
        '風': '神経性の症状や循環の問題が生じやすく、変動が激しい',
        '水': '浮腫や分泌物の異常が生じやすく、感情と連動しやすい'
    }
    return tendencies.get(element, '独特な症状パターンを示す')

def get_daily_manifestation(planet, sign, element):
    """日常生活での現れ方を返す"""
    return f"{sign}の特性と{element}のエネルギーが組み合わさり、独特な表現パターンを生み出す"

def generate_medical_constitution(name, archetype, celestial_data):
    """第3章：医学的体質分析を生成（2,500文字）"""
    
    text = f"""
【第3章：ASTRO-MEDICAL体質論による包括的健康分析】

{name}様の体質は、{archetype['body_type']}として分類され、これは古代医学と現代の統合医療の両方の観点から重要な意味を持ちます。

■ 四体液説に基づく体質分析

{archetype['body_type']}は、体内の液体バランスと密接に関連しています：

1. 優勢な体液：{get_dominant_humor(archetype['body_type'])}
   この体液の過剰は、{get_humor_excess_symptoms(archetype['body_type'])}といった症状を引き起こす可能性があります。

2. 不足しやすい体液：{get_deficient_humor(archetype['body_type'])}
   この不足は、{get_humor_deficiency_symptoms(archetype['body_type'])}として現れることがあります。

■ 臓器システムの特徴

{name}様の天体配置から、以下の臓器システムに特別な注意が必要です：

◆ 心臓血管系（太陽の影響）
太陽が{celestial_data.get('sun', {}).get('sign', '牡羊座')}にあることから、心臓のリズムと活力に{celestial_data.get('sun', {}).get('element', '火')}的な特徴が現れます。定期的な有酸素運動と、情熱を注げる活動が心臓の健康を保つ鍵となります。

◆ 消化器系（月の影響）
月が{celestial_data.get('moon', {}).get('sign', '蟹座')}に位置することは、消化器系が感情状態に敏感であることを示しています。ストレス管理と規則正しい食事時間が特に重要です。

◆ 神経系（水星の影響）
水星の配置は、神経系の反応パターンを決定づけます。{celestial_data.get('mercury', {}).get('element', '風')}の影響により、情報処理が活発で、過度の刺激に注意が必要です。

■ 季節と生体リズム

{archetype['element_combination']}の組み合わせは、特定の季節に強さと弱さを示します：

- 春：再生と成長のエネルギーが高まり、新しいことを始めるのに適した時期
- 夏：活動性がピークに達し、社交的な活動が活発になる時期
- 秋：内省と整理の時期で、不要なものを手放すのに適している
- 冬：休息と充電の時期で、内的な成長に焦点を当てるべき時期

■ 体質改善のための具体的指針

1. 栄養学的アプローチ
{archetype['body_type']}の体質には、以下の栄養素が特に重要です：
- タンパク質：体重1kgあたり1.2-1.5gを目安に
- ビタミンB群：神経系の健康維持に必須
- ミネラル：特に{get_important_minerals(archetype['element_combination'])}が重要
- 水分：1日2-2.5リットルの清潔な水

2. 運動療法
{archetype['temperament']}の気質に適した運動：
- 有酸素運動：週3-4回、30-45分
- 筋力トレーニング：週2回、主要筋群をカバー
- 柔軟性：毎日10-15分のストレッチ
- マインドフルネス：瞑想やヨガを週2-3回

3. 睡眠と休息
最適な睡眠時間：7-8時間
理想的な就寝時間：{get_ideal_sleep_time(archetype['element_combination'])}
起床時間：日の出前後が理想的

■ 予防医学的観点

{name}様の体質から、以下の健康問題に注意が必要です：

1. 30代で注意すべきこと：エネルギー管理と初期の慢性疾患予防
2. 40代で注意すべきこと：ホルモンバランスと代謝の変化
3. 50代以降：骨密度と認知機能の維持

定期的な健康診断では、特に{get_health_check_focus(archetype['body_type'])}の項目に注目してください。
"""
    
    return text

def get_dominant_humor(body_type):
    """優勢な体液を返す"""
    humors = {
        '胆汁質': '黄胆汁（火のエネルギー）',
        '憂鬱質': '黒胆汁（地のエネルギー）',
        '多血質': '血液（風のエネルギー）',
        '粘液質': '粘液（水のエネルギー）'
    }
    for humor in humors:
        if humor in body_type:
            return humors[humor]
    return '複合的な体液バランス'

def get_humor_excess_symptoms(body_type):
    """体液過剰の症状を返す"""
    if '胆汁質' in body_type:
        return '過度の熱感、炎症、興奮性'
    elif '憂鬱質' in body_type:
        return '停滞感、重さ、憂うつ'
    elif '多血質' in body_type:
        return '落ち着きのなさ、散漫、過度の楽観'
    elif '粘液質' in body_type:
        return '浮腫、倦怠感、鈍重さ'
    return '複合的な症状'

def get_deficient_humor(body_type):
    """不足しやすい体液を返す"""
    if '胆汁質' in body_type:
        return '粘液（水のエネルギー）'
    elif '憂鬱質' in body_type:
        return '血液（風のエネルギー）'
    elif '多血質' in body_type:
        return '黒胆汁（地のエネルギー）'
    elif '粘液質' in body_type:
        return '黄胆汁（火のエネルギー）'
    return 'バランスの偏り'

def get_humor_deficiency_symptoms(body_type):
    """体液不足の症状を返す"""
    return '活力低下、免疫力の低下、回復力の遅延'

def get_important_minerals(element_combination):
    """重要なミネラルを返す"""
    minerals_map = {
        '火': 'マグネシウム、鉄分',
        '地': 'カルシウム、亜鉛',
        '風': 'カリウム、マンガン',
        '水': 'ナトリウム、ヨウ素'
    }
    result = []
    for element in element_combination.split('×'):
        if element in minerals_map:
            result.append(minerals_map[element])
    return '、'.join(result) if result else 'バランスよく各種ミネラル'

def get_ideal_sleep_time(element_combination):
    """理想的な就寝時間を返す"""
    if '火' in element_combination:
        return '22:00-23:00'
    elif '地' in element_combination:
        return '22:30-23:30'
    elif '風' in element_combination:
        return '23:00-24:00'
    elif '水' in element_combination:
        return '21:30-22:30'
    return '22:00-23:00'

def get_health_check_focus(body_type):
    """健康診断で注目すべき項目を返す"""
    if '胆汁質' in body_type:
        return '肝機能、炎症マーカー、血圧'
    elif '憂鬱質' in body_type:
        return 'ホルモンバランス、骨密度、消化機能'
    elif '多血質' in body_type:
        return '血糖値、甲状腺機能、神経伝達物質'
    elif '粘液質' in body_type:
        return 'リンパ機能、水分代謝、免疫系'
    return '総合的な健康指標'

def generate_holistic_prescriptions(name, archetype, celestial_data):
    """第4章：ホリスティック処方箋を生成（食養生とアロマテラピー中心、2,500文字以上）"""
    
    # エレメントの分析
    elements = archetype['element_combination'].split('×')
    dominant_element = elements[0] if elements else '火'
    
    text = f"""
【第4章：{name}様のための食養生とアロマテラピー処方箋】

{name}様の{archetype['name']}というアーキタイプと{archetype['body_type']}の体質に基づき、日本の風土に適した食養生とアロマテラピーを中心とした、実践的な健康増進プログラムをご提案いたします。

■ 食養生プログラム - 四大元素に基づく体質別食事療法

{name}様の{archetype['element_combination']}体質に最適化された食養生指針：

◆ 陰陽バランスの基本原則
{get_yinyang_balance_advice(archetype['element_combination'])}

◆ 推奨食材と調理法
{get_detailed_food_therapy(dominant_element, archetype['body_type'])}

◆ 季節別の食養生
{get_seasonal_dietary_advice(dominant_element)}

◆ 1日の食事リズム
- 朝食（7:00-8:00）：{get_breakfast_advice(dominant_element)}
- 昼食（12:00-13:00）：{get_lunch_advice(dominant_element)}
- 夕食（18:00-19:00）：{get_dinner_advice(dominant_element)}
- 間食：{get_snack_advice(dominant_element)}

◆ 避けるべき食材と食習慣
{get_foods_to_avoid(dominant_element, archetype['body_type'])}

■ アロマテラピー処方 - エレメント別精油プログラム

{archetype['element_combination']}のバランスを整える精油処方：

{get_aroma_prescription(dominant_element, archetype['temperament'])}

◆ 日常での具体的な使用法
{get_aroma_daily_usage(dominant_element)}

◆ 症状別アロマブレンド
{get_symptom_specific_aroma(archetype['body_type'])}

■ 症状・課題別の統合ケアプラン

{name}様の{archetype['temperament']}に起こりやすい不調への対処法：

{get_integrated_care_plan(dominant_element, archetype['body_type'])}

■ ライフスタイル医学的アプローチ

{archetype['temperament']}に適した生活習慣の改善：

◆ 運動療法
{get_exercise_prescription(dominant_element, archetype['body_type'])}

◆ 呼吸法とリラクゼーション
{get_breathing_exercises(dominant_element)}

◆ 入浴療法
{get_bathing_therapy(dominant_element, archetype['body_type'])}

■ 日常生活への実践的な統合方法

周波数による調整：
- 528Hz：DNA修復と愛の周波数 - 朝の瞑想時に
- 432Hz：自然との調和 - 作業中のBGMとして
- 639Hz：人間関係の改善 - 対人ストレス時に

■ ライフスタイル医学

1. 運動処方
{archetype['temperament']}に最適な運動メニュー：
- 月曜：ヨガ45分（柔軟性と呼吸）
- 火曜：有酸素運動30分（心肺機能）
- 水曜：筋トレ30分（上半身）
- 木曜：太極拳またはピラティス45分（バランス）
- 金曜：筋トレ30分（下半身）
- 土曜：好きなスポーツ60分（楽しみ）
- 日曜：散歩30分（回復）

2. 環境調整
- 寝室：{get_bedroom_setup(archetype['element_combination'])}
- 仕事場：{get_workspace_setup(archetype['element_combination'])}
- リビング：観葉植物と自然光を重視

■ 季節ごとのケアプログラム

春（3-5月）：デトックスと再生
夏（6-8月）：活動と社交
秋（9-11月）：収穫と感謝
冬（12-2月）：内省と計画

これらの処方は、{name}様の個性に合わせてカスタマイズ可能です。無理なく、楽しみながら実践することが最も重要です。
"""
    
    return text

def get_recommended_foods(element_combination):
    """推奨食材を返す"""
    foods = {
        '火': '赤い食材、スパイス、発酵食品',
        '地': '根菜、全粒穀物、ナッツ類',
        '風': '葉物野菜、軽い食材、フルーツ',
        '水': '海産物、水分の多い野菜、スープ'
    }
    result = []
    for element in element_combination.split('×'):
        if element in foods:
            result.append(foods[element])
    return '、'.join(result) if result else 'バランスの取れた多様な食材'

def get_restricted_foods(element_combination):
    """制限食材を返す"""
    if '火' in element_combination:
        return '過度に辛い食べ物、アルコール、揚げ物'
    elif '地' in element_combination:
        return '重い乳製品、過度の肉類、砂糖'
    elif '風' in element_combination:
        return '冷たい飲み物、生野菜の過剰摂取、カフェイン'
    elif '水' in element_combination:
        return '塩分の多い食品、冷凍食品、粘液を増やす食材'
    return '極端な味付けや加工食品'

def get_main_crystal(element_combination):
    """メインクリスタルを返す"""
    crystals = {
        '火': 'カーネリアン（活力と情熱）',
        '地': 'スモーキークォーツ（グラウンディング）',
        '風': 'シトリン（知性と創造性）',
        '水': 'ムーンストーン（感情の調和）'
    }
    elements = element_combination.split('×')
    if elements[0] in crystals:
        return crystals[elements[0]]
    return 'クリアクォーツ（万能）'

def get_support_crystals(element_combination):
    """サポートクリスタルを返す"""
    return 'アメジスト（精神性）、ローズクォーツ（愛）、ブラックトルマリン（保護）'

def get_bedroom_setup(element_combination):
    """寝室のセットアップを返す"""
    if '火' in element_combination:
        return '暖色系の照明、南向きの配置'
    elif '地' in element_combination:
        return 'アースカラーの装飾、低めのベッド'
    elif '風' in element_combination:
        return '風通しの良い配置、軽やかなカーテン'
    elif '水' in element_combination:
        return 'ブルー系の色調、加湿器の設置'
    return 'バランスの取れた自然な空間'

def get_workspace_setup(element_combination):
    """仕事場のセットアップを返す"""
    return '自然光、植物、整理整頓された空間'

def generate_life_planning(name, archetype, celestial_data):
    """第5章：人生設計とライフプランニングを生成（2,500文字）"""
    
    text = f"""
【第5章：{name}様の天命を生きるためのライフプランニング】

{archetype['name']}というアーキタイプを持つ{name}様の人生は、独自の時間軸とリズムで展開します。占星医学の観点から、最適な人生設計をご提案いたします。

■ ライフサイクルと重要な転換期

◆ 29-30歳：土星回帰（Saturn Return）
最初の大きな成熟期。{archetype['element_combination']}の統合が始まり、真の個性が確立される時期。キャリアの方向性を定め、人生の基盤を築く重要な時期です。

◆ 36-37歳：ノードの2回目の回帰
運命的な出会いや転機が訪れやすい時期。{name}様の{archetype['name']}としての使命が明確になり、社会的な役割が確立されます。

◆ 42-44歳：天王星対衝（Uranus Opposition）
「中年の危機」とも呼ばれる革新の時期。従来の価値観を見直し、後半生に向けた新しい方向性を模索します。{archetype['temperament']}の深い部分が活性化されます。

◆ 50-51歳：キロン回帰（Chiron Return）
「傷ついた治療者」の帰還。人生の傷や課題が癒しの源泉となり、他者への貢献が始まる時期です。

◆ 58-60歳：第2土星回帰
真の円熟期。蓄積された知恵が結実し、{archetype['name']}としての完成形に近づきます。

■ キャリアデザインと適職

{archetype['name']}の特性を活かせる職業領域：

1. 創造的リーダーシップ
{archetype['talents']}を活かし、革新的なプロジェクトを推進する役割。起業家、プロデューサー、クリエイティブディレクターなど。

2. 癒しと変容の仕事
{archetype['body_type']}の理解を活かし、他者の成長を支援する役割。セラピスト、コーチ、医療従事者など。

3. 知識と教育
{celestial_data.get('mercury', {}).get('element', '風')}の影響を活かし、知識を伝える役割。教育者、作家、研究者など。

4. 美と調和の創造
{celestial_data.get('venus', {}).get('element', '地')}のエネルギーを表現する役割。アーティスト、デザイナー、音楽家など。

■ 人間関係のダイナミクス

{archetype['element_combination']}の組み合わせは、特定のタイプの人々を引き寄せます：

◆ 相性の良いパートナー
- 補完的エレメントを持つ人：{get_complementary_elements(archetype['element_combination'])}
- 同じ価値観を共有しながらも、異なる表現方法を持つ人
- {name}様の成長を促進し、同時に安定感を提供できる人

◆ ビジネスパートナーシップ
- {archetype['challenges']}を補完できる能力を持つ人
- 実務能力と創造性のバランスが取れている人
- 長期的なビジョンを共有できる人

◆ メンターと弟子
- メンター：{name}様より一回り上の世代で、同じアーキタイプの成熟形を体現している人
- 弟子：{name}様の経験から学びたいと願う、純粋な探求心を持つ人

■ 富と豊かさの創造

{archetype['name']}にとっての真の豊かさ：

1. 経済的側面
- 収入源の多様化：{archetype['talents']}を複数の形で収益化
- 投資戦略：{get_investment_style(archetype['element_combination'])}
- 金銭管理：{archetype['temperament']}に適した管理方法の確立

2. 時間の豊かさ
- 創造的な時間：1日2時間以上確保
- 回復の時間：週1日は完全休養
- 成長の時間：月10時間以上の学習

3. 関係性の豊かさ
- 深い絆を持つ人々との定期的な交流
- 新しい出会いへの開放性
- 孤独な時間の大切さも認識

■ 健康寿命の最大化

{archetype['body_type']}の特性を考慮した長寿の秘訣：

1. 30代：予防の基礎作り
- 定期健診の習慣化
- ストレス管理技術の習得
- 運動習慣の確立

2. 40代：バランスの調整
- ホルモンバランスの観察
- 食生活の最適化
- 心理的な成熟

3. 50代：智慧の活用
- 経験を活かした健康管理
- 次世代への貢献準備
- 精神的な深まり

4. 60代以降：統合と超越
- 全体性の実現
- 遺産（レガシー）の創造
- 宇宙的視点の獲得

■ スピリチュアルな成長の道

{archetype['name']}の霊的進化：

第1段階：自己認識（20-35歳）
- 自分が何者かを理解する
- 才能と課題を受け入れる
- 個人的な力を確立する

第2段階：他者との関係（35-50歳）
- 深い絆を形成する
- 社会的な貢献を始める
- カルマ的な関係を癒す

第3段階：宇宙との一体（50歳以降）
- より大きな目的を理解する
- 無条件の愛を体現する
- 次元を超えた意識へ

■ 人生の最終章に向けて

{name}様の{archetype['name']}としての完成は、単なる個人的な達成を超えて、集合意識への貢献となります。あなたが体現する{archetype['element_combination']}のエネルギーは、周囲の人々にも影響を与え、より大きな調和の一部となっていきます。

人生の各段階で得た智慧を統合し、次世代へ伝えることが、{archetype['name']}としての究極の使命となるでしょう。
"""
    
    return text

def get_complementary_elements(element_combination):
    """補完的エレメントを返す"""
    complements = {
        '火': '風（刺激と拡大）、地（安定と具現化）',
        '地': '水（感情の潤い）、火（活性化）',
        '風': '火（情熱）、水（深み）',
        '水': '地（構造）、風（流通）'
    }
    elements = element_combination.split('×')
    results = []
    for element in elements:
        if element in complements:
            results.append(complements[element])
    return ' / '.join(results) if results else '多様なエレメント'

def get_investment_style(element_combination):
    """投資スタイルを返す"""
    if '火' in element_combination:
        return '成長株、ベンチャー投資、短期的なリターン重視'
    elif '地' in element_combination:
        return '不動産、配当株、長期保有戦略'
    elif '風' in element_combination:
        return '分散投資、テクノロジー株、情報重視'
    elif '水' in element_combination:
        return 'ESG投資、社会的インパクト投資、直感重視'
    return 'バランス型ポートフォリオ'

# 食養生とアロマテラピーのヘルパー関数

def get_yinyang_balance_advice(element_combination):
    """陰陽バランスのアドバイスを返す"""
    if '火' in element_combination:
        return "陽性が強いため、陰性食材（葉物野菜、夏野菜、果物）でバランスを取ることが重要です。"
    elif '地' in element_combination:
        return "陰性がやや強いため、陽性食材（根菜類、肉類、スパイス）で温めることが大切です。"
    elif '風' in element_combination:
        return "軽やかさが過剰になりやすいため、グラウンディング効果のある根菜類を中心に。"
    elif '水' in element_combination:
        return "水分が停滞しやすいため、温性スパイスと利尿作用のある食材で代謝を促進。"
    return "陰陽のバランスを意識した中庸の食事を心がけましょう。"

def get_detailed_food_therapy(element, body_type):
    """詳細な食物療法を返す"""
    therapies = {
        '火': """
• 推奨食材：きゅうり、すいか、トマト、緑豆、ミント、梨、豆腐
• 調理法：生食、茸でる、蒸す（涸性・寒性の性質を活かす）
• 具体的な献立例：
  - 朝：グリーンスムージー、ヨーグルトとフルーツ
  - 昼：冷やし中華、サラダボウル
  - 夕：豆腐と夏野菜のさっぱり煮物
• 注意点：辛いスパイス、揚げ物、アルコールは控えめに""",
        '地': """
• 推奨食材：生姜、ごぼう、人参、羊肉、シナモン、黒ゴマ
• 調理法：煮る、炒める、シチュー、煮込み（温性・熱性を引き出す）
• 具体的な献立例：
  - 朝：生姜入りお粥、温かいスープ
  - 昼：根菜の煮物、きんぴらごぼう
  - 夕：鶏肉と根菜のポトフ
• 注意点：冷たい飲食物、生もの、冷性食材は避ける""",
        '風': """
• 推奨食材：根菜類、全粒穀物、甘みのある食材（人参、りんご、米）
• 調理法：煮る、蒸す、グラウンディング効果のある調理
• 具体的な献立例：
  - 朝：オートミール、玄米おにぎり
  - 昼：根菜たっぷりの味噌汁定食
  - 夕：かぼちゃのスープ、さつまいもご飯
• 注意点：カフェイン過多、刺激物、軽すぎる食事は避ける""",
        '水': """
• 推奨食材：温性スパイス（生姜、シナモン）、小豆、はと麦、海藻
• 調理法：炒める、スパイス使用、温かい調理
• 具体的な献立例：
  - 朝：スパイスティー、温かいスープ
  - 昼：小豆ご飯、カレー
  - 夕：生姜焖き、ハトムギ茶
• 注意点：冷たい飲食物、乳製品過多、甘いもの過多は避ける"""
    }
    return therapies.get(element, "バランスの取れた食事を心がけましょう")

def get_seasonal_dietary_advice(element):
    """季節別の食養生アドバイスを返す"""
    return f"""
• 春：苦味のある春野菜（ふきのとう、たらの芽）でデトックス
• 夏：冷却作用のある夏野菜で体内の熱を管理
• 秋：潤いを補う白い食材（梨、れんこん、大根）
• 冬：温性食材と煮込み料理でエネルギー蓄積
"""

def get_breakfast_advice(element):
    """朝食のアドバイスを返す"""
    advice = {
        '火': "フルーツ、ヨーグルト、グリーンスムージーで体内の熱を冷ます",
        '地': "温かいお粥やスープで消化器を温める",
        '風': "玄米やオートミールでグラウンディング",
        '水': "スパイスティーと温かい食事で代謝を促進"
    }
    return advice.get(element, "消化に良い温かい食事")

def get_lunch_advice(element):
    """昼食のアドバイスを返す"""
    advice = {
        '火': "サラダボウルや冷製パスタでクールダウン",
        '地': "根菜の煮物やシチューでエネルギー補給",
        '風': "バランスの取れた定食で安定感を",
        '水': "スパイシーなカレーやエスニック料理"
    }
    return advice.get(element, "バランスの良い食事")

def get_dinner_advice(element):
    """夕食のアドバイスを返す"""
    advice = {
        '火': "豆腐や白身魚のさっぱりした料理",
        '地': "温かいポトフや鶏肉の煮込み",
        '風': "消化に優しいスープや蒸し料理",
        '水': "生姜を使った炒め物や焦き魚"
    }
    return advice.get(element, "消化に優しい軽めの食事")

def get_snack_advice(element):
    """間食のアドバイスを返す"""
    advice = {
        '火': "水分の多い果物（スイカ、梨）",
        '地': "ナッツ類、ドライフルーツ",
        '風': "甘い果物（りんご、バナナ）",
        '水': "スパイス入りナッツ、ジンジャーティー"
    }
    return advice.get(element, "季節の果物やナッツ")

def get_foods_to_avoid(element, body_type):
    """避けるべき食材と食習慣を返す"""
    avoidances = {
        '火': "辛いスパイス、アルコール、揚げ物、コーヒーの過剰摂取",
        '地': "冷たい飲み物、アイスクリーム、生野菜の過剰摂取",
        '風': "カフェイン過多、不規則な食事、ながら食い",
        '水': "乳製品過多、砂糖の過剰摂取、冷たい飲食物"
    }
    return avoidances.get(element, "過度の加工食品と不規則な食事")

def get_aroma_prescription(element, temperament):
    """エレメント別アロマ処方を返す"""
    prescriptions = {
        '火': """
火のエネルギー調整ブレンド：
• 鎮静：ラベンダー（3滴）、カモミール（2滴） - 過剰な熱を鎮める
• 心の平和：サンダルウッド（2滴） - 内なる平和と瞑想
• 愛の火：ローズ（1滴） - 怒りを愛に変容
使用例：イライラした時にハンカチに垂らして深呼吸""",
        '地': """
地のエネルギー活性化ブレンド：
• 軽やかさ：ペパーミント（2滴）、レモン（2滴） - 重さを解放
• 浄化：ユーカリ（2滴） - 新鮮さと変化
• 代謝促進：グレープフルーツ（1滴） - 軽やかな変化
使用例：朝のディフューザーで活力を高める""",
        '風': """
風のエネルギー鎮静ブレンド：
• グラウンディング：ベチバー（3滴）、シダーウッド（2滴） - 大地との繋がり
• 神経鎮静：ラベンダー（2滴）、カモミール（1滴） - 穏やかさ
• 感情との繋がり：イランイラン（1滴） - 感情調整
使用例：足裏にベチバーを塗布して安定感を得る""",
        '水': """
水のエネルギー調整ブレンド：
• デトックス：ジュニパー（2滴）、サイプレス（2滴） - 流れの促進
• 軽やかさ：グレープフルーツ（2滴）、レモン（1滴） - 浄化
• 明晰さ：ローズマリー（1滴） - 論理性と集中
使用例：入浴時に加えてデトックスを促進"""
    }
    return prescriptions.get(element, "バランスブレンドを使用")

def get_aroma_daily_usage(element):
    """アロマの日常使用法を返す"""
    return f"""
• 朝：ディフューザーで活性化ブレンドを30分間
• 昼：ハンカチに1滴垂らしてリフレッシュ
• 夕：入浴時に3-5滴をバスタブに
• 寝る前：枕元にティッシュで1滴で安眠へ
"""

def get_symptom_specific_aroma(body_type):
    """症状別アロマブレンドを返す"""
    if '胆汁質' in body_type:
        return "不眠にはラベンダー、イライラにはカモミール"
    elif '憂鬱質' in body_type:
        return "気分の落ち込みにはベルガモット、疲労にはペパーミント"
    elif '多血質' in body_type:
        return "不安にはベチバー、思考過多にはイランイラン"
    elif '粘液質' in body_type:
        return "倦怠感にはグレープフルーツ、むくみにはジュニパー"
    return "症状に応じたブレンドを選択"

def get_integrated_care_plan(element, body_type):
    """統合ケアプランを返す"""
    if element == '火':
        return """
◆ 過剰な「火」による、いらだちと不眠への対処：

1. 食事療法：
   - 夕食に「きゅうりとワカメの酢の物」を一品加える
   - 日中の飲み物をコーヒーから「緑茶」や「ミントティー」に変える
   - デザートにスイカや梨を選ぶ

2. アロマテラピー：
   - 就寝前：ぬるめのお湯にラベンダー3滴で入浴
   - 日中のいらだち：ローズの希釈オイルを手首に塗布

3. ライフスタイル：
   - 就寝1時間前にスマホを手放し、照明を落とす
   - 毎日10分の「鎮静の時間」を設ける
"""
    elif element == '風':
        return """
◆ 過剰な「風」による、不安と思考過多への対処：

1. 食事療法：
   - 白米を玄米に変えてグラウンディング
   - 毎食「根菜の煮物」や「かぼちゃのスープ」を取り入れる
   - カフェインを減らし、ハーブティーに切り替え

2. アロマテラピー：
   - 日中の不安感：ベチバーを足裏に塗布
   - 思考が止まらない時：イランイランを深く吸入

3. ライフスタイル：
   - 1日の終わりに5分間のジャーナリング
   - 週末に足で土や芝生に触れる時間を作る
"""
    else:
        return """
◆ バランス調整のための統合ケア：

1. 食事療法：体質に合わせた食材選びと調理法
2. アロマテラピー：エレメントバランスを整える精油
3. ライフスタイル：規則正しい生活と適度な運動
"""

def get_exercise_prescription(element, body_type):
    """運動処方を返す"""
    prescriptions = {
        '火': "ヨガ、水泳、太極拳などのクールダウン系運動を週に3-4回",
        '地': "ウォーキング、ジョギング、ダンスなどの活性化運動を毎日30分",
        '風': "グラウンディングヨガ、武道、ウエイトトレーニングで安定感を",
        '水': "エアロビクス、ダンス、サウナで代謝を活性化"
    }
    return prescriptions.get(element, "適度な有酸素運動とストレッチ")

def get_breathing_exercises(element):
    """呼吸法を返す"""
    exercises = {
        '火': "4-7-8呼吸法（4秒吸って7秒止めて8秒吐く）でクールダウン",
        '地': "腹式呼吸で深くゆっくりと、体を温める",
        '風': "丁寧な鼻呼吸で5分間、心を落ち着かせる",
        '水': "火の呼吸（カパラバティ）で代謝を促進"
    }
    return exercises.get(element, "深呼吸でリラックス")

def get_bathing_therapy(element, body_type):
    """入浴療法を返す"""
    therapies = {
        '火': "ぬるめのお湯（38-39度）に15-20分、ラベンダーを加えて",
        '地': "温かいお湯（40-41度）に岩塩を加えてデトックス",
        '風': "半身浴でジャーマンカモミールを加えてリラックス",
        '水': "熱めのお湯（41-42度）に生姜やシナモンを加えて温まる"
    }
    return therapies.get(element, "適温のお湯でリラックス")

def generate_epilogue(name, archetype):
    """エピローグを生成（500文字）"""
    
    text = f"""
【エピローグ：{name}様へのメッセージ】

この12,000文字を超える詳細なASTRO-MEDICAL REPORTは、{name}様の{archetype['name']}というアーキタイプが持つ無限の可能性を解き明かすための地図です。

しかし、地図は道そのものではありません。実際の旅路は、{name}様自身が一歩一歩歩んでいくものです。このレポートで示された指針は、あくまでも可能性であり、運命は{name}様の選択と行動によって創造されていきます。

{archetype['tagline']}という本質を生きることは、時に困難を伴うかもしれません。しかし、その困難こそが{name}様を成長させ、真の自己実現へと導く貴重な機会となります。

宇宙は{name}様の存在を祝福しています。太陽と月、そして全ての惑星たちが、{name}様の人生という壮大な交響曲を奏でています。その音楽に耳を傾け、自分のリズムで踊ることを恐れないでください。

{archetype['name']}として生きることは、世界に対する{name}様独自の贈り物です。その贈り物を惜しみなく分かち合うことで、{name}様自身もまた、想像を超える豊かさを受け取ることになるでしょう。

願わくば、この占星医学的な洞察が、{name}様の人生により深い意味と方向性をもたらし、健康と幸福、そして魂の充足への道を照らす光となりますように。

織田先生の16原型論に基づく、{name}様専用のASTRO-MEDICAL REPORTを終えるにあたり、宇宙の祝福と共に。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
監修：織田剛
ASTRO-MEDICAL SYSTEM © 2024
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    return text

if __name__ == '__main__':
    # Railway環境では環境変数PORTを使用
    import os
    port = int(os.environ.get('PORT', 5000))
    # Production環境ではdebug=Falseに
    debug_mode = os.environ.get('FLASK_ENV', 'production') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
