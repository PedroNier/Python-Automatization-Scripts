import ssl
from imapclient import IMAPClient


#As variáveis que vão ser usadas para acessar a conta

HOST = 'imap.gmail.com'
USERNAME = 'youremail@gmail.com'
PASSWORD = 'your password'

#A lista de remetentes e nomes para se acrescentar nas pastas.
EMAIL_MAPA = {
    'notification@emails.tiktok.com': 'TikTok',
    'notification@service.tiktok.com': 'TikTok',
    'billing@shopify.com': 'Shopify',
    'mike@tailwindapp.com': 'Pinterest',
    'info@pingenerator.com': 'Pinterest',
    'no-reply@tailwindapp.com': 'Pinterest',
    'email@email.shopify.com': 'Shopify',
    'recommendations@discover.pinterest.com': 'Pinterest',
    'recommendations@explore.pinterest.com': 'Pinterest',
    'danny@tailwindapp.com': 'Pinterest',
    'team@clickbank.com': 'Clickbank'

}

# Conexão com o servidor
def organize_emails():
    #Conexão com provedor de e-mail e à conta
    try:
        context = ssl.create_default_context()
        with IMAPClient(HOST, ssl=True) as client:
            print(f"Conectando a {HOST}...")
            client.login(USERNAME, PASSWORD)
            print("Login bem-sucedido")
            
            #Escolhe a pasta INBOX para filtrar os e-mails
            client.select_folder('INBOX')
            print("Pasta INBOX selecionada.")

            #Separa o nome das pastas
            pastas_lista = client.list_folders()
            pastas_nomes = [info[2] for info in pastas_lista]

            #Pega os valores do dicionario e coloca como nome das pastas
            pastas_a_criar = set(EMAIL_MAPA.values())

            #Interação para a criação das pastas, o código vai verificar se a página já existe, senão, vai ser criado a pasta.
            for pasta_destino in pastas_a_criar:
                if pasta_destino not in pastas_nomes:
                    client.create_folder(pasta_destino)
                    print(f"Pasta {pasta_destino} foi criada com sucesso.")

            print("Começando organização por remetente")

            #Iteração para verificar se os remetentes fazem parte dos e-mails listados e os envia para as respectivas pastas
            for remetente, pasta_destino in EMAIL_MAPA.items():
                print (f"-> Processando remetente: {remetente}...")
                criteria_list = ['FROM', remetente]
                messages = client.search(criteria_list)
                if not messages:
                    print("Nenhum e-mail foi encontrado de {remetente}")
                    continue
            
                print(f"Encontrado {len(messages)} para organizar. Movendo para {pasta_destino}")
            
                client.move(messages, pasta_destino)

            print("Organização de e-mails concluída.")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    organize_emails()