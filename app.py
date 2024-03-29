import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(
    page_title="User Engagement Dashboard",
    layout="wide")
    #initial_sidebar_state="expanded"

st.title("USER ENGAGEMENT DASHBOARD")
tab1, tab2 = st.tabs(["Users","Modules"])

# Load CSV files
users = pd.read_csv(r"C:\Users\TaleyaHusn\Desktop\User Engagement\User-Engagement\Taleya - User Engagement\users.csv")
user_designations = pd.read_csv(r"C:\Users\TaleyaHusn\Desktop\User Engagement\User-Engagement\Taleya - User Engagement\user_designations.csv")
geo_tables = pd.read_csv(r"C:\Users\TaleyaHusn\Desktop\User Engagement\User-Engagement\Taleya - User Engagement\geo_tables.csv")
ahoy_visits = pd.read_csv(r"C:\Users\TaleyaHusn\Desktop\User Engagement\User-Engagement\Taleya - User Engagement\ahoy_visits.csv")
ahoy_events = pd.read_csv(r"C:\Users\TaleyaHusn\Desktop\User Engagement\User-Engagement\Taleya - User Engagement\ahoy_events.csv")

# Data processing
users = users.dropna(subset=['user_designation_id'])
ahoy_events['time'] = pd.to_datetime(ahoy_events['time'], format="%Y-%m-%d %H:%M:%S.%f", errors='coerce')
merged_ev = pd.merge(ahoy_visits, ahoy_events, left_on='id', right_on='visit_id')
merged_ev['time'] = pd.to_datetime(merged_ev['time'], format="%Y-%m-%d %H:%M:%S.%f", errors='coerce')

with tab1:
    #with st.sidebar:
        #st.title("User Engagement Dashboard")
        #geography_type_list = list(users.geography_type.unique())
        #selected_geography_type = st.selectbox('Select a geography', geography_type_list)
        #ahoy_events = ahoy_events.dropna(subset=['time'])
        #years = ahoy_events['time'].dt.year.unique()
        #selected_year = st.sidebar.selectbox("Select Year", options=years)

    def plot_user_engagement(ahoy_events):
        #ahoy_events_year = ahoy_events[ahoy_events['time'].dt.year == selected_year]
        ahoy_events['hour'] = ahoy_events['time'].dt.hour
        unique_visit_count_per_hour = ahoy_events.groupby('hour')['visit_id'].nunique()
        result_df = pd.DataFrame({'Hour': unique_visit_count_per_hour.index, 'Visit_Count': unique_visit_count_per_hour.values})
        user_count = px.line(result_df, x='Hour', y='Visit_Count', title=f'User Engagement by Hour')
        user_count.update_xaxes(title='Hour')
        user_count.update_yaxes(title='Number of Visits')
        return user_count

    def format_unique_user_count(users):
        unique_user_count = users['id'].nunique()

        if unique_user_count > 1000000:
            if unique_user_count % 1000000 == 0:
                return f'{unique_user_count // 1000000} M'
            return f'{round(unique_user_count / 1000000, 1)} M'
        elif unique_user_count > 1000:
            return f'{unique_user_count // 1000} K'
        return unique_user_count

    # Average time spent per visit
    ahoy_events['date'] = ahoy_events['time'].dt.date
    last_occurrence_time = ahoy_events.groupby(['user_id', 'date', 'visit_id'])['time'].max().reset_index()
    last_occurrence_time.rename(columns={'time': 'last_occurrence_time'}, inplace=True)
    first_occurrence_time = ahoy_events.groupby(['user_id', 'date', 'visit_id'])['time'].min().reset_index()
    first_occurrence_time.rename(columns={'time': 'first_occurrence_time'}, inplace=True)
    occurrence_times = pd.merge(first_occurrence_time, last_occurrence_time, on=['user_id', 'date', 'visit_id'])
    occurrence_times['time_diff'] = occurrence_times['last_occurrence_time'] - occurrence_times['first_occurrence_time']
    mean_time_spent = occurrence_times['time_diff'].mean()

    def format_time_diff(time_diff):
        if time_diff > pd.Timedelta('1h'):
            if time_diff % pd.Timedelta('1h') == pd.Timedelta('0s'):
                return f'{time_diff / pd.Timedelta("1h")} hours'
            return f'{round(time_diff / pd.Timedelta("1h"), 1)} hours'
        if time_diff > pd.Timedelta('1m'):
            return f'{time_diff / pd.Timedelta("1m")} minutes'
        if time_diff > pd.Timedelta('1s'):
            return f'{time_diff / pd.Timedelta("1s")} seconds'
        return f'{time_diff / pd.Timedelta("1ms")} milliseconds'

    mean_time_spent_minutes = mean_time_spent.total_seconds() / 60

    # Convert the mean time spent to a string with two decimal places
    mean_time_spent_formatted = f"{mean_time_spent_minutes:.2f} minutes"

    def display_geography_bar_chart(users):
        geography_counts = users.groupby('geography_type')['id'].nunique()
        geography_counts_sorted = geography_counts.sort_values(ascending=False)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=geography_counts_sorted.index,
            y=geography_counts_sorted.values
        ))
        fig.update_layout(
            title="Geography Distribution",
            xaxis_title="Geography Type",
            yaxis_title="Unique User Count",
            width=350,
            height=400
        )
        return fig

    ahoy_events['year_month'] = ahoy_events['time'].dt.to_period('M').dt.to_timestamp()
    total_monthly_counts = ahoy_events.groupby('year_month').size().reset_index(name='total_visit_count')
    total_monthly_counts['year_month'] = pd.to_datetime(total_monthly_counts['year_month'])
    most_visited_module = ahoy_events['name'].value_counts().idxmax()

    def plot_monthly_visit_counts():
        # Filter the data for the selected year
        
        # Create Plotly line chart
        monthly_counts = px.line(total_monthly_counts, x='year_month', y='total_visit_count',
                                labels={'total_visit_count': 'Total Visits', 'year_month': 'Year-Month'},
                                title=f'Monthly Visit Counts')
        monthly_counts.update_traces(hovertemplate='<b>Year-Month</b>: %{x}<br><b>Total Visits</b>: %{y}<br><b>Most Visited Module</b>: ' + most_visited_module)

        
        monthly_counts.update_layout(xaxis_title='Year-Month',
                                    yaxis_title='Total Visits',
                                    title_x=0.5,
                                    hovermode='x unified')
        
        return monthly_counts

    #Active user
    #unique_users_in_users_table = users['id'].nunique()
    unique_users_in_ahoy_visits_table = ahoy_visits['user_id'].nunique()
    active_users = unique_users_in_ahoy_visits_table 
    #active_users_percent = round(active_users_ratio * 100, 2)

    #Engagement based on designation
    unique_user_ids = ahoy_visits['user_id'].unique()
    user_designation_ids = users[users['id'].isin(unique_user_ids)][['id', 'user_designation_id']]
    result_df = pd.merge(user_designation_ids, user_designations, left_on='user_designation_id',right_on='id', how='left')
    result_df.rename(columns={'name_en': 'designation_name'}, inplace=True)
    designation_count= result_df['designation_name'].value_counts()
    top_10 = designation_count.sort_values(ascending=False).head(10)
    count_designation = px.bar(top_10, x=top_10.index, y=top_10.values, labels={'x':'Designation', 'y':'Count'})
    count_designation.update_layout(title=f'Engagement Based on Designation')

    #Segmentation based on browser
    browser_counts = ahoy_visits['browser'].value_counts().reset_index()
    browser_counts.columns = ['Browser', 'User Count']
    browser_counts_sorted = browser_counts.sort_values(by='User Count', ascending=False)
    top_10_browsers = browser_counts_sorted.head(10)
    browser = px.bar(top_10_browsers, x='Browser', y='User Count', 
                        labels={'User Count': 'Number of Users', 'Browser': 'Browser'},
                        title='Top 10 Browsers')

    #Device count
    filtered_device_counts = ahoy_visits[ahoy_visits['device_type'].isin(['Mobile', 'Desktop', 'Phablet', 'Tablet'])]

    # Calculate device counts for remaining device types
    device_counts = filtered_device_counts['device_type'].value_counts().reset_index()
    device_counts.columns = ['Device Type', 'User Count']

    # Create bar chart using Plotly Express
    device = px.bar(device_counts, x='Device Type', y='User Count',
                    title='User Segmentation based on device type',
                    labels={'User Count': 'User Count', 'Device Type': 'Device Type'})

    device.update_layout(width=350, height=400)

    col = st.columns((1.5, 3.0, 2.0), gap='medium')

    # Unique user count
    with col[0]:
        st.markdown("##### User Count")
        unique_user_count = format_unique_user_count(users)
        st.write(unique_user_count)

    # Average time spent per visit
    with col[1]:
        st.markdown("##### Active Users")
        st.write( active_users)


    #User visit by year
    with col[1]:
        monthly_count = plot_monthly_visit_counts()
        st.plotly_chart(monthly_count)
    # User Engagement by hour
    with col[1]:
        user_count = plot_user_engagement(ahoy_events)
        st.plotly_chart(user_count)


    # Display geography donut chart
    with col[0]:
        fig = display_geography_bar_chart(users)
        st.plotly_chart(fig)

    with col[2]:
        st.markdown('##### Average Time Spent per Visit ')
        st.write(mean_time_spent_formatted)

    with col[2]:
        st.plotly_chart(count_designation)

    with col[2]:
        st.plotly_chart(browser)

    with col[0]:
        st.plotly_chart(device)
    

with tab2:

    ahoy_events['time'] = pd.to_datetime(ahoy_events['time'], format="%Y-%m-%d %H:%M:%S.%f", errors='coerce')
    ahoy_events.dropna(subset=['time'], inplace=True)
    ahoy_events['date'] = ahoy_events['time'].dt.date

    last_visit_time = ahoy_events.groupby(['name', 'date', 'visit_id'])['time'].max().reset_index()
    last_visit_time.rename(columns={'time': 'last_visit_time'}, inplace=True)

    first_visit_time = ahoy_events.groupby(['name', 'date', 'visit_id'])['time'].min().reset_index()
    first_visit_time.rename(columns={'time': 'first_visit_time'}, inplace=True)

    total_time = pd.merge(first_visit_time, last_visit_time, on=['name', 'date', 'visit_id'])
    total_time['time_diff'] = total_time['last_visit_time'] - total_time['first_visit_time']
    total_time['name'] = total_time['name'].replace(['Data explorer', 'Data Explorer', 'data_explorer'], 'data-explorer')
    total_time['name'] = total_time['name'].replace(['Abha Dashboard', 'abha_dashboard'], 'abha-dashboard')
    total_time['name'] = total_time['name'].replace(['Prasav Watch', 'prasav_watch'], 'prasav-watch')
    average_time_per_part = total_time.groupby('name')['time_diff'].mean().reset_index(name='average_time')
    average_time_per_part['average_time_hours'] = average_time_per_part['average_time'] / pd.Timedelta(hours=1)
    average_time_per_part = average_time_per_part.sort_values(by='average_time_hours', ascending=False)
    avg_time_dashboard_part = px.bar(average_time_per_part, x='name', y='average_time_hours', title='Average Time for Each Dashboard-Part', 
             labels={'name': 'Dashboard-Part', 'average_time_hours': 'Average Time (hours)'})
    avg_time_dashboard_part.update_layout(width=650, height = 600)

#Most visited module
    visit_counts = total_time.groupby('name')['visit_id'].count().reset_index(name='visit_count')
    visit_count_sorted = visit_counts.sort_values(by='visit_count', ascending=False)
    bar_chart = px.bar(visit_count_sorted, x='name', y='visit_count', title='Most Visited Module',
                   labels={'visit_count': 'Visits', 'name': 'Name'})
    bar_chart.update_layout(width=650,height=600)
    col = st.columns((3.0, 3.0, 2.0), gap='large')



    with tab2:
        with col[0]:
            st.plotly_chart(avg_time_dashboard_part)
    with tab2:
        with col[1]:
            st.plotly_chart(bar_chart)

