import streamlit as st
from google import genai

# --- 1. 網頁介面與風格設定 ---
# 增加 initial_sidebar_state="expanded" 確保側邊欄預設開啟
st.set_page_config(page_title="AI Sleep Guardian", page_icon="🌙", layout="wide", initial_sidebar_state="expanded")

# 透過 CSS 強制加寬側邊欄，讓長標題能完整顯示不換行
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background-color: #00d4ff;
        color: black;
        font-weight: bold;
    }
    /* 在這裡設定側邊欄的寬度為 400px */
    [data-testid="stSidebar"] {
        min-width: 400px !important;
        max-width: 400px !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌙 AI Sleep Guardian：大學生作息優化助理")
st.markdown("將靜態衛教升級為動態干預，協助你在學業高壓與健康間取得平衡。")

# --- 2. 側邊欄：深度個人化選項 ---
st.sidebar.header("🛡️ 個人化健康參數")

# API Key 設定 (優先從 secrets 讀取)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    api_key = st.sidebar.text_input("輸入 Gemini API Key", type="password")

# 個人基本資料
col1, col2 = st.sidebar.columns(2)
with col1:
    age = st.number_input("年齡", min_value=15, max_value=60, value=18)
with col2:
    major = st.text_input("科系/領域", placeholder="醫學資訊 / 智慧資安")

# 生理時鐘與體質
chronotype = st.sidebar.select_slider(
    "生理時鐘類型",
    options=["極端早起鳥", "一般作息", "暗夜貓子"],
    value="一般作息"
)

caffeine_limit = st.sidebar.selectbox(
    "咖啡因敏感度",
    ["不喝咖啡", "喝完照樣秒睡", "正常代謝 (下午喝沒事)", "高度敏感 (中午後喝會失眠)"],
    index=2
)

# 今日活動狀態
st.sidebar.divider()
st.sidebar.header("動態狀況偵測 (情境感知)")
sleep_hours = st.sidebar.slider("昨晚睡眠時數 (偵測睡眠負債)", 0.0, 12.0, 4.0, 0.5)
stress_level = st.sidebar.slider("今日心理壓力指數 (1-10)", 1, 10, 8)
exercise = st.sidebar.selectbox("今日運動強度", ["無", "輕度 (散步)", "中度 (慢跑/球類)", "重度 (健身/高強度)"])

# 明日行程輸入
st.sidebar.subheader("📅 明日最早的挑戰紀錄")
next_event_detail = st.sidebar.text_area(
    "具體行程描述 (如：早八期末考、專案發表)", 
    placeholder="例如：早上 08:30 有資安實務期末考，需要高強度專注力...",
    height=100
)

# --- 3. 核心邏輯：AI 反饋生成 ---
if st.button("🚀 生成動態睡眠處方 (AI 干預)"):
    if not api_key:
        st.warning("請先設定 API Key 喔！")
    elif not next_event_detail:
        st.error("請輸入明日挑戰內容，以便 AI 進行情境感知分析。")
    else:
        with st.spinner("AI 睡眠教練正在根據醫學實證進行推論..."):
            try:
                client = genai.Client(api_key=api_key)
                
                prompt = f"""
                你是一位專門服務大學生的「AI 睡眠教練」，具備睡眠醫學與醫學資訊背景。
                請針對以下這位 {age} 歲、就讀 {major} 的學生提供建議。
                
                【使用者情境資料】
                - 時型：{chronotype} | 咖啡因：{caffeine_limit}
                - 現狀：昨晚僅睡 {sleep_hours} 小時，今日壓力等級 {stress_level}/10。
                - 明日挑戰：{next_event_detail}
                
                請根據企劃書設計目標，提供以下四個維度的建議（請使用溫暖且具專業感的語氣）：
                
                1. **科學熬夜與動態睡眠處方**：
                   針對明日的挑戰，計算出今晚最遲的入睡時間，以及今天是否建議進行 Power Nap（小睡）。
                
                2. **咖啡因攝取策略 (針對體質)**：
                   根據其咖啡因敏感度「{caffeine_limit}」，提供精準的飲用截止時間。若選擇不喝咖啡，請改為推薦「提神替代方案」。
                
                3. **死線衝刺模式：腦力斷電儀式**：
                   針對其壓力等級，設計一個 5-10 分鐘的睡前儀式（如藍光管理或特定呼吸法），協助其交感神經由亢奮轉為放鬆。
                
                4. **教練的鼓勵**：
                   結合其 {major} 的背景給予一句具備共感的打氣。
                """

                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=prompt
                )

                st.success("✅ 已根據情境生成動態處方")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"運算過程發生錯誤：{e}")