import streamlit as st
import streamlit.components.v1 as components
import json
import os
import base64
import hashlib
import time
from dotenv import load_dotenv
from pathlib import Path

# 用脚本所在目录的绝对路径加载 .env，避免工作目录不一致
_env_path = Path(__file__).parent / ".env"
load_dotenv(_env_path, override=True)

# ===== API 配置（纯 ASCII 清洗） =====
def _clean_env(key, default=""):
    val = os.getenv(key, default)
    if val:
        val = val.strip().strip('"').strip("'")
        val = val.encode("ascii", errors="ignore").decode("ascii")
    return val or default

DASHSCOPE_API_KEY = _clean_env("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = _clean_env("DASHSCOPE_BASE_URL",
    "https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1")
DASHSCOPE_MODEL = _clean_env("DASHSCOPE_MODEL", "deepseek-v4-flash")

# ===== 常量配置 =====
IMAGES_DIR = "images"
os.makedirs(IMAGES_DIR, exist_ok=True)

# ===== 页面配置 =====
st.set_page_config(
    page_title="西湖文脉图志 · AI文化遗产平台",
    page_icon="🏛️",
    layout="wide",
)

# ==================== 文化元素数据库 ====================
CULTURE_DATA = {
    "断桥残雪": {
        "poems": ["君到姑苏见，人家尽枕河。古宫闲地少，水港小桥多。——杜荀鹤《送人游吴》",
                   "断桥残雪不成归，湖色苍茫入望非。——许承祖《西湖志》"],
        "legends": ["白蛇传中白娘子与许仙相遇之地，发生了一段千古传诵的爱情故事", "相传桥拱有白蛇出没，因而得名"],
        "history": "断桥始建于唐代，原名宝祐桥，后改称断桥。元代又称段家桥。桥长8.8米，宽8.6米，单孔净跨6.1米。",
        "famous_people": ["白娘子", "许仙", "小青"],
        "timeline": {"唐代": "断桥始建", "宋元": "多次重修", "清代": "定名「断桥残雪」为西湖十景之一", "2011年": "列入世界文化遗产名录"},
        "recommendations": ["春季观赏杨柳依依", "冬季雪后初霁最佳", "傍晚夜景灯光很美"]
    },
    "浙江省博物馆": {
        "poems": ["南朝四百八十寺，多少楼台烟雨中。——杜牧《江南春》"],
        "legends": ["馆藏越窑青瓷代表了中国瓷器的鼎盛时期", "有「江南第一家」之称的浦江郑氏文物"],
        "history": "始建于1929年，是浙江省规模最大的综合性博物馆。馆藏文物超过十万件，涵盖书画、陶瓷、青铜器、越窑青瓷等。",
        "famous_people": ["丰子恺", "沙孟海"],
        "timeline": {"1929年": "浙江省博物馆创建", "1976年": "书画部独立建制", "2013年": "推出「越地长歌」基本陈列", "2020年": "之江分馆开放"},
        "recommendations": ["建议参观时间2-3小时", "重点看越窑青瓷展区", "关注「南宋御街」特展"]
    },
    "苏堤": {
        "poems": ["欲把西湖比西子，淡妆浓抹总相宜。——苏轼《饮湖上初晴后雨》", "六桥烟柳映清波，十里春风十里歌。——苏东坡"],
        "legends": ["苏东坡主持疏浚西湖时所筑，以湖泥筑堤，全长近三公里", "苏堤春晓为西湖十景之首"],
        "history": "宋元祐四年（1089年），苏东坡任杭州通判，疏浚西湖，以湖泥筑堤，后人称苏堤。堤上建有六桥。",
        "famous_people": ["苏轼（苏东坡）", "林逋"],
        "timeline": {"1089年": "苏东坡疏浚西湖筑苏堤", "南宋": "苏堤成为御花园", "清代": "「苏堤春晓」列为十景之首", "2011年": "列入世界文化遗产"},
        "recommendations": ["春季桃花盛开时最美", "清晨走堤看日出", "骑行游览全程约1小时"]
    },
    "曲院风荷": {
        "poems": ["毕竟西湖六月中，风光不与四时同。接天莲叶无穷碧，映日荷花别样红。——杨万里", "红藕香残玉簟秋。轻解罗裳，独上兰舟。——李清照"],
        "legends": ["曲院原是南宋皇家酒坊，因附近多荷花，故名曲院风荷", "西湖十景之一，以夏日荷花闻名"],
        "history": "曲院风荷位于西湖西北角，濒临岳湖。南宋时此处为皇家酿酒之地，周围遍植荷花。",
        "famous_people": ["杨万里", "李清照"],
        "timeline": {"南宋": "设立曲院（皇家酒坊）", "元代": "曲院荒废", "清代": "重建列为十景", "1980s": "扩建至数百亩"},
        "recommendations": ["最佳观赏期：6-8月", "清晨荷香最浓", "可品尝荷花茶、莲子羹"]
    },
    "雷峰塔景区": {
        "poems": ["雷锋夕照照孤山，十里松风九里湾。——董嗣杲", "烟光山色淡溟濛，千尺浮图兀倚空。——张岱"],
        "legends": ["雷峰夕照为西湖十景之一", "白娘子传说中，法海将白娘子镇压于雷峰塔下", "民间有「雷峰塔倒掉，西湖水干」的谚语"],
        "history": "雷峰塔又名皇妃塔、西关砖塔，始建于北宋开宝八年（975年），为吴越国王钱俶因黄妃得子而建。原塔于1924年倒塌，2002年重建。",
        "famous_people": ["钱俶", "白娘子", "法海", "许仙"],
        "timeline": {"975年": "雷峰塔始建", "1924年": "古塔倒塌", "2002年": "重建落成", "2011年": "列入世界文化遗产"},
        "recommendations": ["黄昏时登塔看夕阳", "塔内有白娘子传说展", "可俯瞰西湖全景"]
    },
    "紫阳山": {
        "poems": ["江湖上、清江畔，月白风清。水天一色，湖山入望。——苏轼"],
        "legends": ["山上有紫阳道观，为纪念道教紫阳真人张伯端而建"],
        "history": "紫阳山位于杭州城南，山上有紫阳道观，始建于北宋。清道光年间重建。",
        "famous_people": ["张伯端（紫阳真人）", "苏轼"],
        "timeline": {"北宋": "紫阳道院始建", "明代": "改称紫阳观", "清代": "多次重修", "近代": "列为道教活动场所"},
        "recommendations": ["清晨登山空气清新", "山上有茶室可品茗"]
    },
    "中国丝绸博物馆": {
        "poems": ["春蚕不应老，昼夜常怀丝。——蒋贻恭", "桑蚕作茧自缠裹，春蚕到死丝方尽。——李商隐"],
        "legends": ["是世界上最大的丝绸博物馆", "展示了中国五千年的丝绸文化史"],
        "history": "1986年建成开放，是中国第一座国家级丝绸博物馆。馆藏文物近万件。",
        "famous_people": ["嫘祖（蚕神）", "黄道婆"],
        "timeline": {"1986年": "博物馆建成开放", "2001年": "扩建改造", "2014年": "G20峰会后升级", "2023年": "推出「丝路千年」特展"},
        "recommendations": ["建议参观时间1.5小时", "体验丝绸文化DIY", "购买丝绸纪念品"]
    },
    "杭州西湖风景名胜区": {
        "poems": ["水光潋滟晴方好，山色空蒙雨亦奇。——苏轼", "乱花渐欲迷人眼，浅草才能没马蹄。——白居易", "山外青山楼外楼，西湖歌舞几时休。——林升"],
        "legends": ["西湖是中国十大风景名胜之一", "2011年被联合国教科文组织列入世界文化遗产名录"],
        "history": "西湖风景名胜区总面积约60平方公里，湖面面积5.66平方公里。由自然山水、人文古迹、宗教艺术、民俗文化等组成。",
        "famous_people": ["白居易", "苏东坡", "林逋", "岳飞", "陆游", "辛弃疾"],
        "timeline": {"秦汉": "西湖形成潟湖", "隋唐": "筑湖堤成型", "南宋": "定临安为行在", "2011年": "列入世界文化遗产"},
        "recommendations": ["全天游览最佳", "环湖骑行或游船", "购买西湖十景明信片"]
    },
    "玉皇山景区": {
        "poems": ["龙湫百丈厓，日落变千态。——吴融"],
        "legends": ["山上有福星观、黄龙洞等景点", "登高远眺西湖的最佳去处之一"],
        "history": "玉皇山海拔239米，是杭州城垣内最高的山峰。山上有福星观，始建于明代。",
        "famous_people": ["张三丰", "黄宾虹"],
        "timeline": {"明代": "福星观始建", "清代": "多次修葺", "当代": "西湖登山热门线路"},
        "recommendations": ["登山约1.5小时", "山顶看西湖全景", "黄龙洞求签祈福"]
    },
    "杭州动物园": {
        "poems": ["两个黄鹂鸣翠柳，一行白鹭上青天。——杜甫"],
        "legends": ["位于西湖风景区南侧", "饲养大熊猫、金丝猴、东北虎等珍稀动物"],
        "history": "杭州动物园占地40公顷，始建于1958年。现有动物200余种。",
        "famous_people": ["竺可桢（创办人之一）"],
        "timeline": {"1958年": "杭州动物园创建", "1980年": "迁入现址", "2010年": "大熊猫馆开放"},
        "recommendations": ["建议参观时间3-4小时", "上午动物最活跃", "可乘坐观光车"]
    },
    "八卦田遗址公园": {
        "poems": ["田上一条斜坂路，山头几处白云居。——释道潜"],
        "legends": ["南宋皇家籍田遗址", "因形状如八卦而得名"],
        "history": "八卦田是南宋绍兴年间（1131-1162年）开辟的皇家籍田，总面积约150亩。",
        "famous_people": ["宋高宗赵构", "宋孝宗赵昚"],
        "timeline": {"1131年": "八卦田开辟", "2007年": "考古发掘", "2012年": "遗址公园建成"},
        "recommendations": ["秋季稻田金黄最美", "可了解南宋农耕文化"]
    },
    "杭州植物园": {
        "poems": ["人间四月芳菲尽，山寺桃花始盛开。——白居易", "竹外桃花三两枝，春江水暖鸭先知。——苏轼"],
        "legends": ["收集植物种类超过5000种", "是集科研、科普、游览于一体的综合性植物园"],
        "history": "杭州植物园占地231公顷，始建于1956年。",
        "famous_people": ["梁希（创建者）"],
        "timeline": {"1956年": "杭州植物园创建", "1980年": "加入国际植物园协会", "2021年": "收集植物5000余种"},
        "recommendations": ["春季赏花最佳", "可参加植物科普活动"]
    },
    "浙大玉泉校区": {
        "poems": ["夜月一帘幽梦，春风十里柔情。——秦观"],
        "legends": ["浙江大学玉泉校区是浙大主校区之一", "创办于1897年，前身为求是书院"],
        "history": "浙江大学玉泉校区位于西湖西北角，始建于1953年。是浙大最具历史感的校区。",
        "famous_people": ["竺可桢校长", "马一浮"],
        "timeline": {"1897年": "求是书院创办", "1928年": "定名国立浙江大学", "1953年": "玉泉校区建成", "2017年": "浙大入选「双一流」"},
        "recommendations": ["校园开放日可参观", "品味求是文化", "周边美食丰富"]
    }
}

# ==================== AI 文化对话功能 ====================
SYSTEM_PROMPT = """你是一位精通杭州西湖文化的AI导览专家，名叫"西湖文脉"。你对西湖及杭州的历史文化、诗词传说、名人轶事、旅游指南等了如指掌。

请根据用户的问题，结合景点信息，提供生动、专业、有趣的回答。回答要求：
1. 引用具体的历史年代、诗词出处、典故来源
2. 适当使用emoji增加可读性
3. 如果用户问的是景点相关，请主动介绍该景点的文化价值
4. 回答尽量结构化，条理清晰
5. 用中文回答"""


def generate_ai_response(spot_name, user_query, culture_data):
    """调用 DashScope API 生成 AI 回复，失败时回退到硬编码"""
    data = culture_data.get(spot_name, {})

    context_text = f"景点: {spot_name}\n"
    if data.get('history'):
        context_text += f"历史: {data['history']}\n"
    if data.get('timeline'):
        context_text += "时间线:\n"
        for era, event in data['timeline'].items():
            context_text += f"  - {era}: {event}\n"
    if data.get('poems'):
        context_text += "相关诗词:\n"
        for poem in data['poems']:
            context_text += f"  - {poem}\n"
    if data.get('legends'):
        context_text += "传说故事:\n"
        for legend in data['legends']:
            context_text += f"  - {legend}\n"
    if data.get('famous_people'):
        context_text += f"相关名人: {', '.join(data['famous_people'])}\n"
    if data.get('recommendations'):
        context_text += "游览建议:\n"
        for rec in data['recommendations']:
            context_text += f"  - {rec}\n"

    if not DASHSCOPE_API_KEY:
        return _hardcoded_response(spot_name, user_query, data)

    try:
        import http.client
        import ssl
        from urllib.parse import urlparse

        payload = {"model": DASHSCOPE_MODEL,
                   "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                                {"role": "user", "content": f"景点背景：\n{context_text}\n\n用户问题：\n{user_query}"}],
                   "temperature": 0.7, "max_tokens": 2000}

        # 直接用 http.client，避免 requests/urllib3 的 header 编码问题
        body_bytes = json.dumps(payload, ensure_ascii=True).encode("ascii")

        parsed = urlparse(DASHSCOPE_BASE_URL)
        host = parsed.hostname
        port = parsed.port or 443
        path = parsed.path + "/chat/completions"

        ctx = ssl.create_default_context()
        conn = http.client.HTTPSConnection(host, port, context=ctx, timeout=15)

        # 所有 header 值确保是纯 ASCII
        headers = {
            "Authorization": "Bearer " + DASHSCOPE_API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "XihuMap/1.0",
        }
        # 强制编码检查
        safe_headers = {}
        for k, v in headers.items():
            safe_headers[k] = v.encode("ascii", errors="replace").decode("ascii")

        conn.request("POST", path, body=body_bytes, headers=safe_headers)
        resp = conn.getresponse()
        resp_body = resp.read().decode("utf-8")

        if resp.status != 200:
            conn.close()
            return f"API 错误 (HTTP {resp.status})。\n\n{_hardcoded_response(spot_name, user_query, data)}"

        body = json.loads(resp_body)
        conn.close()

        msg = body["choices"][0]["message"]
        content = msg.get("content", "")
        if not content:
            return f"模型思考超时，请重试。\n\n{_hardcoded_response(spot_name, user_query, data)}"
        return content
    except Exception as e:
        import traceback
        detail = traceback.format_exc()
        return f"❌ 调用异常：{type(e).__name__}: {e}\n```\n{detail[-400:]}\n```\n\n{_hardcoded_response(spot_name, user_query, data)}"


def _hardcoded_response(spot_name, user_query, data):
    response = f"关于【{spot_name}】：\n\n"
    response += data.get('history', '这是西湖畔的文化景点。')
    poems = data.get('poems', [])
    if poems:
        response += f"\n\n📜 {poems[0]}"
    return response


# ===== 用户管理 =====
USERS_FILE = "users.json"


def _load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def _hash_pw(pw):
    return hashlib.sha256(f"xihu_{pw}_map".encode()).hexdigest()


def register_user(username, password):
    users = _load_users()
    if username in users:
        return False, "用户名已存在"
    users[username] = _hash_pw(password)
    _save_users(users)
    return True, "注册成功"


def login_user(username, password):
    users = _load_users()
    if username not in users:
        return False, "用户不存在"
    if users[username] != _hash_pw(password):
        return False, "密码错误"
    return True, "登录成功"


def spot_file(username):
    return f"spots_data_{username}.json"


# ===== 工具函数 =====
def get_image_base64(filepath):
    if filepath and os.path.exists(filepath):
        with open(filepath, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return None


def load_spots():
    user = st.session_state.get("current_user", "")
    data_file = spot_file(user) if user else "spots_data.json"
    if os.path.exists(data_file):
        try:
            with open(data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []
    return []


def save_spots():
    user = st.session_state.get("current_user", "")
    data_file = spot_file(user) if user else "spots_data.json"
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(st.session_state.spots, f, ensure_ascii=False, indent=2)


# ===== 初始化 Session State =====
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"  # "login" | "register"
if "spots" not in st.session_state or not st.session_state.spots:
    st.session_state.spots = load_spots()
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None
if "highlight_index" not in st.session_state:
    st.session_state.highlight_index = None
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "captured_coords" not in st.session_state:
    st.session_state.captured_coords = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = {}

# ——— 处理 URL query params（地图点击回传） ———
qp = st.query_params
needs_rerun = False

if "mx" in qp and "my" in qp:
    try:
        _x = float(qp["mx"]); _y = float(qp["my"])
        st.session_state.captured_coords = (round(_x, 1), round(_y, 1))
        needs_rerun = True
    except (ValueError, TypeError):
        pass

if "hl" in qp:
    try:
        _idx = int(qp["hl"])
        if 0 <= _idx < len(st.session_state.spots):
            st.session_state.highlight_index = _idx
            needs_rerun = True
    except (ValueError, TypeError):
        pass

if needs_rerun:
    st.query_params.clear()
    st.rerun()

# ===== 加载底图 =====
hero_path = os.path.join(IMAGES_DIR, "another.jpg")
MAP_Y_MAX = 100.0
MAP_IMG_B64 = None
if os.path.exists(hero_path):
    try:
        from PIL import Image
        with Image.open(hero_path) as im:
            w, h = im.size
        MAP_Y_MAX = round(100.0 * h / w, 1)
    except Exception:
        MAP_Y_MAX = 100.0
    MAP_IMG_B64 = get_image_base64(hero_path)

# ===== 页面头部 =====
st.markdown("""
<div style="text-align:center;padding:20px 0 0 0;">
    <h1 style="font-family:'KaiTi','STKaiti','楷体',serif;color:#1a1a2e;margin-bottom:4px;
        font-size:2.2rem;letter-spacing:4px;font-weight:400;">西湖文脉图志</h1>
    <p style="color:#8e8e9a;font-size:14px;letter-spacing:3px;font-weight:300;">
        杭州文化遗产数字化平台
    </p>
</div>
""", unsafe_allow_html=True)

# ===== 用户登录 / 注册 =====
if st.session_state.current_user is None:
    st.markdown("---")
    col_auth, col_spacer, _ = st.columns([1, 0.5, 2])
    with col_auth:
        if st.session_state.auth_mode == "login":
            st.markdown("""
                <div style="font-size:18px;font-weight:500;color:#1a1a2e;margin-bottom:16px;letter-spacing:1px;">
                登录
                </div>""", unsafe_allow_html=True)
            with st.form("login_form"):
                lu = st.text_input("用户名", placeholder="用户名", key="login_user", label_visibility="collapsed")
                lp = st.text_input("密码", type="password", placeholder="密码", key="login_pw", label_visibility="collapsed")
                c1, c2 = st.columns(2)
                with c1:
                    if st.form_submit_button("登录", use_container_width=True):
                        if not lu:
                            st.error("请输入用户名")
                        elif not lp:
                            st.error("请输入密码")
                        else:
                            ok, msg = login_user(lu, lp)
                            if ok:
                                st.session_state.current_user = lu
                                st.session_state.spots = load_spots()
                                st.success(f"欢迎，{lu}")
                                st.rerun()
                            else:
                                st.error(msg)
                with c2:
                    if st.form_submit_button("注册", use_container_width=True):
                        st.session_state.auth_mode = "register"
                        st.rerun()
        else:
            st.markdown("""
                <div style="font-size:18px;font-weight:500;color:#1a1a2e;margin-bottom:16px;letter-spacing:1px;">
                注册
                </div>""", unsafe_allow_html=True)
            with st.form("register_form"):
                ru = st.text_input("用户名", placeholder="用户名", key="reg_user", label_visibility="collapsed")
                rp = st.text_input("密码", type="password", placeholder="密码", key="reg_pw", label_visibility="collapsed")
                rp2 = st.text_input("确认密码", type="password", placeholder="再次输入密码", key="reg_pw2", label_visibility="collapsed")
                c1, c2 = st.columns(2)
                with c1:
                    if st.form_submit_button("注册", use_container_width=True):
                        if not ru:
                            st.error("请输入用户名")
                        elif not rp:
                            st.error("请输入密码")
                        elif rp != rp2:
                            st.error("两次密码不一致")
                        else:
                            ok, msg = register_user(ru, rp)
                            if ok:
                                st.session_state.current_user = ru
                                st.session_state.spots = []
                                save_spots()
                                st.success(f"注册成功，欢迎 {ru}")
                                st.rerun()
                            else:
                                st.error(msg)
                with c2:
                    if st.form_submit_button("返回登录", use_container_width=True):
                        st.session_state.auth_mode = "login"
                        st.rerun()
    st.stop()

# ===== 已登录：显示用户名 & 登出 =====
with st.sidebar:
    st.markdown(
        f"""<div style="display:flex;align-items:center;justify-content:space-between;
        background:#1a1a2e;color:#c9a96e;padding:10px 14px;border-radius:8px;font-size:13px;
        margin-bottom:8px;letter-spacing:1px;">
        <span>▸ {st.session_state.current_user}</span>
        <span style="font-size:10px;color:#8e8e9a;">已登录</span>
        </div>""",
        unsafe_allow_html=True)
    if st.button("退出登录", use_container_width=True, type="secondary"):
        st.session_state.current_user = None
        st.session_state.spots = []
        st.session_state.highlight_index = None
        st.session_state.captured_coords = None
        st.rerun()
    # 项目说明
    if "show_about" not in st.session_state:
        st.session_state.show_about = False
    if st.button("项目说明", use_container_width=True, type="secondary"):
        st.session_state.show_about = not st.session_state.show_about
        st.rerun()
    st.divider()

# ===== 项目说明页 =====
if st.session_state.show_about:
    st.markdown("""
    <div style="text-align:center;padding:24px 0 10px 0;">
        <span style="font-size:24px;font-weight:600;color:#1a1a2e;letter-spacing:4px;">西湖文脉图志</span>
        <p style="color:#8e8e9a;font-size:13px;margin-top:4px;">AI 驱动的杭州文化遗产数字化平台</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### ① 项目介绍")
    st.markdown("""
**西湖文脉图志**是一款 AI 驱动的杭州文化遗产数字化平台。以西湖周边人文景点为切入点，
构建了集**交互式地图可视化**、**AI 智能文化导览**、**多用户协同管理**于一体的数字人文工具。

平台采用 Streamlit 全栈框架，前端通过自定义 HTML/CSS/JavaScript 实现高交互性地图组件
（支持缩放、平移、坐标选址），后端通过 Python 对接 DeepSeek V4 大语言模型 API 提供
智能问答能力。数据层采用文件型 JSON 存储，实现多用户数据隔离。

**设计思路**：地图优先（高精度底图+可视化标注）、文化纵深（13 景点结构化文化数据库）、
AI 赋能（大模型驱动的深度文化导览）、用户自主（独立账号体系+个人笔记管理）。
""")

    st.markdown("---")

    st.markdown("### ② 功能介绍")

    features = [
        ("🗺️ 交互式地图",
         "以高精度西湖地图为底图，支持**滚轮缩放**与**拖拽平移**。鼠标悬停实时显示坐标，"
         "点击图片任意位置即可选址添加标注。已有地点以红色圆点+编号标记在地图上，"
         "高亮地点呈金色脉动光晕。支持通过侧边栏搜索精准定位。"),
        ("📍 地点管理",
         "完整的**CRUD 操作**：添加（地图点击选址或手动输入坐标）、编辑（名称、坐标、笔记、图片）、"
         "删除。每个地点可上传实拍图片，支持自定义笔记记录个人见闻与思考。"),
        ("🤖 AI 文脉对话",
         "基于 **DeepSeek V4 大语言模型**，为每个地点提供智能文化导览。用户可选择任意已添加地点，"
         "通过自然语言对话获取诗词鉴赏、历史解读、传说讲述、名人介绍等服务。"
         "内置 13 个经典西湖景点的结构化文化数据库（诗词、传说、历史时间线），"
         "API 不可用时自动回退到本地资料库。支持快捷提问与自由输入。"),
        ("👤 多用户体系",
         "完整的**注册/登录**系统，密码 SHA-256 哈希加密存储。每位用户拥有独立的数据文件，"
         "标注、笔记、图片相互隔离。支持随时登出与重新登录。"),
        ("🔍 智能搜索",
         "侧边栏输入关键词即可**模糊搜索**所有地点名称，搜索结果展示坐标信息。"
         "点击定位按钮，地图高亮标记自动切换至对应地点。"),
        ("📝 个人笔记",
         "每个地点可添加**个性化笔记**，记录游览心得、研究资料或个人感悟。"
         "笔记以优雅的斜体样式呈现在地点卡片中，与坐标、图片协同展示。"),
        ("📋 项目说明",
         "内置完整的项目说明文档，包含项目介绍、功能说明、AI 使用披露、"
         "人员分工与 GitHub 仓库链接，方便评审与展示。"),
    ]

    for title, desc in features:
        st.markdown(
            f'<div style="background:#faf8f5;border-left:3px solid #c9a96e;'
            f'padding:10px 14px;margin:10px 0;border-radius:0 6px 6px 0;">'
            f'<span style="font-size:15px;font-weight:600;color:#1a1a2e;">{title}</span><br>'
            f'<span style="color:#555;font-size:13px;line-height:1.7;">{desc}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    st.markdown("### ③ AI 使用披露")

    st.markdown("**第一层：项目中讨论的 AI（文化遗产主题）**")
    st.markdown("""
本项目以 AI 与文化遗产保护为核心主题。接入 DeepSeek V4 大语言模型，为每个景点提供
诗词鉴赏、历史解读、传说讲述、名人介绍等智能导览服务。手工整理了 13 个西湖景点的
诗词、传说、历史时间线、相关名人、游览建议等结构化数据，作为 AI 对话的知识背景。
设计了专门的 System Prompt，引导 AI 以文化导览专家的角色进行回答。
""")

    st.markdown("**第二层：制作网页所借助的 AI**")
    st.markdown("""
| 环节 | AI 工具 | 作用 |
|------|---------|------|
| 框架搭建 | Claude | 生成 Streamlit 项目骨架，设计页面布局与导航结构 |
| 地图组件 | Claude | 编写自定义 HTML/CSS/JS 交互地图代码 |
| API 对接 | Claude | 调试 DeepSeek API 调用链路，解决编码与认证问题 |
| 数据整理 | Claude | 协助整理 13 个景点的文化资料，生成结构化 JSON |
| UI 优化 | Claude | 设计高级感配色方案、卡片样式、排版美化 |
| 用户系统 | Claude | 实现多用户登录注册、数据隔离的完整用户体系 |
| 调试修复 | Claude | 诊断并修复 Python 3.13 环境下 HTTP 库的编码兼容问题 |

**重要声明**：AI 工具在本项目中作为开发辅助使用，所有核心创意、设计方案、
文化内容的最终审核均由团队成员完成。AI 生成的代码经过人工审查和测试后方才整合入项目。
""")

    st.markdown("---")

    st.markdown("### ④ 人员分工")
    members = [
        ("辛泽宇", "整体框架搭建、系统设计",
         ["整体框架搭建：确定 Streamlit 全栈技术路线，设计页面布局与模块划分",
          "系统架构设计：规划多用户数据隔离方案、API 调用链路、数据存储结构",
          "项目进度管理：统筹各成员任务分配，把控开发节奏与里程碑",
          "代码审查与集成：审核各模块代码质量，整合功能组件为完整产品"]),
        ("郑悦霖", "项目开发、功能实现",
         ["交互式地图组件开发：实现缩放、平移、悬停坐标显示、点击选址等功能",
          "景点管理模块：实现添加、编辑、删除景点的完整 CRUD 操作",
          "AI 对话功能集成：对接 DeepSeek API，实现文化导览智能问答",
          "UI 细节优化：高级感配色方案、卡片设计、响应式排版",
          "编码兼容性调试：解决 Python 3.13 环境下 HTTP 库的编码问题"]),
        ("黄麒文", "素材采集、项目优化、展示",
         ["外部素材收集：西湖地图图片、景点实拍照片、文化参考资料",
          "文化数据整理：协助整理诗词、传说、历史时间线等结构化文化数据",
          "整体项目优化：测试各功能模块，发现并报告问题，提出改进建议",
          "Pre 展示准备：准备现场展示材料与演讲内容"]),
        ("卢俞辰", "素材采集、项目优化、展示",
         ["外部素材收集：补充景点资料，搜集相关文化文献与多媒体素材",
          "文化内容审核：校验文化数据的准确性与完整性",
          "整体项目优化：用户体验测试，提出界面与交互改进方案",
          "Pre 展示准备：协助准备展示材料，参与现场展示与答辩"]),
    ]
    for name, role, tasks in members:
        st.markdown(f"**{name}** — *{role}*")
        for t in tasks:
            st.markdown(f"- {t}")

    st.markdown("---")

    st.markdown("### ⑤ GitHub 仓库")
    st.markdown("""
项目完整源码：https://github.com/zhengyl848/7-26-AI-creation.git

包含所有代码、数据与文化资料，欢迎访问与 Star。
""")

    st.markdown("---")
    st.caption("清华大学无穹书院 · 实践支队 · 2026")
    st.markdown("---")

    with st.sidebar:
        if st.button("关闭说明", use_container_width=True):
            st.session_state.show_about = False
            st.rerun()

# ===== Tab 导航 =====
tab1, tab2 = st.tabs(["地图", "文脉对话"])

# ==================== TAB 1: 景点地图 ====================
with tab1:
    # ===== 侧边栏 =====
    with st.sidebar:
        st.markdown("#### 搜索")
        sq = st.text_input("搜索地点", placeholder="输入名称关键字...", label_visibility="collapsed",
                           value=st.session_state.search_query)
        if sq != st.session_state.search_query:
            st.session_state.search_query = sq

        if st.session_state.search_query:
            q = st.session_state.search_query.lower()
            results = [(i, s) for i, s in enumerate(st.session_state.spots) if q in s["name"].lower()]
            st.session_state.search_results = results
            if not results:
                st.warning("未找到匹配的地点")
            else:
                st.success(f"找到 {len(results)} 个结果")
                for idx, (si, spot) in enumerate(results):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.write(f"**{spot['name']}** ({spot['x']}, {spot['y']})")
                    with c2:
                        if st.button("📍", key=f"locate_{si}"):
                            st.session_state.highlight_index = si
                            st.rerun()
        else:
            st.session_state.search_results = []
            if st.button("清除选中", use_container_width=True):
                st.session_state.highlight_index = None
                st.rerun()

        st.divider()
        st.markdown("#### 管理")

        with st.expander("+ 添加地点", expanded=st.session_state.captured_coords is not None):
            coords = st.session_state.captured_coords
            if coords:
                st.markdown(
                    f"""<div style="background:#d4edda;border:1px solid #c3e6cb;
                    border-radius:8px;padding:10px 14px;margin-bottom:12px;">
                    ✅ 已选址：<b>X={coords[0]:.1f}, Y={coords[1]:.1f}</b></div>""",
                    unsafe_allow_html=True)
                if st.button("❌ 清除选址", use_container_width=True):
                    st.session_state.captured_coords = None
                    st.rerun()
            else:
                st.info("💡 在地图上**单击**选址，或直接输入坐标")

            with st.form("add_spot_form"):
                new_name = st.text_input("名称", placeholder="例如：六和塔")
                c1, c2 = st.columns(2)
                with c1:
                    mx = st.number_input("X坐标", value=float(coords[0]) if coords else 50.0,
                                         min_value=0.0, max_value=100.0, step=0.5)
                with c2:
                    my = st.number_input("Y坐标", value=float(coords[1]) if coords else 50.0,
                                         min_value=0.0, max_value=100.0, step=0.5,
                                         help=f"0=最上边, {MAP_Y_MAX}=最下边")
                new_desc = st.text_area("📝 笔记", placeholder="记录你的想法、见闻...", height=100)
                new_image = st.file_uploader("上传景点图片", type=["png", "jpg", "jpeg"], key="add_image")

                if st.form_submit_button("确认添加", use_container_width=True):
                    if not new_name:
                        st.error("请输入名称")
                    else:
                        imgf = ""
                        if new_image:
                            imgf = f"spot_{int(time.time())}.png"
                            with open(os.path.join(IMAGES_DIR, imgf), "wb") as f:
                                f.write(new_image.getbuffer())
                        st.session_state.spots.append({
                            "name": new_name, "x": round(mx, 1), "y": round(my, 1),
                            "description": new_desc or "", "image_file": imgf})
                        save_spots()
                        st.session_state.captured_coords = None
                        st.success(f"已添加：{new_name}")
                        st.rerun()

        st.divider()
        st.markdown("#### 地点列表")
        if not st.session_state.spots:
            st.caption("暂无地点")

        for i, spot in enumerate(st.session_state.spots):
            with st.expander(spot["name"]):
                st.write(f"📍 坐标: ({spot['x']}, {spot['y']})")
                desc = spot["description"]
                st.write(desc[:80] + "..." if len(desc) > 80 else desc)
                img_file = spot.get("image_file", "")
                if img_file and os.path.exists(os.path.join(IMAGES_DIR, img_file)):
                    st.image(os.path.join(IMAGES_DIR, img_file), caption="当前图片", use_container_width=True)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("编辑", key=f"edit_{i}"):
                        st.session_state.edit_index = i
                        st.rerun()
                with c2:
                    if st.button("删除", key=f"delete_{i}"):
                        if spot.get("image_file") and os.path.exists(os.path.join(IMAGES_DIR, spot["image_file"])):
                            os.remove(os.path.join(IMAGES_DIR, spot["image_file"]))
                        st.session_state.spots.pop(i)
                        save_spots()
                        st.success(f"已删除：{spot['name']}")
                        st.rerun()

    # ===== 编辑地点 =====
    if st.session_state.edit_index is not None:
        idx = st.session_state.edit_index
        spot = st.session_state.spots[idx]
        st.header(f"✏️ 编辑地点：{spot['name']}")
        with st.form("edit_spot_form"):
            ename = st.text_input("名称", value=spot["name"])
            c1, c2 = st.columns(2)
            with c1:
                ex = st.number_input("X坐标", value=float(spot["x"]), min_value=0.0, max_value=100.0, step=0.5)
            with c2:
                ey = st.number_input("Y坐标", value=float(spot["y"]), min_value=0.0, max_value=100.0, step=0.5)
            edesc = st.text_area("📝 笔记", value=spot["description"], height=150)
            cur_img = spot.get("image_file", "")
            if cur_img and os.path.exists(os.path.join(IMAGES_DIR, cur_img)):
                st.image(os.path.join(IMAGES_DIR, cur_img), caption="当前图片", use_container_width=True)
            eimg = st.file_uploader("上传新图片（留空则保留原图）", type=["png", "jpg", "jpeg"], key="edit_image")
            c1, c2 = st.columns(2)
            with c1:
                if st.form_submit_button("💾 保存", use_container_width=True):
                    imgf = cur_img
                    if eimg:
                        if cur_img and os.path.exists(os.path.join(IMAGES_DIR, cur_img)):
                            os.remove(os.path.join(IMAGES_DIR, cur_img))
                        imgf = f"spot_{int(time.time())}.png"
                        with open(os.path.join(IMAGES_DIR, imgf), "wb") as f:
                            f.write(eimg.getbuffer())
                    st.session_state.spots[idx] = {"name": ename, "x": ex, "y": ey,
                                                   "description": edesc, "image_file": imgf}
                    save_spots()
                    st.session_state.edit_index = None
                    st.success(f"已保存：{ename}")
                    st.rerun()
            with c2:
                if st.form_submit_button("❌ 取消", use_container_width=True):
                    st.session_state.edit_index = None
                    st.rerun()
        st.stop()

    # ===== 构建交互式地图 HTML =====
    def build_map_html(img_b64, y_max, spots_list, captured_xy, hl_idx):
        spots_json = json.dumps([
            {"x": s["x"], "y": s["y"], "name": s["name"], "index": i, "highlighted": (i == hl_idx)}
            for i, s in enumerate(spots_list)], ensure_ascii=False)
        cap_json = json.dumps(list(captured_xy), ensure_ascii=False) if captured_xy else "null"
        return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#f5f0e8;font-family:system-ui,sans-serif;overflow:hidden}}
#container{{width:100%;height:630px;position:relative;overflow:hidden;background:#f5f0e8;border-radius:8px;border:1px solid #e0dbd0;}}
#viewport{{position:absolute;top:30px;left:30px;transform-origin:0 0}}
#map-img{{display:block;width:100%;height:auto;user-select:none;-webkit-user-drag:none}}
.pin{{position:absolute;transform:translate(-50%,-50%);cursor:pointer;z-index:10;filter:drop-shadow(0 1px 2px rgba(0,0,0,0.5))}}
.pin .dot{{display:block;width:16px;height:16px;background:#e74c3c;border:2.5px solid #fff;border-radius:50%;transition:all .15s}}
.pin.hl .dot{{background:#f39c12;width:24px;height:24px;box-shadow:0 0 14px rgba(243,156,18,0.8)}}
.pin .lbl{{display:block;text-align:center;color:#fff;font-size:10px;font-weight:bold;margin-top:-14px;text-shadow:0 1px 2px #000}}
.clk{{position:absolute;transform:translate(-50%,-50%);z-index:20;pointer-events:none}}
.clk::after{{content:'';display:block;width:26px;height:26px;border:3px solid #e74c3c;border-radius:50%;background:rgba(231,76,60,0.3);animation:pulse 1s ease-out infinite}}
@keyframes pulse{{0%{{transform:scale(0.5);opacity:1}}100%{{transform:scale(1.6);opacity:0}}}}
.badge{{position:absolute;bottom:12px;right:12px;background:rgba(0,0,0,0.55);color:#fff;padding:5px 12px;border-radius:6px;font-size:12px;pointer-events:none;z-index:30}}
.coords{{position:absolute;top:8px;left:8px;background:rgba(0,0,0,0.6);color:#fff;padding:3px 10px;border-radius:4px;font-size:12px;pointer-events:none;z-index:30;display:none}}
</style></head><body>
<div id="container">
    <div id="viewport" style="cursor:crosshair">
        <img id="map-img" src="data:image/jpeg;base64,{img_b64}" draggable="false">
        <div id="pins-layer"></div><div id="clk-layer"></div>
    </div>
    <div class="coords" id="coords-display"></div>
    <div class="badge" id="zoom-badge">🔍 100%</div>
</div>
<script>
(function(){{
    var Y_MAX={y_max},spots={spots_json},captured={cap_json};
    var zoom=1,panX=0,panY=0,isPanning=false,hasMoved=false,psX,psY;
    var container=document.getElementById('container'),viewport=document.getElementById('viewport');
    var img=document.getElementById('map-img'),pinsLayer=document.getElementById('pins-layer');
    var clkLayer=document.getElementById('clk-layer'),zoomBadge=document.getElementById('zoom-badge');
    var coordsDisplay=document.getElementById('coords-display');
    function updateView(){{viewport.style.transform='translate('+panX+'px,'+panY+'px) scale('+zoom+')';zoomBadge.textContent='🔍 '+Math.round(zoom*100)+'%';}}
    function imgCoords(e){{var r=img.getBoundingClientRect();return{{x:Math.round(Math.max(0,Math.min(100,(e.clientX-r.left)/r.width*100))*10)/10,y:Math.round(Math.max(0,Math.min(Y_MAX,(e.clientY-r.top)/r.height*Y_MAX))*10)/10}};}}
    img.addEventListener('click',function(e){{if(hasMoved){{hasMoved=false;return;}}var coords=imgCoords(e);var ir=img.getBoundingClientRect();for(var i=0;i<spots.length;i++){{var sx=ir.left+(spots[i].x/100)*ir.width,sy=ir.top+(spots[i].y/Y_MAX)*ir.height;if(Math.hypot(e.clientX-sx,e.clientY-sy)<22){{window.top.location.search='?hl='+spots[i].index;return;}}}}window.top.location.search='?mx='+coords.x+'&my='+coords.y;}});
    img.addEventListener('mousemove',function(e){{if(isPanning)return;var c=imgCoords(e);coordsDisplay.style.display='block';coordsDisplay.textContent='X='+c.x+'  Y='+c.y;coordsDisplay.style.left=(e.clientX-container.getBoundingClientRect().left+18)+'px';coordsDisplay.style.top=(e.clientY-container.getBoundingClientRect().top-28)+'px';}});
    img.addEventListener('mouseleave',function(){{coordsDisplay.style.display='none';}});
    container.addEventListener('wheel',function(e){{e.preventDefault();var oldZ=zoom;zoom=Math.max(0.2,Math.min(6,zoom*(e.deltaY>0?0.88:1.13)));var rect=container.getBoundingClientRect(),cx=e.clientX-rect.left,cy=e.clientY-rect.top;panX=cx-(cx-panX)*(zoom/oldZ);panY=cy-(cy-panY)*(zoom/oldZ);updateView();}},{{passive:false}});
    img.addEventListener('mousedown',function(e){{isPanning=true;hasMoved=false;psX=e.clientX-panX;psY=e.clientY-panY;container.style.cursor='grabbing';e.preventDefault();}});
    window.addEventListener('mousemove',function(e){{if(!isPanning)return;if(Math.abs(e.clientX-psX-panX)>2||Math.abs(e.clientY-psY-panY)>2)hasMoved=true;panX=e.clientX-psX;panY=e.clientY-psY;updateView();}});
    window.addEventListener('mouseup',function(){{isPanning=false;container.style.cursor='crosshair';}});
    function renderPins(){{pinsLayer.innerHTML='';spots.forEach(function(s){{var pin=document.createElement('div');pin.className='pin'+(s.highlighted?' hl':'');pin.style.left=(s.x/100*100)+'%';pin.style.top=(s.y/Y_MAX*100)+'%';pin.title=s.name;var dot=document.createElement('span');dot.className='dot';var lbl=document.createElement('span');lbl.className='lbl';lbl.textContent=s.index+1;pin.appendChild(dot);pin.appendChild(lbl);pin.addEventListener('click',function(ev){{ev.stopPropagation();hasMoved=false;window.top.location.search='?hl='+s.index;}});pinsLayer.appendChild(pin);}});}}
    function renderClk(){{clkLayer.innerHTML='';if(captured){{var dot=document.createElement('div');dot.className='clk';dot.style.left=(captured[0]/100*100)+'%';dot.style.top=(captured[1]/Y_MAX*100)+'%';clkLayer.appendChild(dot);}}}}
    renderPins();renderClk();
}})();
</script></body></html>"""

    # ===== 地图显示 =====
    if MAP_IMG_B64:
        components.html(
            build_map_html(MAP_IMG_B64, MAP_Y_MAX, st.session_state.spots,
                           st.session_state.captured_coords, st.session_state.highlight_index),
            height=645)
    else:
        st.warning("未找到地图图片 another.jpg")
    st.caption("滚轮缩放 · 拖拽平移 · 点击选址 · 悬停显示坐标")

    # ===== 地点卡片 =====
    if st.session_state.spots:
        st.markdown("---")
        st.markdown("#### 地点")
        cols = st.columns(3)

        def create_spot_card(spot, idx):
            img_file = spot.get("image_file", "")
            has_image = img_file and os.path.exists(os.path.join(IMAGES_DIR, img_file))
            if has_image:
                b64 = get_image_base64(os.path.join(IMAGES_DIR, img_file))
                img_block = (f'<div style="width:100%;height:180px;overflow:hidden;">'
                             f'<img src="data:image/png;base64,{b64}" style="width:100%;height:100%;object-fit:cover;"></div>') if b64 else ""
            else:
                hues = [210, 15, 120, 45, 180, 330, 90, 270, 30, 150, 0, 60, 300]
                h = hues[idx % len(hues)]
                img_block = (f'<div style="width:100%;aspect-ratio:16/10;'
                             f'background:linear-gradient(160deg,hsl({h},25%,25%),hsl({(h+30)%360},20%,15%));'
                             f'display:flex;align-items:center;justify-content:center;">'
                             f'<span style="font-size:40px;opacity:0.5;">—</span></div>')
            hl = st.session_state.highlight_index
            border_color = "#c9a96e" if idx == hl else "#e8e4dc"
            extra = "box-shadow:0 2px 20px rgba(201,169,110,0.2);" if idx == hl else ""
            badge = ('<span style="display:inline-block;background:#c9a96e;color:#fff;font-size:10px;padding:1px 7px;'
                     'border-radius:3px;margin-left:6px;font-weight:400;">选中</span>' if idx == hl else "")
            culture_info = CULTURE_DATA.get(spot['name'], {})
            culture_badge = ('<span style="color:#c9a96e;font-size:10px;margin-left:6px;font-weight:400;">文脉</span>' if culture_info else "")
            desc = spot["description"]
            has_note = bool(desc and desc.strip())
            note_html = ""
            if has_note:
                short_note = desc[:120] + "…" if len(desc) > 120 else desc
                note_html = (f'<p style="color:#6b6b76;font-size:12px;line-height:1.7;margin:0 0 10px 0;'
                             f'font-style:italic;">{short_note}</p>')
            s_name = spot['name']
            s_x = spot['x']
            s_y = spot['y']
            img_icon = "📷" if has_image else "—"
            return (
                '<div style="border:1px solid ' + border_color + ';border-radius:6px;margin-bottom:18px;'
                'background:#fcfbf9;' + extra + 'transition:all 0.2s ease;overflow:hidden;">'
                + img_block +
                '<div style="padding:12px 14px 14px 14px;">'
                '<div style="display:flex;align-items:baseline;justify-content:space-between;margin-bottom:4px;">'
                '<span style="color:#1a1a2e;font-size:14px;font-weight:500;letter-spacing:0.5px;">'
                + s_name + badge + culture_badge + '</span>'
                '<span style="color:#b0ad9f;font-size:10px;font-weight:400;">No. ' + str(idx+1) + '</span>'
                '</div>'
                + note_html +
                '<div style="display:flex;justify-content:space-between;align-items:center;'
                'border-top:1px solid #ede9e2;padding-top:8px;">'
                '<span style="color:#b0ad9f;font-size:10px;">(' + str(s_x) + ', ' + str(s_y) + ')</span>'
                '<span style="color:#c9a96e;font-size:10px;">' + img_icon + '</span>'
                '</div></div></div>'
            )

        for i, spot in enumerate(st.session_state.spots):
            with cols[i % 3]:
                st.markdown(create_spot_card(spot, i), unsafe_allow_html=True)

    # ===== 页脚 =====
    st.markdown("---")
    st.markdown("""<div style="text-align:center;padding:15px;">
        <p style="font-size:12px;color:#b0ad9f;letter-spacing:1px;">西湖文脉图志</p>
    </div>""", unsafe_allow_html=True)

# ==================== TAB 2: AI 文化对话 ====================
with tab2:
    st.markdown("""
    <div style="background:#1a1a2e;padding:20px 24px;border-radius:6px;color:#c9a96e;margin-bottom:24px;">
        <span style="font-size:16px;letter-spacing:2px;">文脉对话</span>
        <span style="color:#8e8e9a;font-size:13px;margin-left:12px;font-weight:300;">选择地点，与 AI 探索其文化底蕴</span>
    </div>""", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.markdown("#### 选择地点")
        spot_names = [s['name'] for s in st.session_state.spots]
        if spot_names:
            sel_spot = st.selectbox("选择地点", spot_names, key="chat_spot_select", label_visibility="collapsed")

            if sel_spot:
                cinfo = CULTURE_DATA.get(sel_spot, {})
                if cinfo:
                    with st.expander("文化资料", expanded=False):
                        st.markdown("**时间线**")
                        for era, event in cinfo.get('timeline', {}).items():
                            st.markdown(f"  - **{era}** {event}")
                        if cinfo.get('poems'):
                            st.markdown("\n**诗词**")
                            for poem in cinfo['poems'][:2]:
                                st.markdown(f"  > {poem}")
                        if cinfo.get('legends'):
                            st.markdown("\n**传说**")
                            for legend in cinfo['legends'][:2]:
                                st.markdown(f"  - {legend}")

            st.markdown("#### 快捷提问")
            for q in ["这里有什么历史？", "相关诗词有哪些？", "有什么传说故事？", "有哪些名人？", "游览建议？"]:
                btn_key = f"quick_{q.replace(' ', '_')[:20]}"
                if st.button(q, key=btn_key, use_container_width=True):
                    st.session_state.chat_messages.setdefault(sel_spot, [])
                    st.session_state.chat_messages[sel_spot].append({"role": "user", "content": q})
                    with st.spinner("…"):
                        response = generate_ai_response(sel_spot, q, CULTURE_DATA)
                    st.session_state.chat_messages[sel_spot].append({"role": "assistant", "content": response})
                    st.rerun()
        else:
            st.warning("暂无地点数据")

    with col_right:
        sel_spot = None
        if spot_names:
            sel_spot = st.session_state.get("chat_spot_select", spot_names[0] if spot_names else None)

        if sel_spot:
            st.markdown(f"#### 「{sel_spot}」")

            if sel_spot not in st.session_state.chat_messages:
                st.session_state.chat_messages[sel_spot] = [{
                    "role": "assistant",
                    "content": f"你好，我是文脉助手。很荣幸为你介绍「{sel_spot}」。\n\n你可以问我关于这里的历史、诗词、传说、名人或游览建议。"}]

            for msg in st.session_state.chat_messages.get(sel_spot, []):
                if msg['role'] == 'user':
                    st.markdown(f"""<div style="background:#f0ede6;padding:10px 14px;border-radius:4px;
                        margin-bottom:8px;margin-left:15%;"><span style="color:#1a1a2e;font-size:13px;">{msg['content']}</span></div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div style="padding:10px 14px;border-radius:4px;
                        margin-bottom:8px;margin-right:15%;">
                        <span style="color:#4a4a55;font-size:13px;white-space:pre-wrap;">{msg['content']}</span></div>""",
                                unsafe_allow_html=True)

            chat_input_key = f"chat_input_{sel_spot}"
            if chat_input_key not in st.session_state:
                st.session_state[chat_input_key] = ""
            user_input = st.text_input("输入问题", key=chat_input_key,
                                       placeholder="例如：这里有什么历史？", label_visibility="collapsed")

            c1, c2 = st.columns([4, 1])
            with c1:
                if st.button("发送", key="send_chat", use_container_width=True):
                    if user_input:
                        st.session_state.chat_messages[sel_spot].append({"role": "user", "content": user_input})
                        with st.spinner("…"):
                            response = generate_ai_response(sel_spot, user_input, CULTURE_DATA)
                        st.session_state.chat_messages[sel_spot].append({"role": "assistant", "content": response})
                        st.rerun()
            with c2:
                if st.button("清空", key="clear_chat", use_container_width=True):
                    st.session_state.chat_messages[sel_spot] = [{
                        "role": "assistant",
                        "content": f"对话已清空。有什么想了解关于「{sel_spot}」的吗？"}]
                    st.rerun()
        else:
            st.info("请先选择一个地点")