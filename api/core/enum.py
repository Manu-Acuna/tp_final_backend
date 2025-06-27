import enum

class PedidoStatus(enum.Enum):
    PENDIENTE = 1
    PROCESANDO = 2
    ENVIADO = 3
    COMPLETADO = 4
    CANCELADO = 5

class PagoStatus(enum.Enum):
    PENDIENTE = 1
    APROBADO = 2
    RECHAZADO = 3