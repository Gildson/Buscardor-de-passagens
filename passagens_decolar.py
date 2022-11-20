"""
Raspagem de passagens aereas do site decolar
para mudar a consulta altere o "NAT" pela sigla do aeroporto que deseja sair
e altere "OPO" pela sigla do aeroporto de destino.
NAT = Natal, Rio Grande do Norte
JPA = João Pessoa, Paraíba
REC = Recife, Pernanbuco
FOR = Fortaleza, Ceará
MCZ = Alagoas, Maceió
AJU = Aracaju, Sergipe
SSA = Salvador, Bahia
GUZ = Guarapari, Espírito Santo
VIX = Vitória, Espírito Santo
RIO = Rio de Janeiro, Rio de Janeiro
BZC = Búzios, Rio de Janeiro
SAO = São Paulo, São Paulo
SJK = São José dos Campos, São Paulo
SJP = São José do Rio Preto, São Paulo

""" 
#Lista dos aeroportos brasileiros
aeroportos_brasileiros = {'NAT':'Natal',
                        'JPA':'João Pessoa',
                        'REC':'Recife',
                        'FOR':'Fortaleza',
                        'MCZ':'Maceio',
                        'AJU':'Aracaju',
                        'SSA':'Salvador',
                        'GUZ':'Guarulhos',
                        'VIX':'Vitória',
                        'RIO':'Rio de Janeiro',
                        'BZC':'Buzíos',
                        'SAO':'São Paulo',
                        'SJK':'São josé dos Campos',
                        'SJP':'São josé do Rio Preto'}

#Lista dos aeroportos portugueses
aeroportos_portugal = {'OPO':'Porto',
                    'BGZ':'Braga',
                    'CBP':'Coimbra'}

from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import mysql.connector #Banco de dados
from mysql.connector import errorcode #erros do mysql

browser = webdriver.Chrome()

#conectar ao banco de dados
con = mysql.connector.connect(host='endereço', database='nome do banco', user='usuario', password='senha')
cursor = con.cursor()

while aeroportos_portugal != 0:
    lista_destino = list(aeroportos_portugal.keys())
    destino = aeroportos_portugal[lista_destino[0]]
    lista_origem = list(aeroportos_brasileiros.keys())
    for e in range(0, len(aeroportos_brasileiros)):
        origem = aeroportos_brasileiros[lista_origem[e]]
        browser.get('https://www.decolar.com/passagens-aereas/'+lista_origem[e]+'/'+lista_destino[0]+'?from=SB&di=2-2:9-3&reSearch=true')
        time.sleep(2)
        conteudo = browser.page_source
        html_soup = BeautifulSoup(conteudo, 'html.parser')
        none = html_soup.find('p', {'class':'eva-3-p empty-state-message-description'})
        try:
            browser.find_element(By.XPATH, "//p[@class='eva-3-p empty-state-message-description']")
            if none:
                print("Não encontrou passagens")
        except:
            #Rola a tela até o final
            last_height = browser.execute_script("return document.body.scrollHeight")
            for i in range(3):
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                time.sleep(5)

                new_height = browser.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            time.sleep(2)
            conteudo = browser.page_source
            html_soup = BeautifulSoup(conteudo, 'html.parser')

            cluster = html_soup.find('div', {'id':'clusters'})
            voos = cluster.find_all('div', {'class':'reduced-cluster'})
            for i in range(0, len(voos)):
                hora = []
                ida = voos[i].find('div', {'class':'cluster-part-0'})
                data_ida = ida.find('div', {'class':'date -eva-3-bold route-info-item-date lowercase'}).get_text()
                hora_ida = ida.find_all('span', {'class':'stops-text text -eva-3-tc-gray-2'})
                hora.append(hora_ida[0].get_text().replace('\xa0',''))
                hora.append(hora_ida[2].get_text().strip())
                hora = "/".join(str(x) for x in hora)
                valor = voos[i].find('span', {'class':'pricebox-big-text price'}).get_text()
                try:
                    sql = "insert into passagens values('{}','{}','{}','{}','{}', curtime())".format(
                        data_ida,
                        hora,
                        valor,
                        origem,
                        destino,
                    )     
                    cursor.execute(sql)
                    con.commit()
                except mysql.connector.Error as err:
                    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                        print("Something is wrong with your user name or password")
                        pass
                    elif err.errno == errorcode.ER_BAD_DB_ERROR:
                        print("Database does not exist")
                        pass
                    else:
                        print(err)
                        pass

    aeroportos_portugal.pop(0)