'''

    Biblioteca de funções úteis para os códigos elaborados
    para a PVMO

    Autores: Francisco Thiago Franca Parente (BHYK)

'''

from collections import OrderedDict
import numpy as np
import datetime as dt
from pandas import DataFrame, Panel, rolling_mean, date_range, read_csv
from pandas import ExcelWriter, Series, to_datetime
import xlrd
import csv
from os.path import isdir
from os import makedirs
from os.path import join
from os import walk as osw
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
from itertools import islice
from matplotlib.dates import DateFormatter, YearLocator, MonthLocator
from matplotlib.dates import DayLocator, HourLocator, MinuteLocator


def check_dir(path):                                            # BHYK
    '''
        Esta função verifica se o diretório existe e, caso ele não exista,
        cria o diretório com a nomeclatura inserida pelo usuário (path)

        path - Diretório que será verificado ou criado

    '''
    if isdir(path) is False:
        makedirs(path)
        new_path = path
    else:
        new_path = path
    return new_path


def import_curr(UCDS, DATEMIN, DATEMAX, INSTR, UNID, BANCO="PROD"): # BHYK/AL4N
    '''
        Esta função importa os dados de corrente

        UCDS - Lista de UCDs que serão verificadas
        DATEMIN - Data inicial do período de interesse
        DATEMAX = Data final do período de interesse
        INSTR - Instrumento de corrente do qual serão extraídos os dados
        UNID - Unidade de medida que será considerada (m/s ou nós)
        BANCO - QUAL BANCO SERÁ UTILIZADO "PROD" OU "DESV"
    '''

    BANCO = BANCO.upper()
    access = PROD_DBACCESS
    if BANCO == "DESV":
        access = DESV_DBACCESS

    UNID = UNID.lower()
    if UNID == u"nós":
        coef = 1.94384449
    elif UNID == u"m/s":
        coef = 1
    else:
        print(u"ERRO - PARÂMETRO 'UNID' ERRADO (nós ou m/s)")
    curr = OrderedDict()
    # lista de UCDs de acordo banco de dados
    UCDLIST = [] # private
    dc = []
    for ucdid in UCDLIST:
        name = pyocnp.ucdname_byid_ocndb(ucdid, str_dbaccess=access)[0]
        if INSTR == 'ADCP':
            try:
                data = FUNCAO_PRIVADA(
                    ucdid,
                    [0, 0],
                    [DATEMIN, DATEMAX],
                    ['HCSP', 'HCDT'],
                    str_dbaccess=access
                )
                print 'CURR: IMPORT ADCP ' + name
                d = {
                    u'Intensidade (' + UNID + ')': data['data0'] * coef,
                    u'Direção': data['data1']}
                dc = DataFrame(
                    data=d,
                    index=data['t']
                )
                dc = dc.reindex(
                    index=date_range(
                        dt.datetime.strptime(DATEMIN, '%d/%m/%Y %H:%M:%S'),
                        dt.datetime.strptime(DATEMAX, '%d/%m/%Y %H:%M:%S'),
                        freq='H'
                    ),
                    fill_value=np.nan)
                curr[name] = dc
            except:
                print(u"ERRO - " + name + u" NÃO TEM DADOS DE ADCP!")

        elif INSTR == 'HADCP':
            try:
                data = FUNCAO_PRIVADA(
                    ucdid,
                    [0, 0],
                    [DATEMIN, DATEMAX],
                    ['HCSP', 'HCDT'],
                    str_dbaccess=access
                )
                print 'CURR: IMPORT HADCP ' + name
                d = {
                    u'Intensidade (' + UNID + ')': data['data0'] * coef,
                    u'Direção': data['data1']
                }
                dc = DataFrame(
                    data=d,
                    index=data['t']
                )
                dc = dc.reindex(
                    index=date_range(
                        dt.datetime.strptime(DATEMIN, '%d/%m/%Y %H:%M:%S'),
                        dt.datetime.strptime(DATEMAX, '%d/%m/%Y %H:%M:%S'),
                        freq='H'
                    ),
                    fill_value=np.nan)
                curr[name] = dc
            except:
                print(u"ERRO - " + name + u" NÃO TEM DADOS DE HADCP!")

        elif INSTR == 'ACQUADOPP':
            try:
                data = FUNCAO_PRIVADA(
                    ucdid,
                    [DATEMIN, DATEMAX],
                    ['HCSP', 'HCDT'], 71,
                    str_dbaccess=access
                )
                print 'CURR: IMPORT ACQUADOPP ' + name
                d = {
                    u'Intensidade (' + UNID + ')': data['data0'] * coef,
                    u'Direção': data['data1']
                }
                dc = DataFrame(
                    data=d,
                    index=data['t'])
                dc = dc.reindex(
                    index=date_range(
                        dt.datetime.strptime(DATEMIN, '%d/%m/%Y %H:%M:%S'),
                        dt.datetime.strptime(DATEMAX, '%d/%m/%Y %H:%M:%S'),
                        freq='H'
                    ),
                    fill_value=np.nan)
                curr[name] = dc

            except:
                print(u"ERRO - " + name + u" NÃO TEM DADOS DE ACQUADOPP!")

    curr = Panel.fromDict(curr)
    return curr


def calc_pa(MODELdata, OBSdata):                                # AL4N
    '''

        Calcula a porcentagem de acerto da previsão segundo método descrito no
        contrato

    '''

    MAPE = np.nanmean(np.absolute(np.divide(MODELdata - OBSdata, OBSdata)))
    PA = 100 * (1 - MAPE)
    return PA


def load_ucd_referencia(FILENAME):                              # AL4N
    '''

        Recupera, a partir do CSV de controle disponível em 'PATH',
        as unidades de referência para a
        avaliação das previsões de vento e onda

    '''

    PATH = 'DIRETORIO_PRIVADO'

    header = 0

    workbook = xlrd.open_workbook(join(PATH, FILENAME))

    CSVname = []
    WNDref = []
    WAVref = []

    for sheet, _ in enumerate(range(workbook.nsheets)):
        for i, _ in enumerate(range(workbook.sheet_by_index(sheet).nrows)):
            if i <= header:
                continue

            CSVname.append(workbook.sheet_by_index(sheet).cell_value(i, 1))

            tmp = workbook.sheet_by_index(sheet).cell_value(i, 2)
            WNDref.append(tmp.split(','))

            tmp = workbook.sheet_by_index(sheet).cell_value(i, 3)
            WAVref.append(tmp.split(','))

    UCDPRIOR = DataFrame(data={'WNDref': WNDref, 'WAVref': WAVref},
                         index=CSVname)

    return UCDPRIOR


def search_csv_stg(PATH, DATA, PER):                            # BHYK
    '''

        Procura os .CSV fornecidos pela stormgeo da data de interesse (DATA)

        PATH - Diretório onde está localizado o .csv
        DATA - Data de interesse
        *** IMPORTANTE *** - A DATA deverá estar no formato dd/mm/yyyy
        PER - indica qual dos dois boletins será avaliado
        (Matutino ou Vespertino)

    '''

    CSVLIST = {}
    c = 0
    for _, _, filenames in osw(PATH):
        for filename in filenames:
            if PER == 'Matutino':
                if filename.endswith(str(DATA[6:10] +
                                         DATA[3:5] +
                                         DATA[0:2]) + '10.csv'):
                    CSVLIST[c] = filename
                    c += 1
            elif PER == 'Vespertino':
                if filename.endswith(str(DATA[6:10] +
                                         DATA[3:5] +
                                         DATA[0:2]) + '19.csv'):
                    CSVLIST[c] = filename
                    c += 1
            else:
                print('ARQUIVO .CSV NÃO ENCONTRADO')
    return CSVLIST


def read_csv_stg(CSV):                                          # BHYK
    '''

        Função que lê o arquivo .CSV seguindo a formatação da planilha
        fornecida pela previsão

        CSVLIST - .csv que será lido

    '''

    CSVFILE = open(CSV, 'rb')
    PREVINF = csv.reader(CSVFILE, delimiter=',')
    HEADERS = PREVINF.next()

    CSVDAT = {}
    for i in HEADERS:
        CSVDAT[i] = []

    for row in PREVINF:
        for i, ii in zip(HEADERS, row):
            CSVDAT[i].append(ii)

    TIME = CSVDAT['\xef\xbb\xbftimestep']
    TEMPO = [dt.datetime.strptime(x, '%Y-%m-%d %H:%M') for x in TIME]
    DATEMIN = TEMPO[0].strftime('%d/%m/%Y %H:%M:%S')
    DATEMAX = TEMPO[-1].strftime('%d/%m/%Y %H:%M:%S')

    WSPD = [float(x) for _, x in enumerate(CSVDAT['windspeed'])]
    WDIR = [float(x) for _, x in enumerate(CSVDAT['winddirection'])]
    WGST = [float(x) for _, x in enumerate(CSVDAT['windspd_10m_gust'])]   #B581
    
    WVHS = [float(x) for _, x in enumerate(CSVDAT['Altura da onda'])]
    WVDIR = [float(x) for _, x in enumerate(CSVDAT['wavedirection'])]
    WVPER = [float(x) for _, x in enumerate(CSVDAT['Período de pico de onda'])]  #B581

    # =============== CRIANDO DATAFRAME COM OS DADOS ============= #

    # VENTO
    WDF = DataFrame(data={'Int. StormGeo': WSPD,
                          'Dir. StormGeo': WDIR,
                          'Gus. StormGeo': WGST},  #B581
                    index=TEMPO)
    WDF = WDF.reindex(index=date_range(
        dt.datetime.strptime(DATEMIN,
                             '%d/%m/%Y %H:%M:%S'),
        dt.datetime.strptime(DATEMAX,
                             '%d/%m/%Y %H:%M:%S'),
        freq='H'),
        fill_value=np.nan)

    # ONDA
    WVF = DataFrame(data={'Hs StormGeo': WVHS,
                          'Dir. StormGeo': WVDIR,
                          'Per. StormGeo': WVPER},  #B581
                    index=TEMPO)
    WVF = WVF.reindex(index=date_range(
        dt.datetime.strptime(DATEMIN,
                             '%d/%m/%Y %H:%M:%S'),
        dt.datetime.strptime(DATEMAX,
                             '%d/%m/%Y %H:%M:%S'),
        freq='H'),
        fill_value=np.nan)

    return WDF, WVF, DATEMIN, DATEMAX


def read_fsi2d_DADAS(PATH, ARQ):                                 # BHYK

    FSICOLMS = {13: [u"Heading", u"VX", u"VY", u"TX", u"TY", u"HX", u"HY",
                     u"HZ", u"VN", u"VE", u"Temperature", u"SV", u"Pressure"],
                14: [u"Heading", u"VX", u"VY", u"VZ", u"TX", u"TY", u"HX",
                     u"HY", u"HZ", u"VN", u"VE", u"Temperature", u"SV",
                     u"Pressure"],
                18: [u"CTDConductivity", u"CTDTemp", u"CTDDepth",
                     u"CTDSalinity", u"CTDSV", u"Heading", u"VX", u"VY", u"TX",
                     u"TY", u"HX", u"HY", u"HZ", u"VN", u"VE", u"Temperature",
                     u"SV", u"Pressure"],
                19: [u"CTDConductivity", u"CTDTemp", u"CTDDepth",
                     u"CTDSalinity", u"CTDSV", u"Heading", u"VX", u"VY", u"VZ",
                     u"TX", u"TY", u"HX", u"HY", u"HZ", u"VN", u"VE",
                     u"Temperature", u"SV", u"Pressure"]}

    df = DataFrame()
    for FILE in ARQ:
        data = read_csv(join(PATH, FILE),
                        error_bad_lines=False,
                        header=None,
                        prefix='Column')
        data.columns = FSICOLMS[len(data.columns)]

        # Retirando linhas erradas
        data.drop(data.index[data.SV != 150000], inplace=True)
        data.drop(
            data.index[
                data[data.columns[0]].str.split('-',
                                                expand=True)[0] == '100.000'],
            inplace=True)

        # Convertendo as datas em datetimes
        data.index = to_datetime(
            data[data.columns[0]].str.split('-', expand=True)[0].values,
            format="%Y%m%d %H%M%S")
        data[data.columns[0]] = data[
            data.columns[0]].str.split(':', expand=True)[1]
        df = df.append(data.copy())

    return df


def read_fsi2d_log_SISMO(PATH, ARQ, SEP, DTI=None, DTF=None, DELTA=None):  # BHYK
    '''
        PATH - Diretório onde estão os CSV que serão lidos
        ARQ - Lista de arquicos .csv que serão lidos
        SEP - ";"" OU ",", depende do arquivo
        DTI - Data e horário que o arquivo foi criado
        DTF - Data e horário que o arquivo foi finalizado
        DELTA - Intervalo entre medições sucessivas ("S" para freq de 1 seg,
                "2S para frequencia de 2 seg")
    '''

    FSICOLMS = {13: [u"Heading", u"VX", u"VY", u"TX", u"TY", u"HX", u"HY",
                     u"HZ", u"VN", u"VE", u"Temperature", u"SV", u"Pressure"],
                14: [u"Heading", u"VX", u"VY", u"VZ", u"TX", u"TY", u"HX",
                     u"HY", u"HZ", u"VN", u"VE", u"Temperature", u"SV",
                     u"Pressure"],
                18: [u"CTDConductivity", u"CTDTemp", u"CTDDepth",
                     u"CTDSalinity", u"CTDSV", u"Heading", u"VX", u"VY", u"TX",
                     u"TY", u"HX", u"HY", u"HZ", u"VN", u"VE", u"Temperature",
                     u"SV", u"Pressure"],
                19: [u"CTDConductivity", u"CTDTemp", u"CTDDepth",
                     u"CTDSalinity", u"CTDSV", u"Heading", u"VX", u"VY", u"VZ",
                     u"TX", u"TY", u"HX", u"HY", u"HZ", u"VN", u"VE",
                     u"Temperature", u"SV", u"Pressure"],
                20: [u"hh:mm:ss", u"mm-dd-yyyy", u"CTDConductivity",
                     u"CTDTemp", u"CTDDepth", u"CTDSalinity", u"CTDSV",
                     u"Heading", u"VX", u"VY", u"TX", u"TY", u"HX", u"HY",
                     u"HZ", u"VN", u"VE", u"Temperature", u"SV", u"Pressure"],
                21: [u"hh:mm:ss", u"mm-dd-yyyy", u"CTDConductivity",
                     u"CTDTemp", u"CTDDepth", u"CTDSalinity", u"CTDSV",
                     u"Heading", u"VX", u"VY", u"VZ", u"TX", u"TY", u"HX",
                     u"HY", u"HZ", u"VN", u"VE", u"Temperature",
                     u"SV", u"Pressure"]}

    df = DataFrame()
    for n, FILE in enumerate(ARQ):
        data = read_csv(join(PATH, FILE),
                        error_bad_lines=False,
                        header=None,
                        prefix='Column',
                        sep=SEP)
        data.columns = FSICOLMS[len(data.columns)]

        # Retirando linhas erradas
        data.drop(data.index[data.SV <= 100000], inplace=True)

        # Convertendo as datas em datetimes
        try:
            data.index = to_datetime(data[u"mm-dd-yyyy"].values +
                                     " " + data[u"hh:mm:ss"].values,
                                     format="%m/%d/%Y %H:%M:%S")
        except:
            dti = dt.datetime.strptime(DTI[n], "%d/%m/%Y %H:%M:%S")
            dtf = dt.datetime.strptime(DTF[n], "%d/%m/%Y %H:%M:%S")
            data.index = date_range(dti, dtf, freq=DELTA)
        df = df.append(data.copy())

    return df


def movingaverage(series, window_size):
    window = np.ones(int(window_size)) / float(window_size)
    return Series(np.convolve(series, window, 'same'), index=series.index)


def repeatnan(a):
    '''
        Função que informa a quantidade de NaNs consecutivos.
    '''

    mask = np.concatenate(([False], np.isnan(a), [False]))
    if ~mask.any():
        return 0
    else:
        idx = np.nonzero(mask[1:] != mask[:-1])[0]
        return (idx[1::2] - idx[::2]).max()


def repeat_condition(a, lim, cond=None):

    '''
        Função que informa a quantidade de vezes consecutivas que uma condição
        se repete em uma série
        a = série
        lim = limite avaliado
        cond = maior para condição maior que o limite e "menor" para condição
        menor que o limite.
    '''
    if cond == None:
        cond = "maior"
    if cond == "maior":
        mask = np.concatenate(([False], a > lim, [False]))
    else:
        mask = np.concatenate(([False], a < lim, [False]))
    if ~mask.any():
        return 0
    else:
        idx = np.nonzero(mask[1:] != mask[:-1])[0]
        return (idx[1::2] - idx[::2])


def window(serie, duracao):
    it = iter(serie)
    result = tuple(islice(it, duracao))
    if len(result) == duracao:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result


def find_nearest(array, value):
    '''
        Acha, em um array, o valor mais próximo ao determinado.
    '''
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]
