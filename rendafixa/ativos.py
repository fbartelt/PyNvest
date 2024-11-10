import numpy as np
from abc import ABC, abstractmethod
from rendafixa.utils import rendimentos, irpf, iof, tempo2dia, round_taxa, cdi2taxa

#definicao das contantes (selic, ipca, di, tr)
SELIC = 10.5
IPCA = 3.926
DI = (SELIC - 0.1)/100
TR = 0.5 # taxa referencial (poupanca)


class Investimento(ABC):
    def __init__(self, valor, prazo, nome="Investimento"):
        self._valor = valor
        self.prazo = prazo
        self.nome = nome

    @abstractmethod
    def rendimento_liquido(self):
        pass

    def __str__(self) -> str:
        if isinstance(self.taxa, (tuple, list)):
            taxa = f"{self.taxa[0]*100:.2f} + {self.taxa[1]*100:.2f}"
        else:
            taxa = f"{self.taxa*100:.2f}"
        msg = "---------------------------------------------------------------\n"
        msg += f"{self.nome} - Taxa: {taxa}% (Valor: {self._valor}, "
        msg += f"Prazo: {self.prazo} dias)\n   "
        msg += f"Rendimento Bruto: {self.rendimento_bruto():.2f},  "
        msg += f"Imposto: {self.impostos():.2f},  "
        msg += f"Total: {self.rendimento_liquido() + self._valor:.2f}"
        return msg

    def __repr__(self) -> str:
        return self.__str__()


class CDB(Investimento):
    def impostos(self):
        bruto = self.rendimento_bruto()
        return irpf(bruto, self.prazo) + iof(bruto, self.prazo)

    def rendimento_bruto(self):
        return rendimentos(self._valor, self.taxa, self.prazo)

    def rendimento_liquido(self):
        return self.rendimento_bruto() - self.impostos()


class LCI_LCA(CDB):
    def impostos(self):
        return 0


class TesouroDireto(CDB):
    #TODO adicionar taxa custodia 0.2%a.a. para todos que nao sao tesouro selic
    def custodia(self, valor=None):
        if valor is None:
            valor = self._valor
        return rendimentos(valor, 0.002, self.prazo)
    
    def impostos(self):
        return super().impostos() + self.custodia()
    
    def __str__(self) -> str:
        old = super().__str__()
        return old + f"\nTaxa Custódia: {self.custodia():.2f}"
    
class FundoInvestimento(CDB):
    def __init__(self, valor, prazo, taxa, taxa_adm, nome="Fundo de Investimento"):
        super().__init__(valor, prazo, nome)
        self.taxa = round_taxa(taxa)
        self.taxa_adm = taxa_adm
    
    def adm(self):
        bruto = self.rendimento_bruto()
        total = bruto + self._valor
        return total * self.taxa_adm
    
    def impostos(self):
        return super().impostos() + self.adm()

    def __str__(self) -> str:
        old = super().__str__()
        return old + f"\nTaxa de Administração: {self.taxa_adm*100:.2f}%"

class Poupanca(Investimento):
    def __init__(self, valor, prazo, selic=SELIC, tr=TR, nome="Poupança"):
        super().__init__(valor, prazo, nome)
        self.selic = selic
        self.tr = tr
        self.taxa = round_taxa(self.get_taxa())

    def get_taxa(self):
        if self.selic <= 8.5:
            return (self.selic * 70 / 100, self.tr / 100)
        else:
            taxa_ = ((1 + 0.5 / 100) ** 12) - 1  # 0.5%a.m. p/ %a.a.
            return (taxa_, self.tr / 100)

    def rendimento_bruto(self):
        return rendimentos(self._valor, self.taxa, self.prazo)

    def rendimento_liquido(self):
        return self.rendimento_bruto()

    def impostos(self):
        return 0

class CDBPreFixado(CDB):
    def __init__(self, valor, prazo, taxa_fixa, unidade="dia", nome="CDB Pré-Fixado"):
        super().__init__(valor, tempo2dia(prazo, unidade), nome)
        self.taxa = round_taxa(taxa_fixa/100)


class CDB_CDI(CDB):
    def __init__(self, valor, prazo, taxa, selic=None, di=None, unidade="dia", nome="CDB CDI"):
        """ taxa = X% CDI """
        if selic is None:
            print(f"Selic não informada, utilizando valor padrão de {SELIC}%")
            self.selic = SELIC
        else:
            self.selic = selic
        if di is None:
            print(f"Taxa DI não informada, utilizando padrão de SELIC-0.1 = {self.selic - 0.1}%")
            self.di = (self.selic - 0.1)
        else:
            self.di = di
        super().__init__(valor, tempo2dia(prazo, unidade), nome)
        self.taxa = round_taxa(cdi2taxa(taxa, self.di))


class CDB_IPCA(CDB):
    def __init__(
        self, valor, prazo, taxa, ipca=None, unidade="dia", nome="CDB IPCA+"
    ):
        if ipca is None:
            print(f"IPCA não informado, utilizando valor padrão de {IPCA}%")
            self.ipca = IPCA
        else:
            self.ipca = ipca
        super().__init__(valor, tempo2dia(prazo, unidade), nome)
        self.taxa = round_taxa((self.ipca/100, taxa/100))


class LCI_LCAPreFixado(LCI_LCA):
    def __init__(
        self, valor, prazo, taxa_fixa, unidade="dia", nome="LCI/LCA Pré-Fixado"
    ):
        super().__init__(valor, tempo2dia(prazo, unidade), nome)
        self.taxa = round_taxa(taxa_fixa/100)


class LCI_LCA_CDI(LCI_LCA):
    def __init__(self, valor, prazo, taxa, selic=None, di=None, unidade="dia", nome="LCI/LCA CDI"):
        if selic is None:
            print(f"Selic não informada, utilizando valor padrão de {SELIC}%")
            self.selic = SELIC
        else:
            self.selic = selic
        if di is None:
            print(f"Taxa DI não informada, utilizando padrão de SELIC-0.1 = {selic - 0.1}%")
            self.di = (selic - 0.1)
        else:
            self.di = di
        super().__init__(valor, tempo2dia(prazo, unidade), nome)
        self.taxa = round_taxa(cdi2taxa(taxa, self.di))


class LCI_LCA_IPCA(LCI_LCA):
    def __init__(
        self,
        valor,
        prazo,
        taxa, 
        ipca=None,
        unidade="dia",
        nome="LCI/LCA IPCA+",
    ):
        if ipca is None:
            print(f"IPCA não informado, utilizando valor padrão de {IPCA}%")
            self.ipca = IPCA
        else:
            self.ipca = ipca
        super().__init__(valor, tempo2dia(prazo, unidade), nome)
        self.taxa = round_taxa((self.ipca/100, taxa/100))


class TesouroPreFixado(TesouroDireto):
    def __init__(
        self, valor, prazo, taxa_fixa, unidade="dia", nome="Tesouro Pré-Fixado"
    ):
        super().__init__(valor, tempo2dia(prazo, unidade), nome)
        self.taxa = round_taxa(taxa_fixa/100)

class Tesouro_IPCA(TesouroDireto):
    def __init__(
        self,
        valor,
        prazo,
        taxa, 
        ipca=None,
        unidade="dia",
        nome="Tesouro IPCA+",
    ):
        if ipca is None:
            print(f"IPCA não informado, utilizando valor padrão de {IPCA}%")
            self.ipca = IPCA
        else:
            self.ipca = ipca
        super().__init__(valor, tempo2dia(prazo, unidade), nome)
        self.taxa = round_taxa((self.ipca/100, taxa/100))

class Tesouro_Selic(TesouroDireto):
    def __init__(
        self,
        valor,
        prazo,
        taxa, 
        selic=None,
        unidade="dia",
        nome="Tesouro Selic+",
    ):
        if selic is None:
            print(f"Selic não informada, utilizando valor padrão de {SELIC}%")
            self.selic = SELIC
        else:
            self.selic = selic
        super().__init__(valor, tempo2dia(prazo, unidade), nome)
        self.taxa = round_taxa((self.selic/100, taxa/100))

    def custodia(self):
        if self._valor <= 10000:
            return 0
        else: 
            return super().custodia(self._valor - 10000)

class FIRF(FundoInvestimento):
    def __init__(self, valor, prazo, taxa, taxa_adm, unidade="dia", nome="FIRF"):
        super().__init__(valor, tempo2dia(prazo, unidade), taxa/100, taxa_adm/100, nome)

class FIA(FundoInvestimento):
    def __init__(self, valor, prazo, taxa, taxa_adm, unidade="dia", nome="FIA"):
        super().__init__(valor, tempo2dia(prazo, unidade), taxa/100, taxa_adm/100, nome)

class FI_incentivada(FundoInvestimento):
    def __init__(self, valor, prazo, taxa, taxa_adm, unidade="dia", nome="FI Incentivada"):
        super().__init__(valor, tempo2dia(prazo, unidade), taxa/100, taxa_adm/100, nome)
    def impostos(self):
        return super().impostos() - irpf(self.rendimento_bruto(), self.prazo)