import psycopg2

DATABASE_URI = "postgresql://restaurantechiclayo_2uyn_user:3nJW2BwDIm7uZ9bCSS8cHSzgkPX0GAQa@dpg-d726rgp9fqoc73a6883g-a.oregon-postgres.render.com/restaurantechiclayo_2uyn"

SCHEMA_FIX = """
-- CAMBIAR CONSTRAINT ÚNICO PARA PERMITIR MISMOS USUARIOS EN DIFERENTES SUCURSALES
ALTER TABLE usuario DROP CONSTRAINT IF EXISTS usuario_username_key;
ALTER TABLE usuario ADD CONSTRAINT usuario_username_sucursal_unique UNIQUE (username, id_sucursal);

-- LIMPIEZA ADICIONAL SI ES NECESARIO
TRUNCATE TABLE detalle_pedido CASCADE;
TRUNCATE TABLE pedido CASCADE;
TRUNCATE TABLE usuario CASCADE;
TRUNCATE TABLE mesa CASCADE;
TRUNCATE TABLE sucursal CASCADE;

-- INSERTAMOS LAS 2 SUCURSALES ESPECÍFICAS
INSERT INTO sucursal (nombre, direccion) VALUES 
('Sucursal Emiliano Niño', 'CALLE EMILIANO NIÑO 648 – LAMBAYEQUE'),
('Sucursal 2 de Mayo', 'CALLE 2 DE MAYO 706 - LAMBAYEQUE')
RETURNING id_sucursal;
"""

def reset_and_seed():
    try:
        conn = psycopg2.connect(DATABASE_URI)
        cur = conn.cursor()
        print("Resetting and Seeding Database (Fixed Schema)...")
        
        cur.execute(SCHEMA_FIX)
        sucursales = cur.fetchall() # List of (id,)
        
        for (sid,) in sucursales:
            print(f"Seeding Branch ID {sid}...")
            
            # CREAR 12 MESAS POR SUCURSAL
            for m_num in range(1, 13):
                cur.execute("INSERT INTO mesa (numero, id_sucursal) VALUES (%s, %s)", (m_num, sid))
            
            # ADMIN (TEXTO PLANO)
            cur.execute("INSERT INTO usuario (username, password_hash, rol, id_sucursal) VALUES (%s, %s, %s, %s)",
                       ('admin1', 'admin123', 'admin', sid))
            
            # 6 MESEROS POR SUCURSAL
            for i in range(1, 7):
                cur.execute("INSERT INTO usuario (username, password_hash, rol, id_sucursal) VALUES (%s, %s, %s, %s)",
                           (f'mesero{i}', f'mesero{i}123', 'mesero', sid))
            
            # COCINA
            cur.execute("INSERT INTO usuario (username, password_hash, rol, id_sucursal) VALUES (%s, %s, %s, %s)",
                       ('cocina', 'cocina123', 'cocina', sid))
        
        conn.commit()
        print("Done.")
    except Exception as e:
        print(f"Error: {e}")
        if 'conn' in locals(): conn.rollback()
    finally:
        if 'conn' in locals():
            cur.close()
            conn.close()

if __name__ == "__main__":
    reset_and_seed()
