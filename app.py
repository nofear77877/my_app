import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体
import matplotlib.font_manager as fm
try:
    font_path = fm.findfont(fm.FontProperties(family=['SimHei', 'WenQuanYi Micro Hei', 'Heiti TC']))
    plt.rcParams["font.family"] = fm.FontProperties(fname=font_path).get_name()
except:
    plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False

# 页面配置
st.set_page_config(
    page_title="企业数字化转型指数查询",
    page_icon="📊",
    layout="wide",
)

# 标题
st.title("📈 企业数字化转型指数查询系统")
st.markdown("输入股票代码，查询企业数字化转型综合指数及技术应用情况")


# 缓存数据加载
@st.cache(allow_output_mutation=True)
def load_data():
    # 加载数据
    data = pd.read_csv('C:/test/text.csv')

    # 数据预处理
    data['股票代码'] = data['股票代码'].astype(int)
    industry_map = {
        10: "电子设备", 15: "机械设备", 40: "建材",
        42: "化工", 50: "金融", 60: "信息技术",
        70: "医药生物", 80: "食品饮料"
    }
    data['行业'] = data['股票代码'].apply(lambda x: industry_map.get(x // 10, "其他"))
    return data


# 加载数据
df = load_data()

# 侧边栏筛选
with st.sidebar:
    st.header("🔍 筛选选项")
    industries = ["全部"] + sorted(df['行业'].unique().tolist())
    selected_industry = st.selectbox("选择行业", industries)
    min_idx, max_idx = df['数字化转型综合指数'].min(), df['数字化转型综合指数'].max()
    # 将 numpy.float64 类型转换为 float 类型
    min_idx = float(min_idx)
    max_idx = float(max_idx)
    index_range = st.slider("指数范围", min_idx, max_idx, (min_idx, max_idx))
    sort_by = st.selectbox("排序方式", [
        "综合指数 (降序)", "综合指数 (升序)",
        "总词频数 (降序)", "总词频数 (升序)"
    ])

    # 应用筛选
    filtered_df = df.copy()
    if selected_industry != "全部":
        filtered_df = filtered_df[filtered_df['行业'] == selected_industry]
    filtered_df = filtered_df[
        (filtered_df['数字化转型综合指数'] >= index_range[0]) &
        (filtered_df['数字化转型综合指数'] <= index_range[1])
    ]
    # 排序
    sort_map = {
        "综合指数 (降序)": ("数字化转型综合指数", False),
        "综合指数 (升序)": ("数字化转型综合指数", True),
        "总词频数 (降序)": ("总词频数", False),
        "总词频数 (升序)": ("总词频数", True)
    }
    col, ascending = sort_map[sort_by]
    filtered_df = filtered_df.sort_values(col, ascending=ascending)
    st.markdown(f"**筛选结果**: {len(filtered_df)} 家企业")

# 主页面查询区域
stock_code = st.number_input("请输入股票代码", min_value=int(df['股票代码'].min()), max_value=int(df['股票代码'].max()))
if st.button("查询"):
    result = filtered_df[filtered_df['股票代码'] == stock_code]
    if result.empty:
        st.warning(f"未找到股票代码为 {stock_code} 的企业信息。")
    else:
        st.write(f"### 企业信息")
        st.write(f"**企业名称**: {result['企业名称'].values[0]}")
        st.write(f"**行业**: {result['行业'].values[0]}")
        st.write(f"**数字化转型综合指数**: {result['数字化转型综合指数'].values[0]}")

        # 绘制各项技术应用情况柱状图
        technologies = ['数字技术应用', '人工智能技术', '区块链技术', '大数据技术', '云计算技术']
        tech_values = result[technologies].values[0]

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(technologies, tech_values)
        ax.set_title('各项技术应用情况')
        ax.set_xlabel('技术类型')
        ax.set_ylabel('应用程度')
        st.pyplot(fig)

# 显示筛选后的表格数据
st.write("### 筛选后的企业数据")
st.dataframe(filtered_df[['股票代码', '企业名称', '行业', '数字化转型综合指数', '总词频数']])