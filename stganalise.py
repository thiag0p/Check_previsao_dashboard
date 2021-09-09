'''
  Autor: Francisco Thiago F. Parente
  Objetivo: Verificar o índice de acerto
  da previsão fornecida pela StormGeo

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


def stg_boletim(CAMUSR, DATA, TMPUSR, DIREC, SGPATH, UND):
    '''
        CAMUSR -> Lista com os nomes dos campos de previsão
        DATA   -> Data do boletim de interesse
        TMPUSR -> Matutino ou Vespertino
        DIREC  -> Diretório onda será salvo excel
        SGPATH -> Diretório onde estão os CSVs da StormGeo
        UND    -> Unidade de medida do vento
    '''
    UNID = UND.lower()

    # CRIANDO ARQUIVO EXCEL PARA REGISTRO DO ÍNDICE DE ACERTO

    writer = ExcelWriter(DIREC + '\\PAs.xlsx')
    sheet = writer.book.add_worksheet('PAs')
    fmt = writer.book.add_format({'align': 'center',
                                  'valign': 'vcenter'})
    fmt2 = writer.book.add_format({'bold': 1,
                                   'border': 1,
                                   'align': 'center',
                                   'valign': 'vcenter',
                                   'fg_color': '#cccccc'})
    sheet.write('A1', u'Campo', fmt2)
    sheet.write('B1', u'Parâmetro', fmt2)
    sheet.merge_range('C1:F1', u'Unidades', fmt2)
    sheet.write('G1', u'PA médio', fmt2)

    # ======================================================================= #
    DATANL = dt.datetime.strptime(DATA, '%d/%m/%Y %H:%M:%S')

    # PLOTANDO E ESCREVENDO NA PLANILHA EXCEL
    linha = 2
    colms = ['C', 'D', 'E', 'F']
    for x, CAMP in enumerate(CAMUSR.values()):

        print('**********************************************\n' +
              CAMUSR.keys()[x] + '\n' +
              '**********************************************')

        # ======== PROCURANDO .CSV DO PERÍODO DE INTERESSE ================ #
        if TMPUSR == 'Matutino':
            ARQ = (SGPATH + '\\StormGeo_' + CAMP + '_' +
                   dt.datetime.strftime(DATANL, '%Y%m%d') + '11.csv')
        else:
            ARQ = (SGPATH + '\\StormGeo_' + CAMP + '_' +
                   dt.datetime.strftime(DATANL, '%Y%m/%d') + '20.csv')

        # ============== LENDO UCDS PRIORITÁRIAS ========================= #

        UCDPRIOR = pdat.load_ucd_referencia(
            'ReferenceStationsByArea_WithCSVname_20180720.xlsx')

        # ========= LENDO .CSV DA ÁREA ESPECÍFICA ======================= #

        WDGDF, WVGDF, DATEMIN, DATEMAX = pdat.read_csv_stg(ARQ)

        # ==================== lENDO OS DADOS OBSERVADOS ============ #

        UCDS_WIND = UCDPRIOR.loc[UCDPRIOR.index[CAMP in UCDPRIOR.index],
                                 'WNDref']
        UCDS_WAVE = UCDPRIOR.loc[UCDPRIOR.index[CAMP in UCDPRIOR.index],
                                 'WAVref']

        #  ============================================  #
        #                   VENTO                        #
        #  ============================================  #

        if not UCDS_WIND.values:
            print(CAMP[0:-6] + ' NAO POSSUI UCD DE REFERENCIA PARA VENTO!')
        else:
            wndy = pdat.get_wndata(UCDS_WIND.values.item(),
                                   DATEMIN,
                                   DATEMAX,
                                   UND)

            if not wndy.minor_axis.any():
                print('NAO POSSUI DADOS NA UCD DE REFERENCIA')
            else:
                if wndy[:, :, u'Intensidade (' + UNID + ')'].isnull().all().all():
                    print('NAO TEM DADOS NESTE PERIODO!')
                else:
                    for _, ucd in enumerate(wndy.items):

                        WDGDF['Int. ' + ucd] = wndy[ucd, :, u'Intensidade (' + UNID + ')'].values
                        WDGDF['Dir. ' + ucd] = wndy[ucd, :, u'Direção'].values

                    # ==================== CALCULO DE INDICE DE ACERTO ========
                    IIWND = {}
                    sheet.write('A' + str(linha), CAMUSR.keys()[x], fmt)
                    sheet.write('B' + str(linha), 'Vento', fmt)

                    for uu, u in enumerate(wndy.items):
                        sheet.write(colms[uu] + str(linha), u, fmt)
                    linha += 1

                    for uu, u in enumerate(wndy.items):
                        IIWND[u] = pdat.calc_pa(WDGDF['Int. StormGeo'].values,
                                                WDGDF['Int. ' + u].values)

                        sheet.write(colms[uu] + str(linha),
                                    np.round(IIWND[u], decimals=1),
                                    fmt)

                    sheet.write('G' + str(linha), np.mean(IIWND.values()), fmt)
                    linha += 1

                    # ==================== PLOTANDO COMPARAÇÃO ================

                    plt.figure(1, figsize=(15, 8))
                    f = plt.subplot(2, 1, 1)
                    leg = []
                    c = 0
                    for p in WDGDF.keys():
                        if p[0:4] == 'Int.':
                            if p[5::] == 'StormGeo':
                                WDGDF[p].dropna().plot(linewidth=2,
                                                       marker='o',
                                                       color='#FF0000',
                                                       markersize=6)
                                leg.append(p)
                            else:
                                if not WDGDF[p].dropna().values.any():
                                    print(u'não tem dados medidos')
                                else:
                                    WDGDF[p].dropna().plot(linewidth=2,
                                                           marker='o',
                                                           grid='on',
                                                           color='#000080',
                                                           alpha=ALPHA[c],
                                                           markersize=4)
                                    leg.append(p + ' (' +
                                               str(np.round(IIWND[p[5::]],
                                                   decimals=1)) + ')')
                                c += 1
                    plt.ylabel(u'Intensidade média do vento (nós)')
                    f.set_xticklabels([])
                    plt.title(CAMUSR.keys()[x])
                    plt.fill_between(WDGDF.index, 20, 28, facecolor='#FFE4B2',
                                     edgecolor='#FFE4B2')
                    plt.fill_between(WDGDF.index, 28, f.get_ylim()[1],
                                     facecolor='#FFB2B2', edgecolor='#FFE4B2')
                    f.grid(True, linewidth=2)
                    f.xaxis.set_major_locator(mdates.HourLocator(interval=12))

                    f = plt.subplot(2, 1, 2)
                    c = 0
                    for p in WDGDF.keys():
                        if p[0:4] == 'Dir.':
                            if p[5::] == 'StormGeo':
                                WDGDF[p].dropna().plot(linewidth=2,
                                                       marker='o',
                                                       color='#FF0000',
                                                       markersize=6)
                            else:
                                if not WDGDF[p].dropna().values.any():
                                    print(u'não tem dados medidos')
                                else:
                                    WDGDF[p].dropna().plot(linewidth=2,
                                                           marker='o',
                                                           grid='on',
                                                           color='#000080',
                                                           alpha=ALPHA[c],
                                                           markersize=4)
                                c += 1
                    plt.ylabel(u'Direção ($\circ$)')

                    plt.legend(leg,
                               prop={'size': 14},
                               bbox_to_anchor=(.5, -.4),
                               loc=10,
                               ncol=len(WDGDF.keys()) / 2)
                    f.xaxis.set_major_formatter(
                        mdates.DateFormatter('%d%b-%Hh'))
                    f.grid(True, linewidth=2)
                    f.xaxis.set_major_locator(mdates.HourLocator(interval=12))

                    plt.savefig(
                        DIREC + '\\' + CAMP + '_vento.png',
                        format='png')

        #  ============================================  #
        #                   ONDA                         #
        #  ============================================  #
        if not UCDS_WAVE.values:
            print(CAMP[0:-6] + ' NAO POSSUI UCD DE REFERENCIA PARA ONDA!')
        else:

            wave, wave_inst = pdat.get_wavedata(UCDS_WAVE.values.item(),
                                                DATEMIN,
                                                DATEMAX)

            if not wave.minor_axis.any():
                print('NAO POSSUI DADOS NA UCD DE REFERENCIA')
            else:
                if wave[:, :, u'Altura significativa (m)'].isnull().all().all():
                    print('NAO TEM DADOS NESTE PERIODO')
                else:
                    for _, ucd in enumerate(wave.items):

                        WVGDF['Hs ' + ucd] = wave[ucd, :, u'Altura significativa (m)'].values
                        WVGDF['Dir. ' + ucd] = wave[ucd, :, u'Direção'].values

                    IIWAV = {}
                    sheet.write('B' + str(linha), 'Onda', fmt)

                    for uu, u in enumerate(wave.items):
                        sheet.write(colms[uu] + str(linha), u, fmt)
                    linha += 1

                    for uu, u in enumerate(wave.items):
                        IIWAV[u] = pdat.calc_pa(WVGDF['Hs StormGeo'].values,
                                                WVGDF['Hs ' + u].values)

                        sheet.write(colms[uu] + str(linha),
                                    np.round(IIWAV[u], decimals=1),
                                    fmt)
                    sheet.write('G' + str(linha), np.mean(IIWAV.values()), fmt)
                    linha += 1

                    plt.figure(2, figsize=(15, 8))

                    # --------------- PLOT ONDA --------------------

                    f = plt.subplot(2, 1, 1)
                    leg = []
                    c = 0
                    for p in WVGDF.keys():
                        if p[0:2] == 'Hs':
                            if p[3::] == 'StormGeo':
                                WVGDF[p].dropna().plot(linewidth=2,
                                                       marker='o',
                                                       color='#FF0000',
                                                       markersize=6)
                                leg.append(p)
                            else:
                                if not WVGDF[p].dropna().values.any():
                                    print(u'não tem dados medidos')
                                else:
                                    WVGDF[p].dropna().plot(linewidth=2,
                                                           marker='o',
                                                           grid='on',
                                                           color='#000080',
                                                           alpha=ALPHA[c],
                                                           markersize=4)
                                    leg.append(p + ' (' +
                                               str(np.round(IIWAV[p[3::]],
                                                   decimals=1)) + ')')
                            c += 1
                    plt.ylabel(u'Altura significativa (m)')
                    f.set_xticklabels([])
                    plt.title(CAMUSR.keys()[x])
                    plt.fill_between(WVGDF.index, 2, 3.5,
                                     facecolor='#FFE4B2',
                                     edgecolor='#FFE4B2')
                    plt.fill_between(WVGDF.index, 3.5,
                                     f.get_ylim()[1],
                                     facecolor='#FFB2B2',
                                     edgecolor='#FFE4B2')
                    plt.ylim(0, f.get_ylim()[1])

                    plt.subplot(2, 1, 2)
                    c = 0
                    for p in WVGDF.keys():
                        if p[0:4] == 'Dir.':
                            if p[5::] == 'StormGeo':
                                WVGDF[p].dropna().plot(linewidth=2,
                                                       marker='o',
                                                       color='#FF0000',
                                                       markersize=6)
                            else:
                                if not WVGDF[p].dropna().values.any():
                                    print(u'não tem dados medidos')
                                else:
                                    WVGDF[p].dropna().plot(linewidth=2,
                                                           marker='o',
                                                           grid='on',
                                                           color='#000080',
                                                           alpha=ALPHA[c],
                                                           markersize=4)
                            c += 1
                    plt.ylabel(u'Direção ($\circ$)')

                    plt.legend(leg,
                               prop={'size': 14},
                               bbox_to_anchor=(.5, -.4),
                               loc=10,
                               ncol=len(WVGDF.keys()) / 2)

                    plt.savefig(
                        DIREC + '\\' + CAMP + '_onda.png',
                        format='png')
        plt.close('all')

    writer.book.close()

    ans = 'FINALIZADO!'

    return ans


def stg_med(CAMUSR, DATAINIC, DATAFINL, TMPUSR, DIREC, SGPATH, UND, OPT):

    # =========================================================================
    # Definindo os dias que serão extraídas as previsões
    days = date_range(dt.datetime.strptime(DATAINIC, '%d/%m/%Y %H:%M:%S'),
                      dt.datetime.strptime(DATAFINL, '%d/%m/%Y %H:%M:%S'),
                      freq='D')

    # =========================================================================
    # Lendo planilha de UCDS prioritárias
    UCDPRIOR = pdat.load_ucd_referencia(
        'ReferenceStationsByArea_ReviewCurrent_20180201.xlsx')
    # =========================================================================

    # Criando planilha excel para registro dos índices de acerto
    writer = ExcelWriter(DIREC + '\\PAs.xlsx')
    # Definindo formato das células da planilha
    fmt = writer.book.add_format({'align': 'center',
                                  'valign': 'vcenter'})
    fmt2 = writer.book.add_format({'bold': 1,
                                   'border': 1,
                                   'align': 'center',
                                   'valign': 'vcenter',
                                   'fg_color': '#cccccc'})
    # Variável de auxílio para elaboração da planilha
    colms = ['C', 'D', 'E', 'F']  # colunas referentes às ucds de referência
    # =========================================================================

    # Início da leitura dos observados + impressão na planilha excel
    # Criando as abas da planilha
    for J in OPT:
        writer.book.add_worksheet('PAs_' + str(J) + 'h')

    # Escrevendo cabeçalho
    for x, J in enumerate(OPT):
        w = writer.book.worksheets()[x]
        w.write('A1', u'Campo', fmt2)
        w.write('B1', u'Parâmetro', fmt2)
        w.merge_range('C1:F1', u'Unidades', fmt2)
        w.write('G1', u'PA médio', fmt2)
        w.set_column('A:A', 31)
        w.set_column('B:B', 12)

    linha = 2  # linha que inicia a imprimir os dados
    # Loop para todos os campos de interesse do usuário
    for x, CAMP in enumerate(CAMUSR.values()):
        # Início da leitura dos dados de previsão
        WDGDF = DataFrame()
        WVGDF = DataFrame()
        # ====================================================================

        for J in OPT:
            # Escrevendo no terminal qual o campo está sendo avaliado
            print('**********************************************\n' +
                  CAMUSR.keys()[x] + ' (' + str(J) + 'h)\n' +
                  '**********************************************')
            WDAJU = DataFrame()
            WVAJU = DataFrame()
            for DATANL in days:
                # Lendo .csv do campo específico
                if TMPUSR == 'Matutino':
                    ARQ = (SGPATH + '\\StormGeo_' + CAMP + '_' +
                           dt.datetime.strftime(DATANL, '%Y%m%d') + '11.csv')
                else:
                    ARQ = (SGPATH + '\\StormGeo_' + CAMP + '_' +
                           dt.datetime.strftime(DATANL, '%Y%m/%d') + '20.csv')
                WD, WV, di, df = pdat.read_csv_stg(ARQ)
                # Gravando as informações no mesmo Dataframe
                WDAJU = WDAJU.append(WD[WD.index[J-24]:WD.index[J-1]])
                WVAJU = WVAJU.append(WV[WV.index[J-24]:WV.index[J-1]])
            WDGDF['Int. StormGeo (' + str(J) + 'h)'] = WDAJU['Int. StormGeo']
            WDGDF['Dir. StormGeo (' + str(J) + 'h)'] = WDAJU['Dir. StormGeo']
            WVGDF['Hs StormGeo (' + str(J) + 'h)'] = WVAJU['Hs StormGeo']
            WVGDF['Dir. StormGeo (' + str(J) + 'h)'] = WVAJU['Dir. StormGeo']

        # ====================================================================

        # Definindo data inicial e data final para acesso aos dados observados
        DTI = dt.datetime.strftime(WDGDF.index[0], '%d/%m/%Y %H:%M:%S')
        DTF = dt.datetime.strftime(WDGDF.index[-1], '%d/%m/%Y %H:%M:%S')
        # =====================================================================

        # Identificando quais as UCD's de referência do campo para cada var
        UCDS_WIND = UCDPRIOR.loc[UCDPRIOR.index == CAMP[0:-6], 'WNDref']
        UCDS_WAVE = UCDPRIOR.loc[UCDPRIOR.index == CAMP[0:-6], 'WAVref']
        # =====================================================================

        # ====================================================================

        # Lendo dados de vento
        # Caso não haja UCD de referência, avisa no terminal e não lê dados
        if not UCDS_WIND.values:
            print(CAMP[0:-6] + ' NAO POSSUI UCD DE REFERENCIA PARA VENTO!')
        else:
            # ================================================================
            #  Ajustando o tempo para hora local
            INIC = dt.datetime.strftime(WDGDF.index[0] + dt.timedelta(hours=2),
                                        '%d/%m/%Y %H:%M:%S')
            FINL = dt.datetime.strftime(WDGDF.index[-1] + dt.timedelta(hours=2),
                                        '%d/%m/%Y %H:%M:%S')
            # ================================================================

            # Lendo Dados de vento da(s) UCD(s)
            wndy = pdat.get_wndata(UCDS_WIND.values.item(), INIC, FINL, UND)
            # Verifica se há dados dados
            if not wndy.minor_axis.any():
                print('VENTO - NAO POSSUI DADOS NA UCD DE REFERENCIA')
            else:
                # Verifica se há dados de intensidade
                if wndy[:, :, u'Intensidade (' + UNID + ')'].isnull().all().all():
                    print('!!!! NAO TEM DADOS DE INTENSIDADE ' +
                          'DO VENTO NESTE PERIODO!!!!')
                # Havendo dados, grava no mesmo Dataframe dos dados da stormgeo
                else:
                    # Loop para as UCD's com dados
                    for _, ucd in enumerate(wndy.items):
                        WDGDF['Int. ' + ucd] = wndy[ucd, :, u'Intensidade (' + UNID + ')'].values
                        WDGDF['Dir. ' + ucd] = wndy[ucd, :, u'Direção'].values
                    # ========================================================

                    # Escrevendo na planilha excel
                    for j, _ in enumerate(OPT):
                        w = writer.book.worksheets()[j]
                        w.write('A' + str(linha), CAMUSR.keys()[x], fmt)
                        w.write('B' + str(linha), 'Vento', fmt)
                        for uu, u in enumerate(wndy.items):
                            w.write(colms[uu] + str(linha), u, fmt)
                    linha += 1
                    # ========================================================

                    # Calculo e impressão na planilha do índice de acerto
                    IIWND = {}
                    for _, u in enumerate(wndy.items):
                        for J in OPT:
                            IIWND[u + ' (' + str(J) + 'h)'] = pdat.calc_pa(
                                WDGDF['Int. StormGeo (' + str(J) + 'h)'].values,
                                WDGDF['Int. ' + u].values)
                    # imprime PA de cada unidade
                    for j, J in enumerate(OPT):
                        w = writer.book.worksheets()[j]
                        for uu, u in enumerate(wndy.items):
                            w.write(colms[uu] + str(linha),
                                    np.round(IIWND[u + ' (' + str(J) + 'h)'],
                                             decimals=1),
                                    fmt)
                        # imprime PA médio
                        p = {}
                        for n, nn in enumerate(IIWND.keys()):
                            if str(J) in nn:
                                p[nn] = IIWND.values()[n]
                        w.write('G' + str(linha), np.mean(p.values()), fmt)
                    linha += 1
                    # ========================================================

                    # Plotando comparação para o vento
                    plt.figure(1, figsize=(15, 8))
                    f = plt.subplot(2, 1, 1)
                    leg = []
                    c = 0
                    for p in WDGDF.keys():
                        if p[0:4] == 'Int.':
                            if p[5:13] != 'StormGeo':
                                if not WDGDF[p].dropna().values.any():
                                    print(u'não tem dados medidos')
                                else:
                                    plt.plot(WDGDF[p].dropna().index,
                                             WDGDF[p].dropna(),
                                             linewidth=1,
                                             marker='o',
                                             color='#000080',
                                             alpha=ALPHA[c],
                                             markersize=3)
                                    leg.append(p[5::])
                                    c += 1
                    for j, J in enumerate(OPT):
                        plt.plot(
                            WDGDF['Int. StormGeo (' + str(J) + 'h)'].dropna().index,
                            WDGDF['Int. StormGeo (' + str(J) + 'h)'].dropna(),
                            linewidth=2,
                            color=STGCOLORS[j],
                            marker='o',
                            markersize=3)
                        leg.append('StormGeo (' + str(J) + 'h)')
                    plt.ylabel(u'Intensidade média do vento (nós)')
                    f.grid(True, linewidth=2)
                    f.xaxis.set_major_locator(mdates.DayLocator(interval=2))
                    f.set_xticklabels([])
                    plt.title(CAMUSR.keys()[x])
                    plt.fill_between(WDGDF.index, 20, 28, facecolor='#FFE4B2',
                                     edgecolor='#FFE4B2')
                    plt.fill_between(WDGDF.index, 28, f.get_ylim()[1],
                                     facecolor='#FFB2B2', edgecolor='#FFE4B2')
                    plt.legend(leg,
                               prop={'size': 14},
                               bbox_to_anchor=(.5, -1.35),
                               loc=10,
                               ncol=len(WDGDF.keys()) / 2)

                    f = plt.subplot(2, 1, 2)
                    c = 0
                    for p in WDGDF.keys():
                        if p[0:4] == 'Dir.':
                            if p[5:13] != 'StormGeo':
                                if not WDGDF[p].dropna().values.any():
                                    print(u'não tem dados medidos')
                                else:
                                    plt.plot(WDGDF[p].dropna().index,
                                             WDGDF[p].dropna(),
                                             linewidth=1,
                                             marker='o',
                                             color='#000080',
                                             alpha=ALPHA[c],
                                             markersize=3)
                                    c += 1
                    for j, J in enumerate(OPT):
                        plt.plot(
                            WDGDF['Dir. StormGeo (' + str(J) + 'h)'].dropna().index,
                            WDGDF['Dir. StormGeo (' + str(J) + 'h)'].dropna(),
                            linewidth=2,
                            color=STGCOLORS[j],
                            marker='o',
                            markersize=3)
                    plt.ylabel(u'Direção ($\circ$)')
                    f.grid(True, linewidth=2)
                    f.xaxis.set_major_locator(mdates.DayLocator(interval=2))
                    f.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))

                    plt.savefig(
                        DIREC + '\\' + CAMP +
                        '_vento.png',
                        format='png')
                    plt.close()
        #  ====================================================================

        # Lendo dados de onda
        # Caso não haja UCD de referência, avisa no terminal e não lê dados
        if not UCDS_WAVE.values:
            print(CAMP[0:-6] + ' NAO POSSUI UCD DE REFERENCIA PARA ONDA!')
        else:
            wave = pdat.get_wavedata(UCDS_WAVE.values.item(), DTI, DTF)
            # Verifica se há dados dados
            if not wave.minor_axis.any():
                print('ONDA - NAO POSSUI DADOS NA UCD DE REFERENCIA')
            else:
                # Verifica se há dado de altura significativa
                if wave[:, :, u'Altura significativa (m)'].isnull().all().all():
                    print('NAO TEM DADOS NESTE PERIODO')
                # Havendo dados, grava no mesmo Dataframe dos dados da stormgeo
                else:
                    for _, ucd in enumerate(wave.items):
                        WVGDF['Hs ' + ucd] = wave[ucd, :, u'Altura significativa (m)'].values
                        WVGDF['Dir. ' + ucd] = wave[ucd, :, u'Direção'].values
                    # ========================================================
                    # Calculo e impressão na planilha do índice de acerto
                    IIWAV = {}
                    for j, _ in enumerate(OPT):
                        w = writer.book.worksheets()[j]
                        w.write('B' + str(linha), 'Onda', fmt)

                    # Escrevendo o nome das unidades
                    for uu, u in enumerate(wave.items):
                        for j, _ in enumerate(OPT):
                            w = writer.book.worksheets()[j]
                            w.write(colms[uu] + str(linha), u, fmt)
                    linha += 1

                    for uu, u in enumerate(wave.items):
                        for J in OPT:
                            IIWAV[u + ' (' + str(J) + 'h)'] = pdat.calc_pa(
                                WVGDF['Hs StormGeo (' + str(J) + 'h)'].values,
                                WVGDF['Hs ' + u].values)

                    # imprime PA de cada unidade
                    for j, J in enumerate(OPT):
                        w = writer.book.worksheets()[j]
                        for uu, u in enumerate(wave.items):
                            w.write(colms[uu] + str(linha),
                                    np.round(IIWAV[u + ' (' + str(J) + 'h)'],
                                             decimals=1),
                                    fmt)
                        # imprime PA médio
                        p = {}
                        for n, nn in enumerate(IIWAV.keys()):
                            if str(J) in nn:
                                p[nn] = IIWAV.values()[n]
                        w.write('G' + str(linha), np.mean(p.values()), fmt)
                    linha += 1
                    # ========================================================

                    # Plotando comparação para onda
                    plt.figure(2, figsize=(15, 8))

                    f = plt.subplot(2, 1, 1)
                    leg = []
                    c = 0
                    for p in WVGDF.keys():
                        if p[0:2] == 'Hs':
                            if p[3:11] != 'StormGeo':
                                if not WVGDF[p].dropna().values.any():
                                    print(u'Não tem dados medidos')
                                else:
                                    plt.plot(WVGDF[p].dropna().index,
                                             WVGDF[p].dropna(),
                                             linewidth=1,
                                             marker='o',
                                             color='#000080',
                                             alpha=ALPHA[c],
                                             markersize=3)
                                    leg.append(p[3::])
                                    c += 1
                    for j, J in enumerate(OPT):
                        plt.plot(
                            WVGDF['Hs StormGeo (' + str(J) + 'h)'].dropna().index,
                            WVGDF['Hs StormGeo (' + str(J) + 'h)'].dropna(),
                            linewidth=2,
                            color=STGCOLORS[j],
                            marker='o',
                            markersize=3)
                        leg.append('StormGeo (' + str(J) + 'h)')
                    plt.ylabel(u'Altura significativa (m)')
                    plt.title(CAMUSR.keys()[x])
                    plt.fill_between(WVGDF.index, 2, 3.5,
                                     facecolor='#FFE4B2',
                                     edgecolor='#FFE4B2')
                    plt.fill_between(WVGDF.index, 3.5,
                                     f.get_ylim()[1],
                                     facecolor='#FFB2B2',
                                     edgecolor='#FFE4B2')
                    plt.ylim(0, f.get_ylim()[1])
                    f.grid(True, linewidth=2)
                    f.xaxis.set_major_locator(mdates.DayLocator(interval=2))
                    f.set_xticklabels([])
                    plt.legend(leg,
                               prop={'size': 14},
                               bbox_to_anchor=(.5, -1.35),
                               loc=10,
                               ncol=len(WVGDF.keys()) / 2)

                    f = plt.subplot(2, 1, 2)
                    c = 0
                    for p in WVGDF.keys():
                        if p[0:4] == 'Dir.':
                            if p[5:13] != 'StormGeo':
                                if not WVGDF[p].dropna().values.any():
                                    print(u'não tem dados medidos')
                                else:
                                    plt.plot(WVGDF[p].dropna().index,
                                             WVGDF[p].dropna(),
                                             linewidth=1,
                                             marker='o',
                                             color='#000080',
                                             alpha=ALPHA[c],
                                             markersize=3)
                                    c += 1
                    for j, J in enumerate(OPT):
                        plt.plot(
                            WVGDF['Dir. StormGeo (' + str(J) + 'h)'].dropna().index,
                            WVGDF['Dir. StormGeo (' + str(J) + 'h)'].dropna(),
                            linewidth=2,
                            color=STGCOLORS[j],
                            marker='o',
                            markersize=3)
                    plt.ylabel(u'Direção ($\circ$)')
                    f.grid(True, linewidth=2)
                    f.xaxis.set_major_locator(mdates.DayLocator(interval=2))
                    f.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))

                    plt.savefig(
                        DIREC + '\\' + CAMUSR.keys()[x] +
                        '_onda.png',
                        format='png')
                    plt.close()

    writer.book.close()
    ans = "FINALIZADO!"
    return ans
