# %%
from rendafixa.ativos import (
    CDBPreFixado,
    CDB_CDI,
    CDB_IPCA,
    LCI_LCAPreFixado,
    LCI_LCA_CDI,
    LCI_LCA_IPCA,
    TesouroPreFixado,
    Tesouro_Selic,
    Tesouro_IPCA,
    Poupanca,
    FIRF,
    FIA,
    FI_incentivada
)

valor = 1000
prazo = 720
# print(f'Valor: {valor}, Prazo: {prazo}')
# print('-------------------------------------')

ipca = 4.42
selic = 11.25
di = selic - 0.1
tr = 0.5

# Conta real para X% CDI:
# (((di + 1) **(1/252) - 1) * (X/100) + 1)**252 - 1
cdb_pre = CDBPreFixado(valor, prazo, taxa_fixa=14, unidade="dia", nome=r"CDB C6 (14%a.a)")
print(cdb_pre)
cdb_pos = CDB_CDI(
    valor, prazo, 125, selic=selic, di=di, unidade="dia", nome=r"CDB Master (125%CDI)"
)
print(cdb_pos)
cdb_hib = CDB_IPCA(
    valor, prazo, taxa=7.5, ipca=ipca, unidade="dia", nome=r"CDB BMG (IPCA+7.5)"
)
print(cdb_hib)
lci_pre = LCI_LCAPreFixado(valor, prazo, 11.8, nome=r"Inter LCA PRE 720dias (Pre 11.8%)")
print(lci_pre)
lci_pos = LCI_LCA_CDI(
    valor, prazo, taxa=92, selic=selic, di=di, unidade="dia", nome=r"LCA ABC (92%CDI)"
)
print(lci_pos)
lci_hib = LCI_LCA_IPCA(
    valor, prazo, taxa=5.5, ipca=ipca, unidade="dia", nome=r"LCA BTG (ipca+5.5)"
)
print(lci_hib)
tes_pre = TesouroPreFixado(valor, prazo, 12.97, nome=r"Tesouro Prefixado (2031) 12.97%")
print(tes_pre)
tes_pos = Tesouro_Selic(valor, prazo, 0.12, selic, nome=r"Tesouro Selic(2029) + 0.12%")
print(tes_pos)
tes_hib = Tesouro_IPCA(valor, prazo, 6.86, ipca, nome=r"Tesouro IPCA+ (2029) 6.86%")
print(tes_hib)
poup = Poupanca(valor, prazo, selic, tr)
print(poup)
# %%
fi1 = FIRF(valor, prazo, 13.51, 0.5, nome=r"BB Asset RF CP LP FIC FI")
fi2 = FIRF(valor, prazo, 12.34, 0.5, nome=r"Inter Conservador FIRF CP")
fi3 = FI_incentivada(valor, prazo, 13.72, 1.58, nome=r"Inter Selection Debentures Incentivadas FIC FIRF CP")
fi4 = FIA(valor, prazo, 19.36, 1, nome=r"Inter Dividendos FIA")
print(fi1)
print(fi2)
print(fi3)
print(fi4)
# %%
