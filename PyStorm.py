'''
    Interface gráfica de comparação entre os dados numéricos fornecidos
    pela StormGeo e os dados coletados pelas UCDs de referência


    Autor: Francisco Thiago Franca Parente
    Criado: 27/03/2018

'''

import Tkinter as tk
from datetime import datetime
import os
import matplotlib.pyplot as plt
from collections import OrderedDict
import stganalise
import datetime as dt
from warnings import filterwarnings

# Desativação de alertas minimizando mensagens no console.
filterwarnings("ignore")

# ======================== Caminho das imagens ===============================

IMGPATH = os.path.abspath('private_path')

# ============ Diretório onde estão os dados da StormGeo =====================

SGPATH = os.path.abspath("private_path")

# ============ Parâmetros de plots e leitura dos dados =======================

UND = u"nós"
LISTBOL = [24, 48, 72, 96, 120, 144]
PERBOL = ['Matutino', 'Vespertino']

# Criando interface gráfica
class PREVOBS:
    u""" Interface Gráfica de confronto entre previsão e observação. """

    USERPATH = os.path.expanduser(u"~")

    def __init__(self, root):
        self._root = root  # Janela gráfica de origem da aplicação.
        self._camp = OrderedDict([
            (u"Bacia de Santos", {
                u"Polo Sul": "PoloSul_15522",
                u"Mexilhão": "Mexilhao_15526"}),
            (u"Bacia de Campos", {
                u"Papa Terra": "PapaTerra_15532",
                u"Badejo-Enchova-Marimbá":
                "BCRasaSul_15534",
                u"Espadarte-Caratinga-Marlim Sul":
                "BCProfundaSul_15533"}),
            (u"Bacia do Espírito Santo", {
                u"Golfinho-Camarupim": "GolfinhoCamarupim_15542"}),
            (u"Todas as Bacias", {
                u"Polo Sul": "PoloSul_15522",
                u"Mexilhão": "Mexilhao_15526",
                u"Merluza": "Merluza_15525",
                u"Sapinhoá": "Sapinhoa_15535",
                u"Lula-Sépia": "Lula_15528",
                u"Uruguá-Tambaú": "Urugua_15527"}),
        ])
        self._anl = {u"Somente um boletim": 1, u"Vários boletins": 2}

        # Imagens
        self._imgfile = os.path.join(IMGPATH, "img.jpg")

        # Frame principal
        self._mainfrm = tk.Frame(self._root, bg='white',
                                 bd=0, relief=tk.FLAT)
        self._mainfrm.pack(fill=tk.BOTH, padx=0, pady=0, side=tk.TOP)
        # Barra/menu "Arquivo".
        self._menubar = tk.Menu(self._mainfrm)
        menu = tk.Menu(self._menubar, tearoff=0)
        menu.add_command(label=u"Sair", command=lambda rt=self._root:
                         (rt.destroy(), plt.close('all')))
        self._menubar.add_cascade(label=u"Arquivo", menu=menu)

        # Associação da barra de opções ao frame principal.
        self._mainfrm.master.config(menu=self._menubar)

        # TÍTULO 1
        self.lb = tk.Label(self._mainfrm, text='PREVISÃO VS OCEANOP',
                           bg="#447ea4", fg="white",
                           font=('Verdana', '16', 'bold'))
        self.lb.pack(side=tk.TOP, fill=tk.X)

        # ============================================================ #
        #                     Frame do Tipo de Análise                 #
        # ============================================================ #

        self.anl_fr = tk.Frame(self._mainfrm, bg='white',
                               bd=2, relief=tk.GROOVE)
        self.anl_fr.pack(fill=tk.X, padx=6, pady=4, side=tk.TOP)

        # Variável mutante do Parâmetro Controle
        # self._param_ctrl_var = tki.StringVar()
        self.anl = tk.StringVar()
        # Menu de Parâmetros disponíveis para consulta.
        self._anl_opt = tk.OptionMenu(self.anl_fr,
                                      self.anl,
                                      *self._anl.keys(),
                                      command=self.ask_anl)
        # Texto Data
        tk.Label(self.anl_fr, bd=0,
                 bg='white', fg='black',
                 text=u"Tipo da Análise", font=('Verdana', '8', 'bold'),
                 relief=tk.FLAT, justify=tk.CENTER).pack(padx=2,
                                                         pady=0,
                                                         fill=tk.X)
        self._anl_opt.pack(padx=0, pady=2, fill=tk.X)

        # ============================================================ #
        #                       Frame Data Inicial                     #
        # ============================================================ #

        self.dti_fr = tk.Frame(self._mainfrm, bg='white',
                               bd=2, relief=tk.GROOVE)
        self.dti_fr.pack(fill=tk.X, padx=6, pady=4, side=tk.TOP)

        self.dti = tk.StringVar()
        self.dti.set((datetime.utcnow()).strftime(u"%d/%m/%Y" + u" %H:00:00"))

        # Texto Data
        tk.Label(self.dti_fr, bd=0,
                 bg='white', fg='black',
                 text=u"Data Inicial", font=('Verdana', '8', 'bold'),
                 relief=tk.FLAT, justify=tk.CENTER).pack(padx=2,
                                                         pady=0,
                                                         fill=tk.X)
        # Campo de entrada da data
        self.dtient = tk.Entry(self.dti_fr, bd=3, width=19,
                               textvariable=self.dti, justify=tk.CENTER)
        self.dtient.pack(padx=0, pady=2, fill=tk.X)

        # ============================================================ #
        #                       Frame Data Final                     #
        # ============================================================ #

        self.dtf_fr = tk.Frame(self._mainfrm, bg='white',
                               bd=2, relief=tk.GROOVE)
        self.dtf_fr.pack(fill=tk.X, padx=6, pady=4, side=tk.TOP)

        self.dtf = tk.StringVar()
        self.dtf.set((datetime.utcnow()).strftime(u"%d/%m/%Y" + u" %H:00:00"))

        # Texto Data
        tk.Label(self.dtf_fr, bd=0,
                 bg='white', fg='black',
                 text=u"Data Final", font=('Verdana', '8', 'bold'),
                 relief=tk.FLAT, justify=tk.CENTER).pack(padx=2,
                                                         pady=0,
                                                         fill=tk.X)
        # Campo de entrada da data
        self.dtfent = tk.Entry(self.dtf_fr, bd=3, width=19,
                               textvariable=self.dtf, justify=tk.CENTER)
        self.dtfent.pack(padx=0, pady=2, fill=tk.X)

        # ============================================================ #
        #                       Frame das Bacias                       #
        # ============================================================ #

        self.campo_fr = tk.Frame(self._mainfrm, bg='white',
                                 bd=2, relief=tk.GROOVE)
        self.campo_fr.pack(fill=tk.X, padx=6, pady=4, side=tk.TOP)

        # Variável mutante do Parâmetro Controle
        # self._param_ctrl_var = tki.StringVar()
        self.campo = tk.StringVar()
        # Menu de Parâmetros disponíveis para consulta.
        self._campo_opt = tk.OptionMenu(self.campo_fr,
                                        self.campo,
                                        *self._camp.keys(),
                                        command=self.ask_camp)
        # Texto Data
        tk.Label(self.campo_fr, bd=0,
                 bg='white', fg='black',
                 text=u"Bacias", font=('Verdana', '8', 'bold'),
                 relief=tk.FLAT, justify=tk.CENTER).pack(padx=2,
                                                         pady=0,
                                                         fill=tk.X)
        self._campo_opt.pack(padx=0, pady=2, fill=tk.X)

        # ============================================================ #
        #                       Frame dos Boletim                      #
        # ============================================================ #

        self.bol_fr = tk.Frame(self._mainfrm, bg='white',
                               bd=2, relief=tk.GROOVE)
        self.bol_fr.pack(fill=tk.X, padx=6, pady=4, side=tk.TOP)

        # Texto Data
        tk.Label(self.bol_fr, bd=0,
                 bg='white', fg='black',
                 text=u"Boletim", font=('Verdana', '8', 'bold'),
                 relief=tk.FLAT, justify=tk.CENTER).pack(padx=2,
                                                         pady=0,
                                                         fill=tk.X)

        # Lista de opções
        self.var = tk.StringVar()
        self.bol = tk.Radiobutton(self.bol_fr,
                                  text=PERBOL[0],
                                  value=PERBOL[0],
                                  variable=self.var,
                                  indicatoron=0)
        self.bol.pack(padx=0, pady=0, fill=tk.X)
        self.bol = tk.Radiobutton(self.bol_fr,
                                  text=PERBOL[1],
                                  value=PERBOL[1],
                                  variable=self.var,
                                  indicatoron=0)
        self.bol.pack(padx=0, pady=0, fill=tk.X)

        # ============================================================ #
        #                Frame das opções de boletins                  #
        # ============================================================ #

        self.optbol_fr = tk.Frame(self._mainfrm, bg='white',
                                  bd=2, relief=tk.GROOVE)
        self.optbol_fr.pack(fill=tk.X, padx=6, pady=4, side=tk.TOP)

        # Texto Data
        tk.Label(self.optbol_fr, bd=0,
                 bg='white', fg='black',
                 text=u"Opções de boletins", font=('Verdana', '8', 'bold'),
                 relief=tk.FLAT, justify=tk.CENTER).pack(padx=2,
                                                         pady=0,
                                                         fill=tk.X)
        # Listbox das opçoes de boletins
        self.listb = tk.Listbox(self.optbol_fr,
                                selectmode=tk.MULTIPLE)

        for n, l in enumerate(LISTBOL):
            self.listb.insert(n, l)

        self.listb["state"] = tk.DISABLED
        self.listb.config(height=7)

        self.listb.pack(padx=1, pady=0, fill=tk.X, side=tk.LEFT)

        # Botão para confirmar as escolhas feitas
        self.btlist = tk.Button(self.optbol_fr,
                                bd=2,
                                text="Confirma",
                                command=self.checklist)
        self.btlist.config(height=5)
        self.btlist.pack(padx=1, pady=0, fill=tk.X, side=tk.RIGHT)

        # ============================================================ #
        #                       Frame de Execução                      #
        # ============================================================ #

        self.bottom_fr = tk.Frame(self._mainfrm, bg='white',
                                  bd=2, relief=tk.GROOVE)
        self.bottom_fr.pack(fill=tk.X, padx=6, pady=4, side=tk.TOP)

        # Campo de entrada da data
        self.buttom = tk.Button(self.bottom_fr,
                                bd=2,
                                text="Run",
                                command=self.run,
                                state=tk.DISABLED)
        self.buttom.pack(padx=0, pady=2, fill=tk.X)

        # ============================================================ #
        #                       Frame da Imagem                        #
        # ============================================================ #

        # self._root.img = tk.PhotoImage(file=self._imgfile )

        # self.img_fr = tk.Frame(self._mainfrm, bg='white',
        #                        bd=0, relief=tk.GROOVE)
        # self.img_fr.pack(fill=tk.X, padx=6, pady=4, side=tk.TOP)

        # tk.Label(self.img_fr, bg='white', bd=1,
        #          image=self._imgfile,
        #          relief=tki.RIDGE).pack(padx=0, pady=0, side=tki.TOP)

        # ============================================================ #
        #                       Frame de Mensagem                      #
        # ============================================================ #

        self.mnsg_fr = tk.Frame(self._mainfrm, bg='white',
                                bd=2, relief=tk.GROOVE)
        self.mnsg_fr.pack(fill=tk.X, padx=6, pady=4, side=tk.TOP)

        # Variável mutante da ensagem
        self._mnsgbox = tk.Text(self.mnsg_fr, bd=1, width=25, fg='black',
                                bg='white', wrap=tk.WORD, height=14,
                                font=('Verdana', '8', 'bold'))
        self._mnsgbox.pack(padx=0, pady=2, fill=tk.X)

    def checklist(self):
        self.listselct = list()
        for s in self.listb.curselection():
            self.listselct.append(self.listb.get(s))

        self._mnsgbox.delete('1.0', tk.END)
        self._mnsgbox.insert(tk.END,
                             u"Período escolhido: " +
                             str(self.var.get()) + '\n' +
                             u"Boletins escolhidos: " +
                             str(self.listselct) + '\n')
        self.buttom["state"] = 'normal'

    def ask_anl(self, dbvalue):
        if self._anl[dbvalue] == 1:

            self.listb["state"] = tk.DISABLED
            self.dtient["state"] = "normal"
            self.dtfent["state"] = tk.DISABLED

        else:
            self.listb["state"] = "normal"
            self.dtient["state"] = "normal"
            self.dtfent["state"] = "normal"

        self._root.update()

    def ask_camp(self, dbvalue):

        self.campo = self._camp[dbvalue]
        self.bol["state"] = "normal"
        self._root.update()

    def run(self):

        self.buttom["state"] = tk.DISABLED

        # ============ Diretório onde serão salvas as imagens e tabela ========

        path = os.path.normpath((u'\\\\petrobras\\petrobras\\SUB\\SUB_OPSUB_' +
                                 'GDSO_OCN\\NP-2\\01.SR e Previsao\\01.Consu' +
                                 'ltorias\\02.Rotinas\\Python\\StormGeo\\' +
                                 'Boletins'))

        # Criando diretório com data e hora de execução
        day = dt.datetime.strftime(dt.datetime.now(), '%Y%m%d_%H%M')
        if os.path.isdir(path + '\\' + day) is False:
            os.mkdir(path + '\\' + day)
        DIREC = (path + '\\' + day)  # Diretrório definido

        try:
            if self.listb["state"] == "normal":
                ans = stganalise.stg_med(self.campo,
                                         self.dti.get(),
                                         self.dtf.get(),
                                         self.var.get(),
                                         DIREC,
                                         SGPATH,
                                         UND,
                                         self.listselct)
            else:
                ans = stganalise.stg_boletim(self.campo,
                                             self.dti.get(),
                                             self.var.get(),
                                             DIREC,
                                             SGPATH,
                                             UND)
            self.buttom["state"] = tk.DISABLED
            self._mnsgbox.insert(tk.END, ans)
        except Exception as error:
            self._mnsgbox.insert(tk.END, "*** Erro***\n")
            self._mnsgbox.insert(tk.END, error)
            self._mnsgbox.tag_add('', "3.0", "8.14")
            self._mnsgbox.tag_configure('',
                                        background="red",
                                        foreground="white")
            self.buttom["state"] = tk.DISABLED

        self._root.update()


def main():
    root = tk.Tk()
    root.title(u"PyStorm")
    root.resizable(width=False, height=False)
    PREVOBS(root)
    root.mainloop()


if __name__ == "__main__":
    main()
