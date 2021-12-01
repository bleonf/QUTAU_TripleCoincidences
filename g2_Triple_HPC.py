"""
Generation of triple correlation function from timestamps file obained from qutools qutau module
The inputs for the user are:
    Test: True if the user wants to generate a simple test data generated randomly (no correlation)
    fig:  True if the user wants to save the histogram
    cluster: True if program is running on machine with multiprocessing capabilities
    
    hist_bins: Number of bins to include in histogram
    nrows: Number of rows to use from the qutau data set
    window: time window to use in qutau units (1=81x10^-12 s)
    n: resolution of coincidences (remainder of t/n will be removed)
    
    data_path: path to timestamps file from qutau
To improve speed, the g2 is prepared using collections.Counter and also for repeated runs the script implements pickle saving for the coincidence counter when all numbers are equal, this works mainly for adjusting bin number in histogram.
""" 
import numpy as np
import matplotlib.pylab as plt
import pandas as pd
from collections import Counter
import gc
import multiprocessing
import pickle
from tqdm import tqdm

#Preset style of output figures
plt.style.use('seaborn-bright')

################
#  Input area  #
################

Test=False
fig=True
cluster=True
data_path="~/Maestria/timestamps_2411"

#Do not change except if trigger and analyzing channels are changed from the begginning 
Trigger=1
Signal=2
Idler=3

hist_bins=200

numbers={10000:(10,1),20000:(10,1),50000:(10,10),100000:(10,1),1200000:(10,1)}
#Comment out one of the sets of nrows,window,n to use "numbers" dictionary (easy to preset values) or manually asign values
nrows=1200000
window=numbers[nrows][0]
n=numbers[nrows][1]

nrows=1200000
window=10
n=1

#####################
#  Data generation  #
#####################

if not Test:
    # data_path="/home/bleon/Documents/Maestria/Clases/Cuantica/timestamps_2411_2"
    data=pd.read_csv(data_path,names=['timestamps','Channel'], nrows=nrows)
else:
    data=pd.DataFrame()
    data['Channel'] = np.random.choice([1,2,3], nrows)
    data["timestamps"]=np.random.rand(nrows)
    
#Data output file, name depends on nrows number
with open("output_"+str(nrows)+".txt","w") as file:
    print("Script started", file=file)

def write_output(x):
    with open("output_"+str(nrows)+".txt","a") as file:
        print(x,file=file)
        
write_output("nrows="+str(nrows))
write_output("window="+str(window))
write_output("n="+str(n))
write_output(data.describe())        
write_output("data done\n")


#data set in individual series
Trigger_all=data[data['Channel']==Trigger][["timestamps"]]
Signal_all=data[data['Channel']==Signal][["timestamps"]]
Idler_all=data[data['Channel']==Idler][["timestamps"]]
lista_trigger=Trigger_all["timestamps"].tolist()

write_output("Trigger shape")
write_output(Trigger_all.shape)

#Triple coincidence counter per time window
def check_trigger(trig):
    count=Counter()
    sig=Signal_all[(Signal_all["timestamps"]>=(trig-window)) & (Signal_all["timestamps"]<=(window+trig))]["timestamps"].copy().apply(lambda x:(x-trig)-((x-trig)%n)).tolist()
    a=len(sig)
    
    idl=Idler_all[(Idler_all["timestamps"]>=(trig-window)) & (Idler_all["timestamps"]<=(window+trig))]["timestamps"].copy().apply(lambda x:(x-trig)-((x-trig)%n))
    b=len(sig)
    for s in sig:
        count.update(idl.copy().apply(lambda x:(x-s)).tolist())
    return count,a,b


try:
    #Checks if a pickle file for the counted elements is found
    with open("elements_sorted"+str(nrows)+"_"+str(window)+"_"+str(n)+".pkl","rb") as file:
        Pickle_result=pickle.load(file)

    final_count=Pickle_result[0]
    count_sig=Pickle_result[1]
    count_idl=Pickle_result[2]
    write_output("Pickle for counter exists\n")
    
except: 
    write_output("Pickle for counter does not exists\n")
    final_count=Counter()       

    if cluster:
        write_output("Starting multiprocesses\n")
        write_output("Starting coincidence counter")
        if __name__=='__main__':
            P=multiprocessing.Pool()
            result=P.map(check_trigger,lista_trigger)        
            P.close()
            P.join()
        count_sig=0
        count_idl=0
    else:
        write_output("Starting coincidence counter")
        result=[check_trigger(trig) for trig in lista_trigger]
        
    for small in tqdm(result):
        final_count+=small[0]
        count_sig+=small[1]
        count_idl+=small[2]

    with open("elements_sorted"+str(nrows)+"_"+str(window)+"_"+str(n)+".pkl","wb") as file:
        pickle.load([final_count,count_sig,count_idl],file)
 
values_items=list(final_count.items())  

#Summary of results in output file    
write_output("Final count done. len:") 
write_output(len(final_count))

write_output("Number of items counted:") 
write_output(len(sorted(final_count.elements())))
    
write_output("Total signal counts in window:") 
write_output(count_sig)

write_output("Total idler counts in window:") 
write_output(count_idl)

write_output("Coincidence window (ps):")
write_output(str(window*81*10**(-12)))

#csv generation in case of needed export
Values=pd.DataFrame(values_items,columns=["Time","Counts"])
Values.to_csv("Values"+str(nrows)+".csv")

if not fig:
    exit()
    
#Scatter plot and histogram generation    
figure=plt.figure()
plt.title("n="+str(n)+", window="+str(window)+", nrows="+str(nrows))
plt.scatter(Values["Time"],Values["Counts"])
plt.savefig("TripleCoinc"+str(nrows)+"_"+str(window)+"_"+str(n)+".pdf")

figure2=plt.figure()
plt.title("n="+str(n)+", window="+str(window)+", nrows="+str(nrows))
plt.hist(sorted(final_count.elements()),bins=hist_bins)
plt.savefig("TripleHist"+str(nrows)+"_"+str(window)+"_"+str(n)+".pdf")
            
    






    
