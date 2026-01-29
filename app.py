import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(
    page_title="Climate Tech Bridge Rounds",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Styling for Premium Aesthetics ---
st.markdown("""
<style>
    /* Reduce top whitespace & Match Header */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    
    header[data-testid="stHeader"] {
        background-color: #0E1117 !important;
    }

    /* Dark Mode Enforcement & Custom Palette */
    [data-testid="stAppViewContainer"] {
        background-color: #0E1117;
        color: #E6EDF3;
    }
    
    /* Metrics Styling */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 600;
        color: #F0F6FC;
    }
    
    [data-testid="stMetricLabel"] {
        color: #8B949E !important;
        font-size: 0.9rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Sidebar Specific Styling */
    [data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }
    
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        font-size: 0.85rem !important;
    }

    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #F0F6FC !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* General Text */
    p, .stMarkdown, li, div {
        color: #C9D1D9;
        font-size: 0.92rem !important;
    }
    
    /* Transparent Dataframes */
    [data-testid="stDataFrame"] {
        background-color: transparent !important;
    }
    [data-testid="stDataFrame"] > div {
        background-color: transparent !important;
    }
    
    /* Plotly Chart Background */
    .js-plotly-plot .plotly .main-svg {
        background: transparent !important;
    }
    
    /* FORCE THEME OVERRIDES */
    /* Checkbox & Radio Buttons */
    div[data-testid="stCheckbox"] label span:first-child {
        background-color: #0E1117 !important;
        border-color: #30363D !important;
    }
    div[data-testid="stCheckbox"] label[data-checked="true"] span:first-child {
        background-color: #00ADB5 !important;
        border-color: #00ADB5 !important;
    }
    
    /* Year Slider (Range) - Clean Layout */
    /* Target the Thumbs (Dots) */
    div[data-testid="stSlider"] div[role="slider"] {
        background-color: #F0F6FC !important;
        border: 2px solid #00ADB5 !important;
        box-shadow: 0 0 5px rgba(0, 173, 181, 0.5);
    }
    /* Target the Active Track (Line between dots) - specific to Streamlit structure */
    div[data-testid="stSlider"] div[data-baseweb="slider"] > div > div > div:nth-child(2) {
        background-color: #00ADB5 !important;
    }
    
    /* Tabs */
    button[data-baseweb="tab"] {
        color: #8B949E !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #00ADB5 !important;
        border-bottom-color: #00ADB5 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("cleaned_trellis_data.csv")
        df['Deal Date'] = pd.to_datetime(df['Deal Date'])
        return df
    except FileNotFoundError:
        st.error("Data file not found. Please run process_data.py first.")
        return pd.DataFrame()

df = load_data()

# Exclude 2014 globally as requested
df = df[df['Year'] != 2014]

if df.empty:
    st.stop()

# --- Title ---
st.title("🌍 Climate Tech Bridge Rounds Analysis")
st.markdown("Visualizing funding trends across sectors, stages, and time.")

# --- Sidebar Filters ---
st.sidebar.header("Filter Analysis")

# Sector Filter
all_sectors = sorted([s for s in df['Sector'].dropna().unique() if s != 'x'])

# Use a checkbox for "Select All"
select_all_sectors = st.sidebar.checkbox("Select All Sectors", value=True)

if select_all_sectors:
    selected_sectors = all_sectors
else:
    selected_sectors = st.sidebar.multiselect(
        "Choose Sectors", 
        all_sectors, 
        default=[]
    )

# Stage Filter
all_stages = sorted([s for s in df['Deal Stage'].dropna().unique() if s != 'x'])

# Use a checkbox for "Select All"
select_all_stages = st.sidebar.checkbox("Select All Stages", value=True)

if select_all_stages:
    selected_stages = all_stages
else:
    selected_stages = st.sidebar.multiselect(
        "Choose Stages", 
        all_stages, 
        default=[]
    )

# Year Filter
min_year = int(df['Year'].min())
max_year = int(df['Year'].max())
selected_years = st.sidebar.slider("Select Year Range", min_year, max_year, (min_year, max_year))

# --- Filtering Logic ---
filtered_df = df[
    (df['Sector'].isin(selected_sectors)) &
    (df['Deal Stage'].isin(selected_stages)) &
    (df['Year'] >= selected_years[0]) &
    (df['Year'] <= selected_years[1])
]

# --- Tabs ---
tab1, tab_strat, tab2, tab3, tab4 = st.tabs(["Market Overview", "Strategic Implications", "Investor Insights", "Extended Insights", "Case Study: CFS"])

with tab1:
    # --- KPI Row ---
    col1, col2, col3, col4 = st.columns(4)

    total_capital = filtered_df['Deal Size'].sum()
    deal_count = len(filtered_df)
    avg_deal_size = filtered_df['Deal Size'].mean() if deal_count > 0 else 0
    unique_companies = filtered_df['Company'].nunique()

    col1.metric("Total Capital Raised", f"${total_capital:,.1f}M")
    col2.metric("Total Deals", deal_count)
    col3.metric("Avg Deal Size", f"${avg_deal_size:,.1f}M")
    col4.metric("Active Companies", unique_companies)

    st.divider()

    # --- Visualizations ---

    # Row 1: Sector & Capital/Valuation Combo
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.subheader("Capital Invested & Median Valuation")
        
        # Aggregation for the combo chart
        # Total Capital (Sum of all deals)
        cap_agg = filtered_df.groupby('Year')['Deal Size'].sum().reset_index(name='Total_Capital')
        
        # Median Valuation (Only considering non-zero valuations)
        val_agg = filtered_df[filtered_df['Valuation'] > 0].groupby('Year')['Valuation'].median().reset_index(name='Median_Valuation')
        
        # Merge
        trend_combo = pd.merge(cap_agg, val_agg, on='Year', how='left')

        fig_combo = go.Figure()

        # Trace 1: Total Capital Invested (Bar)
        fig_combo.add_trace(go.Bar(
            x=trend_combo['Year'],
            y=trend_combo['Total_Capital'],
            name='Total Capital Invested',
            marker_color='#849F86',
            yaxis='y1'
        ))

        # Trace 2: Median Valuation (Line)
        fig_combo.add_trace(go.Scatter(
            x=trend_combo['Year'],
            y=trend_combo['Median_Valuation'],
            name='Median Valuation',
            mode='lines+markers',
            line=dict(color='#4CAF50', width=3), 
            yaxis='y2'
        ))

        fig_combo.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            font_color="#E6EDF3", 
            hovermode='x unified',
            title=dict(text="Evolution of Bridge Financing (2015-2025)", font=dict(color="#FFFFFF", size=20)),
            xaxis=dict(showgrid=False, color="#E6EDF3", title="Year"),
            yaxis=dict(
                title=dict(text="Total Capital ($M)", font=dict(color="#849F86")),
                tickfont=dict(color="#849F86"),
                showgrid=True, 
                gridcolor="#30363D"
            ),
            yaxis2=dict(
                title=dict(text="Median Valuation ($M)", font=dict(color="#4CAF50")),
                tickfont=dict(color="#4CAF50"),
                anchor="x",
                overlaying="y",
                side="right",
                showgrid=False
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(color="#E6EDF3")
            )
        )
        st.plotly_chart(fig_combo, use_container_width=True)

    with row1_col2:
        st.subheader("Investment by Sector")
        sector_agg = filtered_df.groupby('Sector')['Deal Size'].sum().reset_index()
        fig_sector = px.pie(
            sector_agg, 
            values='Deal Size', 
            names='Sector', 
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Teal,
            title="Capital Distribution by Sector"
        )
        fig_sector.update_traces(textposition='inside', textinfo='percent+label')
        fig_sector.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            font_color="#E6EDF3", 
            legend=dict(font=dict(color="#E6EDF3")),
            title=dict(font=dict(color="#FFFFFF", size=20))
        )
        st.plotly_chart(fig_sector, use_container_width=True)

    # Row 2: Bubble Chart (Full Width for Spacing)
    st.subheader("Deal Activity")
    # Clean data for bubble chart
    bubble_df = filtered_df.dropna(subset=['Deal Size', 'Deal Stage', 'Sector']).copy()

    # Fix for bubbles with 0 Valuation:
    # We want them to appear (size > 0) but indicate they are unknown.
    # We'll calculate a 'Plot_Size' column.
    # If Valuation > 0, use Valuation. If 0, use a default minimum (e.g. 20) so it's visible.
    bubble_df['Plot_Size'] = bubble_df['Valuation'].apply(lambda x: x if x > 0 else 30)
    bubble_df['Valuation_Label'] = bubble_df['Valuation'].apply(lambda x: f"${x:,.1f}M" if x > 0 else "N/A")

    # Label top 10 deals by size
    if not bubble_df.empty:
        top_deals_indices = bubble_df.nlargest(10, 'Deal Size').index
        bubble_df['Label'] = bubble_df.apply(lambda x: x['Company'] if x.name in top_deals_indices else '', axis=1)

        fig_bubble = px.scatter(
            bubble_df,
            x="Deal Date",
            y="Deal Size",
            size="Deal Size",
            color="Sector",
            hover_name="Company",
            hover_data={'Valuation': True, 'Deal Size': True, 'Deal Date': True},
            text="Label",
            size_max=80, 
            color_discrete_sequence=px.colors.qualitative.Bold,
            title="Time vs. Size (Bubble Size = Deal Size)"
        )
        fig_bubble.update_traces(textposition='top center', textfont=dict(color='#FFFFFF'))
        fig_bubble.update_layout(
            height=600, 
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            font_color="#E6EDF3", 
            xaxis=dict(showgrid=False, color="#E6EDF3", title="Deal Date"), 
            yaxis=dict(showgrid=True, gridcolor="#30363D", color="#E6EDF3", title="Deal Size ($M)"),
            legend=dict(
                font=dict(color="#E6EDF3"),
                title=dict(font=dict(color="#E6EDF3"))
            ),
            title=dict(font=dict(color="#FFFFFF", size=20))
        )
        st.plotly_chart(fig_bubble, use_container_width=True)
    else:
        st.info("Not enough data with Valuation metrics for Bubble Chart")

    # Row 3: Deal Count by Stage & Trend Line
    row3_col1, row3_col2 = st.columns(2)

    with row3_col1:
        st.subheader("Deal Count by Stage")
        stage_counts = filtered_df['Deal Stage'].value_counts().reset_index()
        stage_counts.columns = ['Deal Stage', 'Count']
        
        fig_stage = px.bar(
            stage_counts,
            x='Count',
            y='Deal Stage',
            orientation='h',
            color='Deal Stage',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            title="Number of Deals per Stage"
        )
        fig_stage.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            font_color="#E6EDF3", 
            xaxis=dict(color="#E6EDF3"),
            yaxis=dict(color="#E6EDF3"),
            showlegend=False,
            title=dict(font=dict(color="#FFFFFF", size=20))
        )
        st.plotly_chart(fig_stage, use_container_width=True)
        st.caption("Development capital refers to private equity or venture financing to support scaling, restructuring, or acquisitions, usually targeting companies with high growth potential but insufficient cash flow. It is used by Pitchbook as an identifier for \"PE Growth/ Expansion\" deals where the stage is not explicitly denoted.")

    with row3_col2:
        st.subheader("Deal Velocity")
        trend_agg = filtered_df.groupby('Year').agg(
            Deal_Count=('Company', 'count'),
            Median_Size=('Deal Size', 'median')
        ).reset_index()

        fig_dual = go.Figure()

        # Trace 1: Deal Count
        fig_dual.add_trace(go.Scatter(
            x=trend_agg['Year'], 
            y=trend_agg['Deal_Count'], 
            name='Deal Count',
            mode='lines+markers',
            line=dict(color='#00ADB5', width=3),
            yaxis='y1'
        ))

        # Trace 2: Median Deal Size
        fig_dual.add_trace(go.Scatter(
            x=trend_agg['Year'], 
            y=trend_agg['Median_Size'], 
            name='Median Deal Size ($M)',
            mode='lines+markers',
            line=dict(color='#FF2E63', width=3, dash='dot'),
            yaxis='y2'
        ))

        fig_dual.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            font_color="#E6EDF3", 
            hovermode='x unified',
            title=dict(text="Count vs. Median Size", font=dict(color="#FFFFFF", size=20)),
            xaxis=dict(showgrid=False, color="#E6EDF3", title="Year"),
            yaxis=dict(
                title=dict(text="Deal Count", font=dict(color="#00ADB5")),
                tickfont=dict(color="#00ADB5"),
                showgrid=True, 
                gridcolor="#30363D",
                rangemode="tozero"
            ),
            yaxis2=dict(
                title=dict(text="Median Deal Size ($M)", font=dict(color="#FF2E63")),
                tickfont=dict(color="#FF2E63"),
                anchor="x",
                overlaying="y",
                side="right",
                showgrid=False,
                rangemode="tozero"
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(color="#E6EDF3")
            )
        )
        st.plotly_chart(fig_dual, use_container_width=True)

    # Row 5: Raw Data View (Moved inside Tab 1 for access/context)
    st.divider()
    with st.expander("View Underlying Data"):
        st.dataframe(filtered_df.style.format({"Deal Size": "${:.2f}M", "Valuation": "${:.2f}M"}))

with tab_strat:
    st.header("Strategic Implications")
    st.markdown("Key takeaways reflecting the 2025 Bridge Round landscape.")
    st.divider()

    # Layout Helper Function
    def strategic_insight(number, title, thesis, implication, metric_label=None, metric_value=None, metric_delta=None, chart=None):
        st.subheader(f"{number}. {title}")
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"**Observation:** {thesis}")
            st.caption(f"**Strategic Implication:** {implication}")
        with c2:
            if chart:
                 st.plotly_chart(chart, use_container_width=True)
            elif metric_label:
                st.metric(metric_label, metric_value, delta=metric_delta)
        st.divider()

    # 1. Structural Feature
    # Create Chart for Insight 1
    mega_bridges = filtered_df[filtered_df['Deal Size'] >= 100].groupby('Year').size().reset_index(name='Count')
    fig_mega = px.bar(mega_bridges, x='Year', y='Count', title="Mega Bridges (>$100M)", color_discrete_sequence=['#FF2E63'])
    fig_mega.update_layout(
        height=250, 
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)", 
        font_color="#E6EDF3", 
        xaxis=dict(showgrid=False, tickmode='linear', dtick=1), 
        yaxis=dict(showgrid=True, gridcolor="#30363D"), 
        margin=dict(l=0, r=0, t=30, b=0)
    )

    strategic_insight(
        1, "Commercialization Bridge vs. Distressed Extension",
        "Bridge rounds in climate hardware have evolved from short-term liquidity patches into a structural financing instrument. Post-2019 data shows a material increase in deal size, with 'Mega Bridges' (>$500M) explicitly supporting FOAK (First-of-a-Kind) deployment and manufacturing scale-up.",
        "Investors must bifurcate their screening logic to distinguish 'Bridge-to-Deployment' (constructive) from 'Bridge-to-Nowhere' (distressed). Large capital inflows suggest these are effectively 'Series N' rounds used for timing alignment.",
        chart=fig_mega
    )

    # 2. Signaling Asymmetry
    strategic_insight(
        2, "Information Asymmetry & Signaling Risk",
        "The definition of a 'bridge' is structurally obscured. Founders and existing investors often label these rounds as 'Extensions', 'Convertibles', or 'Project-linked Equity' to mitigate negative signaling associated with flat/down rounds.",
        "Screen-based diligence will systematically underestimate 'true' bridge risk. Diligence requires qualitative reconstruction of the cap table dynamics to identify disguised bridges.",
        None, None, None
    )

    # 3. Exogenous Friction
    # Create Chart for Insight 3
    avg_size_trend = filtered_df.groupby('Year')['Deal Size'].mean().reset_index(name='Avg_Size')
    fig_avg = px.line(avg_size_trend, x='Year', y='Avg_Size', title="Avg Deal Size ($M)", color_discrete_sequence=['#00ADB5'])
    fig_avg.update_layout(
        height=250, 
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)", 
        font_color="#E6EDF3", 
        xaxis=dict(showgrid=False, tickmode='linear', dtick=1), 
        yaxis=dict(showgrid=True, gridcolor="#30363D"), 
        margin=dict(l=0, r=0, t=30, b=0)
    )

    strategic_insight(
        3, "Exogenous Friction as Primary Driver",
        "Empirical data suggests bridge rounds cluster around exogenous bottlenecks rather than pure company failure. Key drivers include government funding latency (LPO, DOE Grants), interconnection queues, and macro-rate tightening.",
        "A bridge does not automatically imply weak fundamentals. **As shown in the chart**, the sharp volatility implies that as projects encounter these 'waiting periods', the capital required to bridge the gap spikes effectively representing the 'cost of duration'.",
        chart=fig_avg
    )

    # 4. Cap Table Reconstruction
    strategic_insight(
        4, "Cap Table Reconstruction (New vs. Insider)",
        "Contrary to the 'insider bailout' narrative, ~52% of observed bridge rounds involve 100% new investor participation. This indicates that bridge rounds are often priced rounds where new strategic capital steps in to reset valuation or terms.",
        "Participation dynamics are a critical signal. 'Insider-only' bridges may signal a lack of external market validation, whereas 'New-led' bridges suggest a strategic entry point.",
        "Deals w/ 100% New Investors", "52%", "External Validation"
    )

    # 5. Capital Stack Complexity
    strategic_insight(
        5, "Capital Stack Complexity & Debt",
        "Bridge financing is increasingly hybrid. We observe a rise in project-linked debt and asset-backed structures being conflated with equity bridges. Headline 'Deal Size' often misrepresents the seniority and risk profile of the capital.",
        "Valuation metrics become less relevant than 'Liquidation Preference' and 'Seniority' in these scenarios. Reviewing the specific instrument structure is paramount.",
        None, None, None
    )

    # 6. Philanthropic Capital (New)
    strategic_insight(
        6, "The Role of Catalytic Capital: The Missing Link",
        "Philanthropic and concessionary capital is notably absent from the bridge round dataset. This suggests that catalytic capital is either risk-averse, lacks access to deal flow, or systematically under-reported in these pivotal 'Valley of Death' moments.",
        "This gap represents a massive, unexploited opportunity. By specifically screening for, and participating in, high-quality bridge rounds, philanthropic allocators could provide the critical 'validation signal' needed to unlock institutional capital and prevent premature mortality of FOAK projects.",
        "Observed Participation", "Low", "Opportunity Gap"
    )

with tab2:
    st.header("Investor Insights")
    st.markdown("Deep dive into the investor landscape for Climate Tech Bridge Rounds.")
    
    # Row 4: Investor Analysis
    st.subheader("Investor Profile Analysis")
    investor_col1, investor_col2 = st.columns(2)

    with investor_col1:
        st.markdown("**Most Active Investors**")
        # Parse Investors column
        # remove rows with empty investors
        investors_series = filtered_df['Investors'].dropna()
        
        # Split by semicolon, explode to individual rows, strip whitespace
        all_investors = investors_series.astype(str).str.split(';').explode().str.strip()
        
        # Count occurrences
        top_investors = all_investors.value_counts().head(10).reset_index()
        top_investors.columns = ['Investor', 'Count']
        
        if not top_investors.empty:
            fig_investor = px.bar(
                top_investors,
                x='Count',
                y='Investor',
                orientation='h',
                color='Count',
                color_continuous_scale=px.colors.sequential.Teal,
                title="Top 10 Most Active Investors"
            )
            fig_investor.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)", 
                font_color="#E6EDF3", 
                xaxis=dict(showgrid=True, gridcolor="#30363D", color="#E6EDF3"),
                yaxis=dict(color="#E6EDF3", categoryorder='total ascending'),
                coloraxis_showscale=False,
                title=dict(font=dict(color="#FFFFFF", size=20))
            )
            st.plotly_chart(fig_investor, use_container_width=True)
        else:
            st.info("No investor data available for the selected filters.")

    with investor_col2:
        st.markdown("**Investor Mix Profile**")
        if 'Investor Mix' in filtered_df.columns:
            mix_counts = filtered_df['Investor Mix'].fillna('Unknown').value_counts().reset_index()
            mix_counts.columns = ['Mix Type', 'Count']
            
            fig_mix = px.pie(
                mix_counts,
                values='Count',
                names='Mix Type',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel,
                title="Deal Distribution by Investor Mix"
            )
            fig_mix.update_traces(textposition='inside', textinfo='percent+label')
            fig_mix.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)", 
                font_color="#E6EDF3", 
                legend=dict(font=dict(color="#E6EDF3")),
                title=dict(font=dict(color="#FFFFFF", size=20))
            )
            st.plotly_chart(fig_mix, use_container_width=True)
        else:
            st.info("Investor Mix data not found.")
    
    st.divider()
    st.markdown("### Deep Dive: New vs. Existing Investor Dynamics")
    st.caption("Based on supplemental analysis.")

    # Data from User Images
    # 1. Top New Participating Investors
    new_investor_data = pd.DataFrame({
        "Investor": ["Temasek Holdings", "Climate Capital", "Lowercarbon Capital", "Collaborative Fund", "E8"],
        "Deals": [8, 7, 6, 6, 5]
    })
    
    # 2. Sector Participation Data
    sector_participation_data = pd.DataFrame({
        "Sector": ["Renewables", "LDES", "Hydrogen", "CDR", "Industrial Decarb", "Buildings", "Mobility", "Food & Ag"],
        "Existing Participation (%)": [12, 22, 17, 21, 20, 32, 11, 25],
        "New Participation (%)":      [92, 91, 87, 88, 87, 79, 89, 83]
    })

    # Metrics Row
    m1, m2, m3 = st.columns(3)
    m1.metric("Deals w/ Existing Investors", "49%")
    m2.metric("Deals w/ New Strategic Inv.", "11%")
    m3.metric("Deals w/ 100% New Investors", "52%")
    
    inv_row2_col1, inv_row2_col2 = st.columns(2)
    
    with inv_row2_col1:
        st.subheader("Most Common *New* Participating Investors")
        fig_new_inv = px.bar(
            new_investor_data,
            x='Deals',
            y='Investor',
            orientation='h',
            color='Deals',
            color_continuous_scale=px.colors.sequential.Viridis,
            title="Top New Investors"
        )
        fig_new_inv.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            font_color="#E6EDF3", 
            yaxis=dict(categoryorder='total ascending', color="#E6EDF3"),
            xaxis=dict(showgrid=True, gridcolor="#30363D", color="#E6EDF3"),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_new_inv, use_container_width=True)

    with inv_row2_col2:
        st.subheader("Investor Participation by Sector")
        # Melt for grouped bar chart
        sector_melt = sector_participation_data.melt(id_vars="Sector", var_name="Type", value_name="Percentage")
        
        fig_part = px.bar(
            sector_melt,
            x="Sector",
            y="Percentage",
            color="Type",
            barmode="group",
            color_discrete_map={
                "Existing Participation (%)": "#F4D35E",  # Muted Yellow
                "New Participation (%)": "#00ADB5"       # Cyan
            },
            title="Avg Existing vs. New Investor Participation"
        )
        fig_part.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            font_color="#E6EDF3", 
            xaxis=dict(color="#E6EDF3"),
            yaxis=dict(showgrid=True, gridcolor="#30363D", color="#E6EDF3", title="Participation (%)"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title="")
        )
        st.plotly_chart(fig_part, use_container_width=True)

with tab3:
    st.header("Extended Insights")
    st.markdown("Additional analysis on company maturity, geography, and sector spread.")

    # 1. Company Age at Deal (Time to Bridge)
    st.subheader("Time to Bridge: Company Age Analysis")
    if 'Year Founded' in filtered_df.columns:
        filtered_df['Company Age'] = filtered_df['Year'] - filtered_df['Year Founded']
        # Filter out negative ages or unreasonable values if any
        age_df = filtered_df[(filtered_df['Company Age'] >= 0) & (filtered_df['Company Age'] < 50)]
        
        if not age_df.empty:
            avg_age = age_df['Company Age'].mean()
            st.metric("Average Age at Bridge Round", f"{avg_age:.1f} Years")
            
            fig_age = px.histogram(
                age_df, 
                x='Company Age', 
                nbins=20,
                color_discrete_sequence=['#00ADB5'],
                title="Distribution of Company Age at Time of Deal"
            )
            fig_age.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)", 
                font_color="#E6EDF3",
                xaxis=dict(title="Years since Founding", showgrid=False, color="#E6EDF3"),
                yaxis=dict(title="Number of Companies", showgrid=True, gridcolor="#30363D", color="#E6EDF3"),
                bargap=0.1
            )
            st.plotly_chart(fig_age, use_container_width=True)
        else:
            st.info("No valid 'Year Founded' data available for age calculation.")
    
    st.divider()

    col_geo, col_box = st.columns(2)

    with col_geo:
        # 2. Geographic Distribution
        st.subheader("Geographic Hotspots")
        # Clean HQ locations - sometimes explicitly City, State or just City
        # We'll just take the top raw values for now as cleaning is complex without NLP
        geo_counts = filtered_df['HQ Location'].value_counts().head(15).reset_index()
        geo_counts.columns = ['Location', 'Count']
        
        fig_geo = px.bar(
            geo_counts,
            x='Count',
            y='Location',
            orientation='h',
            color='Count',
            color_continuous_scale=px.colors.sequential.Bluyl,
            title="Top 15 HQ Locations"
        )
        fig_geo.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            font_color="#E6EDF3", 
            xaxis=dict(showgrid=True, gridcolor="#30363D", color="#E6EDF3"),
            yaxis=dict(categoryorder='total ascending', color="#E6EDF3"),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_geo, use_container_width=True)

    with col_box:
        # 3. Sector Valuation Spread
        st.subheader("Deal Size Distribution by Sector")
        fig_box = px.box(
            filtered_df,
            x="Deal Size",
            y="Sector",
            color="Sector",
            color_discrete_sequence=px.colors.qualitative.Bold,
            title="Deal Size Variance per Sector"
        )
        fig_box.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            font_color="#E6EDF3", 
            xaxis=dict(title="Deal Size ($M)", showgrid=True, gridcolor="#30363D", color="#E6EDF3"),
            yaxis=dict(showgrid=False, color="#E6EDF3"),
            showlegend=False
        )
        st.plotly_chart(fig_box, use_container_width=True)

with tab4:
    st.header("Case Study: Commonwealth Fusion Systems (CFS)")
    st.markdown("**(Fusion Energy • Devens, MA • Founded 2018)**")
    
    st.markdown("""
    **Deal Overview:**
    In June 2025, CFS raised a massive **$863M Series B2** round. This round is technically a "Bridge" between their 2021 Series B and the future commercialization phase. 
    It stands out for its structural complexity and the strategic expansion of the investor base.
    """)
    
    # Key Stats Row
    cfs_col1, cfs_col2, cfs_col3, cfs_col4 = st.columns(4)
    cfs_col1.metric("Total Deal Size", "$863M")
    cfs_col2.metric("Equity Component", "$763M")
    cfs_col3.metric("New Debt", "$100M")
    cfs_col4.metric("Total Investors", "47")
    
    st.divider()

    # Deal History Table (Reconstructed from Image)
    st.subheader("Deal History")
    deal_history = pd.DataFrame([
        {"Deal": "Deal #9", "Type": "Series B2", "Date": "26-Jun-2025", "Amount": "$863.00M", "Raised to Date": "$2.86B", "Status": "Completed"},
        {"Deal": "Deal #8", "Type": "Early Stage VC", "Date": "23-Jun-2022", "Amount": "N/A", "Raised to Date": "$2.00B", "Status": "Completed"},
        {"Deal": "Deal #7", "Type": "Series B", "Date": "30-Nov-2021", "Amount": "$1.80B", "Raised to Date": "$2.00B", "Status": "Completed"},
        {"Deal": "Deal #6", "Type": "Grant", "Date": "31-Dec-2020", "Amount": "$1.37M", "Raised to Date": "$199.00M", "Status": "Completed"},
        {"Deal": "Deal #5", "Type": "Series A", "Date": "26-May-2020", "Amount": "$84.00M", "Raised to Date": "$199.00M", "Status": "Completed"},
        {"Deal": "Deal #4", "Type": "Grant", "Date": "07-Apr-2020", "Amount": "$3.70M", "Raised to Date": "$115.00M", "Status": "Completed"},
        {"Deal": "Deal #3", "Type": "Series A", "Date": "27-Jun-2019", "Amount": "$115.00M", "Raised to Date": "$115.00M", "Status": "Completed"},
        {"Deal": "Deal #2", "Type": "Accelerator", "Date": "01-Oct-2018", "Amount": "N/A", "Raised to Date": "N/A", "Status": "Completed"},
        {"Deal": "Deal #1", "Type": "Spin-Off", "Date": "01-Jan-2018", "Amount": "N/A", "Raised to Date": "N/A", "Status": "Completed"},
    ])
    st.dataframe(deal_history, use_container_width=True)

    st.divider()

    # Narrative Content
    col_narrative, col_quotes = st.columns([1.5, 1])

    with col_narrative:
        st.subheader("Why a Bridge Round?")
        st.markdown("""
        **1. Bridging to Commercialization (SPARC):**
        Fusion hardware is incredibly capital-intensive. This bridge financing ensures CFS has the runway to complete the construction and commissioning of **SPARC**, their first commercial facility. This milestone is critical to demonstrate net energy gain without forcing a premature Series C or IPO.
        
        **2. Accelerating for AI & Data Center Demand:**
        The round was driven by the urgent global need for baseload clean power, specifically citing the "explosive demand from AI and data centers." This macro tailwind justified raising nearly $1B despite a tougher venture climate.
        """)
        
        st.markdown("""
        > *"The fact that it’s a first of a kind technology is a wrinkle that then has a big impact on where the capital will come from. We’re not entirely sure, but we are pretty committed to doing this. And our investors are pretty committed to doing this."*  
        > — **Bob Mumgaard, CEO**
        """)

        st.subheader("Deal Structure & Investor Dynamics")
        st.markdown("""
        **Quantifiables:**
        *   **$763M Equity / $100M Debt**: A healthy mix, leveraging debt for capex-heavy machinery while preserving equity.
        *   **Investor Mix**: The round saw a distinct shift from pure-play VC to "deep pockets" capital. 
            *   *New Entrants*: Sovereign Wealth (Temasek, K4), Pension Funds, and Multinational Corporates (Eni, Japanese Consortium).
            *   *Follow-on*: Existing insiders (Breakthrough, Khosla, Google) doubled down, signaling high conviction.
        """)

    with col_quotes:
        st.subheader("Investor Voices")
        st.info("""
        **"A rare fusion of visionary leadership, scientific breakthrough, and executional excellence."**  
        — Dennis Lynch, Morgan Stanley
        """)
        
        st.info("""
        **"CFS is redefining what it takes to build a deep tech unicorn... turning breakthrough science into a global industry."**  
        — Mike Schroepfer, Founder, Gigascale Capital
        """)

        st.info("""
        **"The most promising path to commercial fusion power in the coming years."**  
        — Breakthrough Energy Ventures
        """)

# Footer
st.markdown("---")
st.caption("Generated by Google Deepmind • Data Source: Trellis Climate Bridge Rounds Research")
