'''
Author: Naixin && naixinguo2-c@my.cityu.edu.hk
Date: 2024-07-26 10:57:48
LastEditors: Naixin && naixinguo2-c@my.cityu.edu.hk
LastEditTime: 2024-10-08 14:17:30
FilePath: /gpt/Users/orince/Desktop/chr/chr/ours.py
Description: 

'''


import sys
import numpy as np
from sklearn.model_selection import train_test_split
import torch
from torchcp.regression.utils.metrics import Metrics
from torchcp.utils.common import calculate_conformal_value


class CIR():

    def __init__(self, model, ymin=None, ymax=None):
        # super().__init__(model)
        self._model = model
        if ymax is None:
            ymax = np.inf
        if ymin is None:
            ymin = -np.inf
        self.ymin = ymin
        self.ymax = ymax

    def calibrate(self, x_calib, y_calib, alpha, init_rate=0.9):
        # init_rate: help initialize to speed up
        q_calib = np.pad(self._model.predict(x_calib), ((0,0),(1, 1)), 'constant', constant_values=(self.ymin,self.ymax))
        n_samples, n_quantiles = q_calib.shape
        # set an initial expected value for k based on alpha to speed up the search process
        threshold_k = int((1-alpha)*n_quantiles* init_rate) + 1
        threshold_k = 1
        # find the shortest interval with k_init interquantile intervals and the corresponding lower and upper index for each sample
        min_index = np.argmin(q_calib[:, threshold_k:] - q_calib[:, :-threshold_k], axis=1)
        lower = min_index
        upper = min_index + threshold_k
        #set initial threshold
        threshold_list = np.ones(n_samples)
        threshold_list.fill(threshold_k)
        # record the lenghth last expanded interquantile interval 
        new_expand=0
        for i in range(n_samples):
            while  threshold_list[i] <= n_quantiles-1:
                if  lower[i] > 0 and upper[i] <  n_quantiles-1:
                    #choose the side with the narrower interquantile interval to expand our interval
                    
                    if  q_calib[i, lower[i]] - q_calib[i, lower[i]-1] <=  q_calib[i, upper[i] +1] - q_calib[i,upper[i]] :  
                        
                        lower[i] -= 1              
                    else:
                      
                        upper[i] += 1  
                # when one side has reached the boundary, expand the other side                                             
                elif  lower[i] == 0 and upper[i] < n_quantiles-1:
        
                    upper[i] += 1 
                            
                elif  upper[i] == n_quantiles-1 and lower[i] > 0:
    
                    lower[i] -= 1               
                #check if y_calib[i] in our interval
                if  (y_calib[i] >= q_calib[i, lower[i]]) & (y_calib[i] <= q_calib[i, upper[i]]): 
                    #add a normalized constant to make the final expanded threshold between 0 and 1
                    threshold_list[i] += 1   
                    break
                #continue expanding
                else:
                    threshold_list[i] += 1       
                         
        level = int((1-alpha)*(n_samples+1))
        self.threshold  =  sorted(threshold_list)[level] 
     
        # return  self.threshold   
        
    def predict(self, x_test):
        q_test = np.pad(self._model.predict(x_test), ((0,0),(1, 1)), 'constant', constant_values=(self.ymin,self.ymax))
        n_samples, n_quantiles = q_test.shape
        # construct basic interval first and cut one side with some probability later
        # print('check',q_test[:, (int(self.threshold)):] - q_test[:, :-int(self.threshold)],' int(self.threshold)', int(self.threshold),q_test.shape)
        min_index = np.argmin(q_test[:, (int(self.threshold)):] - q_test[:, :-int(self.threshold)], axis=1)
        lower = min_index
        upper = min_index + int(self.threshold)
        interval_list=np.stack((q_test[np.arange(n_samples), lower], q_test[np.arange(n_samples), upper]), axis=1) 

        return np.array(interval_list)




class CIR_rank():

    def __init__(self, model, ymin=None, ymax=None):
        # super().__init__(model)
        self._model = model
        if ymax is None:
            ymax = np.inf
        if ymin is None:
            ymin = -np.inf
        self.ymin = ymin
        self.ymax = ymax

    def calibrate(self, x_calib, y_calib, alpha, init_rate=0.9):
        # init_rate: help initialize to speed up
        q_calib = np.pad(self._model.predict(x_calib), ((0,0),(1, 1)), 'constant', constant_values=(self.ymin,self.ymax))
        n_samples, n_quantiles = q_calib.shape
        # set an initial expected value for k based on alpha to speed up the search process
        threshold_k = int((1-alpha)*n_quantiles* init_rate) + 1
        threshold_k = 1
        # find the shortest interval with k_init interquantile intervals and the corresponding lower and upper index for each sample
        min_index = np.argmin(q_calib[:, threshold_k:] - q_calib[:, :-threshold_k], axis=1)
        lower = min_index
        upper = min_index + threshold_k
        #set initial threshold
        threshold_list = np.ones(n_samples)
        threshold_list.fill(threshold_k)
        # record the lenghth last expanded interquantile interval 
        new_expand=0
        for i in range(n_samples):
            while  threshold_list[i] <= n_quantiles-1:
                if  lower[i] > 0 and upper[i] <  n_quantiles-1:
                    #choose the side with the narrower interquantile interval to expand our interval
                    
                    if  q_calib[i, lower[i]] - q_calib[i, lower[i]-1] <=  q_calib[i, upper[i] +1] - q_calib[i,upper[i]] :  
                        new_expand =  q_calib[i, lower[i]]-q_calib[i, lower[i]-1]
                        lower[i] -= 1              
                    else:
                        new_expand = q_calib[i, upper[i] +1] - q_calib[i,upper[i]] 
                        upper[i] += 1  
                # when one side has reached the boundary, expand the other side                                             
                elif  lower[i] == 0 and upper[i] < n_quantiles-1:
                    new_expand = q_calib[i, upper[i] +1] - q_calib[i,upper[i]] 
                    upper[i] += 1 
                            
                elif  upper[i] == n_quantiles-1 and lower[i] > 0:
    
                    new_expand =  q_calib[i, lower[i]]-q_calib[i, lower[i]-1]
                    lower[i] -= 1               
                #check if y_calib[i] in our interval
                if  (y_calib[i] >= q_calib[i, lower[i]]) & (y_calib[i] <= q_calib[i, upper[i]]): 
                    #add a normalized constant to make the final expanded threshold between 0 and 1
                    self.normalized_constant=(np.max(y_calib)*100)
                    threshold_list[i] += new_expand/self.normalized_constant       
                    break
                #continue expanding
                else:
                    threshold_list[i] += 1       
                         
        level = int((1-alpha)*(n_samples+1))
        self.threshold  =  sorted(threshold_list)[level]    
       
        # return  self.threshold   
        
    def predict(self, x_test):
        q_test = np.pad(self._model.predict(x_test), ((0,0),(1, 1)), 'constant', constant_values=(self.ymin,self.ymax))
        n_samples, n_quantiles = q_test.shape
        # construct basic interval first and cut one side with some probability later
        # print('check',q_test[:, (int(self.threshold)):] - q_test[:, :-int(self.threshold)],' int(self.threshold)', int(self.threshold),q_test.shape)
        min_index = np.argmin(q_test[:, (int(self.threshold)):] - q_test[:, :-int(self.threshold)], axis=1)
        lower = min_index
        upper = min_index + int(self.threshold)
        interval_list=np.stack((q_test[np.arange(n_samples), lower], q_test[np.arange(n_samples), upper]), axis=1) 

        for i, row in enumerate(q_test):
       
            if  lower[i] > 0 and upper[i] <  n_quantiles-1:
                if q_test[i,lower[i]] - q_test[i,lower[i]-1] < q_test[i,upper[i]+1] - q_test[i,upper[i]]:
                    if (q_test[i,lower[i]] - q_test[i,lower[i]-1])/self.normalized_constant > self.threshold - int(self.threshold):
                        interval_list[i]=[q_test[i,lower[i]-1], q_test[i,upper[i]]]  
                     
                else:
                    if (q_test[i,upper[i]+1] - q_test[i,upper[i]])/self.normalized_constant > self.threshold - int(self.threshold):
                        interval_list[i]=[q_test[i,lower[i]], q_test[i,upper[i]+1]]
                    
            
            elif  lower[i] == 0 and upper[i] < n_quantiles-1:
                if (q_test[i,upper[i]+1] - q_test[i,upper[i]])/self.normalized_constant > self.threshold - int(self.threshold):
                    interval_list[i]=[q_test[i,lower[i]], q_test[i,upper[i]+1]]
                  
                   
            elif  upper[i] == n_quantiles-1 and lower[i] > 0:
                if (q_test[i,lower[i]] - q_test[i,lower[i]-1])/self.normalized_constant > self.threshold - int(self.threshold):
                    interval_list[i]=[q_test[i,lower[i]-1], q_test[i,upper[i]]]   
                   
        return np.array(interval_list)


    
        
