==================
CSV Pago de ventas
==================

Este módulo añade un asistente que permite leer pagos de un fichero en formato
csv, busca las ventas de las que provienen finalizando su flujo de trabajo y
los añade al extracto correspondiente.

Configuración
=============

Para configurar la importación de extractos a partir de ventas hay que:
  * Crear un diario de tipo "Extracto" a través del menú Contabilidad >
    Configuración > Diarios > Diarios.
  * Crear un diario de extracto cuyo diario sea el del apartado anterior a
    través del menú Contabilidad > Configuración > Extratos > Diarios de
    extracto.
  * Crear un perfil de importación de ficheros CSV a través del menú
    Administración > Importación CSV > Perfiles CSV de pago de ventas,
    asignando el diario de extracto bancario anterior al mismo.

Funcionamiento
==============

Para importar extractos de ventas en estado confirmado hay que:
  * Crear un extracto y dejarlo en estado borrador a través del menú
    Contabilidad > Extractos > Todos los Extractos.
  * Ejecutar el asistente que se encuentra en el menú Ventas > Importar
    extractos desde archivo CSV.

Una vez realizada la importación de un archivo CSV abrir el extracto y
comprovar que se han importado correctamente todas las líneas del fichero
abriendo los registros relacionados.
