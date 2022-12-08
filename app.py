import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from css import get_css
import plotly.express as px


st.markdown(get_css(), unsafe_allow_html=True)
st.header("World Overview")

#PAGE LAYOUT
st.sidebar.markdown("# Welcome to Tension Predictor")
st.sidebar.write("This model predicts tension within a country based on a feature set by Global Economy using a XG Boost Classifier model. For computational reasons a lot of data has been imputed with an iterative imputer. For more information, please contact Le Wagon London.")
st.sidebar.write("Source: Global Economy")

#LOAD Data
df = pd.read_csv("animation.csv")
full_df = df[["country", "year", "prob", "code"]]

features_used = df.drop(columns=["Unnamed: 0", "target", "country", "year", "prob", "code"])
feature_list = features_used.columns
# list_of_edited = [f"Column {i}: {x}" for i, x  in enumerate(feature_list)]
# st.write(", \n ".join(x for x in list_of_edited))

feature_definition_df = pd.read_csv("feature_definition.csv")

col1, col2 = st.columns([6, 1])

#ANIMATION
# if animate:
    #SLIDER
with col1:
    data = full_df
    fig = px.choropleth(full_df,
                            locations = "code",
                            color="prob",
                            animation_frame="year",
                            color_continuous_scale="RdYlGn_r",
                            locationmode="ISO-3",
                            scope="world",
                            range_color=(0, 1),
                            title="Probability of War")

    fig.update_layout(
    autosize=False,
    width=1000,
    height=400,
    paper_bgcolor='#c29972',
    plot_bgcolor='#c29972' ,
    geo=dict(bgcolor= '#c29972', showframe=False, projection_scale=1),
    margin = dict(
                        l=0,
                        r=0,
                        b=0,
                        t=0,
                        pad=4,
                        autoexpand=True
                    )
            )

    st.write(fig)


#DISPLAY GENERAL METRICS
with col2:
    st.subheader("Key Features 2022")
    st.metric("Economic Growth", "2.09%", "0.39%")
    st.metric("Political stability index", "0.42", "6.3%")
    st.metric("Corruption Perception Index", "0.43", "0.2%")

#Choose Country

col3, col4 = st.columns([1, 1])
col5, col6 = st.columns([1,1])

with col3:
    st.markdown('## Tension analysis: country of interest')

    COUNTRY_SELECTED = st.selectbox('Select countries', data["country"].unique())


    country_chosen = full_df[full_df["country"] == COUNTRY_SELECTED]
    probability2022_country = round(list(country_chosen[country_chosen["year"] == 2022]["prob"])[0],2)


    st.write(f"{COUNTRY_SELECTED}'s tension gauge {probability2022_country} for 2022.")
    st.write(f"Conflict probability over the years for {COUNTRY_SELECTED}.")

with col5:
    def plot_country(self):
        fig_2 = plt.figure()
        ax = plt.gca()
        country_chosen[["year", "prob"]].set_index("year").plot(ax=ax, color='#246CAE')
        plt.xlabel('years')
        plt.ylabel("probability")
        plt.legend(loc="upper right")
        st.pyplot(fig_2)
    plot_country(COUNTRY_SELECTED)

with col4:
    #SENTIMENT ANALYSIS
    st.markdown(f"## Sentiment analysis: {COUNTRY_SELECTED}")

    st.write("An analysis showing positive or negative sentiment from UN General Assembly speeches. Each block is a given country's annual speech. The red shows negative tone, and the blue shows positive. The hue is dependent on the intensity.")

    #LOAD DATA
    sentiment_df = pd.read_csv("sentiment_master.csv")


with col6:
    country_code = full_df[full_df["country"] == COUNTRY_SELECTED]["code"].reset_index()["code"][0]
    if len(sentiment_df[sentiment_df["country"] == country_code]) == 0:
        st.write("Data not available")

    else:

        def sentiment_graph(df,cc, country):
            df = (df[df["country"]==cc])
            fig = go.Figure(
            data=go.Heatmap(
                z=df["Overall_Sentiment_Score"],
                x=df["year"],
                y=df["new_sentiment_score"],
                colorscale=px.colors.sequential.RdBu,
                    )
                )
            fig.update_layout(
                title=go.layout.Title(
                    text=f"Sentiment Analysis for {country}"
                ),
                autosize=False,
                width=592,
                height=451,
            )
            fig.update_layout(yaxis_autorange = "reversed")
            return fig

        sentiment_chart = sentiment_graph(df=sentiment_df,cc=country_code,country=COUNTRY_SELECTED)

        st.plotly_chart(sentiment_chart)



#Choose Feature

feature_selected = st.selectbox('Select Feature', feature_list, label_visibility="collapsed")
st.write('Definition:')
st.write(list(feature_definition_df[feature_definition_df["Feature"] == feature_selected]["Definition"])[0])

def plot_country_feature(COUNTRY_SELECTED, feature_selected):
    fig_3 = plt.figure()
    ax = plt.gca()
    df[df["country"] == COUNTRY_SELECTED][[feature_selected, "year"]].set_index("year").plot(ax=ax,color=['#246CAE','#99C270'])
    plt.xlabel('years')
    plt.ylabel(list(feature_definition_df[feature_definition_df["Feature"] == feature_selected]["Metric"])[0])
    plt.legend(loc="upper right")
    st.pyplot(fig_3)

plot_country_feature(COUNTRY_SELECTED, feature_selected)

#Choose Country to compare

st.markdown('## Comparison with another country')
COUNTRIES_COMPARE_SELECTED = st.selectbox('Select country to compare',  data["country"].unique(), index=2)
st.write(f"Conflict probability comparison over the years for {COUNTRY_SELECTED} and {COUNTRIES_COMPARE_SELECTED}")

country1 = full_df[full_df["country"] == COUNTRY_SELECTED]
country2 = full_df[full_df["country"] == COUNTRIES_COMPARE_SELECTED]

comparison = country1.merge(country2, how="outer", on="year")
comparison[COUNTRY_SELECTED] = comparison["prob_x"]
comparison[COUNTRIES_COMPARE_SELECTED] = comparison["prob_y"]
comparison.drop(columns=["country_x", "code_x", "country_y", "code_y", "prob_x", "prob_y"], inplace=True)

def plot_country_compare(COUNTRY_SELECTED, COUNTRIES_COMPARE_SELECTED):
    fig_4 = plt.figure()
    x = comparison["year"]
    y1= comparison[COUNTRY_SELECTED]
    y2=comparison[ COUNTRIES_COMPARE_SELECTED]
    #plt.plot(ax=ax, x=x, y=y,color=['#7099C2','#99C270'])
    plt.plot(x, y1, "-b", label=COUNTRY_SELECTED)
    plt.plot(x, y2, "-r", label=COUNTRIES_COMPARE_SELECTED)
    plt.gca().get_lines()[0].set_color("#246CAE")
    plt.gca().get_lines()[1].set_color('#C84541')
    plt.legend(loc="upper right")
    plt.xlabel('years')
    plt.ylabel('probability')
    st.pyplot(fig_4)

plot_country_compare(COUNTRY_SELECTED, COUNTRIES_COMPARE_SELECTED)
