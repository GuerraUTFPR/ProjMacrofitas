#coding: utf-8
from flask import request, render_template
from web import app
from web.forms.searchForm import SearchForm
from scrapping.floraDoBrasil import getOneEntry
from scrapping.floraDoBrasil import getData as getDataFloraDoBrasil
from scrapping.plantList import getAllEntries as getDataSpeciesLink
from scrapping.plantList import getOneEntry as getOneEntryPlantList
from location.gbif import getLocation
from web.forms.importForm import ImportForm
from preprocessing.core import main as preProcess

# Route para buscar informações de uma única planta
@app.route('/busca', methods=['GET', 'POST'])
def busca():
    form = SearchForm(request.form)

    if (request.method == 'POST' and form.validate()):
        planta = request.form['plant']

        nome_flora, status_flora, nome_aceito_flora = getOneEntry(searchTerm=planta, outputPath='', notFoundPath='')
        nome_plantList, status_plantList, nome_aceito_plantList = getOneEntryPlantList(planta)

        nome_aceito_flora = nome_flora if nome_aceito_flora == '' else nome_aceito_flora
        nome_aceito_plantList = nome_plantList if nome_aceito_plantList == '' else nome_aceito_plantList

        status_flora, status_plantList = parseStatus(status_flora), parseStatus(status_plantList)

        dataComparation = [nome_flora, status_flora.decode('utf-8'), nome_aceito_flora, status_plantList.decode('utf-8'), nome_plantList, 'Diferente' if status_flora != status_plantList else '']
        locations_gbif = getLocation(planta, '', False)

        return render_template(os.path.join('data','searchResult.html'), plant_searched=planta,form=form, dataComparation=dataComparation, dataLocation=locations_gbif)
    return render_template(os.path.join('search','searchPlant.html'), form=form)

# Route para buscar informações de todas as plantas de um arquivo
@app.route('/inserirDados', methods=['GET','POST'])
def importar():
    form = ImportForm(request.form)
    if (request.method == 'POST' and form.validate()):
        filename = request.files['arquivo'].filename

        extensao = filename.split('.')[1]
        request.files['arquivo'].save(os.path.join('data','ListaMacrofitas.{}').format(extensao))
        preProcess()
        # Implementar threads para melhorar performance
        getDataFloraDoBrasil(allDataset=True)
        getDataSpeciesLink()
        # Script do flora do Brasil pra tabela 2 aqui
        # Scripts de localizacao aqui
        # Script de sumarizacao aqui

        return render_template('index.html')

    return render_template(os.path.join('import','importFile.html'), form=form)

def parseStatus(status):
    if status == 'NOME_ACEITO':
        status = 'Aceito'
    elif status == 'SINONIMO':
        status = 'Sinônimo'
    else:
        status = 'Não Encontrado'

    return status


if __name__ == "__main__":
    app.run(debug=True)