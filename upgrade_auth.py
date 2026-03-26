import psycopg2
from werkzeug.security import generate_password_hash

DATABASE_URI = "postgresql://restaurantechiclayo_2uyn_user:3nJW2BwDIm7uZ9bCSS8cHSzgkPX0GAQa@dpg-d726rgp9fqoc73a6883g-a.oregon-postgres.render.com/restaurantechiclayo_2uyn"

UPGRADE_SQL = """
-- TABLA DE SUCURSALES
CREATE TABLE IF NOT EXISTS sucursal (
    id_sucursal SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    direccion TEXT
);

-- TABLA DE USUARIOS
CREATE TABLE IF NOT EXISTS usuario (
    id_usuario SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    rol TEXT NOT NULL, -- 'admin', 'mesero', 'cocina'
    id_sucursal INTEGER REFERENCES sucursal(id_sucursal)
);

-- MODIFICAR TABLAS EXISTENTES PARA SOPORTAR MULTI-SUCURSAL
-- (Using IF NOT EXISTS logic via subqueries or just try/catch in python)
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='mesa' AND column_name='id_sucursal') THEN
        ALTER TABLE mesa ADD COLUMN id_sucursal INTEGER REFERENCES sucursal(id_sucursal);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='pedido' AND column_name='id_sucursal') THEN
        ALTER TABLE pedido ADD COLUMN id_sucursal INTEGER REFERENCES sucursal(id_sucursal);
    END IF;
END $$;
"""

def upgrade_auth():
    try:
        conn = psycopg2.connect(DATABASE_URI)
        cur = conn.cursor()
        print("Connected to PostgreSQL for Auth Upgrade.")
        
        # Create tables
        cur.execute(UPGRADE_SQL)
        
        # Check if we already have seeds
        cur.execute("SELECT COUNT(*) FROM sucursal")
        if cur.fetchone()[0] == 0:
            print("Seeding initial data...")
            # Insert Branch
            cur.execute("INSERT INTO sucursal (nombre, direccion) VALUES ('Dragón Norteño - Chiclayo Principal', 'Av. Central 123') RETURNING id_sucursal")
            sucursal_id = cur.fetchone()[0]
            
            # Update existing mesas to belong to this branch
            cur.execute("UPDATE mesa SET id_sucursal = %s", (sucursal_id,))
            
            # Insert Users
            # Admin
            cur.execute("INSERT INTO usuario (username, password_hash, rol, id_sucursal) VALUES (%s, %s, %s, %s)",
                       ('admin1', generate_password_hash('admin123'), 'admin', sucursal_id))
            
            # 6 Waiters
            for i in range(1, 7):
                cur.execute("INSERT INTO usuario (username, password_hash, rol, id_sucursal) VALUES (%s, %s, %s, %s)",
                           (f'mesero{i}', generate_password_hash(f'mesero{i}'), 'mesero', sucursal_id))
            
            # Kitchen (cocina)
            cur.execute("INSERT INTO usuario (username, password_hash, rol, id_sucursal) VALUES (%s, %s, %s, %s)",
                       ('cocina', generate_password_hash('cocina123'), 'cocina', sucursal_id))
            
            print("Seeding completed successfully.")
        
        conn.commit()
    except Exception as e:
        print(f"Error during upgrade: {e}")
        if 'conn' in locals(): conn.rollback()
    finally:
        if 'conn' in locals():
            cur.close()
            conn.close()

if __name__ == "__main__":
    upgrade_auth()
