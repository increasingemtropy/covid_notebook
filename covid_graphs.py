import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import numpy as np
from scipy.signal import convolve2d

import urllib.request
from io import StringIO

# Get data from the following URLS
MARKERS = 'ov^.psDPx*<>+pDov^.ps'
URL_C='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
URL_D='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
#URL_R='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv'

# Get the data from the input URLS
def get_data(url, add_total=False, n_largest=None):
    response = urllib.request.urlopen(url)
    data = response.read()      # a `bytes` object
    text = data.decode('utf-8') # a `str`; this step can't be used if data is binary

    # Create dataframe
    df = pd.read_csv(StringIO(text), sep=',') # index_col=[0, 1, 2, 3
    
    # Reshape data
    df = df.melt(id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'], var_name='Date', value_name='Cases')

    # Merge various regions of countries
    df = df.groupby(['Country/Region', 'Date']).sum()
    
    # Pivot table
    df = df.pivot_table(values='Cases', columns='Date', index='Country/Region')

    # Ignore 'Others' which refers to ships mostly
    df = df.loc[df.index != 'Cruise Ship']

    # Take only top countries ordered by the latest stats
    # if n_largest is not None:
    #     df = df.nlargest(n_largest, df.columns[-1])

    # Print some data to the console
    print(df.nlargest(10, df.columns[-1]))

    # Transpose rows/columns so that rows correspond to days
    df = df.reset_index()
    df = df.melt(id_vars=['Country/Region'], value_name='Cases')
    df = df.pivot_table(values='Cases', columns='Country/Region', index='Date')
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    # Start date is 1st February 2020
    #df = df.loc[df.index >= '2020-02-01']
    df = df.loc[df.index >= '2020-02-20']
    
    # Add a total by summing all countries
    if add_total:
        df['World'] = df.sum(axis=1)

    return df

def plot_data(df, title='', min=None, max=None, ylog=False, stack=False, subplot=111, fig=None, yticks=None, gf=False, timebase = 28):
    # ax = df.plot(logy=True)
    
    # Create new fig
    if fig is None:
        fig = plt.figure()
        
    # Add to existing fig 
    ax = fig.add_subplot(subplot)
    
    # Create x and y data for plotting 
    x = df.index.to_numpy()
    x_t = df.index.to_numpy(dtype='float64')
    y = df.to_numpy()
    
    # If the user wants a graph of Growth Rate, do some spooky mathemagic....
    # After, x and y should contain something like the exponential growth rate (NOT R)
    # This part needs better commenting!
    if gf:
        x = x[2:]
        y = y[2:]
        x_t = x_t[2:]
        # Get the y difference
        y = np.diff(y, axis=0)
        y = np.insert(y, 0, y[0],axis=0)
        y = np.insert(y, -1, y[-1], axis=0)
        # Smooth it out
        y = convolve2d(y, [[0.25], [0.5], [0.25]], mode='valid')
        # Find the difference of the log
        y = np.diff(np.log(y + 1e-3), axis=0)
        y = np.insert(y, 0, y[0],axis=0)
        y = np.insert(y, -1, y[-1], axis=0)
        y = convolve2d(y, [[0.25], [0.5], [0.25]], mode='valid')
        x = x[2:]
        x_t = x_t[2:]
        print(x.shape, y.shape)
        
    if stack:
        ax.stackplot(x, y.transpose(), labels=df.columns)
    else:
        # Mark data point every 7 days
        ax.plot(x, y, markevery=7)

    # Set axes, grid and ticks
    if min is not None and max is not None:
        ax.set_ylim([min, max])
    if ylog:
        ax.set_yscale('log')
        locmin = plticker.LogLocator(base=10.0, subs=(1,10 ))
        ax.yaxis.set_major_formatter(plticker.FormatStrFormatter("%.0f"))
        ax.yaxis.set_major_locator(locmin)

    ax.grid(axis='y', which='major', linewidth=0.8)
    ax.grid(axis='y', which='minor', linewidth=0.3)
    ax.grid(axis='x', which='both')    
    
    ax.xaxis.set_major_locator(plticker.MultipleLocator(base=timebase))
    ax.xaxis.set_minor_locator(plticker.MultipleLocator(base=timebase/2))

    if stack:
        ax.legend(loc='upper left')
    else:
        for i, line in enumerate(ax.get_lines()):
            line.set_marker(MARKERS[i])
            #line.get_color()
            if gf:
                # calc the trendline
                z = np.polyfit(x_t[4:], y[4:, i], 1)
                p = np.poly1d(z)
                ax.plot(x, p(x_t), "--", color=line.get_color())

        ax.legend(ax.get_lines(), df.columns, loc='upper left')
    
    # Set graph title
    ax.set_title(title)
    
    ax.yaxis.tick_right()
    
    return ax

# Function definitions end!
######################################################################
# MAIN starts here!

# Import data, and create difference data
df1 = get_data(URL_C, add_total=True)
df2 = df1.diff()
df3 = get_data(URL_D, n_largest=12, add_total=True)
df4 = df3.diff()

# If your internet connection is down, uncomment this to read saved data from the last session
# df1 = pd.read_csv('conf.csv',index_col='Date')
# df2 = pd.read_csv('conf_new.csv',index_col='Date')
# df3 = pd.read_csv('dead.csv',index_col='Date')
# df4 = pd.read_csv('dead_new.csv',index_col='Date')
# df1.index = pd.to_datetime(df1.index)
# df2.index = pd.to_datetime(df2.index)
# df3.index = pd.to_datetime(df3.index)
# df4.index = pd.to_datetime(df4.index)

# Countries of interest
countries1 = ['United Kingdom','Ireland', 'France', 'Italy', 'Spain', 'US', 'World']
countries2 = ['Germany','Austria', 'Denmark', 'Norway', 'Sweden', 'Finland', 'Russia']
countries3 = ['Japan','Korea, South','China']


# Create a 2x2 plot of the first two country groups, cases and deaths
if True:
    fig = plt.figure(figsize=(14, 7))
    plot_data(df2.filter(countries1).rolling(14).sum() / 2, min=1, max=df2['World'].max()*50, ylog=True, stack=False, title='Weekly cases', fig=fig, subplot=221)
    fig.set_tight_layout(True)
    
    plot_data(df4.filter(countries1).rolling(14).sum() / 2, min=1, max=df4['World'].max()*50, ylog=True, stack=False, title='Weekly deaths', fig=fig, subplot=222)
    fig.set_tight_layout(True)
    
    plot_data(df2.filter(countries2).rolling(14).sum() / 2, min=2, max=df2.filter(countries2).rolling(14).sum().max().max()*10, ylog=True, stack=False, title='Weekly cases', fig=fig, subplot=223)
    fig.set_tight_layout(True)
    
    plot_data(df4.filter(countries2).rolling(14).sum() / 2, min=2, max=df4.filter(countries2).rolling(14).sum().max().max()*10, ylog=True, stack=False, title='Weekly deaths', fig=fig, subplot=224)
    fig.set_tight_layout(True)
    
    #plt.tight_layout()
    plt.subplots_adjust(left=0.10, bottom=0.05, right=0.95, top=0.95)
    plt.show()

    
# Create 2x2 plot for different country groups
if False:
    fig = plt.figure(figsize=(14,7))
    #plot_data(df1, min=10, max=20000, ylog=True, title='Total confirmed cases', fig=fig, subplot=221)
    plot_data(df1.filter(['Italy', 'Spain', 'France', 'Germany', 'Switzerland', 'Austria', 'United Kingdom', 'Netherlands', 'Belgium', 'Portugal', 'Ireland', 'Czechia', 'Poland']), min=10, max=500000, ylog=True, title='Total confirmed cases', fig=fig, subplot=221)
    plot_data(df1.filter(['Norway', 'Sweden', 'Denmark', 'Finland', 'Estonia', 'Latvia', 'Lithuania']), min=10, max=500000, ylog=True, title='Total confirmed cases', fig=fig, subplot=222)
    plot_data(df1.filter(['US', 'Australia', 'Malaysia', 'Canada']), min=10, max=10000000, ylog=True, title='Total confirmed cases', fig=fig, subplot=223)
    plot_data(df1.filter(['China', 'Iran', 'Korea, South', 'Japan', 'Singapore', 'Bahrain']), min=10, max=2000000, ylog=True, title='Total confirmed cases', fig=fig, subplot=224)
    
    plt.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95, wspace=0.10, hspace=0.15)
#plt.tight_layout()

# Plot graphs of raw daily fatalities for a few countries of interest
if False:
    #plot_data(df2, min=10, max=10000, ylog=True, title='Daily confirmed cases')
    plot_data(df3.filter(['Italy', 'Spain', 'France', 'Germany', 'United Kingdom', 'Netherlands', 'Sweden', 'Norway', 'Finland', 'US', 'Iran']), min=1, max=50000, ylog=True, title='Total fatalities')
    #plot_data(df4, min=1, max=1000, ylog=True, yticks=[1, 2, 5, 10, 20, 50, 100, 200, 500, 1000], title='Daily fatalities')

# Plot growth rates for the world and a few selected countries
if False:
    fig = plt.figure()
    plot_data(df1.filter(['World']), min=-1, max=1, title='Growth factor', gf=True, fig=fig, subplot=221)
    plot_data(df1.filter(['United Kingdom']), min=-1, max=1, title='Growth factor', gf=True, fig=fig, subplot=222)
    plot_data(df1.filter(['US']), min=-1, max=1, title='Growth factor', gf=True, fig=fig, subplot=223)
    plot_data(df1.filter(['Germany']), min=-1, max=1, title='Growth factor', gf=True, fig=fig, subplot=224)
    plt.show()

# Produce 3 plots of weekly cases for 3 country groups    
if False:
    fig = plt.figure(figsize=(14, 7))
    filter1 = df2.filter(countries1).rolling(14).sum() / 2
    plot_data(filter1, min=1, max=filter1.max().max()*50, ylog=True, stack=False, title='Weekly cases', fig=fig)
    fig.set_tight_layout(True)
    
    fig = plt.figure(figsize=(14, 7))
    filter2 = df2.filter(countries2).rolling(14).sum() / 2
    plot_data(filter2, min=1, max=filter2.max().max()*50, ylog=True, stack=False, title='Weekly cases', fig=fig)
    fig.set_tight_layout(True)
    
    fig = plt.figure(figsize=(14, 7))
    filter3 = df2.filter(countries3).rolling(14).sum() / 2
    plot_data(filter3, min=1, max=filter3.max().max()*50, ylog=True, stack=False, title='Weekly cases', fig=fig)
    fig.set_tight_layout(True)  

# Save data from this session
df1.to_csv('conf.csv')
df2.to_csv('conf_new.csv')
df3.to_csv('dead.csv')
df4.to_csv('dead_new.csv')
