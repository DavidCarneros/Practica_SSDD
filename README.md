# Practica_SSDD 

Curso: 2018/2019

Nombre: David Carneros Prado

Asignatura: Sistemas Distribuidos 

Escuela superior de informatica (Ciudad Real) 


El objetivo principal del proyecto es diseñar un sistema cliente-servidor que permita la extracción de ficheros de audio a partir de la URL de clips de youtube. Este sistema debe ser escalable, permitiendo la creación bajo demanda de nuevos servidores encargados de las tareas de descarga y extracción de los audios. Además, estos servidores deben interconectarse y sincronizarse de forma automática entre sí, proporcionando de esta manera un sistema de alta disponibilidad
La implementación de este proyecto permitirá al alumno trabajar los siguientes aspectos:
* Comunicación asíncrona
* Manejo de canales de eventos
* Despliegue de servidores de forma dinámica
* Gestión de un grid


## Dependencias

* ZeroC-Ice 3.7
* Python3.7
* CMD para python
* Youtube-dl 


## PASOS PARA EJECUTAR:

# Servidor

* 1º Crear los nodos. para ello se ejecutar el script ./startNode1.sh
   Si se quiere tener con 2 nodos ejecutar el script ./startNode2.sh

* 2º Copiar los binarios ejecutando el script ./copy_binaries.sh

* 3º Abrir el icegridgui, cargar el xml:
    ** - un nodo ---> downloader.xml
    ** - dos nodos --> downloader_2nodos.xml

* 4º Llevarlo a registro, distribuir la aplicación y iniciar todos los servidores



# Cliente 

* 1ª ejecutar el cliente:  ./Client.py --Ice.Config=client.config

* 2ª Conectarnos a la factoria (depende de a la factoria que nos queramos conectar)
    ** - connect SchedulerFactory1 -t -e 1.1 @ DownloaderFactory1.SchedulerFactoryAdapter
    ** - connect SchedulerFactory2 -t -e 1.1 @ DownloaderFactory2.SchedulerFactoryAdapter2

* 3º Creamos el scheduler: create_schedule Name

* 4ª Para descargar: add_download url

