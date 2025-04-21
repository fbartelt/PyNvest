import numpy as np
from abc import ABC, abstractmethod
from rendafixa.utils import rendimentos, irpf, iof, tempo2dia, round_taxa, cdi2taxa, rendimento_real

# definicao das constantes (selic, ipca, di, tr)
SELIC = 14.25
IPCA = 5.48
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
    
    @abstractmethod
    def rendimento_bruto(self):
        pass

    @abstractmethod
    def impostos(self):
        pass

    @property
    def valor(self):
        """Retorna o valor atual do investimento."""
        return self._valor

    @valor.setter
    def valor(self, novo_valor):
        """Define um novo valor para o investimento, garantindo que ele seja positivo."""
        if novo_valor <= 0:
            raise ValueError("O valor do investimento deve ser positivo.")
        self._valor = novo_valor

    def _string_taxa(self):
        if isinstance(self.taxa, (tuple, list)):
            return f"{self.taxa[0]*100:.2f} + {self.taxa[1]*100:.2f}"
        else:
            return f"{self.taxa*100:.2f}"

    def _header(self):
        taxa = self._string_taxa()
        msg = "-"*70 + "\n"
        msg += f"{self.nome} - Taxa: {taxa}% (Valor: {self._valor}, Prazo: {self.prazo} dias)"
        return msg
    
    def _footer(self):
        bruto = self.rendimento_bruto()
        liquido = self.rendimento_liquido()
        imposto = self.impostos()
        total = self.rendimento_liquido() + self._valor
        msg = f"Rendimento Bruto: {bruto:.2f}, Imposto: {imposto:.2f}\n"
        msg += f"Rendimento Liquido: {liquido:.2f}    Total: {total:.2f}"
        rendimento_real_ = rendimento_real(total, IPCA, self.prazo, unidade='dia')
        msg += f"\nRendimento Real: {rendimento_real_:.2f} (adotando inflação de {IPCA}%a.a.)"
        return msg

    def __str__(self) -> str:
        header = self._header()
        footer = self._footer()
        msg = f"{header}\n{footer}"
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
    def custodia(self, valor=None):
        if valor is None:
            valor = self._valor
        return rendimentos(valor, 0.002, self.prazo)
    
    def impostos(self):
        return super().impostos() + self.custodia()
    
    def _footer(self):
        bruto = self.rendimento_bruto()
        liquido = self.rendimento_liquido()
        custodia = self.custodia()
        imposto = self.impostos() - custodia
        total = self.rendimento_liquido() + self._valor
        msg = f"Rendimento Bruto: {bruto:.2f}, Imposto + Custodia: {imposto:.2f} + {custodia:.2f}\n"
        msg += f"Rendimento Liquido: {liquido:.2f}    Total: {total:.2f}"
        rendimento_real_ = rendimento_real(total, IPCA, self.prazo, unidade='dia')
        msg += f"\nRendimento Real: {rendimento_real_:.2f} (adotando inflação de {IPCA}%a.a.)"
        return msg
    
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

    def _footer(self):
        bruto = self.rendimento_bruto()
        liquido = self.rendimento_liquido()
        adm_ = self.adm()
        imposto = self.impostos() - adm_
        total = self.rendimento_liquido() + self._valor
        msg = f"Rendimento Bruto: {bruto:.2f}, Imposto + Administração: {imposto:.2f} + {adm_:.2f}\n"
        msg += f"Rendimento Liquido: {liquido:.2f}    Total: {total:.2f}"
        rendimento_real_ = rendimento_real(total, IPCA, self.prazo, unidade='dia')
        msg += f"\nRendimento Real: {rendimento_real_:.2f} (adotando inflação de {IPCA}%a.a.)"
        return msg

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
    """Investimento em CDB com rentabilidade pré-fixada.

    Esta classe modela um Certificado de Depósito Bancário (CDB) com uma taxa de 
    rentabilidade anual fixa, herdando da classe `CDB` genérica.

    Parameters
    ----------
    valor : float
        O valor do investimento no CDB.
    prazo : int
        O prazo do investimento, na unidade especificada.
    rentabilidade : float
        A taxa de rentabilidade anual do CDB em percentual (ex.: 8.5 para 8,5% ao ano).
    unidade : str, optional
        Unidade de tempo para o prazo, como "dia", "mes" ou "ano". O valor padrão é "dia".
    nome : str, optional
        O nome do investimento. O valor padrão é "CDB Pré-Fixado".

    Attributes
    ----------
    taxa : float
        Taxa de rentabilidade anual do CDB no formato decimal, calculada com base 
        na rentabilidade percentual fornecida.

    Examples
    --------
    Criar uma instância de CDB pré-fixado e acessar a taxa de rentabilidade:

    >>> cdb = CDBPreFixado(valor=1000, prazo=365, rentabilidade=8.5, unidade="dia")
    """
    def __init__(self, valor, prazo, rentabilidade, unidade="dia", nome="CDB Pré-Fixado"):
        super().__init__(valor, tempo2dia(prazo, unidade), nome)
        self.taxa = round_taxa(rentabilidade/100)


class CDB_CDI(CDB):
    """Investimento em CDB com rentabilidade atrelada ao CDI.

    Esta classe modela um Certificado de Depósito Bancário (CDB) com uma taxa de
    rentabilidade atrelada ao CDI, herdando da classe `CDB` genérica.

    Parameters
    ----------
    valor : float
        O valor do investimento no CDB.
    prazo : int
        O prazo do investimento, na unidade especificada.
    rentabilidade : float
        A taxa de rentabilidade do CDB em percentual do CDI (ex.: 125 para 125% do CDI).
    selic : float, optional
        A taxa SELIC em percentual, utilizada para calcular o CDI. O valor padrão é `SELIC`.
    di : float, optional
        A taxa DI em percentual, utilizada para calcular o CDI. O valor padrão é SELIC-0.1%.
    unidade : str, optional
        Unidade de tempo para o prazo, como "dia", "mes" ou "ano". O valor padrão é "dia".
    nome : str, optional
        O nome do investimento. O valor padrão é "CDB CDI".
    
    Attributes
    ----------
    taxa : float
        Taxa de rentabilidade anual do CDB no formato decimal, calculada com base 
        na rentabilidade percentual fornecida.
    
    Examples
    --------
    Criar uma instância de CDB atrelado ao CDI e acessar a taxa de rentabilidade:

    >>> cdb = CDB_CDI(valor=1000, prazo=365, rentabilidade=125, selic=10.5, di=10.4, unidade="dia")
    """
    def __init__(self, valor, prazo, rentabilidade, selic=None, di=None, unidade="dia", nome="CDB CDI"):
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
        self.taxa = round_taxa(cdi2taxa(rentabilidade, self.di))


class CDB_IPCA(CDB):
    def __init__(
        self, valor, prazo, rentabilidade, ipca=None, unidade="dia", nome="CDB IPCA+"
    ):
        if ipca is None:
            print(f"IPCA não informado, utilizando valor padrão de {IPCA}%")
            self.ipca = IPCA
        else:
            self.ipca = ipca
        super().__init__(valor, tempo2dia(prazo, unidade), nome)
        self.taxa = round_taxa((self.ipca/100, rentabilidade/100))


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
