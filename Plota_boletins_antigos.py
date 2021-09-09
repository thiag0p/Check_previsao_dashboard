'''
  Autor: Francisco Thiago F. Parente
  Objetivo: Verificar o índice de acerto da previsão fornecida pela StormGeo

  Criação: 24/01/2018

'''

# Diretório onde estão os códigos da funções da MOP
from funcpvmo import data as pdat
import matplotlib.pyplot as plt
import numpy as np
from pandas import ExcelWriter, date_range, DataFrame
import datetime as dt
import matplotlib.dates as mdates

# Variável que ajusta a opacidade do plot dos dados observados
ALPHA = [1, .5, .3, .1]
# Cores referente a série temporal da StormGeo
STGCOLORS = ['#FF0000', '#006400', '#FBC006',
             '#3B1845', '#E09085', '#8470FF']
# Lista com os nomes dos campos de previsão
CAMUSR = "Papa_Terra_15532"
# Data do boletim de interesse
DATA = u"18/05/2019 00:00:00"
# Matutino ou Vespertino
TMPUSR = "Matutino"
# Diretório onda será salvo excel
DIREC = u"C:\\Users\\bhyk\\Desktop\\teste"
# Diretório onde estão os CSVs da StormGeo
SGPATH = 'path_privado'
# Unidade de medida
UND = u"nós"

# ======================================================================= #
DATANL = dt.datetime.strptime(DATA, '%d/%m/%Y %H:%M:%S')

# PLOTANDO E ESCREVENDO NA PLANILHA EXCEL
linha = 2
colms = ['C', 'D', 'E', 'F']

print('**********************************************\n' +
      CAMUSR + '\n' +
      '**********************************************')

# ======== PROCURANDO .CSV DO PERÍODO DE INTERESSE ================ #
if TMPUSR == 'Matutino':
    ARQ = (SGPATH + '\\StormGeo_' + CAMUSR + '_' +
           dt.datetime.strftime(DATANL, '%Y%m%d') + '11.csv')
else:
    ARQ = (SGPATH + '\\StormGeo_' + CAMUSR + '_' +
           dt.datetime.strftime(DATANL, '%Y%m/%d') + '20.csv')

    # ========= LENDO .CSV DA ÁREA ESPECÍFICA ======================= #
WDGDF, WVGDF, DATEMIN, DATEMAX = pdat.read_csv_stg(ARQ)

#  =========================================================================  #
#                               VENTO                                         #
#  =========================================================================  #

# ==================== PLOTANDO COMPARAÇÃO ================

plt.figure(1, figsize=(15, 8))
f = plt.subplot(2, 1, 1)
WDGDF["Int. StormGeo"].dropna().plot(linewidth=2,
                                     marker='o',
                                     color='#FF0000',
                                     markersize=6)
plt.ylabel(u'Intensidade média do vento (nós)')
f.set_xticklabels([])
plt.title(CAMUSR)
plt.fill_between(WDGDF.index, 20, 28, facecolor='#FFE4B2',
                 edgecolor='#FFE4B2')
plt.fill_between(WDGDF.index, 28, f.get_ylim()[1],
                 facecolor='#FFB2B2', edgecolor='#FFE4B2')
f.grid(True, linewidth=2)
f.xaxis.set_major_locator(mdates.HourLocator(interval=12))

f = plt.subplot(2, 1, 2)
WDGDF["Dir. StormGeo"].dropna().plot(linewidth=2,
                                     marker='o',
                                     color='#FF0000',
                                     markersize=6)
plt.ylabel(u'Direção ($\circ$)')
f.xaxis.set_major_formatter(
    mdates.DateFormatter('%d%b-%Hh'))
f.grid(True, linewidth=2)
f.xaxis.set_major_locator(mdates.HourLocator(interval=12))

plt.savefig(
    DIREC + '\\' + CAMUSR[0:7] + '_vento_' + DATA[0:2] + '.png',
    format='png')

#  ============================================  #
#                   ONDA                         #
#  ============================================  #
plt.figure(2, figsize=(15, 8))
f = plt.subplot(2, 1, 1)
WVGDF[u"Hs StormGeo"].dropna().plot(linewidth=2,
                                    marker='o',
                                    color='#FF0000',
                                    markersize=6)

plt.ylabel(u'Altura significativa (m)')
f.set_xticklabels([])
plt.title(CAMUSR)
plt.fill_between(WVGDF.index, 2, 3.5,
                 facecolor='#FFE4B2',
                 edgecolor='#FFE4B2')
plt.fill_between(WVGDF.index, 3.5,
                 f.get_ylim()[1],
                 facecolor='#FFB2B2',
                 edgecolor='#FFE4B2')
plt.ylim(0, f.get_ylim()[1])
f.grid(True, linewidth=2)

plt.subplot(2, 1, 2)
WVGDF[u"Dir. StormGeo"].dropna().plot(linewidth=2,
                                      marker='o',
                                      color='#FF0000',
                                      markersize=6)
plt.ylabel(u'Direção ($\circ$)')
f.grid(True, linewidth=2)

plt.savefig(
    DIREC + '\\' + CAMUSR[0:7] + '_onda_' + DATA[0:2] + '.png',
    format='png')
