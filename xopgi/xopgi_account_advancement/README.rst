=======================================
 Gestión de cobros y pagos anticipados
=======================================

El Odoo gestiona dos tipos de cuentas de Payable y Receivables relacionadas
con los Partners.  Cuando se crea una factura de cliente se utiliza la cuenta
Receivable configurada para el cliente.  Cuando se crea una factura de
proveedor se utiliza la cuenta Payable.

Estas cuentas se utilizan para cobros y pagos a crédito.  Sin embargo, muchas
operaciones tienen pagos o cobros anticipados; y varias empresas utilizan
cuentas dedicadas para la gestión de cobros y pagos anticipados.

El Odoo no facilita este tipo de gestión.

Funciones de este addon
=======================

- Cuentas dedicadas cobros y pagos anticipados.  Cada Partner puede tener
  configurada su cuenta de Cobros Anticipados y Pagos anticipados.

  La compañía tiene las Cuentas de Cobros y Pagos anticipados por defecto para
  los nuevos partners.

  En la información contable el total a cobrar y a pagar se diferencian entre
  los Payables, Receivable y los anticipos.


- Cambios en la facturación.

  En las facturas de clientes se puede rebajar saldo de los cobros
  anticipados.  En las facturas de proveedor se puede rebajar saldo de los
  pagos anticipados.

  Al igual que pasa cuando hay "débitos pendientes", el sistema saca una
  notificación.

  La interfaz de usuario se modifica de dos formas:

  1) Se añade un botón de 'Rebajar'.  Al apretarlo sale una ventana con
     información similar a la que se utiliza para registrar pagos.  En el
     saldo a rebajar se propone el máximo monto posible.

  2) Se añade al final de la lista de débitos pendientes, un enlace de
     'Rebajar' ``$tanto`` del anticipo de ``$cuanto``.

     Apretar aquí tiene el mismo efecto que poner el máximo posible en el
     diálogo de rebajar.

..
   Local Variables:
   ispell-dictionary: "es"
   End:
