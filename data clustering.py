# -*- coding: utf-8 -*-
"""
Created on Thu Nov 25 22:23:13 2021

@author: Qilin Zhang
for clustering
"""
import numpy as np
import csv
import torch
from sklearn.metrics import r2_score


import numpy as np
from sklearn_extra.cluster import KMedoids
from sklearn_extra.cluster import CommonNNClustering 
import tslearn.metrics as metrics
from tslearn.clustering import silhouette_score
from tslearn.preprocessing import TimeSeriesScalerMeanVariance
from tslearn.generators import random_walks
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from processing_traffic import ProcessTraffic
from processing_iri import ProcessIRI
from processing_construction import ProcessCons
from feature_fusion import Trans, ClimateFusion, OutFusion

# Construction
out_cons = ProcessCons()

# Climate
out_climate = ClimateFusion()

# Traffic
out_trf = ProcessTraffic('TRF_TREND')

# IRI
out_iri = ProcessIRI('MON_HSS_PROFILE_SECTION')

trans = Trans()

# matching out_iri, out_trf and out_climate
out_final = OutFusion(out_iri, out_trf, out_climate, trans, out_cons)

normal = []
scaler = MinMaxScaler()
for i in out_final:
    section = np.array(i)
    section1 = scaler.fit_transform(section)
    normal.append(section1)

history_len = 7
prediction_len = 5
window_len = history_len + prediction_len 

iri_n = [] 
for i in normal:
    total_len = len(i)
    if total_len > window_len: 
        iri_n.append(i[:,0:1])
           

iri = []
for i in iri_n:
    reverse = i[::-1] 
    iri.append(reverse)            


distortions = []
scores = []
dists = metrics.cdist_dtw(iri) # dba + dtw

# dists = metrics.cdist_soft_dtw_normalized(X,gamma=.5) # softdtw
min_cluster = 2
max_cluster = 40
for i in  range (min_cluster , max_cluster+1):
    km = KMedoids(n_clusters=i,max_iter=1000)
    y_pred = km.fit_predict(dists)
    
    score = silhouette_score(dists,y_pred,metric="euclidean")
    scores.append(score)
    distortions.append(km.inertia_)
    #print(km.labels_)
    #print(km.medoid_indices_)
    
plt.plot(range (min_cluster , max_cluster+1), scores, marker= 'o' )
plt.xlabel( 'Number of clusters' )
plt.ylabel( 'Silhouette score' )
plt.grid()
#plt.savefig('./figure/silhouette.eps', format='eps', bbox_inches='tight')
plt.show()

plt.plot(range (min_cluster , max_cluster+1), distortions, marker= 'x' )
plt.xlabel( 'Number of clusters' )
plt.ylabel( 'Sum of distances to cluster center' )
plt.grid()
#plt.savefig('./figure/distance.eps', format='eps', bbox_inches='tight')
plt.show()



num_cluster = 7

km = KMedoids(n_clusters= num_cluster, max_iter=1000)
#km = CommonNNClustering(eps=0.9, min_samples=1)

dists = metrics.cdist_dtw(iri) #  dtw
y_pred = km.fit_predict(dists)
np.fill_diagonal(dists,0)
score = silhouette_score(dists,y_pred,metric="euclidean")
label = km.labels_
print(label)
print("silhouette_score: " + str(score))

for yi in range(num_cluster):
    for index, element in enumerate(y_pred):
        if element == yi:
            plt.plot(iri[index], 'lightgray',linewidth=0.5)
    plt.plot(iri[km.medoid_indices_[yi]], 'orangered')
    plt.title('Cluster %d' % (yi + 1))
    plt.xlabel( 'Year' )
    plt.ylabel( 'Normalised IRI' )
    x = range(0,23,1)
    plt.xticks(x,['t','t-1','t-2','t-3','t-4','t-5','t-6','t-7','t-8','t-9','t-10','t-11','t-12','t-13','t-14','t-15','t-16','t-17','t-18','t-19','t-20','t-21','t-22'],rotation=60)
    name = './figure/cluster ' + str(yi) + '.eps'
    #plt.savefig(name, format='eps', bbox_inches='tight')
    plt.show()


f = open('cluster_results.csv','w',encoding='utf-8',newline='')
csv_writer = csv.writer(f)
csv_writer.writerow(label) # 注意writerow和writerows的区别
f.close()

