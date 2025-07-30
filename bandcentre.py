import matplotlib.pyplot as plt
import pandas as pd
import argparse
import sys
from os.path import join, isfile, isdir
from os import listdir,getcwd



# get argument from command line with the number of processors
def get_args():
    parser = argparse.ArgumentParser(description='Calculate band centres from DOS files')
    parser.add_argument('--inipath', type=str, help='Directory with all DOS calculations subdirectories', default='Calcs')
    parser.add_argument('--startE', type=int, help='Initial energy for band centre calculation', default=-100)
    parser.add_argument('--endE', type=int, help='Final energy for band centre calculation', default=0)
    return parser.parse_args()

def read_dos(filename,totalpath):
    #read first line of file as string
    datapath=join(totalpath,filename)
    with open(datapath) as f:
        first_line = f.readline()
    listnames=first_line.split(' ')[1:]
    listnames[-1]=listnames[-1][:-1]
    # #read the data from the file and store it in a pandas dataframe with the names from the listnames
    df = pd.read_csv(datapath, comment='#', sep=' ', header=None, names=listnames)
    return df

def calc_bandcentre(df,tagsDOS,rangeE):
    bandcentres=[]
    for tagdos in tagsDOS:
        dosSum=0
        dosxE=0
        for i in range(len(df['energy'])-1):
            energy=df['energy'][i]
            if energy >=min(rangeE) and energy <=max(rangeE): 
                deltaE=df['energy'][i+1] - energy
                dos=abs(df[tagdos][i])
                dosxE+=energy*deltaE*dos
                dosSum+=dos*deltaE
        bandcentres.append(dosxE/dosSum)
    return bandcentres

def getbandcentre(tagsDOS,rangeE,systems,results,name,spec,files):
    dftot=pd.DataFrame()
    for file in files:
        j=0
        df=read_dos(file,totalpath)
        df[tagsDOS[2]]=abs(df[tagsDOS[0]])+abs(df[tagsDOS[1]])
        bands=calc_bandcentre(df,tagsDOS,rangeE)
        for i in range(len(tagsDOS)):
            systems.append(file.split('.')[0]+'-'+tagsDOS[i])    
            results.append(bands[i])
            if j==0:
                dftot[tagsDOS[i]]=df[tagsDOS[i]]
            else:
                dftot[tagsDOS[i]]=dftot[tagsDOS[i]]+df[tagsDOS[i]]
        j+=1

    dftot['energy']=df['energy']
    bands=calc_bandcentre(dftot,tagsDOS,rangeE)
    for i in range(len(tagsDOS)):
        systems.append(spec+'CusBr-'+tagsDOS[i])    
        results.append(bands[i])
    return systems, results




# Define the main path, files to read
initpath=str(get_args().inipath)
namepaths=[dir for dir in listdir(initpath) if isdir(join(initpath, dir))]
Irfiles=['Ir_dos-cus.dat','Ir_dos-br.dat']
Ofiles=['O_dos-cus.dat','O_dos-br.dat']

# define the range of energies to consider for the band centre calculation
rangeE=[int(get_args().startE), int(get_args().endE)]

resultsdf=pd.DataFrame()
resultssys=[]
for name in namepaths:
    totalpath=join(initpath,name)
    systems=[]
    results=[]
    tagsDOS=['d(up)','d(down)','total']
    systems, results = getbandcentre(tagsDOS, rangeE, systems, results, name,'Ir',Irfiles)
    tagsDOS=['p(up)','p(down)','total']
    systems, results = getbandcentre(tagsDOS, rangeE, systems, results, name,'O',Ofiles)

    resultsdf[name]=results

resultsdf['systems']=systems

resultsdf.to_csv('DOS.csv')