#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import tkinter
import customtkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests
import schedule 
import time
import datetime
from selenium import webdriver
from bs4 import BeautifulSoup
import xlsxwriter
from styleframe import StyleFrame
import pandas as pd

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")
class temperatureClass :
    
    #constructor
    def __init__(self,base_temperature,url,app):
        print('\n inside init')
        self.url = url ;
        self.base_temperature = base_temperature ;
        self.dayNumber = 0;
        self.indDayNo = 0;
        self.Temp =[]
        self.highTemp = [];
        self.lowTemp = [];
        self.avgTemp = [];
        self.gDD = [];
        self.cumGDD = [];
        self.window = app;
        
    #Extracting from website        
    def extractTempFromWeb(self):
        print('inside extract from web')
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--incognito')
        chrome_options.add_argument('--headless')

        self.Temp=[];
        driver = webdriver.Chrome(options = chrome_options)
        source =driver.get('https://weather.com/weather/tenday/l/7f3924e156afb7814c8d12d1e4ea0138b2e46869a57075ebc763c2963d75ec82')

        source_code=driver.page_source

        soup = BeautifulSoup(source_code,'lxml')
        tempFromWeb =soup.find_all('div',class_='DailyContent--ConditionSummary--2gdfo')
    
        for tempExtraction in tempFromWeb:
            self.Temp.append(tempExtraction.find('span',{'class' : 'DailyContent--temp--1s3a7'}).get_text())
        
        print("\n Temp low and high mixed->",self.Temp)
        self.highLowTempExtraction()
        
    
    #Manipulating extracted data to not overwrite existing data    
    def highLowTempExtraction(self):
        print('\n inside high low')
        j=0;
        k=0;
        dayNo = self.dayNumber
        ht = [];
        lt = [] ;
        
        print("\n self.dayNumber->",dayNo)
        
        del self.lowTemp[dayNo:len(self.Temp)]
        del self.highTemp[dayNo:len(self.Temp)]
        del self.avgTemp[dayNo:len(self.Temp)]
        del self.gDD[dayNo:len(self.Temp)]
        del self.cumGDD[dayNo:len(self.Temp)]
        while j<len(self.Temp)-2:
            self.highTemp.insert(dayNo,self.Temp[j].replace("°",""));
            self.lowTemp.insert(dayNo,self.Temp[j+1].replace("°",""));
            self.avgTemp.insert(dayNo,(float(self.highTemp[dayNo])+float(self.lowTemp[dayNo]))/2.0)
            self.gDD.insert(dayNo,self.avgTemp[dayNo] - self.base_temperature);
            if (dayNo==0):
                self.cumGDD.insert(self.indDayNo,0)
            else :
                if(self.cumGDD[len(self.cumGDD)-1]>140):
                    self.apiCallToWise(dayNo)
                    break
                self.cumGDD.insert(dayNo,self.cumGDD[dayNo-1]+self.gDD[dayNo])
            j=j+2
            dayNo = dayNo+1
        self.dayNumber = self.dayNumber+1
        
        print("\n lt->",self.lowTemp)
        print("\n ht->",self.highTemp)
        print("\n gDD->",self.gDD)
        print("\n cumGDD->",self.cumGDD)
        print("\n dayNumber->",self.dayNumber)
    
    #To call WISE by entering the URL    
    def apiCallToWise(self,dayNo):
        self.plotGddStatistics(dayNo);
        """payload = {
            "Ch": 0,
            "Md": 0,
            "Val": 1,
            "Stat": 1,
            "PsCtn": 1,
            "PsStop": 0,
            "PsIV": 0
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic cm9vdDowMDAwMDAwMA==",
            "Cookie": "Cookie=adamsessionid=12965427BA2"
        }


        Flag = True;
        while(Flag):
            response = requests.request("POST", self.url, json=payload, headers=headers)
            time.sleep(3)
            print(response)
            Flag = False;

        payload1 = {
            "Ch": 0,
            "Md": 0,
            "Val": 0,
            "Stat": 0,
            "PsCtn": 1,
            "PsStop": 0,
            "PsIV": 0
        }
        response = requests.request("POST", url, json=payload1, headers=headers)

        print(response)"""
        
    def plotGddStatistics(self,dayNo):
        print('Inside Graph')
        x = range(0,dayNo,1)
        d=[]
        for i in x:
            print(i)
            d.append(i)
        print(d);
        data ={'days':d,'Cumulative GDD': self.cumGDD}
        print(data)
        dataframe=pd.DataFrame(data)
        print(dataframe)
        print("all good")
        main_window=self.window;
        figure = plt.Figure(figsize=(5,3),dpi=100)
        figure_plot= figure.add_subplot(1,1,1);
        figure_plot.set_ylabel('Cumulative GDD')
        line_graph = FigureCanvasTkAgg(figure,main_window)
        line_graph.get_tk_widget().pack(side=customtkinter.RIGHT,fill=customtkinter.BOTH)
        dataframe = dataframe[['days','Cumulative GDD']].groupby('days').sum()
        dataframe.plot(kind='line', legend=True,ax=figure_plot,color='g',marker='o',fontsize = 10)
        figure_plot.set_title(f'Cumulative GDD vs Day \n{dayNo} days from now , It is anticipated to find weed')
        

app=customtkinter.CTk()
tc = temperatureClass(48,"https://www.google.com",app)
app.geometry("1020x1020")
app.title("Floral Notification Hub")
nameLabel = customtkinter.CTkLabel(app,text="Welcome to Floral Hub Notification for Irvine , CA!")
nameLabel.place(relx=0.50, rely=0.25, anchor=tkinter.CENTER)
button = customtkinter.CTkButton(app,text="START PREDICTION",command=tc.extractTempFromWeb)

button.place(relx=0.50, rely=0.50, anchor=tkinter.CENTER)
app.mainloop()

