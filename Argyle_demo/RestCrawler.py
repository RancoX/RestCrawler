import os
import shutil
import requests
import re
import time
import warnings
from datetime import datetime
from dateutil.relativedelta import relativedelta
import concurrent.futures
import pandas as pd
from io import StringIO
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go


'''


This is a demo project built by Ranco Xu for the potential interview with Rest Super


This project was created at 9am 18 May 2022 and was finished on 11pm 18 May 2022


This demo project is a web crawler that does the following things

    1. scraping historical performance data from REST super's website and save them to the corresponding folder




    2. clean and extract the data for a nominated fund using Regex and save it to pandas dataframe




    3. data transformation and calculations




    4. dynamic visualization using plotly (line chart as demonstration)




The source code was fully written by Ranco Xu in May 2022 at Brissy aka the best place on this blue planet and I hereby grant anyone who has this code the ability to redistribute it freely :)




'''


warnings.filterwarnings('ignore')


class RestCrawler:

    def __init__(self, MainWindow, folder_name='Demo', start_date='31/01/2014', months_under_analysis=36, funds=['Core Strategy', ], debug=True):

        # PARAMETER declaration

        self.MainWindow = MainWindow

        self.folder_name = folder_name

        self.start_date = start_date

        self.how_many_months = months_under_analysis

        self._funds = funds

        self._debug = debug

        if debug:

            self.saveTo = os.path.join(os.getcwd(), self.folder_name)

        # print some user friendly prompt

        self.MainWindow.sbar.showMessage("Now downloading files...")

    def run(self):

        # this is the main process of the project where all the methods execute

        if not self._debug:

            self.create_folder()

            self.multi_download()

        self.MainWindow.sbar.showMessage('All files downloaded!')

        self.create_dataframe()

        self.line_chart()

    def create_folder(self):

        # 1-create necessary folder

        self.saveTo = os.path.join(os.getcwd(), self.folder_name)

        # check if saveTo path already exists, if so, delete the whole file tree

        if os.path.exists(self.saveTo):

            shutil.rmtree(self.saveTo)

        os.mkdir(self.saveTo)

    def multi_download(self):

        # 1-scraping all historical performance report csv from REST super website and save them to saveTo folder

        # 1.1-create all downloadable links (long story here how to get these links)

        start_date_obj = datetime.strptime(self.start_date, r'%d/%m/%Y')

        month_to_download = [(start_date_obj+relativedelta(months=+i, day=31)



                              ).strftime(r'%d%b%Y') for i in range(self.how_many_months)]

        self.urls = ['https://rest.com.au/client/Templates/Rest/InvestmentSection/csvexport/csvexport.aspx?action=investmentperformance&type=rest&date=' +



                     month for month in month_to_download]

        # 1.2 use multi-threading to speed up downloading process as this is a I/O process

        with concurrent.futures.ThreadPoolExecutor() as executor:

            # executor.map(self.csv_download, self.urls)

            # execute and update mainwindow progree bar

            for i, url in enumerate(self.urls):

                executor.submit(self.csv_download, url)

                time.sleep(0.5)

                self.MainWindow.pbar.setValue(i+1)

    def csv_download(self, url):

        # csv downloader that will be used in threadings

        csv_content = requests.get(url).content

        filename = f"{url[-4:]}_{url[-7:-4]}_{url[-9:-7]}.csv"

        filepath = os.path.join(self.saveTo, filename)

        with open(filepath, 'wb') as wf:

            wf.write(csv_content)

            time.sleep(0.1)

            print(f"{filename} has been downloaded.")

    def create_dataframe(self):

        # 2. clean and extract the data for a nominated fund using Regex and save it to pandas dataframe

        # 2.1 set up working directory

        cur_path = os.getcwd()

        os.chdir(self.saveTo)

        # 2.2 create empty dataframe container

        self.df = pd.DataFrame()

        # 2.3 read and clean data from csv and then update the dataframe

        for csv in os.listdir(self.saveTo):

            with open(csv, 'r') as rf:

                contents = rf.readlines()

                for fund in self._funds:

                    # regex to match selected fund

                    for line in contents:

                        if re.search(fund+','+'.*%+', line):

                            row = f"{csv[:-4]},{line.strip()}"

                            # print(line)

                            row = StringIO(row)

                            row = pd.read_csv(row, sep=',', header=None)

                            self.df = pd.concat(
                                [self.df, row], ignore_index=True, axis=0)

                            break

        # return to previous working directory

        os.chdir(cur_path)

        # 3-dataframe transformation

        # 3.1-set column names

        self.df.set_axis(['Date', 'Option', '10yr', '7yr', '5yr',
                         '3yr', '1yr', '6m', '3m', 'FYTD'], axis=1, inplace=True)

        # 3.2 format dates and reorder

        self.df.Date = self.df.Date.apply(
            datetime.strptime, args=('%Y_%b_%d',))

        self.df.sort_values(by='Date', inplace=True)

        self.df.Date = self.df.Date.apply(
            datetime.strftime, args=('%d-%m-%Y',))

        # 3.3 change the numeric columns to float

        self.df = self.df.replace(r'\s*%', '', regex=True)

        # 3.4 output to csv file under the current folder

        self.df.to_csv('Output.csv', na_rep='N/A', index=False)

        return self.df

    def line_chart(self):

        # 4. dynamic visualization using plotly

        # 4.1-simple line chart

        self.df = self.df.astype({'10yr': 'float', '7yr': 'float', '5yr': 'float',
                                 '3yr': 'float', '1yr': 'float', '6m': 'float', '3m': 'float', 'FYTD': 'float'})

        self.df['Date'] = pd.to_datetime(self.df['Date'], format='%d-%m-%Y')

        self.df['Year'] = self.df['Date'].apply(lambda d: d.year)

        self.df['Month'] = self.df['Date'].apply(lambda d: d.month)

        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

        app = Dash(__name__, external_stylesheets=external_stylesheets)

        app.layout = html.Div([



            html.Div([



                dcc.Dropdown(id='fund_selector',
                             options=self._funds, value=self._funds[1])



            ], style={'width': '50%', 'display': 'inline-block', 'float': 'top'}),







            html.Br(),



            html.Div([



                dcc.Graph(id='line_chart', hoverData={
                          'points': [{'customdata': 'Core Strategy'}]})



            ], style={'width': '50%', 'paddingTop': 20}),




            html.Br(),



            html.Div([



                dcc.Slider(id='year_selector', min=self.df['Year'].min(), max=self.df['Year'].max(), step=None,



                           value=self.df['Year'].min(), marks={str(yr): str(yr) for yr in self.df['Year'].unique()})



            ], style={'width': '50%', 'float': 'bottom', 'marginLeft': 20}),



        ])

        @app.callback(



            Output(component_id='line_chart', component_property='figure'),



            Input(component_id='fund_selector', component_property='value'),



            Input(component_id='year_selector', component_property='value')



        )
        def update_linechart(fund, year):

            # filter by user inputs

            dff = self.df[(self.df['Option'] == fund)
                          & (self.df['Year'] == year)]

            # drop na

            dff.dropna(inplace=True)

            fig = px.scatter(data_frame=dff, x='Date',



                             y='5yr',



                             hover_name='Option',



                             color='3m'



                             )

            fig.update_traces(customdata=dff['Option'], marker={'size': 12})

            fig.add_trace(go.Scatter(x=dff['Date'], y=dff['5yr'], mode='lines', line={
                          'color': 'gray', 'width': 1, 'dash': 'dash'}))

            fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0},



                              hovermode='closest',



                              transition={'duration': 300},



                              title=f"{year} return for {fund} Fund",



                              title_y=0.995,



                              title_x=0.5



                              )

            return fig

        self.MainWindow.open_browser()

        app.run_server(debug=False, dev_tools_hot_reload=True, port=8000)


if __name__ == '__main__':

    options = ['Core Strategy', 'Balanced', 'Capital Stable', 'Diversified', 'High Growth', 'Cash', 'Bonds', 'Shares',
               'Property', 'Australian Shares', 'Australian Shares - Indexed', 'Overseas Shares', 'Overseas Shares - Indexed']

    MyCrawler = RestCrawler(folder_name='Raw_Rest_data',



                            start_date='25/01/2019',



                            months_under_analysis=40,



                            funds=options,



                            debug=False)

    # run the web crawler

    MyCrawler.run()
