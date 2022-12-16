import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def Cap_df(q0, q1, q2, q3, v, nol1, nol2):
    t = 0.034
    c = 0.966
    k_jam = c * 5280 / 14.7 + t * 5280 / 47
    df = pd.DataFrame([q0, q1, q2, q3], columns=['q'])
    df['Cap'] = [1, 2, 3, 4]
    df['kj'] = [k_jam * nol1, k_jam * nol2, k_jam * nol1, k_jam * nol2]
    if v == 25:
        df['Cap'][0] = 1100 * nol1
        df['Cap'][1] = 1100 * nol2
        df['Cap'][2] = df['Cap'][0]
        df['Cap'][3] = df['Cap'][1]

    elif v == 35:
        df['Cap'][0] = 1460 * nol1
        df['Cap'][1] = 1460 * nol2
        df['Cap'][2] = df['Cap'][0]
        df['Cap'][3] = df['Cap'][1]

    elif v == 45:
        df['Cap'][0] = 1400 * nol1
        df['Cap'][1] = 1400 * nol2
        df['Cap'][2] = df['Cap'][0]
        df['Cap'][3] = df['Cap'][1]
    else:
        print('Speed limit should be 25, 35, or 45.')

    return df


def Cyclelength(df):

    y1 = df['q'][0] / df['Cap'][0]
    y2 = max(df['q'][1], df['q'][3]) / df['Cap'][1]
    lost = 10 / 60  ## 10 sec used as a typical value in unit of minute
    Cy = max(1, lost / (1 - y1 - y2))
    G1 = y1 * (Cy - lost)
    G2 = Cy - lost - G1

    return Cy, G1, G2


def df_plot(org_df, v, j):
    Cy, G1, G2 = Cyclelength(org_df)
    lost = 10 / 60
    # create a dataframe for all coefficients needed
    coe = pd.DataFrame(columns=['kf', 'kc', 'Uoc', 'Ucj', 'Ucf', 'Ufj',
                                't1', 't2', 't3', 'T', 'x1', 'x2', 'x3']
                       , index=[0, 1, 2, 3])
    Coe = pd.concat([org_df, coe], axis=1, join='outer')

    # q-k curves coefficient calculations
    Coe['kf'] = Coe['q'] / v
    Coe['kc'] = Coe['Cap'] / v

    Coe['Uoc'] = Coe['Cap'] / Coe['kc']
    Coe['Ucj'] = -Coe['Cap'] / Coe['kj']
    Coe['Ucf'] = (Coe['Cap'] - Coe['q']) / (Coe['kc'] - Coe['kf'])
    Coe['Ufj'] = -Coe['q'] / (Coe['kj'] - Coe['kf'])

    Coe['t1'][0] = 0
    Coe['t2'][0] = (G2 + lost) / 60
    Coe['t1'][1] = (G2 + lost) / 60
    Coe['t2'][1] = Cy / 60

    if j > 2:
        Coe['t1'][2] = Coe['t1'][0]
        Coe['t1'][3] = Coe['t1'][1]
        Coe['t2'][2] = Coe['t2'][0]
        Coe['t2'][3] = Coe['t2'][1]

    # values for state diagram
    Coe['T'] = (Coe['t2'] - Coe['t1']) * Coe['Ufj'] / (Coe['Ucj'] - Coe['Ufj'])
    Coe['x1'] = Coe['Ucj'] * Coe['T']
    Coe['x2'] = 0.005 * Coe['Uoc']
    Coe['x3'] = 0.005 * v
    Coe['x4'] = 0.005 * Coe['Ucf']
    Coe['t3'] = Coe['t2'] + Coe['T']

    return Coe