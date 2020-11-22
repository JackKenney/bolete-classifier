import pandas as pd
import numpy as np
from collections import defaultdict

all_labels = pd.read_csv("./data_pipeline/clean_data/labels.csv")
features = pd.read_csv("./data_pipeline/clean_data/features.csv")
ids = pd.read_csv("./data_pipeline/clean_data/final_ids.csv")

selected_ids = ids["OldID"].values
selected_idxs = []
for i in range(len(all_labels)):
    if all_labels.loc[i]["ID"] in selected_ids:
        selected_idxs.append(i)
labels = all_labels.loc[selected_idxs]

feats = [col for col in labels if col.startswith("F")][:-5]
edibility = [col for col in labels if col.startswith("F")][-5:]


def get_num_species():
    return len(selected_ids)


def get_old_id(new_id):
    old_id = int(ids.loc[ids["NewID"] == new_id]["OldID"].values)
    return old_id


def get_feats(new_id):
    species_id = get_old_id(new_id)
    features = labels.loc[labels["ID"] == species_id][feats]
    return features.to_numpy()


def get_name(new_id):
    species_id = get_old_id(new_id)
    return labels.loc[labels["ID"] == species_id]["NewName"].to_string().split()[1]


def get_edibility(species_id):
    species_id = get_old_id(species_id)
    ed = np.argmax(labels.loc[labels["ID"] == species_id][edibility].values[0])
    return ed


def similarity(a, b):
    return np.sum(a * b)


## Vectorized Version ##
Feats4All = labels.loc[:, feats].to_numpy()


def lookalikes(spec_id, p):
    species = get_feats(spec_id)
    idxs = np.where(Feats4All.dot(species.T) >= p * similarity(species, species))[0]
    return idxs


def species_from_feats(feats, p):
    idxs = np.where(Feats4All.dot(feats.T) >= p * similarity(feats, feats))[0]
    return idxs


pd.set_option("display.max_colwidth", 100)


def print_feats(species_id):
    feats = get_feats(species_id)
    idxs = np.where(feats > 0)[1]
    print(idxs)
    for idx in idxs:
        print(features.loc[features["id"] == idx + 1]["feature"].to_string()[-15:])
    print()


def performance(tau_hat, t):
    acc = t in tau_hat
    M = len(selected_ids)
    return ((M - len(tau_hat)) * acc) / M


def get_performance(u, t, p):
    tau_hat = species_from_feats(u, p)
    return performance(tau_hat, t)


def estimate_performance(u, p):
    res = np.zeros((len(selected_ids),))
    for t in range(len(selected_ids)):
        perf = get_performance(u, t, p)
        # print(perf)
        res[t] = perf
    return res


def get_performance_direct(ids, t, p):
    size_of_tau_hat = len(lookalikes(ids[0], p))
    tau_hat = ids[:size_of_tau_hat]
    return performance(tau_hat, t)


def estimate_performance_direct(ids, p):
    res = np.zeros((len(selected_ids),))
    for t in range(len(selected_ids)):
        perf = get_performance_direct(ids, t, p)
        res[t] = perf
    return res
