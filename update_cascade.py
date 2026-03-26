import psycopg2

DATABASE_URI = "postgresql://restaurantechiclayo_2uyn_user:3nJW2BwDIm7uZ9bCSS8cHSzgkPX0GAQa@dpg-d726rgp9fqoc73a6883g-a.oregon-postgres.render.com/restaurantechiclayo_2uyn"

CASCADE_FIX = """
-- CAMBIAR RESTRICT A CASCADE PARA QUE AL ELIMINAR EL PEDIDO SE ELIMINEN SUS ITEMS
ALTER TABLE detalle_pedido DROP CONSTRAINT IF EXISTS detalle_pedido_id_pedido_fkey;
ALTER TABLE detalle_pedido ADD CONSTRAINT detalle_pedido_id_pedido_fkey 
    FOREIGN KEY (id_pedido) REFERENCES pedido(id_pedido) ON DELETE CASCADE;
"""

def update_cascade():
    try:
        conn = psycopg2.connect(DATABASE_URI)
        cur = conn.cursor()
        print("Updating foreign key to ON DELETE CASCADE...")
        cur.execute(CASCADE_FIX)
        conn.commit()
        print("Success.")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        if 'conn' in locals():
            cur.close()
            conn.close()

if __name__ == "__main__":
    update_cascade()
