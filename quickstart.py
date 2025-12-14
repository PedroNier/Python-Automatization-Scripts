import os.path
import google.auth

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]


#Verifica todos os arquivos do drive
def list_files(service):
    results = (
        service.files().list(
            q="trashed = false",
            fields="nextPageToken, files(id, name, mimeType)",
            pageSize=1000
    ).execute()
    )

    items = results.get('files',[])

    if not items:
            print("No file found")
            return
    print("Files found: ")
    for item in items:
        print(f"- {item['name']} ID: {item['id']}, Type: {item['mimeType']}")

    return items

#Deixa especificado internamente os tipos de arquivos de acordo com os mimeTypes do Google e define o nome da pasta de acordo com o tipo de arquivo
def get_folder_name_from_mimetype(mime_type):
    """Mapeia o mimeType de um arquivo para um nome de pasta de destino."""
    
    # Dicionário de Mapeamento
    mime_map = {
        # Tipos Google (Docs)
        'application/vnd.google-apps.document': 'Documentos Google',
        'application/vnd.google-apps.spreadsheet': 'Planilhas Google',
        'application/vnd.google-apps.presentation': 'Apresentacoes Google',
        
        # Tipos Comuns de Documentos
        'application/pdf': 'Documentos PDF',
        'application/msword': 'Documentos Word',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Documentos Word',
        'text/plain': 'Arquivos de Texto',
        
        # Tipos de Imagem
        'image/jpeg': 'Imagens',
        'image/png': 'Imagens',
        'image/gif': 'Imagens',
        
        # Tipos de Vídeo e Áudio
        'video/mp4': 'Videos',
        'audio/mpeg': 'Audios',
        
        # Arquivos Compactados
        'application/zip': 'Compactados',
        'application/x-rar-compressed': 'Compactados',
    }
    
    # Retorna o nome da pasta mapeada ou "Outros" se não for encontrado
    for key, folder_name in mime_map.items():
        if key in mime_type:
            return folder_name
            
    # Ignora pastas
    if mime_type == 'application/vnd.google-apps.folder':
        return None 

    # Caso não seja mapeado
    return "Outros"

#Verifica se a pasta do tipo de arquivo já existe, e se já existir vai ignorar, se não, vai criar com os dados específicos.
def check_and_create_folder(service, folder_name):
    query = (
        f"name='{folder_name}' and "
        "mimeType='application/vnd.google-apps.folder' and "
        "'root' in parents and "
        "trashed=false"
    )
    response = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id)'
    ).execute()

    files = response.get('files', [])

    if files:
        return files[0].get('id')
    
    print(f"-> Pasta '{folder_name}' não encontrada. Criando...")
    
    file_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    folder = service.files().create(body=file_metadata, fields="id").execute()

    print(f"Pasta '{folder_name} criada com sucesso com o ID {folder.get('id')}.")
    return folder.get("id")


#Vai processar os arquivos listados na list_file e mover os arquivos para suas respectivas pastas de acordo com o tipo.
def organize_files(service, files_to_organize):
    if not files_to_organize:
        print("Nenhum arquivo para organizar.")
        return
    
    #Para não precisar sempre fazer a recall para o check_and_create_folder, esse dicionario armazena a pasta que foi criada e o código vai sempre conferir nessa variável para economizar memória
    folder_cache = {}

    print("\n--- INICIANDO PROCESSAMENTO E ORGANIZAÇÃO ---")

    for item in files_to_organize:
        file_id = item.get('id')
        file_type = item.get('mimeType')
        file_name = item.get('name')

        folder_name = get_folder_name_from_mimetype(file_type)

        if folder_name is None:
            continue

        if folder_name not in folder_cache:
            folder_id = check_and_create_folder(service, folder_name)
            folder_cache[folder_name] = folder_id
        else:
            folder_id = folder_cache[folder_name]

        print(f"[*] {file_name} -> Pasta: {folder_name}")

        #Usa a função básica de mover arquivos entre pastas, relacionando os arquivos com as pastas listaados no organizer_file
        move_file(service, file_id, folder_id)

    print("\n Organização concluída!")

def move_file(service, file_id, folder_id):
    try:
        # 1. OBTEM A LISTA DE PAIS ATUAIS DO ARQUIVO
        # CORRIGIDO: Certificando-se de que '.execute()' está sendo chamado corretamente.
        file_parents = service.files().get(
            fileId=file_id, 
            fields='parents'
        ).execute() 

        # 2. FORMATA ESSES PAIS EM UMA STRING SEPARADA POR VÍRGULAS
        # Isso garante que REMOVEREMOS TODAS as pastas em que o arquivo está.
        previous_parents = ",".join(file_parents.get('parents', []))
        
        # 3. EXECUTA A ATUALIZAÇÃO
        # Remove TODAS as pastas antigas (previous_parents) e adiciona a nova (folder_id).
        service.files().update(
            fileId=file_id, 
            addParents=folder_id,
            removeParents=previous_parents,
            fields='id, parents' 
        ).execute()
        
        print(f"-> Movido com sucesso o arquivo {file_id}")

    except HttpError as error:
        # Imprime o erro 403 completo para diagnóstico
        print(f"ERRO HttpError ao mover o arquivo {file_id}: {error}")
    except Exception as e:
        # Captura outros erros de execução
        print(f"ERRO desconhecido ao mover o arquivo {file_id}: {e}")

def main():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        #If there are no valid credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        #Saving the credentials for next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    try:
        service = build("drive", "v3", credentials=creds)

        #Chama a lista de arquivos para uma variável e depois chama a função organize_files para processar essa lista
        files_to_organize = list_files(service)
        organize_files(service, files_to_organize)
        
    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()
