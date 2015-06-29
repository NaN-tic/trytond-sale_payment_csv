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
  * Ejecutar el asistente que se encuentra en el menú Contabilidad > Extractos > Importar
    extractos de ventas desde CSV.

Una vez realizada la importación de un archivo CSV abrir el extracto y
comprovar que se han importado correctamente todas las líneas del fichero
abriendo los registros relacionados.

Uso
===

Para importar los extractos de los pagos realizados a través de
Redsys, Paypal... hay que crear unos perfiles que asignan los campos de los
ficheros csv a los campos de las tablas de la base de datos de Tryton.  Yo
ya he configurado estos perfiles de importación así que de eso ya no tienes
que preocuparte a menos que fallen.

Una vez hecho esto, hay que crear los diarios de extracto. Para ello hay
que abrir el menú Contabilidad > Configuración > Extractos > Diarios de
extracto, y crear un diario extractos y desajuste de extractos para Paypal
y para Redsys (esto también os lo he hecho yo).

A continuación se tendrían que crear los extractos para la importación,
aunque si no lo haces, creo recordar que el programa lo hace
automáticamente. Para ello se tiene que abrir el menú Contabilidad >
Extractos > Todos los extractos, y crear los diarios de extractos y de
desajuste de extractos para Paypay, Redsys...

Seguidamente hay que importar los archivos csv con los extractos. Para ello
hay que abrir el menú Contabilidad > Extractos > Importar extractos de
ventas desde CSV, y en el asistente que se abre, introducir el perfil
correspondiente a la plataforma (Paypal o Redsys) y el fichero que quieres
importar (que debe concordar con la plataforma correspondiente).

Una vez realizada la importación queda por comprobar el resultado de la
misma. Para ello hay que abrir el menú Contabilidad > Extractos > Registros
de importación CSV. Vienen ordenados por fecha de más nuevo a más antiguo,
por lo tanto, el último en haberse realizado aparecerá arriba del todo. Hay
que abrirlo haciendo doble clic sobre él con el botón izquierdo del ratón
para que se abra la vista de tipo formulario. Aquí puede verse el resultado
de la importación de cada línea del fichero csv: las líneas verdes indican
que la importación se ha realizado correctamente y las rojas que ha habido
algún problema. En el comentario puede verse dicho problema de forma que
ayude a tomar una decisión para corregirlo.

Cuando todo esté correctamente importado únicamente queda validar el
extracto correspondiente. Para ello hay que abrir nuevamente el menú
Contabilidad > Extractos > Todos los extractos, abrir el extracto que se
desea validad y, tras comprobar que todo está correctamente, hacer clic
sobre el botón "Validar". Una vez validado sólo queda "Confirmar" el
extracto para que quede conciliado contablemente.
