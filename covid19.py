#!/usr/bin/env python
# coding: utf-8

# In[1]:


from PIL import Image
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import RendererAgg
_lock = RendererAgg.lock
import calendar
import math


# In[2]:


st.set_page_config(page_title='Covid19 - Kenya', layout='wide', initial_sidebar_state='auto')


# In[3]:


st.markdown("<h1 style='text-align: center; color: white;'>Covid19 Dashboard - Kenya</h1>", unsafe_allow_html=True)

page_bg_img = '''
<style>
body {
background-image: url('https://wallpaperaccess.com/full/3257326.jpg');
background-size: cover;
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)


# In[4]:


data_load_state = st.text('Loading data...')

cases_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
recoveries_url ='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'
deaths_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
ke_url = 'https://raw.githubusercontent.com/Munga-Em/Covid19-dashboard-Kenya/main/covid19KE.csv'
codes_url = 'https://raw.githubusercontent.com/Munga-Em/Covid19-dashboard-Kenya/main/codes.csv'
data        = pd.read_csv(ke_url)
worldwide   = pd.read_csv(cases_url)
recoveries  = pd.read_csv(recoveries_url)
deaths      = pd.read_csv(deaths_url)
codes       = pd.read_csv(codes_url)

data_load_state.text('Loading data...done!')


# In[5]:


#list of months for sorting data where necessary
cats = ['Jan', 'Feb', 'Mar', 'Apr','May','Jun', 'Jul', 'Aug','Sep', 'Oct', 'Nov', 'Dec']

#fill missing values in Kenya dataframe
data = data.fillna(0)
data = data.rename(columns=lambda x: x.strip())


#Cases, scope - Kenya
casesKE = worldwide[worldwide['Country/Region']=='Kenya']
casesKE = casesKE.stack().reset_index()

#Recoveries, scope - Kenya
recKE = recoveries[recoveries['Country/Region']=='Kenya']
recKE = recKE.stack().reset_index()

#Deaths, scope - Kenya
deathsKE = deaths[deaths['Country/Region']=='Kenya']
deathsKE = deathsKE.stack().reset_index()

#Kenya recovery and fatality rates
fatalityperc = deathsKE.iloc[-1, 2]/casesKE.iloc[-1, 2]
recoveryperc = recKE.iloc[-1, 2]/casesKE.iloc[-1, 2]

#Values for plotting donut charts on fatality and recovery   
fatality_values =[deathsKE.iloc[-1, 2], casesKE.iloc[-1, 2]-deathsKE.iloc[-1, 2]]  
recovery_values =[recKE.iloc[-1, 2], casesKE.iloc[-1, 2]-recKE.iloc[-1, 2]]


# In[6]:


#Daily cases in Kenya
casesKE1 = casesKE.drop('level_0', axis=1).rename(columns = {'level_1':'Date', 0:'Total cases'}).drop([0,1,2], axis=0)
casesKE1['Total cases'] = pd.to_numeric(casesKE1['Total cases'])
casesKE1['cases'] = casesKE1['Total cases'].diff().fillna(0)

#Daily recoveries in Kenya
recKE1 = recKE.drop('level_0', axis=1).rename(columns = {'level_1':'Date', 0:'Total recoveries'}).drop([0,1,2], axis=0)
recKE1['Total recoveries'] = pd.to_numeric(recKE1['Total recoveries'])
recKE1['recoveries'] = recKE1['Total recoveries'].diff().fillna(0)

#Daily deaths in Kenya
deathsKE1 = deathsKE.drop('level_0', axis=1).rename(columns = {'level_1':'Date', 0:'Total deaths'}).drop([0,1,2], axis=0)
deathsKE1['Total deaths'] = pd.to_numeric(deathsKE1['Total deaths'])
deathsKE1['deaths'] = deathsKE1['Total deaths'].diff().fillna(0)

#Merge the three dataframes to one
KE_data = casesKE1.merge(recKE1, on = 'Date', how ='right')
KE_data = KE_data.merge(deathsKE1, on = 'Date', how = 'right')
KE_data['Date'] = pd.to_datetime(KE_data['Date'])

#Merge and replace KE_data on recoveries with data from MoH
data['Date'] = pd.to_datetime(data['Date'])
recs1 = data.iloc[:, [0,5]]
KE_data = KE_data.merge(recs1)


# In[7]:


#Kenya figures aggregated by sum, monthly
KE_data1 = KE_data.set_index('Date')
KE_monthly = KE_data1.resample('M').ffill().reset_index()
KE_monthly['month'] = KE_monthly['Date'].dt.month
KE_monthly['month'] = KE_monthly['month'].apply(lambda x: calendar.month_abbr[x])
KE_monthly['month'] = pd.Categorical(KE_monthly['month'], categories=cats, ordered=True)

#Positivity rate
data['Date'] = pd.to_datetime(data['Date'])
data.columns = data.columns.str.strip()
data2 = pd.DataFrame(data.iloc[:,:7])
data2 = data2.fillna(0)
data2['month1'] = data2['Date'].dt.month
data2['month'] = data2['month1'].apply(lambda x: calendar.month_abbr[x])
data2['rate'] = data2['Positive cases']/data2['Sample size']

#Cumulative cases by gender
data3 = data2.drop(['Date','rate','month1'], axis=1).fillna(0)
data3 = data3.groupby(['month']).sum()
data3.index = pd.CategoricalIndex(data3.index, categories=cats, ordered=True)
data3 = data3.sort_index()
data3 = data3.cumsum(axis=0)
data3 = data3.reset_index()

#Monthly cases by gender
gender = data.iloc[:,[0,3,4]]
gender = gender.fillna(0).reset_index()
gender['month1'] = gender['Date'].dt.month
gender['month'] = gender['month1'].apply(lambda x: calendar.month_abbr[x])
gender['Month_yr'] = gender['Date'].dt.strftime('%b-%Y')
gender = pd.pivot_table(gender, values=['Male','Female'], index='month',aggfunc=sum)
gender.index = pd.CategoricalIndex(gender.index, categories=cats, ordered=True)
gender = gender.sort_index()
gender = gender.reset_index()


# In[8]:


#define a function to tranform raw worldwide data to the desired format

def wrangle(raw_data):
    raw_data = raw_data.rename(columns={"Country/Region": "Country"}).drop(['Province/State', 'Lat', 'Long'], axis=1)
    raw_data = raw_data.groupby('Country').sum().reset_index().set_index('Country')
    raw_data = raw_data.stack().reset_index()
    raw_data = raw_data.rename(columns={'level_1':'Date'})
    raw_data['Date'] = pd.to_datetime(raw_data['Date'])
    raw_data['month'] = raw_data['Date'].dt.month
    raw_data['Month_yr'] = raw_data['Date'].dt.strftime('%b-%Y')
    raw_data = raw_data[raw_data['Country']!='Diamond Princess']
    raw_data = raw_data[raw_data['Country']!='MS Zaandam']
    raw_data = raw_data.set_index('Date')
    raw_data = raw_data.groupby([raw_data.index.strftime('%Y-%m'), 'Country']).tail(1)
    df = pd.DataFrame(raw_data)
    return df


# In[9]:


#Transform the data using the function above
worldwide_cases = wrangle(worldwide)
worldwide_recovs = wrangle(recoveries)
worldwide_deaths = wrangle(deaths)


# In[10]:


#Rename columns appropriately
worldwide_cases = worldwide_cases.rename(columns={0:'Cases'})
worldwide_recovs = worldwide_recovs.rename(columns={0:'recovs'})
worldwide_deaths = worldwide_deaths.rename(columns={0:'deaths'})


# In[11]:


#Merge the dataframes and calculate active cases
world1 = worldwide_cases.merge(worldwide_recovs)
world1 = world1.merge(worldwide_deaths)
world1['Active cases'] = world1['Cases'] - world1['deaths'] - world1['recovs']
world_cases = world1.merge(codes, how='left')


# In[12]:


#Get cases in Africa for the map
Africa_cases = world_cases[world_cases['Continent'] == 'Africa']


# In[13]:


#Get maximum and mid number of active cases, for the colorbar ranges
max_cases = world_cases['Active cases'].max()
max_cases_africa = Africa_cases['Active cases'].max() 

mid_point = world_cases['Active cases'].median()
mid_cases_africa = Africa_cases['Active cases'].median()


# In[14]:


#Cases per county, show top 10 counties only, per month
data1 = data.set_index('Date')
data5 = pd.DataFrame(data1.iloc[:,6:].stack())
data5.index.names = ['Date', 'County']
data5 = data5.rename(columns={0: "new cases"}).reset_index()
data5['month'] = data5['Date'].dt.month
data5['Month_yr'] = data5['Date'].dt.strftime('%b-%Y')
data5 = data5.drop(['Date'], axis=1)
data5 = data5.groupby(['month', 'Month_yr','County'], as_index=False)['new cases'].sum()
data5['total_cases'] = data5.groupby('County')['new cases'].transform('cumsum')
data6 = data5.sort_values(by=['month', 'total_cases'], ascending=[True, False]).groupby('month').head(10)


# In[15]:


counties = data6.iloc[-10: , 2].to_list()
data7 =[]

for county in counties:
    data7.append(data5[data5['County']== county])


# In[16]:


data8 = pd.concat(data7).sort_values(by=['month', 'total_cases'], ascending = [True, False])


# In[17]:


st.markdown("<h1 style='text-align: left; color: black;'>Overview</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.beta_columns(3)

with col1:
    with _lock:
        fig, axs = plt.subplots(nrows=2, ncols=2, sharex=True, sharey=True)
        axs[0,0].text(0.5,0.5, '{:,.0f}'.format(data['Sample size'].sum()), fontsize=30, weight='bold', ha='center', color='gray')
        axs[0,0].text(0.5,0.3, 'tests done', fontsize=18, ha='center', color='white')
        axs[1,0].text(0.5,0.5, '{:,.0f}'.format(casesKE.iloc[-1, 2]), fontsize=30, weight='black', ha='center', color='orange')
        axs[1,0].text(0.5,0.3, ' positive cases', fontsize=18, ha='center', color='white')
        axs[0,1].text(0.5,0.5, '{:,.0f}'.format(recKE.iloc[-1, 2]), fontsize=30, weight='heavy', ha='center', color='green')
        axs[0,1].text(0.5,0.3, ' recoveries', fontsize=18, ha='center', color='white')
        axs[1,1].text(0.5,0.5, '{:,.0f}'.format(deathsKE.iloc[-1, 2]), fontsize=30, weight='extra bold', ha='center', color='red')
        axs[1,1].text(0.5,0.3, ' deaths', fontsize=18, ha='center', color='white')
        for i in range(2):
            for j in range(2):
                axs[i, j].axis('off')
                axs[i, j].xaxis.set_major_locator(plt.NullLocator())
                axs[i, j].yaxis.set_major_locator(plt.NullLocator())
        plt.grid(False)
        plt.gca().patch.set_facecolor('0.0')
        fig.patch.set_alpha(0.0)
        st.pyplot(fig)
        
with col2:
    fig = go.Figure(data=[go.Pie(values=recovery_values, hole=.9, hoverinfo='skip')])
    config = {'displayModeBar': False}
    fig.update_layout(title={'text': 'Recovery rate', 'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'})
    fig.add_annotation(x=0.5, y=0.5, text=("{:.2%}".format(recoveryperc) + ' of total cases'), showarrow=False)
    fig.update_traces(textinfo='none', hoverinfo='skip')
    trace = dict(hoverinfo='skip')
    fig.layout.update(showlegend=False, font=dict(size=18, color='white'), paper_bgcolor='rgba(0,0,0,0)',
                                                   plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, config = config, use_container_width=True)   
    
with col3:
    fig = go.Figure(data=[go.Pie(values=fatality_values, hole=.9, hoverinfo='skip')])
    config = {'displayModeBar': False}
    fig.update_layout(title={'text': 'Fatality rate', 'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'})
    fig.add_annotation(x=0.5, y=0.5, text=("{:.2%}".format(fatalityperc) + ' of total cases'), showarrow=False)
    fig.update_traces(textinfo='none')
    trace = dict(hoverinfo='skip')
    fig.layout.update(showlegend=False, font=dict(size=18, color='white'), paper_bgcolor='rgba(0,0,0,0)',
                                                  plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, config=config, use_container_width=True)


# In[18]:


col3, col4 = st.beta_columns(2)

with col3:
    st.markdown("<h2 style='text-align: center; color: white;'>Positivity rate</h2>", unsafe_allow_html=True)
    fig = px.line(data2, x='Date', y='rate', hover_data={'Date': False}, height = 600)
    fig.layout.update(hovermode='x', yaxis=dict(title='Rate', titlefont=dict(size=18), color = '#FFFFFF', tickformat= ',.2%',
                                                visible=True, showgrid=False),
                      xaxis=dict(title='Date', titlefont=dict(size=18), color = '#FFFFFF', showline=False, showgrid=False),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hoverlabel=dict(font_size=16,
                                                                                                   bgcolor='white',
                                                                                                   font_family='Rockwell'))
    fig.update_traces(hovertemplate=None)
    st.plotly_chart(fig, config=config, use_container_width=True)
    
with col4:
    st.markdown("<h2 style='text-align: left; color: white;'>Daily confirmed cases, recoveries and fatalities</h2>",
                unsafe_allow_html=True)
    fig = px.line(KE_data, x='Date', y =['cases','Recoveries','deaths'], hover_data={'Date': False},
                  color_discrete_map={'cases': '#0000FF',
                                      'Recoveries': '#008000',
                                      'deaths':'#8B0000'},
                 height = 600)
    fig.layout.update(hovermode='x',
                      yaxis=dict(title='Count', titlefont=dict(size=18), color = '#FFFFFF',
                                 tickformat=',.0f', visible=True, showgrid=False, dtick=500),
                      xaxis=dict(title='Date', titlefont=dict(size=18), color = '#FFFFFF', showline=False, showgrid=False),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hoverlabel=dict(font_size=16,
                                                                                                   bgcolor='white',
                                                                                                   font_family='Rockwell'),
                     legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(family="Courier", size=18, color='white')))
    fig.update_layout(legend_title_text='')
    fig.update_traces(hovertemplate=None)
    st.plotly_chart(fig, config=config, use_container_width=True)


# In[19]:


col5, col6 = st.beta_columns(2)

with col5:
    st.markdown("<h2 style='text-align: center; color: white;'>Monthly positive cases by gender</h2>",
                unsafe_allow_html=True)
    fig = px.bar(gender, x ='Month_yr', y = ['Male','Female'], hover_data={'month': False, 'value':':,.0f'}, height = 600)
    fig.layout.update(hovermode='x', yaxis=dict(title='Count', titlefont=dict(size=18), color = '#FFFFFF', tickformat=',.0f',
                                                visible=True, showgrid=False),
                      xaxis=dict(title='Month', titlefont=dict(size=18), color = '#FFFFFF', showline=True, showgrid=False),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hoverlabel=dict(font_size=16,
                                                                                                   bgcolor='white',
                                                                                                   font_family='Rockwell'),
                     legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(family="Courier", size=18, color='white')))
    fig.update_traces(hovertemplate=None)
    fig.update_layout(legend_title_text='')
    st.plotly_chart(fig, config=config, use_container_width=True)
    
with col6:
    st.image('https://images.squarespace-cdn.com/content/v1/5a5baed98dd041eb3ccb3b54/1587154921968-9AMAU6PK1GBTUMK4G9J1/ke17ZwdGBToddI8pDm48kOMRtONU7S1qv5qBL4yMXihZw-zPPgdn4jUwVcJE1ZvWQUxwkmyExglNqGp0IvTJZamWLI2zvYWH8K3-s_4yszcp2ryTI0HqTOaaUohrI8PIh8syG9K-XlBOeDXbnxME-_Pv-Us1_JucYSxo44gphNUKMshLAGzx4R3EDFOm1kBS/signs+and+symptomes+graphic+small.jpg', width = 600)


# In[20]:


col7, col8 = st.beta_columns(2)

with col7:
    st.markdown("<h2 style='text-align: center; color: white;'>Total cases, recoveries and fatalities</h2>",
                unsafe_allow_html=True)
    fig = px.line(KE_monthly, x='month',y = ['Total cases','Total recoveries','Total deaths'],
                  hover_data={'value':':,.0f','month': False}, color_discrete_map={'Total cases': '#0000FF',
                                                                                   'Total recoveries': '#008000',
                                                                                   'Total deaths':'#8B0000'},
                 height = 600)
    fig.layout.update(hovermode='x', yaxis=dict(title='Count', titlefont=dict(size=18), color = '#FFFFFF', tickformat=',.0f',
                                                        visible=True, showgrid=False),
                      xaxis=dict(title='Month-2020', titlefont=dict(size=18), color = '#FFFFFF', showline=False, showgrid=False),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hoverlabel=dict(font_size=16,
                                                                                                   bgcolor='white',
                                                                                                   font_family='Rockwell'),
                     legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(family="Courier", size=18, color='white')))
    fig.update_traces(hovertemplate=None)
    fig.update_layout(legend_title_text='')
    st.plotly_chart(fig, config=config, use_container_width=True)
    
with col8:
    st.markdown("<h2 style='text-align: center; color: white;'>Total cases by gender</h2>",
                unsafe_allow_html=True)
    fig = px.line(data3, x='month', y = ['Male','Female'], hover_data = {'month': False}, height = 600)
    fig.layout.update(hovermode='x', yaxis=dict(title='Count', titlefont=dict(size=18), color = '#FFFFFF', tickformat=',.0f',
                                                        visible=True, showgrid=False),
                      xaxis=dict(title='Month-2020', titlefont=dict(size=18), color = '#FFFFFF', showline=False, showgrid=False),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hoverlabel=dict(font_size=16,
                                                                                                   bgcolor='white',
                                                                                                   font_family='Rockwell'),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(family="Courier", size=18, color='white')))
    fig.update_traces(hovertemplate=None)
    fig.update_layout(legend_title_text='')
    st.plotly_chart(fig, config=config, use_container_width=True)


# In[21]:


col9, col10 = st.beta_columns(2)

with col9:
    st.markdown("<h2 style='text-align: center; color: white;'>Positive cases per county over time</h2>",
                unsafe_allow_html=True)
    st.markdown("<p style='text-align: left; color: white;'>Showing top 10 counties only</p>",
                unsafe_allow_html=True)
    
    data = []
    x_axis_data = []
    y_axis_data = []

    for county in data7:
        x_axis = county['month'].to_list()
        y_axis = county['total_cases'].to_list()
        x_axis_data.append(x_axis)
        y_axis_data.append(y_axis)


    for i, j in zip(x_axis_data, y_axis_data):
        data.append(go.Scatter(x=np.array([1]), y=np.array(y_axis_data[0]), mode='lines'))
    
    

    layout = {'xaxis' :{'range': [3, x_axis_data[0][-1]], "title": "Month", "titlefont": {'size': 18},
                        'showline': True, 'showgrid': False, 'color': '#FFFFFF'},
              'yaxis' :{'range': [0, math.ceil((data5['total_cases'].max()/1000))*1000], "title": "Positive cases",
                       "titlefont": {'size': 18}, 'color': '#FFFFFF',
                        'tickformat': ',.0f', 'visible': True, 'showgrid': False},
              'hovermode' :'x',
              'updatemenus' :[
                  {'buttons' : [
                      {"args": [None, {"frame": {"duration": 2000, "redraw": True},
                                       "fromcurrent": True,
                                       "transition": {"duration": 2000, "easing": "cubic-in-out"}}],
                       "label": "Play",
                       "method": "animate"
                      },
                      {"args": [[None], {"frame": {"duration": 0, "redraw": False},
                                         "mode": "immediate",
                                         "transition": {"duration": 0}}],
                       "label": "Pause",
                       "method": "animate"
                      }
                  ],
                   "direction": "left",
                   "pad": {"r": 10, "t": 87},
                   "showactive": False,
                   "type": "buttons",
                   "x": 0.1,
                   "xanchor": "right",
                   "y": 0,
                   "yanchor": "top"}
              ]
             }

    sliders = {"active": 0,
               "yanchor": "top",
               "xanchor": "left",
               "currentvalue": {"font": {"size": 20},
                                "prefix": "month:",
                                "visible": True,
                                "xanchor": "right"},
               "transition": {"duration": 200, "easing": "cubic-in-out"},
               "pad": {"b": 10, "t": 50},
               "len": 0.9,
               "x": 0.1,
               "y": 0,
               "steps": []
              }

    frames = []

    for month in data8['month'].unique():
        frame = {"data": [], "name": str(month)}
        for county in data8['County'].unique():
            data_by_month = data8[data8['month'] <= int(month)]
            data_by_month_county = data_by_month[data_by_month['County'] == county]
            data_dict = {
                "x": list(data_by_month_county['month']),
                "y": list(data_by_month_county['total_cases']),
                "mode": 'lines',
                "name": county
            }
            frame["data"].append(data_dict)
        
        frames.append(frame)
        slider_step = {"args": [[month],
                                {"frame": {"duration": 2000, "redraw": True},
                                 "mode": "immediate",
                                 "transition": {"duration": 2000}}
                               ],
                       "label": str(month),
                       "method": "animate"}
        sliders["steps"].append(slider_step)


    layout['sliders'] = [sliders]
    
    fig = go.Figure(
        data = data,
        layout =layout,
        frames = frames
    )

    fig.layout.update(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      hoverlabel=dict(font_size=16, font_family='Rockwell'),
                     legend=dict(font=dict(family="Courier", size=14, color='white')),
                      autosize=False, width=800, height=500)
    fig.layout.updatemenus[0].font = (dict(color='white'))
    fig.layout.sliders[0].currentvalue =(dict(prefix='Month:')) 
    fig.layout.sliders[0].font =(dict(color='white'))
    fig.update_traces(hovertemplate=None)


    st.plotly_chart(fig, config = config, use_column_width=True)
    
with col10:
    st.markdown("<h2 style='text-align: center; color: white;'>Active cases over time - Africa</h2>",
                unsafe_allow_html=True)

    fig = px.choropleth(Africa_cases,locations='Country', locationmode='country names',
                        color='Active cases', animation_frame='Month_yr', hover_name='Country',
                        hover_data = {'Active cases':':,.0f','Country': False,
                                      'month': False, 'period': Africa_cases['Month_yr']},
                        animation_group='Active cases', color_continuous_scale='reds',
                        range_color=[0,max_cases_africa], color_continuous_midpoint=mid_cases_africa,
                        scope='africa', center=None,  width=1000, height=800)
    fig.update_geos(fitbounds="locations", visible = False, showcoastlines=True, coastlinecolor="RebeccaPurple", showcountries = True,
                    showland=True,showocean=True, oceancolor="LightBlue", showlakes=True, lakecolor="Blue")
    fig.layout.update(yaxis=dict(titlefont=dict(size=18), color = '#FFFFFF', showgrid=False),
                      xaxis=dict(titlefont=dict(size=18), color = '#FFFFFF', showgrid=False))
    fig.update_layout(hovermode='x unified', height=800, width =1000, coloraxis_colorbar_x=-0.2,
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)', hoverlabel=dict(font_size=16, bgcolor='white', font_family='Rockwell'),
                     coloraxis_colorbar=dict(title='', tickfont=dict(size=14, color='white')))
    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1000
    fig.layout.updatemenus[0].font = (dict(color='white'))
    fig.layout.sliders[0].currentvalue =(dict(prefix='Month:')) 
    fig.layout.sliders[0].font =(dict(color='white'))
    fig.update_traces(hovertemplate=None)
    st.plotly_chart(fig, config=config, use_container_width=True)


# In[22]:


st.markdown("<p style='text-align: left; color: white;'>View world map of active cases over time</p>",
                unsafe_allow_html=True)
if st.checkbox('Show map'):
    fig = px.choropleth(world_cases,locations='Country', locationmode='country names', color='Active cases',
                        animation_frame='Month_yr', hover_name='Country', hover_data = {'Active cases':':,.0f',
                                                                                     'Country':False,
                                                                                     'month':False,
                                                                                     'period': worldwide_cases['Month_yr']},
                        animation_group='Active cases', color_continuous_scale='reds',
                        range_color=[0,max_cases], color_continuous_midpoint=mid_point, scope='world',
                        center=None,  width=1000, height=800)
    fig.update_geos(fitbounds="locations", visible = False, showcoastlines=True, coastlinecolor="RebeccaPurple", showcountries = True,
                    showland=True,showocean=True, oceancolor="LightBlue", showlakes=True, lakecolor="Blue")
    fig.layout.update(yaxis=dict(titlefont=dict(size=18), color = '#FFFFFF', showgrid=False),
                     xaxis=dict(titlefont=dict(size=18), color = '#FFFFFF', showgrid=False))
    fig.update_layout(height=600, width =900, coloraxis_colorbar_x=-0, paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)', hoverlabel=dict(font_size=16, bgcolor='white', font_family='Rockwell'),
                    coloraxis_colorbar=dict(title='', tickfont=dict(size=14, color='white')))
    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1000
    fig.layout.updatemenus[0].font = (dict(color='white'))
    fig.layout.sliders[0].currentvalue =(dict(prefix='Month:')) 
    fig.layout.sliders[0].font =(dict(color='white'))
    fig.update_traces(hovertemplate=None)
    st.plotly_chart(fig, config=config, use_container_width=True)

