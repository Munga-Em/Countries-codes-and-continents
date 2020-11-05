#!/usr/bin/env python
# coding: utf-8

# In[1]:


from PIL import Image
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import RendererAgg
_lock = RendererAgg.lock
import calendar


# In[2]:


st.set_page_config(page_title='Covid19 - Kenya',
                        layout='wide', initial_sidebar_state='auto')


# In[3]:


st.markdown("<h1 style='text-align: center; color: red;'>Covid19 Dashboard - Kenya</h1>", unsafe_allow_html=True)

page_bg_img = '''
<style>
body {
background-image: url('https://st.depositphotos.com/1032577/3572/i/450/depositphotos_35727883-stock-photo-black-background.jpg');
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


cats = ['Jan', 'Feb', 'Mar', 'Apr','May','Jun', 'Jul', 'Aug','Sep', 'Oct', 'Nov', 'Dec']
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

#Kenya figures aggregated by sum, monthly
KE_data['Date'] = pd.to_datetime(KE_data['Date'])
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


data3 = data2.drop(['Date','rate','month1'], axis=1).fillna(0)
data3 = data3.groupby(['month']).sum()
data3.index = pd.CategoricalIndex(data3.index, categories=cats, ordered=True)
data3 = data3.sort_index()
data3 = data3.cumsum(axis=0)
data3 = data3.reset_index()

gender = data.iloc[:,[0,3,4]]
gender = gender.fillna(0).reset_index()
gender['month1'] = gender['Date'].dt.month
gender['month'] = gender['month1'].apply(lambda x: calendar.month_abbr[x])
gender = pd.pivot_table(gender, values=['Male','Female'], index='month',aggfunc=sum)
gender.index = pd.CategoricalIndex(gender.index, categories=cats, ordered=True)
gender = gender.sort_index()
gender = gender.reset_index()


# In[6]:


worldwide_cases = worldwide.rename(columns={"Country/Region": "Country"})
worldwide_cases = worldwide_cases.drop(['Province/State', 'Lat', 'Long'], axis=1)
worldwide_cases = worldwide_cases.groupby('Country').sum().reset_index()
worldwide_cases = worldwide_cases.set_index('Country')
worldwide_cases = pd.DataFrame(worldwide_cases.stack().reset_index())
worldwide_cases = worldwide_cases.rename(columns={'level_1':'Date', 0: 'Total cases'})
worldwide_cases['Date'] = pd.to_datetime(worldwide_cases['Date'])
worldwide_cases = worldwide_cases.set_index('Date')
worldwide_cases = worldwide_cases.groupby('Country', as_index=False)['Total cases'].resample('M').ffill()
worldwide_cases = worldwide_cases.set_index('Country').unstack().reset_index().rename(columns ={0:'Positive cases'})
worldwide_cases['month'] = worldwide_cases['Date'].dt.month
worldwide_cases['Month_yr'] = worldwide_cases['Date'].dt.strftime('%b-%Y')
worldwide_cases = worldwide_cases[worldwide_cases['Country']!='Diamond Princess']
worldwide_cases = worldwide_cases[worldwide_cases['Country']!='MS Zaandam']


# In[7]:


worldwide_recovs = recoveries.rename(columns={"Country/Region": "Country"}).drop(['Province/State', 'Lat', 'Long'], axis=1)
worldwide_recovs = worldwide_recovs.groupby('Country').sum().reset_index().set_index('Country')
worldwide_recovs = pd.DataFrame(worldwide_recovs.stack().reset_index())
worldwide_recovs = worldwide_recovs.rename(columns={'level_1':'Date', 0: 'Total cases'})
worldwide_recovs['Date'] = pd.to_datetime(worldwide_recovs['Date'])
worldwide_recovs = worldwide_recovs.set_index('Date')
worldwide_recovs = worldwide_recovs.groupby('Country', as_index=False)['Total cases'].resample('M').ffill()
worldwide_recovs = worldwide_recovs.set_index('Country').unstack().reset_index().rename(columns ={0:'Recoveries'})
worldwide_recovs['month'] = worldwide_recovs['Date'].dt.month
worldwide_recovs['Month_yr'] = worldwide_recovs['Date'].dt.strftime('%b-%Y')
worldwide_recovs = worldwide_recovs[worldwide_recovs['Country']!='Diamond Princess']
worldwide_recovs = worldwide_recovs[worldwide_recovs['Country']!='MS Zaandam']


# In[8]:


worldwide_deaths = deaths.rename(columns={"Country/Region": "Country"}).drop(['Province/State', 'Lat', 'Long'], axis=1)
worldwide_deaths = worldwide_deaths.groupby('Country').sum().reset_index().set_index('Country')
worldwide_deaths = pd.DataFrame(worldwide_deaths.stack().reset_index())
worldwide_deaths = worldwide_deaths.rename(columns={'level_1':'Date', 0: 'Total cases'})
worldwide_deaths['Date'] = pd.to_datetime(worldwide_deaths['Date'])
worldwide_deaths = worldwide_deaths.set_index('Date')
worldwide_deaths = worldwide_deaths.groupby('Country', as_index=False)['Total cases'].resample('M').ffill()
worldwide_deaths = worldwide_deaths.set_index('Country').unstack().reset_index().rename(columns ={0:'Deaths'})
worldwide_deaths['month'] = worldwide_deaths['Date'].dt.month
worldwide_deaths['Month_yr'] = worldwide_deaths['Date'].dt.strftime('%b-%Y')
worldwide_deaths = worldwide_deaths[worldwide_deaths['Country']!='Diamond Princess']
worldwide_deaths = worldwide_deaths[worldwide_deaths['Country']!='MS Zaandam']


# In[9]:


world1 = worldwide_cases.merge(worldwide_recovs, on = ['Date', 'Country']).drop(['month_y', 'Month_yr_y'], axis=1)
world1 = world1.rename(columns = {'month_x': 'month', 'Month_yr_x':'Month_yr'})
world1 = world1.merge(worldwide_deaths, on = ['Date', 'Country']).drop(['month_y', 'Month_yr_y'], axis=1)
world1 = world1.rename(columns = {'month_x': 'month', 'Month_yr_x':'Month_yr'})
world1['Active cases'] = world1['Positive cases'] - world1['Deaths'] - world1['Recoveries']


# In[10]:


world_cases = world1.merge(codes, how='left')


# In[11]:


max_cases = world_cases['Active cases'].max()
Africa_cases = world_cases[world_cases['Continent'] == 'Africa']
max_cases_africa = Africa_cases['Active cases'].max() 


# In[12]:


mid_point = world_cases['Active cases'].median()
mid_cases_africa = Africa_cases['Active cases'].median()


# In[13]:


data1 = data.set_index('Date')
data5 = pd.DataFrame(data1.iloc[:,6:].stack())
data5.index.names = ['Date', 'County']
data5 = data5.rename(columns={0: "new cases"}).reset_index()
data5['month'] = data5['Date'].dt.month
data5['Month_yr'] = data5['Date'].dt.strftime('%b-%Y')
data5 = data5.drop(['Date'], axis=1)
data5 = data5.groupby(['month','County', 'Month_yr'], as_index=False)['new cases'].sum()
data5['total_cases'] = data5.groupby('County')['new cases'].transform('cumsum')
data5 = data5.sort_values(by=['month', 'total_cases'], ascending=[True, False]).groupby('month').head(10)


# In[14]:


st.markdown("<h1 style='text-align: left; color: black;'>Overview</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.beta_columns((3))

with col1:
    with _lock:
        fig, axs = plt.subplots(nrows=2, ncols=2, sharex=True, sharey=True)
        axs[0,0].text(0.5,0.5, '{:,.0f}'.format(data['Sample size'].sum()), fontsize=30, weight='bold', ha='center', color='gray')
        axs[0,0].text(0.5,0.3, 'tests done', fontsize=18, ha='center')
        axs[1,0].text(0.5,0.5, '{:,.0f}'.format(casesKE.iloc[-1, 2]), fontsize=30, weight='black', ha='center', color='orange')
        axs[1,0].text(0.5,0.3, ' positive cases', fontsize=18, ha='center')
        axs[0,1].text(0.5,0.5, '{:,.0f}'.format(recKE.iloc[-1, 2]), fontsize=30, weight='heavy', ha='center', color='green')
        axs[0,1].text(0.5,0.3, ' recoveries', fontsize=18, ha='center')
        axs[1,1].text(0.5,0.5, '{:,.0f}'.format(deathsKE.iloc[-1, 2]), fontsize=30, weight='extra bold', ha='center', color='red')
        axs[1,1].text(0.5,0.3, ' deaths', fontsize=18, ha='center')
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
    fig.layout.update(showlegend=False, font=dict(size=18, color='green'), paper_bgcolor='rgba(0,0,0,0)',
                                                   plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, config = config)   
    
with col3:
    fig = go.Figure(data=[go.Pie(values=fatality_values, hole=.9, hoverinfo='skip')])
    config = {'displayModeBar': False}
    fig.update_layout(title={'text': 'Fatality rate', 'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'})
    fig.add_annotation(x=0.5, y=0.5, text=("{:.2%}".format(fatalityperc) + ' of total cases'), showarrow=False)
    fig.update_traces(textinfo='none')
    trace = dict(hoverinfo='skip')
    fig.layout.update(showlegend=False, font=dict(size=18, color='green'), paper_bgcolor='rgba(0,0,0,0)',
                                                  plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, config=config)


# In[15]:


col4, col5 = st.beta_columns(2)
    
with col4:
    st.markdown("<h2 style='text-align: center; color: green;'>Positivity rate</h2>", unsafe_allow_html=True)
    fig = px.line(data2, x='Date', y='rate',hover_data={'Date': False})
    fig.layout.update(hovermode='x', yaxis=dict(title='Rate', titlefont=dict(size=18), tickformat= ',.2%',
                                                visible=True, showgrid=False),
                      xaxis=dict(title='Date', titlefont=dict(size=18), showline=True, showgrid=False),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hoverlabel=dict(font_size=16,
                                                                                                   bgcolor='white',
                                                                                                   font_family='Rockwell'))
    fig.update_traces(hovertemplate=None)
    st.plotly_chart(fig)
    
with col5:
    st.markdown("<h2 style='text-align: left; color: green;'>Daily confirmed cases, recoveries and fatalities</h2>",
                unsafe_allow_html=True)
    fig = px.line(KE_data, x='Date', y =['cases','recoveries','deaths'],
                  hover_data={'value':':,.0f','Date': False},
                  color_discrete_map={'cases': '#0000FF',
                                      'recoveries': '#00FF00',
                                      'deaths':'#8B0000'})
    fig.layout.update(hovermode='x', yaxis=dict(title='Count', titlefont=dict(size=18), tickformat=',.0f',
                                                        visible=True, showgrid=False),
                      xaxis=dict(title='Date', titlefont=dict(size=18), showline=True, showgrid=False),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hoverlabel=dict(font_size=16,
                                                                                                   bgcolor='white',
                                                                                                   font_family='Rockwell'))
    fig.update_traces(hovertemplate=None)
    st.plotly_chart(fig)


# In[16]:


col6, col7 = st.beta_columns(2)
with col6:
    st.markdown("<h2 style='text-align: center; color: green;'>Monthly positive cases by gender</h2>",
                unsafe_allow_html=True)
    fig = px.bar(gender, x ='month', y = ['Male','Female'], hover_data={'month': False, 'value':':,.0f'})
    fig.layout.update(hovermode='x', yaxis=dict(title='Count', titlefont=dict(size=18), tickformat=',.0f',
                                                visible=True, showgrid=False),
                      xaxis=dict(title='Month', titlefont=dict(size=18), showline=True, showgrid=False),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hoverlabel=dict(font_size=16,
                                                                                                   bgcolor='white',
                                                                                                   font_family='Rockwell'))
    fig.update_traces(hovertemplate=None)
    st.plotly_chart(fig)
    
with col7:
    
    st.image('https://images.squarespace-cdn.com/content/v1/5a5baed98dd041eb3ccb3b54/1587154921968-9AMAU6PK1GBTUMK4G9J1/ke17ZwdGBToddI8pDm48kOMRtONU7S1qv5qBL4yMXihZw-zPPgdn4jUwVcJE1ZvWQUxwkmyExglNqGp0IvTJZamWLI2zvYWH8K3-s_4yszcp2ryTI0HqTOaaUohrI8PIh8syG9K-XlBOeDXbnxME-_Pv-Us1_JucYSxo44gphNUKMshLAGzx4R3EDFOm1kBS/signs+and+symptomes+graphic+small.jpg', width=600)


# In[17]:


col8, col9 = st.beta_columns(2)
with col8:
    st.markdown("<h2 style='text-align: center; color: green;'>Total cases, recoveries and fatalities</h2>",
                unsafe_allow_html=True)
    fig = px.line(KE_monthly, x='month',y = ['Total cases','Total recoveries','Total deaths'],
                  hover_data={'value':':,.0f','month': False}, color_discrete_map={'Total cases': '#0000FF',
                                                                                   'Total recoveries': '#00FF00',
                                                                                   'Total deaths':'#8B0000'})
    fig.layout.update(hovermode='x', yaxis=dict(title='Count', titlefont=dict(size=18), tickformat=',.0f',
                                                        visible=True, showgrid=False),
                      xaxis=dict(title='Month-2020', titlefont=dict(size=18), showline=True, showgrid=False),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hoverlabel=dict(font_size=16,
                                                                                                   bgcolor='white',
                                                                                                   font_family='Rockwell'))
    fig.update_traces(hovertemplate=None)
    st.plotly_chart(fig)
    
with col9:
    st.markdown("<h2 style='text-align: center; color: green;'>Total cases by gender</h2>",
                unsafe_allow_html=True)
    fig = px.line(data3, x='month', y = ['Male','Female'], hover_data = {'month': False})
    fig.layout.update(hovermode='x', yaxis=dict(title='Count', titlefont=dict(size=18), tickformat=',.0f',
                                                        visible=True, showgrid=False),
                      xaxis=dict(title='Month-2020', titlefont=dict(size=18), showline=True, showgrid=False),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hoverlabel=dict(font_size=16,
                                                                                                   bgcolor='white',
                                                                                                   font_family='Rockwell'))
    fig.update_traces(hovertemplate=None)
    st.plotly_chart(fig)


# In[18]:


col10, col11 = st.beta_columns(2)
with col10:
    st.markdown("<h2 style='text-align: center; color: green;'>Positive cases per county over time</h2>",
                unsafe_allow_html=True)
    st.text('Showing top 10 counties only')
    fig = px.bar(data5, x='total_cases', y='County', orientation='h', hover_name= None, color='County', hover_data = {'month': False, 'period': data5['Month_yr']},
                 animation_frame='month', animation_group='County', range_x=[0,data5.total_cases.max()])
    fig.layout.update(yaxis=dict(titlefont=dict(size=18), showgrid=False),
                      xaxis=dict(titlefont=dict(size=18), tickformat=',.0f', showline=True, showgrid=False))
    fig.update_layout(yaxis={'categoryorder':'total descending'},  paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)', hoverlabel=dict(font_size=16, bgcolor='white', font_family='Rockwell'))
    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 2000
    st.plotly_chart(fig)
    
with col11:
    st.markdown("<h2 style='text-align: center; color: green;'>Positive cases over time - Africa</h2>",
                unsafe_allow_html=True)

    fig = px.choropleth(Africa_cases,locations='Country', locationmode='country names',
                        color='Active cases', animation_frame='month', hover_name='Country',
                        hover_data = {'Active cases':':,.0f','Country': False,
                                      'month': False, 'period': Africa_cases['Month_yr']},
                        animation_group='Active cases', color_continuous_scale='reds',
                        range_color=[0,max_cases_africa], color_continuous_midpoint=mid_cases_africa,
                        scope='africa', center=None, width=900, height=600)
    fig.update_geos(showcoastlines=True, coastlinecolor="RebeccaPurple", showcountries = True,
                    showland=True,showocean=True, oceancolor="LightBlue", showlakes=True, lakecolor="Blue")
    fig.layout.update(yaxis=dict(titlefont=dict(size=18), showgrid=False),
                      xaxis=dict(titlefont=dict(size=18), showgrid=False))
    fig.update_layout(hovermode='x unified', height=800, width =1000, coloraxis_colorbar_x=-0,
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)', hoverlabel=dict(font_size=16, bgcolor='white', font_family='Rockwell'))
    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1000
    fig.update_traces(hovertemplate=None)
    st.plotly_chart(fig)


# In[19]:


st.markdown("<h2 style='text-align: left; color: green;'>Worldwide positive cases over time</h2>",
            unsafe_allow_html=True)

fig = px.choropleth(world_cases,locations='Country', locationmode='country names', color='Active cases',
                    animation_frame='month', hover_name='Country', hover_data = {'Active cases':':,.0f',
                                                                                 'Country':False,
                                                                                 'month':False,
                                                                                 'period': worldwide_cases['Month_yr']},
                    animation_group='Active cases', color_continuous_scale='reds',
                    range_color=[0,max_cases], color_continuous_midpoint=mid_point, scope='world',
                    center=None, width=900, height=600)
fig.update_geos(showcoastlines=True, coastlinecolor="RebeccaPurple", showcountries = True,
                showland=True,showocean=True, oceancolor="LightBlue", showlakes=True, lakecolor="Blue")
fig.layout.update(yaxis=dict(titlefont=dict(size=18), showgrid=False),
                  xaxis=dict(titlefont=dict(size=18), showgrid=False))
fig.update_layout(height=600, width =900, coloraxis_colorbar_x=-0.15, paper_bgcolor='rgba(0,0,0,0)',
                  plot_bgcolor='rgba(0,0,0,0)', hoverlabel=dict(font_size=16, bgcolor='white', font_family='Rockwell'))
fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1000
fig.update_traces(hovertemplate=None)
st.plotly_chart(fig)

