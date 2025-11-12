import os
import sys
import pdb
import torch
import pickle
import time
   
    
print("Is CUDA available? {}".format(torch.cuda.is_available()))

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm.autonotebook import tqdm
from sklearn.model_selection import train_test_split

sys.path.insert(0, '..')

from chr import models
from chr import coverage
from chr.black_boxes import QNet, QRF
from chr.black_boxes_r import QBART
from chr.methods import CHR
from chr.others import CQR, CQR2, DistSplit, DCP, Oracle
from chr.others_r import DistSplit as DistSplitR
from chr.ours import CIR,CIR_rank,CIR_random,CIR_cut

from chr.utils import evaluate_predictions

# Default arguments
n_data = 2000
symmetry = 0
batch = 2021
batch_size = 10
alpha = 0.1

# Input arguments
n_data = int(sys.argv[1])
symmetry = int(sys.argv[2])
alpha = float(sys.argv[3])
batch = int(sys.argv[4])
batch_size = int(sys.argv[5])


tmp_file = "tmp_synthetic_rf/synthetic_s"+str(int(symmetry))+"_n"+str(int(n_data)) + "_b"+str(int(batch)) + ".pk"
outfile = "results_rf/synthetic_s"+str(int(symmetry))+"_n"+str(int(n_data)) + "_b"+str(int(batch)) +"_a"+str(float(alpha))+ ".txt"
results = pd.DataFrame()

for seed in np.arange(batch*1000, batch*1000+batch_size):
    np.random.seed(seed)
    torch.manual_seed(seed)

    data_model = models.Model_Ex1(symmetry=symmetry/100)

    # Generate training samples
    X_data, Y_data = data_model.sample(n_data)
    Y_data += 0

    # Uniform lower and upper limits for Y
    y_min = min(Y_data) + 0
    y_max = max(Y_data) + 0
    # y_min = -20 + 0
    # y_max = 20 + 0

    # Generate test samples
    n_test = 1000
    X_test, Y_test = data_model.sample(n_test)
    Y_test += 0

    # Split the data
    X_train, X_calib, Y_train, Y_calib = train_test_split(X_data, Y_data, test_size=0.5, random_state=2020)

    # Which black-box model?
    bbox_name = "RF"

    # Initialize the black-box and the conformalizer
    if bbox_name=="NNet":
        # grid_quantiles = np.arange(0.01,0.995,0.005)
        grid_quantiles = np.arange(0.01,1.0,0.01)
        bbox = QNet(grid_quantiles, 1, no_crossing=True, batch_size=1000, dropout=0.1,
                    num_epochs=2000, learning_rate=0.0005, calibrate=10)
    elif bbox_name=="RF":
        grid_quantiles = np.arange(0.01,1.0,0.01)
        bbox = QRF(grid_quantiles, n_estimators=100, min_samples_leaf=40, random_state=2020)
    elif bbox_name=="BART":
        grid_quantiles = np.arange(0.01,1.0,0.01)
        bbox = QBART(grid_quantiles, random_state=2020)

    # Train the black-box model
    if os.path.exists(tmp_file):
        print("Loading black box model...")
        filehandler = open(tmp_file, 'rb')
        bbox = pickle.load(filehandler)
    else:
        print("Training black box model...")
        bbox.fit(X_train, Y_train)
        filehandler = open(tmp_file, 'wb')
        pickle.dump(bbox, filehandler)


    ###############################
    # Apply all conformal methods #
    ###############################

    # CHR
    chr = CHR(bbox, ymin=y_min, ymax=y_max, y_steps=100, randomize=True)
    start_time = time.time()
    chr.calibrate(X_calib, Y_calib, alpha)
    bands_chr = chr.predict(X_test)
    time_cost = time.time() - start_time
    res_chr = evaluate_predictions(bands_chr, Y_test, X=X_test)
    res_chr["Time"] = time_cost
    res_chr["Method"] = "CHR"
    

    # CQR
    cqr = CQR(bbox)
    start_time = time.time()
    cqr.calibrate(X_calib, Y_calib, alpha)
    bands_cqr = cqr.predict(X_test)
    time_cost = time.time() - start_time
    
    res_cqr = evaluate_predictions(bands_cqr, Y_test, X=X_test)
    res_cqr["Time"] = time_cost
    res_cqr["Method"] = "CQR"

    # CQR2
    cqr2 = CQR2(bbox)
    start_time = time.time()
    cqr2.calibrate(X_calib, Y_calib, alpha)
    bands_cqr2 = cqr2.predict(X_test)
    time_cost =  time.time() - start_time
    
    res_cqr2 = evaluate_predictions(bands_cqr2, Y_test, X=X_test)
    res_cqr2["Time"] = time_cost
    res_cqr2["Method"] = "CQR2"

    # DCP
    dcp = DCP(bbox, ymin=y_min, ymax=y_max)
    start_time = time.time()
    dcp.calibrate(X_calib, Y_calib, alpha)
    bands_dcp = dcp.predict(X_test)
    time_cost =  time.time() - start_time
    
    res_dcp = evaluate_predictions(bands_dcp, Y_test, X=X_test)
    res_dcp["Time"] = time_cost
    res_dcp["Method"] = "DCP"

    # Dist-split
    distsplit = DistSplit(bbox, ymin=y_min, ymax=y_max)
    start_time = time.time()
    distsplit.calibrate(X_calib, Y_calib, alpha)
    bands_distsplit = distsplit.predict(X_test)
    time_cost =  time.time() - start_time
    
    res_distsplit = evaluate_predictions(bands_distsplit, Y_test, X=X_test)
    res_distsplit["Time"] = time_cost
    res_distsplit["Method"] = "DistSplit"
    ########################################################################
    #CIR with rank choice
    cir_rank = CIR_rank(bbox, ymin=y_min, ymax=y_max)
    start_time = time.time()
    cir_rank.calibrate(X_calib, Y_calib, alpha)
    bands_cir_rank = cir_rank.predict(X_test)
    time_cost =  time.time() - start_time
    
    res_cir_rank = evaluate_predictions(bands_cir_rank, Y_test, X=X_test)
    res_cir_rank["Time"] = time_cost
    res_cir_rank["Method"] = "CIR_rank"
    
    #CIR with random choice
    cir_random = CIR_random(bbox,ymin=y_min, ymax=y_max)
    start_time = time.time()
    cir_random.calibrate(X_calib, Y_calib, alpha)
    bands_cir_random = cir_random.predict(X_test,random_state=seed)
    time_cost =  time.time() - start_time
    
    res_cir_random = evaluate_predictions(bands_cir_random, Y_test, X=X_test)
    res_cir_random["Time"] = time_cost
    res_cir_random["Method"] = "CIR_random"
    
    #CIR with cut lengths
    cir_cut = CIR_cut(bbox,ymin=y_min, ymax=y_max)
    start_time = time.time()
    cir_cut.calibrate(X_calib, Y_calib, alpha)
    bands_cir_cut = cir_cut.predict(X_test)
    time_cost =  time.time() - start_time
    
    res_cir_cut = evaluate_predictions(bands_cir_cut, Y_test, X=X_test)
    res_cir_cut["Time"] = time_cost
    res_cir_cut["Method"] = "CIR_cut"
    
    #CIR
    cir = CIR(bbox,ymin=y_min, ymax=y_max)
    start_time = time.time()
    cir.calibrate(X_calib, Y_calib, alpha)
    bands_cir = cir.predict(X_test)
    time_cost =  time.time() - start_time
    
    res_cir = evaluate_predictions(bands_cir, Y_test, X=X_test)
    res_cir["Time"] = time_cost
    res_cir["Method"] = "CIR"
    ########################################################################

    # # Dist-split (R)
    # distsplit_r = DistSplitR()
    # distsplit_r.fit_calibrate(X_data, Y_data, alpha)
    # bands_distsplit_r = distsplit_r.predict(X_test)

    # res_distsplit_r = evaluate_predictions(bands_distsplit_r, Y_test, X=X_test)
    # res_distsplit_r["Method"] = "DistSplitR"

    # Oracle
    oracle = Oracle(data_model, alpha, ymin=y_min, ymax=y_max)
    bands_oracle = oracle.predict(X_test) + 20

    res_oracle = evaluate_predictions(bands_oracle, Y_test, X=X_test)
    res_oracle["Method"] = "Oracle"

    ###################
    # Combine results #
    ###################

    res = pd.concat([res_chr, res_cqr, res_cqr2, res_dcp, res_distsplit, res_oracle,res_cir,res_cir_random,res_cir_rank,res_cir_cut])
    res["Alpha"] = alpha
    res["n"] = n_data
    res["Symmetry"] = symmetry
    res["Skewness"] = oracle.skeweness
    res["Seed"] = seed

    print(res)

    # Save results
    results = pd.concat([results, res])
    results.to_csv(outfile, index=False)
