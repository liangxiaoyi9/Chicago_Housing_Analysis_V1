import numpy as np
import pandas as pd
from chart_studio.plotly import plot, iplot
import chart_studio.plotly as py
import plotly.graph_objs as go
import plotly.io as pio


def main():

    df_all = pd.read_csv('chicago_housing_all_residential.csv', sep=',')
    df_all = df_cleaning(df_all)

    # area_data = area_ppsf_by_yr(df_all, 'Chicago, IL')
    # print(area_data.values)

    area_list = ['Chicago, IL', 'Chicago, IL - Central Chicago', 'Chicago, IL - Far North Side',
                 'Chicago, IL - Far Southeast Side', 'Chicago, IL - Far Southwest Side', 'Chicago, IL - North Side',
                 'Chicago, IL - Northwest Side', 'Chicago, IL - South Side', 'Chicago, IL - Southwest Side',
                 'Chicago, IL - West Side']
    df_by_area = mult_area_ppsf_by_yr(df_all, area_list)
    # print(df_by_area.get('Chicago, IL'))

    color_list = ['firebrick', 'pink', 'green', 'lawngreen', 'olive', 'skyblue', 'purple', 'yellow',
                  'orange', 'salmon']
    ppsf_by_yr_plot(df_by_area, color_list, 'Price Per Square Foot by Region', filenm='fig1.png')

    area_list = ['Chicago, IL - Near North Side', 'Chicago, IL - The Loop', 'Chicago, IL - Near South Side',
                 'Chicago, IL - North Center', 'Chicago, IL - Lake View', 'Chicago, IL - Lincoln Park',
                 'Chicago, IL - Avondale', 'Chicago, IL - Logan Square']
    df_by_area = mult_area_ppsf_by_yr(df_all, area_list)

    color_list = ['pink', 'green', 'lawngreen', 'skyblue', 'orange', 'darkred', 'gray', 'brown']
    ppsf_by_yr_plot(df_by_area, color_list, 'The Most Expensive Communities in Chicago', filenm='fig2.png')


def df_cleaning(df):
    """Before analysis, data needs to be cleaned up as necessary. Put all data cleaning
    steps here for organization.

    :param df: dataframe that needs cleaning
    :return: the same dataframe that has been cleaned up
    :raises: error if input is not a dataframe

    >>> df_all = pd.read_csv('chicago_housing_all_residential.csv', sep=',')
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

    # df['Median Sale Price'] = [x[1: -1] for x in df['Median Sale Price']]
    df['Median Sale Price'] = [x[1:] for x in df['Median Sale Price'].str.replace('K', '000')]
    df['Median Sale Price'] = df['Median Sale Price'].str.replace(',', '')
    df['Median Sale Price'] = pd.to_numeric(df['Median Sale Price'])
    df['Period Begin'] = pd.to_datetime(df['Period Begin'])
    df['Period End'] = pd.to_datetime(df['Period End'])
    # df.head(15)

    return df


def area_ppsf_by_yr(df, region):
    """Returns medium sale price per sqrft by year, given the residential dataframe and
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

    area_data = df[df['Region'] == region]
    area_data_by_yr = area_data.groupby(area_data['Period End'].dt.year)['Median Sale Ppsf'].median()

    return area_data_by_yr


def mult_area_ppsf_by_yr(df, region_list):
    """Given a list of regions, loop through and return medium sale price per sqrft by year
    for all the specified regions on the list.

    :param df: The specific dataframe imported in the main function
    :param region_list: A list of specified regions/areas/communities
    :return: A dictionary reflecting the list of regions and its corresponding medium sale ppsf by year

    >>> df_all = pd.read_csv('chicago_housing_all_residential.csv', sep=',')
    >>> df_all = df_cleaning(df_all)
    >>> area_list = ['Chicago, IL', 'Chicago, IL - Central Chicago', 'Chicago, IL - Far North Side']
    >>> df_by_area = mult_area_ppsf_by_yr(df_all, area_list)
    >>> list(df_by_area.keys()) == area_list
    True
    """

    area_df_dict = {}
    for i in region_list:
        area_df = area_ppsf_by_yr(df, i)
        area_df_dict.update({i: area_df})

    return area_df_dict


def ppsf_by_yr_plot(df_dict, colors, chart_title, filenm):
    """ Plot out medium sale ppsf by year for each specified region in
    the specified dataframe.

    :param df_dict: dictionary of medium ppsf data by region
    :param colors: a list of colors to be graphed for each region
    (Should be same length as number of regions in the dataframe)
    :param chart_title: Give the plotted graph a title
    :param filenm: Chart will be outputed to file.  Give output filename
    :return: No explicit return. Final result is outputed to file.

    >>> df_all = pd.read_csv('chicago_housing_all_residential.csv', sep=',')
    >>> df_all = df_cleaning(df_all)
    >>> area_list = ['Chicago, IL', 'Chicago, IL - Central Chicago', 'Chicago, IL - Far North Side']
    >>> df_by_area = mult_area_ppsf_by_yr(df_all, area_list)
    >>> color_list = ['firebrick', 'pink', 'green', 'black']
    >>> ppsf_by_yr_plot(df_by_area, color_list, 'title','file.png')
    Traceback (most recent call last):
    ValueError: Length of df_dict and colors must be equal.
    """

    dict_keys_list = list(df_dict.keys())

    if not len(dict_keys_list) == len(colors):
        raise ValueError('Length of df_dict and colors must be equal.')

    color_dict = {dict_keys_list[i]: colors[i] for i in range(len(dict_keys_list))}

    fig = go.Figure()

    for i in df_dict.keys():

        df = df_dict.get(i)
        fig.add_trace(go.Scatter(x=df.index, y=df.values,
                                 name=i, line=dict(color=color_dict.get(i), width=1)))

    # Edit the layout
    fig.update_layout(title=chart_title, xaxis_title='Year', yaxis_title='Ppsf($)')

    # fig.show(renderer='browser')
    fig.write_image(filenm)


if __name__ == '__main__':
    main()

