#   Candidato:  Fábio do Nascimento Patão
#
#   Olá, este é meu código para o desafio de desenvolvimento.
#   Estou fazendo uma API em python puro, sem uso de framework
#

from http.server import BaseHTTPRequestHandler, HTTPServer         
from urllib.parse import unquote
import json
from datetime import datetime
import requests

#       FUNÇÕES DOS MÓDULOS IMPORTADOS
#   
#    BaseHTTPRequestHandler: é uma classe que lida com requisições GET, POST e etc.
#    HTTPServer: é uma classe que cria o servidor
#   
#    unquote: permite ç e outros caracteres especiais na url
#
#    json: Módulo que trabalha com json
#    datetime: para lidar com as datas do /age
#
#    requests: para puxar os dados da API do IBGE





class minhaAPI(BaseHTTPRequestHandler):

    def do_POST(self):
        if self.path == '/age':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            content_length = int(self.headers['Content-Length'])
            dados = self.rfile.read(content_length)
            dados_decoded = dados.decode('utf-8') #transformando os dados em utf-8
            
            try:
                dados_json = json.loads(dados_decoded)

                if 'name' in dados_json and 'birthdate' in dados_json and 'date' in dados_json: #Verifica se tem todos os campos

                    birthdate = datetime.strptime(dados_json['birthdate'], '%Y-%m-%d').date()
                    date = datetime.strptime(dados_json['date'], "%Y-%m-%d").date()
                    hoje = datetime.now().date()  # Obtém apenas a data atual sem hora e minuto

                    # Calcula a idade hoje
                    idade_hoje = hoje.year - birthdate.year - ((hoje.month, hoje.day) < (birthdate.month, birthdate.day))

                    # Calcula a idade na data fornecida
                    idade = date.year - birthdate.year - ((date.month, date.day) < (birthdate.month, birthdate.day))

                    if date<hoje:
                        self.send_error(400,'date deve ser uma data futura')
                        return

                    response = {
                        "quote": f"Olá, {dados_json['name']}! Você tem {idade_hoje} anos e em {date.day}/{date.month}/{date.year} você terá {idade}",
                        "ageNow": f"{idade_hoje}",
                        "ageThen": f"{idade}"
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                else:
                    self.send_error(400, 'Formato inválido de body')
                    return
            except ValueError:
                # Se não for possível carregar os dados em JSON, retorna um erro 400 Bad Request
                self.send_error(400, 'Bad Request', 'Invalid JSON format')
                return



    #minha API está herdando de BaseHTTPRequestHandler,  e ela possui seus métodos GET e POST
    #Eu vou sobrecrevê-los
    def do_GET(self):
        if self.path.startswith('/municipio-bairros/'):
            # CONFIGURANDO O HEADER
            self.send_response(200)                                 # Código de status 200 = OK
            self.send_header('Content-type', 'application/json')    # O tipo do conteúdo do get é um json!
            self.end_headers()                                      # Terminamos o header
            
            nome_municipio = unquote(self.path.split('/')[-1]) # Nome do município em nossa URL
            nome_formatado = nome_municipio.replace('-', ' ').lower()
            print("Request OK")
            print("Nome do município:", nome_formatado) 
            

            municipio_request = requests.get('https://servicodados.ibge.gov.br/api/v1/localidades/municipios')
            if municipio_request.status_code == 200:
                dados_municipios = municipio_request.json()

                for municipio in dados_municipios:
                    if municipio['nome'].lower() == nome_formatado:
                        municipio_id = municipio['id']
                        print(f'Municipio id: {municipio_id}')
                        break
                else:
                    self.send_error(404, 'Município não encontrado')
                    return
            else:
                self.send_error(404, 'Falha de conexão API')
                return
            
            subdistrito_request = requests.get(f'https://servicodados.ibge.gov.br/api/v1/localidades/municipios/{municipio_id}/subdistritos')
            if subdistrito_request.status_code == 200:
                dados_subdistrito = subdistrito_request.json()
                self.wfile.write(json.dumps(dados_subdistrito).encode('utf-8'))
            
            else:
                self.send_error(404, 'ID não encontrado')
                return

        else:
            self.send_error(404, 'Não encontrado')
            return
        
    

        

def run(server_class=HTTPServer, handler_class=minhaAPI, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Servidor iniciado na porta {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()




# Atenção especial https://servicodados.ibge.gov.br/api/v1/localidades/subdistritos
# DUQUE DE CAXIAS - BELFORD ROXO