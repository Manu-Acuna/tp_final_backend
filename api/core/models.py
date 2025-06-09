from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from api.core.database import Base


class Roles(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    # __table_args__ = (Constraint("nombre IN ('vendedor', 'repositor')", name="valid_roles"))

    usuarios = relationship("Usuarios", back_populates="roles")


class Usuarios(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    registry_date = Column(DateTime)
    rol_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"))
    rol = relationship("Roles", back_populates="usuarios")


class Productos(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    price = Column(Integer)
    stock = Column(Integer)
    category_id = Column(Integer, ForeignKey("categorias.id"))

    category = relationship("Categorias")


class Categorias(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)


class Comprobantes(Base):
    __tablename__ = "comprobantes"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String)
    fecha = Column(DateTime)
    number = Column(Integer)
    description = Column(String)

class Movimientos(Base):
    __tablename__ = "movimientos"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime)
    quantity = Column(Integer)
    product_id = Column(Integer, ForeignKey("productos.id"))
    user_id = Column(Integer, ForeignKey("usuarios.id"))
    comprobante_id = Column(Integer, ForeignKey("comprobantes.id"))

    product = relationship("Productos")
    user = relationship("Usuarios")
    comprobante = relationship("Comprobantes")

