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

- Se requiere la configuración de dos tipos de cuentas especiales para Cobros
  y Pagos Anticipados; y la configuración de los diarios de Cobros y Pagos
  Anticipados.

- Cuentas dedicadas cobros y pagos anticipados.  Cada Partner puede tener
  configurada su cuenta de Cobros Anticipados y Pagos anticipados.

- Cambios en la facturación.

  En las facturas de clientes se puede rebajar saldo de los cobros
  anticipados. En las facturas de proveedor se puede rebajar saldo de los
  pagos anticipados.

  Al igual que pasa cuando hay "débitos pendientes", el sistema saca una
  notificación y muestra la cuenta de cobro o pago anticipado asociada a la
  venta o compra.

  La interfaz de usuario se modifica:

  1) Para el caso de las facturas de clientes se muestra una lista con los
     montos de cada una de las cuentas de Cobros Anticipados donde hay un
     saldo para el cliente.

  2) Para el caso de las facturas de proveedor se muestra una lista con los
     montos de cada una de las cuentas de Pagos Anticipados donde hay un saldo
     para el proveedor.


..
   Local Variables:
   ispell-dictionary: "es"
   End:
