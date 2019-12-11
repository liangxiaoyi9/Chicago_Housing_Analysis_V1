# chicago_housing_analysis.py
# student: Joy Liang


import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots


def main():

    # read file
    df_all = pd.read_csv('chicago_housing_all_residential.csv', sep=',')
    df_all = df_cleaning(df_all)

    df_mort = pd.read_csv('MORTGAGE30US.csv', sep=',')
    df_mort['DATE'] = pd.to_datetime(df_mort['DATE'])

    side_list = ['Chicago, IL', 'Chicago, IL - Central Chicago', 'Chicago, IL - Far North Side',
                 'Chicago, IL - Far Southeast Side', 'Chicago, IL - Far Southwest Side', 'Chicago, IL - North Side',
                 'Chicago, IL - Northwest Side', 'Chicago, IL - South Side', 'Chicago, IL - Southwest Side',
                 'Chicago, IL - West Side']
    df_by_side = mult_area_ppsf_by_yr(df_all, side_list)
    perc_by_area = mult_area_perc_by_yr(df_all, side_list)

    side_color_list = ['firebrick', 'pink', 'green', 'lawngreen', 'olive', 'skyblue', 'purple', 'yellow',
                       'orange', 'navy']
    ppsf_by_yr_plot(df_by_side, side_color_list, 'Median Sale Price Psf in Chicago (by side)', filenm='fig1.png')
    perc_by_yr_plot(perc_by_area, side_color_list, '% Change of House Price in Chicago (by side)', filenm='fig')

    comm_list = ['Chicago, IL - Near North Side', 'Chicago, IL - The Loop', 'Chicago, IL - Near South Side',
                 'Chicago, IL - North Center', 'Chicago, IL - Lake View', 'Chicago, IL - Lincoln Park',
                 'Chicago, IL - Avondale', 'Chicago, IL - Logan Square']
    df_by_comm = mult_area_ppsf_by_yr(df_all, comm_list)
    perc_by_area = mult_area_perc_by_yr(df_all, comm_list)

    comm_color_list = ['pink', 'green', 'lawngreen', 'skyblue', 'orange', 'darkred', 'gray', 'navy']
    ppsf_by_yr_plot(df_by_comm, comm_color_list, 'The Most Expensive Communities in Chicago', filenm='fig2.png')
    perc_by_yr_plot(perc_by_area, comm_color_list, '% Change of House Price in Chicago (Community)', filenm='fig')

    # store seasonal activity data
    chi_data = season_activity(df_all, 'Chicago, IL')
    season_color_list = ['orange', 'lightblue']
    season_by_month_plot(chi_data, season_color_list, 'Seasonal Activity', filenm='fig')

    # store percentage of monthly sale data
    month_lst = list(range(1, 13))
    month_sale_share = monthly_sale_share(df_all, month_lst)
    monthly_sale_share_plot(month_sale_share, 'Share of Homes Sale in Unit by Month', filenm='fig_share.png')

    # store average monthly unit sold each year data
    unit_sold_monthly_yr = monthly_unit_sold_yr(df_all, 'Chicago, IL')
    monthly_unit_sold_yr_plot(unit_sold_monthly_yr, 'Avg Monthly Unit Sold from 2012 - 2019 in Chicago, IL',
                              filenm='fig_sale.png')

    # store mortgage rate and median sale Ppsf data
    df_chi = area_ppsf_by_yr(df_all, 'Chicago, IL')
    mort_vs_mppsf_plot(df_chi, df_mort, 'Mortgage Rate vs. House Price in Chicago', filenm='fig_mortgage.png')


def df_cleaning(df):
    """Before analysis, data needs to be cleaned up as necessary. Put all data cleaning
    steps here for organization.

    :param df: dataframe that needs cleaning
    :return: the same dataframe that has been cleaned up
    :raises: error if input is not a dataframe

    >>> df_all = pd.read_csv('chicago_housing_all_residential_test.csv', sep=',')
    >>> df_all = df_cleaning(df_all)
    >>> df_all['Period Begin'].dtypes == 'datetime64[ns]'
    True
    >>> df_all['Period End'].dtypes == 'datetime64[ns]'
    True
    >>> df_all['Median Sale Ppsf'].dtypes == 'float64'
    True
    >>> test_data = {'Chicago, IL': 200}
    >>> test_data = df_cleaning(test_data)
    Traceback (most recent call last):
    ValueError: Input must be a dataframe.
    """

    if not isinstance(df, pd.DataFrame):
        raise ValueError('Input must be a dataframe.')

    df['Median Sale Price'] = [x[1:] for x in df['Median Sale Price'].str.replace('K', '000')]
    df['Median Sale Price'] = df['Median Sale Price'].str.replace(',', '')
    df['Median Sale Price'] = pd.to_numeric(df['Median Sale Price'])
    df['Period Begin'] = pd.to_datetime(df['Period Begin'])
    df['Period End'] = pd.to_datetime(df['Period End'])
    df['Month'] = df['Period Begin'].dt.month
    df['Year'] = df['Period Begin'].dt.year
    # df.head(15)

    return df


def area_ppsf_by_yr(df, region):
    """Returns medium sale price per square foot by year, given the residential dataframe and
    specified region.

    :param df: The specific dataframe imported in the main function
    :param region: Specified region/area/community
    :return: a dataframe reflecting the specified region's medium sale ppsf by year

    >>> df_all = pd.read_csv('chicago_housing_all_residential_test.csv', sep=',')
    >>> df_all = df_cleaning(df_all)
    >>> df_by_area = area_ppsf_by_yr(df_all, 'Chicago, IL metro area')
    >>> float(df_by_area.values)
    98.43043363
    """

    area_data = df[df['Region'] == region]  # get area information
    area_data_by_yr = area_data.groupby(area_data['Year'])['Median Sale Ppsf'].median()

    return area_data_by_yr


def mult_area_ppsf_by_yr(df, region_list):
    """Given a list of regions, loop through and return medium sale price per square foot by year
    for all the specified regions on the list.

    :param df: The specific dataframe imported in the main function
    :param region_list: A list of specified regions/areas/communities
    :return: A dictionary reflecting the list of regions and its corresponding medium sale ppsf by year

    >>> df_all = pd.read_csv('chicago_housing_all_residential_test.csv', sep=',')
    >>> df_all = df_cleaning(df_all)
    >>> area_list = ['Chicago, IL', 'Chicago, IL - Central Chicago', 'Chicago, IL - Far North Side']
    >>> df_by_area = mult_area_ppsf_by_yr(df_all, area_list)
    >>> list(df_by_area.keys()) == area_list
    True
    """

    # initialize a dictionary for regions and its corresponding median sale ppsf by year
    area_price_dict = {}
    for i in region_list:
        yr_ppsf = area_ppsf_by_yr(df, i)  # get year and its corresponding Median Sale Ppsf
        area_price_dict.update({i: yr_ppsf})

    return area_price_dict


def ppsf_by_yr_plot(df_dict, colors, chart_title, filenm):
    """ Plot out medium sale ppsf by year for each specified region in
    the specified dataframe.

    :param df_dict: dictionary of medium ppsf data by region
    :param colors: a list of colors to be graphed for each region
    (Should be same length as number of regions in the dataframe)
    :param chart_title: Give the plotted graph a title
    :param filenm: Chart will be outputted to file.  Give output filename
    :return: No explicit return. Final result is outputted to file.

    >>> df_all = pd.read_csv('chicago_housing_all_residential_test.csv', sep=',')
    >>> df_all = df_cleaning(df_all)
    >>> area_list = ['Chicago, IL', 'Chicago, IL - Central Chicago', 'Chicago, IL - Far North Side']
    >>> df_by_area = mult_area_ppsf_by_yr(df_all, area_list)
    >>> color_list = ['firebrick', 'pink', 'green', 'black']
    >>> ppsf_by_yr_plot(df_by_area, color_list, 'title','file.png')
    Traceback (most recent call last):
    ValueError: Length of df_dict and colors must be equal.
    """

    dict_regions_list = list(df_dict.keys())  # region list

    if not len(dict_regions_list) == len(colors):
        raise ValueError('Length of df_dict and colors must be equal.')

    color_dict = {dict_regions_list[i]: colors[i] for i in range(len(dict_regions_list))}

    fig = go.Figure()

    for i in df_dict.keys():
        df = df_dict.get(i)  # get values with key as "i"
        fig.add_trace(go.Scatter(x=df.index, y=df.values,
                                 name=i, line=dict(color=color_dict.get(i), width=1)))

    # Edit the layout
    fig.update_layout(title=chart_title, xaxis_title='Year', yaxis_title='Ppsf($)')

    fig.write_image(filenm)


def mult_area_perc_by_yr(df, region_list):
    """Given a list of regions, loop through and return percentage change by year
    for all the specified regions/communities on the list.

    :param df: The specific dataframe imported in the main function
    :param region_list: A list of specified regions/areas/communities
    :return: A dictionary reflecting the list of regions and its corresponding percentage change by year

    >>> df_all = pd.read_csv('chicago_housing_all_residential_test.csv', sep=',')
    >>> df_all = df_cleaning(df_all)
    >>> area_list = ['Chicago, IL', 'Chicago, IL - Central Chicago', 'Chicago, IL - Far North Side']
    >>> df_by_area = mult_area_perc_by_yr(df_all, area_list)
    >>> list(df_by_area.keys()) == area_list
    True
    """

    # initialize a dictionary for regions and its corresponding median sale ppsf by year
    area_perc_dict = {}
    for i in region_list:
        yr_ppsf = area_ppsf_by_yr(df, i)  # get year and its corresponding Median Sale Ppsf
        yr_perc = yr_ppsf.pct_change() * 100
        area_perc_dict.update({i: yr_perc})

    return area_perc_dict


def perc_by_yr_plot(df_dict, colors, chart_title, filenm):
    """ Plot out percentage change by year for each specified regions/community in
    the specified dataframe.

    :param df_dict: dictionary of percentage change data by region
    :param colors: a list of colors to be graphed for each region
    (Should be same length as number of regions in the dataframe)
    :param chart_title: Give the plotted graph a title
    :param filenm: Chart will be outputted to file.  Give output filename
    :return: No explicit return. Final result is outputted to file.

    >>> df_all = pd.read_csv('chicago_housing_all_residential_test.csv', sep=',')
    >>> df_all = df_cleaning(df_all)
    >>> area_list = ['Chicago, IL', 'Chicago, IL - Central Chicago', 'Chicago, IL - Far North Side']
    >>> df_by_area = mult_area_perc_by_yr(df_all, area_list)
    >>> color_list = ['firebrick', 'pink', 'green', 'black']
    >>> perc_by_yr_plot(df_by_area, color_list, 'title','file.png')
    Traceback (most recent call last):
    ValueError: Length of df_dict and colors must be equal.
    """

    dict_regions_list = list(df_dict.keys())  # region list

    if not len(dict_regions_list) == len(colors):
        raise ValueError('Length of df_dict and colors must be equal.')

    color_dict = {dict_regions_list[i]: colors[i] for i in range(len(dict_regions_list))}

    for i in df_dict.keys():

        df = df_dict.get(i)
        fig_perc = go.Figure(data=go.Scatter(x=df.index, y=df.values,
                                             name=i, line=dict(color=color_dict.get(i), width=1)))

        # Edit the layout
        fig_perc.update_layout(title_text=chart_title + ' - ' + i, yaxis_title='percentage change (%)')

        fig_perc.write_image(filenm + '_' + i + '.png')


def season_activity(df, region):
    """ Return a dataframe including Period End, Median Sale Ppsf and Homes Sold given the region as Chicago, IL.

    :param df: The specific dataframe imported in the main function
    :param region:
    :return: a dataframe reflecting the overall Chicago's housing seasonality activity for
    Median Sale Ppsf and Homes Sold

    >>> df_all = pd.read_csv('chicago_housing_all_residential_test.csv', sep=',')
    >>> df_all = df_cleaning(df_all)
    >>> chi_data = season_activity(df_all, 'Chicago, IL')
    >>> chi_data.index[0]
    Timestamp('2014-01-31 00:00:00')
    """

    df_sub = df[['Period End', 'Median Sale Ppsf', 'Homes Sold']][df['Region'] == region]
    df_sub_by_month = df_sub.set_index('Period End')

    return df_sub_by_month


def season_by_month_plot(chi_data, colors, bar_title, filenm):
    """ Plot out seasonality activity by month for Chicago in
    the specified dataframe.

    :param chi_data: dataframe of seasonality activity for Chicago, IL
    :param colors: a list of colors to be graphed for each region
    :param bar_title: Give the plotted graph a title
    :param filenm: Chart will be outputted to file.  Give output filename
    :return: No explicit return. Final result is outputted to file.

    >>> df_all = pd.read_csv('chicago_housing_all_residential.csv', sep=',')
    >>> df_all = df_cleaning(df_all)
    >>> chi_data = season_activity(df_all, 'Chicago, IL')
    >>> color_list = ['firebrick', 'pink', 'green']
    >>> season_by_month_plot(chi_data, color_list, 'title','file.png')
    Traceback (most recent call last):
    ValueError: Length of df_dict and colors must be equal.
    """
    columns_list = list(chi_data.columns)

    if not len(columns_list) == len(colors):
        raise ValueError('Length of df_dict and colors must be equal.')

    color_dict = {columns_list[i]: colors[i] for i in range(len(columns_list))}

    for i in columns_list:

        fig_season = go.Figure(data=go.Bar(x=chi_data.index, y=chi_data[i],
                                           name=i, marker_color=color_dict.get(i)))

        # Edit the layout
        fig_season.update_layout(title=bar_title + ' - ' + i + ' from 2012 - 2019')

        fig_season.write_image(filenm + '_' + i + '.png')


def monthly_sale_share(df, month):
    """Analyze seasonality per month from 2013 - 2018 because they have full year data. Return the percentage
     of home sales in unit attributed to a specified month
     :param df: The specific dataframe imported in the main function
     :param month: from January to December
     :return: a list for the share of the total home sales attributed to a specified month

    >>> df_all = pd.read_csv('chicago_housing_all_residential_test.csv', sep=',')
    >>> df_all = df_cleaning(df_all)
    >>> month_lst = [1, 2, 3]
    >>> len(monthly_sale_share(df_all, month_lst))
    3
     """

    df_sub_chi = df[(df['Year'] > 2012) & (df['Year'] < 2019) & (df['Region'] == 'Chicago, IL')]
    total_sales = df_sub_chi['Homes Sold'].sum()

    monthly_sale_share_lst = []

    for i in month:
        share_monthly_sale = df_sub_chi['Homes Sold'].loc[df_sub_chi['Month'] == i].sum()/total_sales
        monthly_sale_share_lst.append(share_monthly_sale)

    return monthly_sale_share_lst


def monthly_sale_share_plot(monthly_share, pie_title, filenm):
    """ Plot out the share of monthly unit sale for Chicago.
    :param monthly_share: a list of the share of monthly unit sale for Chicago, IL
    :param pie_title: Give the plotted graph a title
    :param filenm: Chart will be outputted to file.  Give output filename
    :return: No explicit return. Final result is outputted to file.
    """

    label_months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                    'October', 'November', 'December']
    colors_list = ['#1f77b4', '#ff7f0e', '#9467bd', '#2ca02c', '#d62728', '#e377c2',
                   '#FDB603', '#639702', '#dacde6', '#faec72', '#9ab973', '#87cefa']

    fig_share = go.Figure(data=go.Pie(labels=label_months,
                                      values=monthly_share,
                                      hoverinfo='label+percent',
                                      marker=dict(colors=colors_list)))
    fig_share.update_layout(title=pie_title)

    fig_share.write_image(filenm)


def monthly_unit_sold_yr(df, region):
    """Given a list of regions, loop through and return average monthly unit sold by year
    for all the specified regions on the list.

    :param df: The specific dataframe imported in the main function
    :param region: A list of specified regions/areas/communities
    :return: A dataframe reflecting the average monthly unit sold by year for all the specified regions

    >>> df_all = pd.read_csv('chicago_housing_all_residential_test.csv', sep=',')
    >>> df_all = df_cleaning(df_all)
    >>> area_list = ['Chicago, IL', 'Chicago, IL - Central Chicago', 'Chicago, IL - Far North Side']
    >>> unit_sold_monthly_yr = monthly_unit_sold_yr(df_all, 'Chicago, IL')
    >>> unit_sold_monthly_yr.values[0]
    1724.0
    """

    area_data = df[df['Region'] == region]
    unit_sold_yr = area_data.groupby(area_data['Year'])['Homes Sold'].sum()
    num_of_month = area_data.groupby(area_data['Year'])['Homes Sold'].count()
    unit_sold_monthly_yr = unit_sold_yr / num_of_month

    return unit_sold_monthly_yr


def monthly_unit_sold_yr_plot(unit_sale_monthly_yr, chart_title, filenm):
    """ Plot out average monthly unit sold by year for Chicago, IL

    :param unit_sale_monthly_yr: series for eaverage monthly unit sold each year
    :param chart_title: Give the plotted graph a title
    :param filenm: Chart will be outputed to file.  Give output filename
    :return: No explicit return. Final result is outputed to file.

    """

    fig_sale = go.Figure(data=go.Scatter(x=unit_sale_monthly_yr.index, y=unit_sale_monthly_yr.values,
                                         line=dict(color='green')))

    # Edit the layout
    fig_sale.update_layout(title=chart_title, xaxis_title='Year', yaxis_title='Avg Monthly Homes Sold in Unit')

    fig_sale.write_image(filenm)


def mort_vs_mppsf_plot(df_house, df_rate, mul_graph_title, filenm):
    """ Plot out 30-year fixed mortgage rate and Chicago area Monthly Median Sale Price per square foot in a graph
    to see if there is a relationship between mortgage rate and house price.

    :param df_house: dataframe of Chicago area including year and annually median sale Ppsf
    :param df_rate: dataframe of 30-year fixed mortgage rate in US
    :param mul_graph_title: Give the plotted graph a title
    :param filenm: graph will be outputted to file.  Give output filename
    :return: No explicit return. Final result is outputted to file.
    """
    fig_mort_price = make_subplots(specs=[[{'secondary_y': True}]])

    fig_mort_price.add_trace(go.Bar(x=df_rate['DATE'],
                                    y=df_rate['MORTGAGE30US'],
                                    name='30-year fixed mortgage rate (2010 - 2019)'),
                             secondary_y=False,)

    fig_mort_price.add_trace(go.Scatter(x=df_house.index,
                                        y=df_house.values,
                                        name='Median Sale Ppsf in Chicago (2012 -2019)',
                                        line=dict(color='orange')),
                             secondary_y=True,)

    fig_mort_price.update_layout(title_text=mul_graph_title)

    fig_mort_price.update_xaxes(title_text='Year')

    fig_mort_price.update_yaxes(title_text='<b>mortgage 30-year fixed rate (%)', secondary_y=False)
    fig_mort_price.update_yaxes(title_text='<b>median sale price per square feet ($)', secondary_y=True)

    fig_mort_price.write_image(filenm)


if __name__ == '__main__':
    main()
