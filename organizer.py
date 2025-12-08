import os
import shutil
from pathlib import Path

home_dir = str(Path.home())


#Define o caminho da pasta que quero organizar
downloads_folder_path = os.path.join(home_dir,"Downloads")

print("Organizando em: ", downloads_folder_path)

#Loop que vai separar os arquivos por extensão e separar em uma pasta própria;

for file in os.listdir(downloads_folder_path):

    #Caso o arquivo esteja na própria pasta que vai organizar, apenas vai ignorar.
    file_path = os.path.join(downloads_folder_path, file)
    if os.path.isdir(file_path):
        continue

    #Separa o arquivo pelo nome e a exxtensão dele
    filename, file_extension = os.path.splitext(file)
    file_extension = file_extension[1:].lower()

    #Caso seja algum tipo de arquivo que não tenham extensão vão ser colocados na pasta "No Extension", se tiverem, vão ser colocados na pasta respectiva de cada extensão.
    if not file_extension:
        folder_name = "No Extension"
    else:
        folder_name = file_extension

    #Define o caminho novo para cada pasta nova criada.
    folder_to_organizer = os.path.join(downloads_folder_path, folder_name)

    #Se a pasta não foi criada ainda, esse trecho vai criar uma nova pasta.
    if not os.path.isdir(folder_to_organizer):
        os.mkdir(folder_to_organizer)

    #Define as variáveis que vão receber o caminho de origem e o caminho de destino para um dos arquivos
    source_path =os.path.join(downloads_folder_path, file)
    destination_path = os.path.join(folder_to_organizer, file)

    #Move os arquivos para a pasta de destino de acordo com as variáveis acima.
    shutil.move(source_path, destination_path)
    print(f"Movido: {file} -> {folder_name}/")

print("\nOrganização concluída!")