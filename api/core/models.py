from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship
from api.core.database import Base


class Usuarios(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True) 
    email = Column(String, unique=True, index=True)
    password = Column(String)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

    direccion = relationship("DireccionesEnvio", back_populates="usuario")
    carrito = relationship("Carrito", back_populates="usuario")
    pedido = relationship("Pedidos", back_populates="usuario")


class DireccionesEnvio(Base):
    __tablename__ = "direccionesEnvio"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String)
    city = Column(String)
    zip_code = Column(String)
    user_id = Column(Integer, ForeignKey("usuarios.id"))

    usuario = relationship("Usuarios", back_populates="direccion")
    pedido = relationship("Pedidos", back_populates="direccion")


class Carrito(Base):
    __tablename__ = "carrito"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"))
    time_tamptz = Column(DateTime)

    usuario = relationship("Usuarios", back_populates="carrito")
    carrito_detalle = relationship("CarritoDetalle", back_populates="carrito")


class CarritoDetalle(Base):
    __tablename__ = "carritoDetalle"

    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer)
    price = Column(Float)
    cart_id = Column(Integer, ForeignKey("carrito.id"))
    product_id = Column(Integer, ForeignKey("productos.id"))

    carrito = relationship("Carrito", back_populates="carrito_detalle")
    producto = relationship("Productos", back_populates="carrito_detalle")


class Productos(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    price = Column(Integer)
    stock = Column(Integer)
    image_url = Column(String, nullable=True) # Añadimos la URL de la imagen
    category_id = Column(Integer, ForeignKey("categorias.id"))

    categoria = relationship("Categorias", back_populates="producto")
    carrito_detalle = relationship("CarritoDetalle", back_populates="producto")
    pedido_detalle = relationship("PedidoDetalle", back_populates="producto")


class Categorias(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    producto = relationship("Productos", back_populates="categoria")


class PedidoDetalle(Base):
    __tablename__ = "pedidoDetalle"
    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer)
    price = Column(Float)
    order_id = Column(Integer, ForeignKey("pedidos.id"))
    product_id = Column(Integer, ForeignKey("productos.id"))
    pedido = relationship("Pedidos", back_populates="detalles")
    producto = relationship("Productos", back_populates="pedido_detalle")


class Pedidos(Base):
    __tablename__ = "pedidos"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime)
    total = Column(Float)
    status = Column(Integer)
    user_id = Column(Integer, ForeignKey("usuarios.id"))
    address_id = Column(Integer, ForeignKey("direccionesEnvio.id"))

    usuario = relationship("Usuarios", back_populates="pedido")
    detalles = relationship("PedidoDetalle", back_populates="pedido")
    direccion = relationship("DireccionesEnvio", back_populates="pedido")
    pagos = relationship("Pagos", back_populates="pedido")


class Pagos(Base):
    __tablename__ = "pagos"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime)
    amount = Column(Float)
    status = Column(Integer)
    order_id = Column(Integer, ForeignKey("pedidos.id"))
    payment_method_id = Column(Integer, ForeignKey("metodosPago.id")) # Corregido
    pedido = relationship("Pedidos", back_populates="pagos")
    metodo_pago = relationship("MetodosPago", back_populates="pagos")


class MetodosPago(Base):
    __tablename__ = "metodosPago"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    pagos = relationship("Pagos", back_populates="metodo_pago")