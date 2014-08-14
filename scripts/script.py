# -*- coding: utf-8 -*- 
# Script para importar os arquivos de candidatos 2014.

import csvkit, json

def generateCand():
	lista = {}
	ufs = ["AC", "AL", "AM", "AP",  "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO","BR"]

	for uf in ufs:
		print 'Getting '+uf
		cand = open("../raw/consulta_cand_2014_"+uf+".txt", 'r')
		cand = csvkit.reader(cand, encoding='iso-8859-1', delimiter=';')
		for c in cand:
			#if c[15] == 'DEFERIDO': #muitas candidaturas ainda nao foram deferidas
			if c[9] not in ['DEPUTADO ESTADUAL']:
				lista[c[10]] = 0
			if c[9] in ['GOVERNADOR', 'PRESIDENTE']: #adiciona tambem o nome de urna nesses casos
				lista[c[13]] = c[10]
			
			

	with open('names.js', 'w') as final:
		header ="var nick = "
		final.write(header+json.dumps(lista))


def mongo_save(itens, clear=False):
    from pymongo import MongoClient
    client = MongoClient()
    db = client.verdinha
    col = db.doacoes
    if (clear):
        col.drop()
    for i in itens:
        col.update({'_id' : i}, itens[i], upsert=True)

def generateDoacoes():
	doacoes_raw = open("../raw/ReceitasCandidatos.txt", 'r')
	doacoes_raw = csvkit.DictReader(doacoes_raw, encoding='iso-8859-1', delimiter=';')

	r = {}
	for d in doacoes_raw:
		_id = d['CPF do candidato']
		if not r.has_key(_id):
			r[_id] = {
				'_id' : _id,
				'nome' : d['Nome candidato'],
				'numero' : d[u'Número candidato'],
				'partido' : d['Sigla Partido'],
				'uf' : d['UF'],
				'doacoes' : {}
			}
		if not r[_id]['doacoes'].has_key(d['CPF/CNPJ do doador']):	
			r[_id]['doacoes'][d['CPF/CNPJ do doador']] = {
				'nome' : d['Nome do doador'],
				'valor' : float(d['Valor receita'].replace(',','.'))
			}
		else:
			r[_id]['doacoes'][d['CPF/CNPJ do doador']]['valor'] += float(d['Valor receita'].replace(',','.'))

	mongo_save(r)
generateDoacoes()