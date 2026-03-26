import psycopg2

DATABASE_URI = "postgresql://restaurantechiclayo_2uyn_user:3nJW2BwDIm7uZ9bCSS8cHSzgkPX0GAQa@dpg-d726rgp9fqoc73a6883g-a.oregon-postgres.render.com/restaurantechiclayo_2uyn"

# PostgreSQL schema based on the SQLite version
# AUTOINCREMENT -> SERIAL
# CURRENT_TIMESTAMP is compatible
SCHEMA_SQL = """
-- DROP TABLES IF THEY EXIST (FOR FRESH START)
DROP TABLE IF EXISTS detalle_pedido;
DROP TABLE IF EXISTS pedido;
DROP TABLE IF EXISTS mesa;
DROP TABLE IF EXISTS producto;
DROP TABLE IF EXISTS categoria;

-- CREAMOS LAS TABLAS 
CREATE TABLE categoria (
    id_categoria SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL
);

CREATE TABLE producto (
    id_producto SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    id_categoria INTEGER,
    FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria)
);

CREATE TABLE mesa (
    id_mesa SERIAL PRIMARY KEY,
    numero INTEGER NOT NULL,
    estado TEXT DEFAULT 'libre'
);

CREATE TABLE pedido (
    id_pedido SERIAL PRIMARY KEY,
    id_mesa INTEGER,
    estado TEXT DEFAULT 'pendiente',
    fecha TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_mesa) REFERENCES mesa(id_mesa)
);

CREATE TABLE detalle_pedido (
    id_detalle_pedido SERIAL PRIMARY KEY,
    id_pedido INTEGER,
    id_producto INTEGER,
    cantidad INTEGER NOT NULL,
    FOREIGN KEY (id_pedido) REFERENCES pedido(id_pedido),
    FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
);

-- INSERTAMOS CANTIDAD DE MESAS DISPONIBLES
INSERT INTO mesa (numero) VALUES
(1), (2), (3), (4), (5), (6), (7), (8), (9), (10), (11), (12);

-- CATEGORIAS DE LA CARTA
INSERT INTO categoria (nombre) VALUES
('Combos'), ('Salchidragón'), ('Duplic Chino'), ('Combos Especiales'), ('Sopas'), 
('Wantanes'), ('Festival de Alitas'), ('Chaufas'), ('Tallarines'), ('Aves + Chaufa'), 
('Tortillas + Chaufa'), ('Enrollado + Chaufa'), ('Aeropuertos'), ('Combinados'), ('Platos Especiales');

-- INSERTAMOS PRODUCTOS POR CATEGORIA (IDs assumed sequential starting at 1)
-- CATEGORIA 1: Combos
INSERT INTO producto (nombre, id_categoria) VALUES
('Alitas Broaster + Papas + Chaufa + Ensalada', 1),
('Mollejitas fritas + Papas + Chaufa + Ensalada', 1),
('1/8 Pollo a la Caja China + Papas + Chaufa + Ensalada', 1),
('Sopa Wantan + Chaufa', 1),
('Alitas Kaypi + Papas + Chaufa + Ensalada', 1),
('Alitas BBQ + Wantanes + Chaufa', 1),
('1/8 Pollo a la brasa + Papas + Chaufa + Ensalada', 1);

-- CATEGORIA 2: Salchidragón
INSERT INTO producto (nombre, id_categoria) VALUES
('Salchidragón', 2);

-- CATEGORIA 3: Duplic Chino
INSERT INTO producto (nombre, id_categoria) VALUES
('Duplic Chino', 3);

-- CATEGORIA 4: Combos Especiales
INSERT INTO producto (nombre, id_categoria) VALUES
('Chijaukay + Alitas Kaypi', 4),
('Pollo con Durazno + Alitas BBQ', 4),
('Costillas BBQ + Pollo con Verdura', 4),
('Alitas Broaster + Mollejitas Fritas', 4);

-- CATEGORIA 5: Sopas
INSERT INTO producto (nombre, id_categoria) VALUES
('Sopa Wantan de Pollo', 5),
('Sopa Wantan Especial', 5),
('Sopa Fuchifu', 5),
('Sopa Ramen', 5);

-- CATEGORIA 6: Wantanes
INSERT INTO producto (nombre, id_categoria) VALUES
('Wantan relleno (docena)', 6),
('Siu Mai (docena)', 6),
('Gyoza especial (media docena)', 6),
('Wantanes sin relleno (media docena)', 6);

-- CATEGORIA 7: Festival de Alitas
INSERT INTO producto (nombre, id_categoria) VALUES
('Festival de Alitas Fin de Semana', 7);

-- CATEGORIA 8: Chaufas
INSERT INTO producto (nombre, id_categoria) VALUES
('Chaufa Vegetariano', 8),
('Chaufa de Pollo', 8),
('Chaufa de Carne', 8),
('Chaufa de Chancho', 8),
('Chaufa de Langostinos', 8),
('Chaufa Especial', 8),
('Chaufa Cinco Sabores', 8),
('Chaufa Dragón', 8),
('Chaufa Pollo + Chancho', 8),
('Chaufa Pollo + Carne', 8);

-- CATEGORIA 9: Tallarines
INSERT INTO producto (nombre, id_categoria) VALUES
('Tallarín Saltado de Pollo', 9),
('Tallarín Saltado de Carne', 9),
('Tallarín Saltado de Chancho', 9),
('Tallarín Saltado de Langostinos', 9),
('Tallarín Saltado Especial', 9);

-- CATEGORIA 10: Aves + Chaufa
INSERT INTO producto (nombre, id_categoria) VALUES
('Pollo Limonkay', 10),
('Pollo Chijaukay', 10),
('Pollo Teriyaki', 10),
('Pollo Tipakay', 10),
('Pollo con Verduras', 10),
('Pollo con Almendra', 10),
('Pollo con Durazno o Piña', 10);

-- CATEGORIA 11: Tortillas + Chaufa
INSERT INTO producto (nombre, id_categoria) VALUES
('Tortilla de Pollo', 11),
('Tortilla de Verdura', 11),
('Tortilla Especial', 11),
('Tortilla Dragón', 11);

-- CATEGORIA 12: Enrollment + Chaufa
INSERT INTO producto (nombre, id_categoria) VALUES
('Enrollado Especial', 12),
('Enrollado de Pollo con Salsa de Ostión', 12),
('Enrollado de Carne con Salsa Tausi', 12);

-- CATEGORIA 13: Aeropuertos
INSERT INTO producto (nombre, id_categoria) VALUES
('Aeropuerto de Pollo', 13),
('Aeropuerto de Carne', 13),
('Aeropuerto de Chancho', 13),
('Aeropuerto de Langostinos', 13),
('Aeropuerto Especial', 13),
('Aeropuerto Dragón', 13),
('Aeropuerto Cinco Sabores', 13),
('Aeropuerto Pollo + Chancho', 13),
('Aeropuerto Pollo + Carne', 13);

-- CATEGORIA 14: Combinados
INSERT INTO producto (nombre, id_categoria) VALUES
('Combinado de Pollo', 14),
('Combinado de Carne', 14),
('Combinado de Chancho', 14),
('Combinado de Langostinos', 14),
('Combinado Especial', 14),
('Combinado Dragón', 14);

-- CATEGORIA 15: Platos Especiales
INSERT INTO producto (nombre, id_categoria) VALUES
('Kan Lu Wantan', 15),
('Ronda Especial', 15),
('Ronda Dragón', 15),
('Lomo Saltado', 15),
('Saltado de Pollo', 15),
('Sahofan con Lomo', 15),
('Saltado Taypa', 15),
('Lomo a lo Pobre', 15),
('Costilla BBQ', 15),
('Costilla a la Caja China', 15),
('Pollo a la Caja China', 15),
('Kaypi con salsa de limón', 15),
('Chancho con salsa de Tamarindo', 15);
"""

def init_db():
    try:
        conn = psycopg2.connect(DATABASE_URI)
        cur = conn.cursor()
        print("Connected to PostgreSQL successfully.")
        
        cur.execute(SCHEMA_SQL)
        conn.commit()
        print("Schema and initial data inserted successfully.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn:
            cur.close()
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    init_db()
