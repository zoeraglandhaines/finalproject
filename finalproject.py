"""
Name: Zoe Ragland-Haines
Class: CS230
Professor Frydenberg
URL:
Info: This app runs various equations to find different analytics about fast food restaurants
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  # [EXTRA] 2 Seaborn charts [SEA1], [SEA2]
import pydeck as pdk
import folium  # [EXTRA][FOLIUM1][FOLIUM2]
from streamlit_folium import st_folium
import numpy as np

sns.set_theme(style="whitegrid")

# [DA1] Clean or manipulate data, lambda function (required)
def clean_data():
    df = pd.read_csv("fast_food_usa.csv")
    df['city'] = df['city'].str.title().fillna("Unknown")
    df['province'] = df['province'].str.upper().fillna("Unknown")
    df['categories'] = df['categories'].fillna("Unknown")
    # [DA1] Clean or manipulate data, lambda function (required)
    df['numbered_categories'] = df['categories'].apply(lambda x: len(x.split(',')))
    return df

data = clean_data()

# [PY2] A function that returns more than one value
def get_list(df):
    cities = ["All"] + sorted(df['city'].unique())
    states = ['All'] + sorted(df['province'].unique())
    return cities, states

cities, states = get_list(data)

# [PY1] A function with two or more parameters, one of which has a default value, called at least twice (once with the default value, and once without)
def filter_data(df, city="All", state="All"):
    if city != "All" and state != "All":
        return df[(df['city'] == city) & (df['province'] == state)]
    elif city != "All":
        return df[df['city'] == city]
    elif state != "All":
        return df[df['province'] == state]
    else:
        return df

default = filter_data(data)  # [PY1] called with default
custom = filter_data(data, city="Boston", state="MA")  # [PY1] called with custom args

# [PY4] A list comprehension
all_categories = ['All'] + sorted({category for categories in data['categories'] for category in categories.split(',')})

# [PY5] A dictionary where you write code to access its keys, values, or items
name_count = data['name'].value_counts().to_dict()

# [ST4] Customized page design features (sidebar, fonts, colors, images, navigation)
st.title("Fast Food USA Explorer")
st.sidebar.header("Fast Food Explorer")
st.sidebar.image("https://www.partstown.com/about-us/wp-content/uploads/2023/11/what-is-considered-fast-food.jpg", width=100)

page = st.sidebar.radio("What would you like to explore?", [
    "Find Restaurants by Location",
    "Number of Restaurants by Location",
    "Restaurant Summary by Location",
    "Summary & Analytics"
])

if page == "Find Restaurants by Location":
    st.header("Find Restaurants by Location")
    st.write(
        "This page will show all restaurants in the area that you choose. To navigate this page, select the city and/or state that you would like to see results from. Enter 'All' for all cities and/or state data in the entire country.")
    # [ST1] At least three Streamlit different widgets (sliders, drop downs, multi-selects, text boxes, etc)
    city = st.selectbox("Enter City: ", cities)
    state = st.selectbox("Enter State: ", states)
    try:
        location_count = filter_data(data, city, state)
        if location_count.empty or 'latitude' not in location_count.columns or 'longitude' not in location_count.columns:
            st.warning("No valid location data to display")
            st.stop()
        location_count['latitude'] = location_count['latitude'].astype(float)
        location_count['longitude'] = location_count['longitude'].astype(float)
        st.dataframe(location_count[['name', 'city', 'province']])
    except Exception as e:
        st.error(f"Error Loading Data: {e}")
        st.stop()

    # [EXTRA][FOLIUM1] 3 additional DA requirements
    st.subheader("Folium Map of Locations")
    try:
        if location_count.empty or 'latitude' not in location_count.columns or 'longitude' not in location_count.columns:
            st.warning("No valid location data to display for this selection.")
        else:
            m = folium.Map(location=[location_count['latitude'].mean(), location_count['longitude'].mean()])
            for idx, row in location_count.iterrows():
                folium.Marker([row['latitude'], row['longitude']], tooltip=row['name']).add_to(m)
            st_folium(m, width=700, height=400)
    except Exception as e:
        st.error(f"Folium map error: {e}")

elif page == "Number of Restaurants by Location":
    st.header("Number of Restaurants by Location")
    # [ST2] At least three Streamlit different widgets (sliders, drop downs, multi-selects, text boxes, etc)
    name = st.selectbox("Choose a Restaurant", ["All"] + sorted(data['name'].unique()))
    state = st.selectbox("Choose State:", states)
    city = st.selectbox("Choose City:", cities)

    filtered = filter_data(data, city, state)
    if name != "All":
        filtered = filtered[filtered['name'] == name]

    if filtered.empty:
        st.warning("No data to display.")
    else:
        #all restaurants
        if name != "All":
            #specific restaurant & city
            if state != "All" or city != "All":
                count = len(filtered)
                location_info = []
                if city != "All": location_info.append(city)
                if state != "All": location_info.append(state)
                location_str = ", ".join(location_info)
                st.write(f"Total {name} locations in {location_str}: {count}")
            #specific restaurant, all cities
            else:
                count = filtered['province'].value_counts()
                st.write(f"Total {name} locations: {count.sum()}")
                # [CHART2] At least two different charts with matplotlib, including titles, colors, labels, legends, as appropriate, one can be a table
                fig, ax = plt.subplots()
                count.plot(kind="bar", color="skyblue", ax=ax)
                ax.set_title(f"{name} Locations by State")
                ax.set_xlabel("State")
                ax.set_ylabel("Number of Locations")
                st.pyplot(fig)
                # [EXTRA][SEA1] 2 Seaborn charts
                st.subheader("Seaborn Barplot")
                fig3, ax3 = plt.subplots()
                sns.barplot(x=count.index, y=count.values, ax=ax3)
                ax3.set_title(f"{name} Locations by State")
                ax3.set_xlabel("State")
                ax3.set_ylabel("Number of Locations")
                st.pyplot(fig3)
        # all restaurants
        else:
            #all restaurants, states
            if state == "All" and city != "All":
                count_by_state = filtered.groupby('province')['name'].count().sort_values(ascending=False)
                st.write(f"Number of Restaurants by State for {city}")
                #matplot bar chart for states
                fig, ax = plt.subplots()
                count_by_state.plot(kind="bar", color="blue", ax=ax)
                ax.set_title(f"Number of Restaurants by State for {city}")
                ax.set_xlabel("State")
                ax.set_ylabel("Number of Restaurants")
                st.pyplot(fig)
                #seaborn barplot for states
                st.subheader("Seaborn Barplot")
                fig3, ax3 = plt.subplots()
                sns.barplot(x=count_by_state.index, y=count_by_state.values, ax=ax3, palette="pastel")
                ax3.set_title(f"Number of Restaurants by State for {city}")
                ax3.set_xlabel("State")
                ax3.set_ylabel("Number of Restaurants")
                st.pyplot(fig3)
            # all restaurants, cities, specific states
            elif state != "All" and city == "All":
                count_by_city = filtered.groupby('city')['name'].count().sort_values(ascending=False)
                st.write(f"Number of Restaurants by City in {state}")
                #matplotlib bar chart for cities
                fig, ax = plt.subplots()
                count_by_city.head(10).plot(kind="bar", color="pink", ax=ax)
                ax.set_title(f"Top 10 Cities by Number of Restaurants in {state}")
                ax.set_xlabel("City")
                ax.set_ylabel("Number of Restaurants")
                st.pyplot(fig)
                #seaborn barplot for cities
                st.subheader("Seaborn Barplot")
                fig3, ax3 = plt.subplots()
                sns.barplot(x=count_by_city.head(10).index, y=count_by_city.head(10).values, ax=ax3, palette="pastel")
                ax3.set_title(f"Top 10 Cities by Number of Restaurants in {state}")
                ax3.set_xlabel("City")
                ax3.set_ylabel("Number of Restaurants")
                plt.xticks(rotation=45)
                st.pyplot(fig3)
            #all restaurants, specific state, city
            elif state != "All" and city != "All":
                count = len(filtered)
                st.write(f"Number of restaurants in {city}, {state}: {count}")
                st.metric("Restaurant Count:", count)
            #all restaurants, states, cities
            else:
                count_by_state = filtered.groupby('province')['name'].count().sort_values(ascending=False)
                st.write("Number of Restaurants by State")
                #matplotlib bar chart for states
                fig, ax = plt.subplots()
                count_by_state.head(10).plot(kind="bar", color="palegreen", ax=ax)
                ax.set_title("Top 10 States by Number of Restaurants")
                ax.set_xlabel("State")
                ax.set_ylabel("Number of Restaurants")
                st.pyplot(fig)
                #seaborn barplot for states
                st.subheader("Seaborn Barplot")
                fig3, ax3 = plt.subplots()
                sns.barplot(x=count_by_state.head(10).index, y=count_by_state.head(10).values, ax=ax3, palette="pastel")
                ax3.set_title("Top 10 States by Number of Restaurants")
                ax3.set_xlabel("State")
                ax3.set_ylabel("Number of Restaurants")
                st.pyplot(fig3)
elif page == "Restaurant Summary by Location":
    st.header("Restaurant Summary by Location")
    # [ST3] At least three Streamlit different widgets  (sliders, drop downs, multi-selects, text boxes, etc)
    city = st.selectbox("Choose a City:", cities)
    state = st.selectbox("Choose a State", states)
    # [DA4] Filter data by one condition
    filtered_data = filter_data(data, city, state)
    st.write(f"Number of Restaurants: {len(filtered_data)}")
    st.dataframe(filtered_data[['name', 'city', 'province']])
    # [CHART2] At least two different charts with matplotlib, including titles, colors, labels, legends, as appropriate, one can be a table
    city_counts = data['city'].value_counts().head(10)
    fig2, ax2 = plt.subplots()
    city_counts.plot(kind="bar", ax=ax2, color="thistle")
    ax2.set_title("Top 10 Cities by Number of Restaurants")
    ax2.set_xlabel("City")
    ax2.set_ylabel("Number of Restaurants")
    st.pyplot(fig2)

    # [EXTRA][SEA2] 2 Seaborn charts
    st.subheader("Seaborn Countplot")
    if not filtered_data.empty:
        fig4, ax4 = plt.subplots()
        top_cities = city_counts.head().index.tolist()
        sns.countplot(y='city',
                      data=filtered_data[filtered_data['city'].isin(top_cities)],
                      order=top_cities, ax=ax4)
        ax4.set_title("Top Cities")
        st.pyplot(fig4)

elif page == "Summary & Analytics":
    st.header("Summary & Extra Analytics")
    # [PY3] Error checking with try/except
    try:
        st.write("Sample Restaurant Count:")
        for k, v in list(name_count.items())[:3]:
            st.write(f"{k}: {v}")
    except Exception as e:
        st.error(f"Error: {e}")
    # [DA2] Sort data by city
    city_sort = data['city'].value_counts().sort_values(ascending=False)
    st.write("Cities With The Most Restaurants:")
    st.write(city_sort.head(3))
    # [DA3] Find Top largest or smallest values of a column
    top_restaurants = data['name'].value_counts().head(3)
    st.write("Top Restaurants:")
    st.write(top_restaurants)
    # [DA9] Add a new column or perform calculations on DataFrame columns
    data['city_state'] = data['city'] + "," + data['province']
    # [DA6] Analyze data with pivot tables
    pivot = pd.pivot_table(data, index='province', columns='name', aggfunc='size', fill_value=0)
    # [DA7] Add/drop/select/create new/group columns
    group_cities = data.groupby('city').size().sort_values(ascending=False).head(5)
    st.sidebar.write("Top 5 Cities with Most Restaurants:")
    st.sidebar.write(group_cities)
    # [DA8] Iterate through rows of a DataFrame with iterrows()
    for idx, row in data.head(1).iterrows():
        st.write(f"{idx}: {row['name']} in {row['city']}, {row['province']}")
    # [PY5] A dictionary where you write code to access its keys, values, or items
    st.write("Restaurant Dictionary Keys:", list(name_count.keys())[:5])
    # [EXTRA][FOLIUM2] Maps made with Folium
    st.subheader("Folium Heatmap of all Locations")
    from folium.plugins import HeatMap
    m2 = folium.Map(location=[data['latitude'].mean(), data['longitude'].mean()])
    HeatMap(data[['latitude', 'longitude']].dropna().values.tolist()).add_to(m2)
    st_folium(m2, width=700, height=400)
    # [EXTRA][PACKAGE]
    st.write("Average number of categories per restaurant:", np.mean(data['numbered_categories']))
