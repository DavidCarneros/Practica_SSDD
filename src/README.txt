###############################################################################
##############   David Carneros Prado   05722152M   ###########################
##############   Sistemas distribuidos  3B          ###########################
###############################################################################


PASOS PARA EJECUTAR:

########################### Servidor ######################################

1º Crear los nodos. para ello se ejecutar el script ./startNode1.sh
   Si se quiere tener con 2 nodos ejecutar el script ./startNode2.sh

2º Copiar los binarios ejecutando el script ./copy_binaries.sh

3º Abrir el icegridgui, cargar el xml:
    - un nodo ---> downloader.xml
    - dos nodos --> downloader_2nodos.xml

4º Llevarlo a registro, distribuir la aplicación y iniciar todos los servidores



############################ Cliente ######################################

1ª ejecutar el cliente:  ./Client.py --Ice.Config=client.config

2ª Conectarnos a la factoria (depende de a la factoria que nos queramos conectar)
    - connect SchedulerFactory1 -t -e 1.1 @ DownloaderFactory1.SchedulerFactoryAdapter
    - connect SchedulerFactory2 -t -e 1.1 @ DownloaderFactory2.SchedulerFactoryAdapter2

3º Creamos el scheduler: create_schedule Name

4ª Para descargar: add_download url
