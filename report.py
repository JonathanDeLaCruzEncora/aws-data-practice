from boto3_utils import get_all_items
import pandas as pd
import streamlit as st
import altair as alt
import boto3

st.title('Report of Data Practice')

# TESTING WITHOUT DYNAMODB (FILES DOWNLOADED FROM DYNAMODB TABLES)
# posts_df = pd.read_csv('test_data/posts_dynamo.csv')
# stream_df = pd.read_csv('test_data/results_dynamo.csv')

# Initialize DynamoDB resource
dynamodb = boto3.resource(
    "dynamodb",
    region_name='us-east-1',# Change to your region
    aws_access_key_id="YOUR ACCESS KEY",
    aws_secret_access_key="YOUR SECRET KEY"
)

posts_table_db = dynamodb.Table("ProcessedData")
stream_table_db = dynamodb.Table("ProcessedStream")

# Use Streamlit session state to cache the data
if 'posts_df' not in st.session_state:
    # Fetch data only if it is not already in session state
    posts_df_data = get_all_items(posts_table_db)
    st.session_state.posts_df = pd.DataFrame(posts_df_data)

if 'stream_df' not in st.session_state:
    stream_df_data = get_all_items(stream_table_db)
    st.session_state.stream_df = pd.DataFrame(stream_df_data)

# Retrieve data from session state
posts_df = st.session_state.posts_df
stream_df = st.session_state.stream_df

st.subheader("Table for Posts")
posts_df = posts_df[['post_id', 'platform', 'post_type', 'reach', 'likes', 'comments', 'shares', 'engagement_rate', 'post_timestamp']]

posts_df['likes'] = pd.to_numeric(posts_df['likes'], errors='coerce')
posts_df['comments'] = pd.to_numeric(posts_df['comments'], errors='coerce')
posts_df['shares'] = pd.to_numeric(posts_df['shares'], errors='coerce')
posts_df['reach'] = pd.to_numeric(posts_df['reach'], errors='coerce')
posts_df['engagement_rate'] = pd.to_numeric(posts_df['engagement_rate'], errors='coerce')
posts_df['post_timestamp'] = pd.to_datetime(posts_df['post_timestamp'], errors='coerce')
posts_df['post_id'] = posts_df['post_id'].astype(str)
posts_df['platform'] = posts_df['platform'].astype(str)
posts_df['post_type'] = posts_df['post_type'].astype(str)

st.dataframe(posts_df.head())

st.subheader("Posts Metrics")
col1, col2 = st.columns(2)

with col1:
    st.text('Amount of each engagement per platform')
    chart_data = posts_df.groupby('platform').agg({
        'likes':'sum', 
        'comments':'sum', 
        'shares':'sum'
    })
    st.bar_chart(chart_data, stack=False)
    
    st.text('Comparison of total engagements and reach per platform')
    chart_data = posts_df.groupby('platform')[['likes', 'comments', 'shares']].sum().sum(axis=1).reset_index()
    chart_data['Reach'] = posts_df.groupby('platform')['reach'].sum()[0]
    chart_data = chart_data.rename(columns={0: 'Engagements'})
    chart_data = chart_data.set_index('platform')
    st.bar_chart(chart_data, stack=False)

with col2:
    st.text('Average engagement rate per platform')
    chart_data = posts_df.groupby('platform').agg({
        'engagement_rate':'mean'
    })
    st.bar_chart(chart_data)
    
    st.text('Engagement rate over time for each post type')
    chart_data = posts_df[['engagement_rate', 'post_timestamp','post_type']]
    chart_data['post_timestamp'] = pd.to_datetime(chart_data['post_timestamp'])
    st.line_chart(chart_data, y='engagement_rate', x='post_timestamp', color='post_type')
##############

st.title("Stream Metrics")
stream_df = stream_df.fillna(0)
stream_df = stream_df.rename(columns={'engagement_counts.Comment':'comments', 'engagement_counts.Like':'likes', 'engagement_counts.Share':'shares'}) 
stream_df = stream_df[['post_id', 'comments', 'likes', 'shares', 'window_start', 'window_end']]
stream_df['window_start'] = pd.to_datetime(stream_df['window_start'])
stream_df['window_end'] = pd.to_datetime(stream_df['window_end'])
st.subheader("Table for Stream")
st.dataframe(stream_df.head())


joined_data_df = stream_df.set_index('post_id').merge(posts_df[['post_id','platform','post_type']].set_index('post_id'), on='post_id', how='left')
platform_total_df = joined_data_df[['comments','likes','shares','platform']].groupby('platform').sum()
platform_total_df = platform_total_df.reset_index()
platform_total_df["total"] = platform_total_df[["comments", "likes", "shares"]].sum(axis=1)

melted_df = platform_total_df.melt(id_vars=['platform', 'total'], 
                          value_vars=['comments', 'likes', 'shares'],
                          var_name='metric', value_name='count')

st.subheader("Total engagement per platform and type of engagement")
c = alt.Chart(melted_df).mark_bar().encode(
    y=alt.Y("count:Q"),  
    x=alt.X("platform:N", sort=alt.EncodingSortField(field="total", order="descending")),
    color=alt.Color("metric:N", scale=alt.Scale(scheme='set2')), 
).properties(
    height=400
)

c2 = alt.Chart(melted_df).mark_bar().encode(
    x=alt.X("count:Q"), 
    y=alt.Y("platform:N", title="Platform", sort=alt.EncodingSortField(field="total", order="descending")),  
    color=alt.Color("metric:N", scale=alt.Scale(scheme='set2')), 
    yOffset="metric:N" 
).properties(
    height=400
)

col1, col2 = st.columns(2)

with col1:
    st.altair_chart(c, use_container_width=True)

with col2:
    st.altair_chart(c2, use_container_width=True)

temp_df = joined_data_df[['platform', 'post_type', 'comments', 'likes', 'shares']]
temp_df = temp_df.reset_index()
temp_df = temp_df.groupby(['post_id'], as_index=False).agg(
    {'platform': 'first',        
     'post_type': 'first',       
     'comments': 'sum',          
     'likes': 'sum',             
     'shares': 'sum'})           

temp_df['total'] = temp_df[['comments', 'likes', 'shares']].sum(axis=1)

temp_df_sorted = temp_df.sort_values(by="total", ascending=False).reset_index(drop=True).reset_index()
temp_df_sorted_top_25 = temp_df_sorted[:25]

c = alt.Chart(temp_df_sorted_top_25).mark_bar().encode(
    y=alt.Y('post_id:N', sort=alt.SortField(field="total", order="descending")),  
    x=alt.X("total:Q", title="Total Engagement"),  
    color=alt.Color("platform:N", scale=alt.Scale(scheme='set2')),  
).properties(
    height=400
)

c2 = alt.Chart(temp_df_sorted_top_25).mark_bar().encode(
    y=alt.Y('post_id:N', sort=alt.SortField(field="total", order="descending")),  
    x=alt.X("total:Q", title="Total Engagement"), 
    color=alt.Color("post_type:N", scale=alt.Scale(scheme='set2')),  
).properties(
    height=400
)

st.subheader('Top 25 posts by total engagement')
chart_option = st.selectbox(
    "Choose Chart Type:",
    ["By Platform", "By Post Type"],
    key='1'
)

if chart_option == "By Platform":
    st.altair_chart(c, use_container_width=True)
elif chart_option == "By Post Type":
    st.altair_chart(c2, use_container_width=True)


temp_df = joined_data_df[['platform', 'post_type', 'comments', 'likes', 'shares', 'window_start']]
temp_df["total"] = joined_data_df[["comments", "likes", "shares"]].sum(axis=1)

st.subheader('Total engagement over time')
chart_option_2 = st.selectbox(
    "Choose Chart Type:",
    ["By Platform", "By Post Type"],
    key='2'
)

hist = alt.Chart(temp_df).mark_bar().encode(
    x=alt.X('window_start:T', bin=alt.Bin(maxbins=30), title='Time'),
    y=alt.Y('sum(total):Q', title='Total of engagements (stacked by platform)'),
    color=alt.Color("platform:N", scale=alt.Scale(scheme='set2')),
    tooltip=['platform:N', 'sum(total):Q']
)

hist2 = alt.Chart(temp_df).mark_bar().encode(
    x=alt.X('window_start:T', bin=alt.Bin(maxbins=30), title='Time'),
    y=alt.Y('sum(total):Q', title='Total of engagements (stacked by post type)'),
    color=alt.Color("post_type:N", scale=alt.Scale(scheme='set2')),
    tooltip=['post_type:N', 'sum(total):Q']
)

line = alt.Chart(temp_df).mark_area( opacity=0.2).encode(
    x='window_start:T',
    y='sum(total):Q'
)

if chart_option_2 == "By Platform":
    st.altair_chart(line + hist, use_container_width=True)
elif chart_option_2 == "By Post Type":
    st.altair_chart(line + hist2, use_container_width=True)


c = alt.Chart(temp_df).mark_line(opacity=0.8).encode(
    x=alt.X('window_start:T', title='Time'),
    y=alt.Y('count():Q', stack=None, title='Density of posts engaged'),
    color=alt.Color("platform:N", scale=alt.Scale(scheme='set2'))
)

c2 = alt.Chart(temp_df).mark_line(opacity=0.8).encode(
    x=alt.X('window_start:T', title='Time'),
    y=alt.Y('count():Q', stack=None, title='Density of posts engaged'),
    color=alt.Color("post_type:N", scale=alt.Scale(scheme='set2'))
)

st.subheader('Density of posts engaged over time')
chart_option_3 = st.selectbox(
    "Choose Chart Type:",
    ["By Platform", "By Post Type"],
    key='3'
)

if chart_option_3 == "By Platform":
    st.altair_chart(c, use_container_width=True)
elif chart_option_3 == "By Post Type":
    st.altair_chart(c2, use_container_width=True)

