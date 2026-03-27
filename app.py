from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

DATABASE_URI = "postgresql://restaurantechiclayo_2uyn_user:3nJW2BwDIm7uZ9bCSS8cHSzgkPX0GAQa@dpg-d726rgp9fqoc73a6883g-a.oregon-postgres.render.com/restaurantechiclayo_2uyn"

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URI, cursor_factory=RealDictCursor)
    return conn

# 🔹 AUTH & SUCURSAL ENDPOINTS
@app.route('/sucursales', methods=['GET'])
def get_sucursales():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM sucursal ORDER BY nombre")
    sucursales = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(sucursales)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    id_sucursal = data.get('id_sucursal')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuario WHERE username = %s AND id_sucursal = %s", (username, id_sucursal))
    user = cur.fetchone()
    cur.close()
    conn.close()

    # COMPARACIÓN DIRECTA (TEXTO PLANO)
    if user and user['password_hash'] == password:
        return jsonify({
            "mensaje": "Login exitoso",
            "user": {
                "id_usuario": user['id_usuario'],
                "username": user['username'],
                "rol": user['rol'],
                "id_sucursal": user['id_sucursal']
            }
        })
    else:
        return jsonify({"error": "Credenciales inválidas o sucursal incorrecta"}), 401


# 🔹 MODIFIED EXISTING ENDPOINTS (FILTER BY SUCURSAL)
@app.route('/categorias', methods=['GET'])
def get_categorias():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM categoria ORDER BY id_categoria")
    categorias = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(categorias)

@app.route('/productos', methods=['GET'])
def get_productos():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM producto ORDER BY id_producto")
    productos = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(productos)

@app.route('/mesas/<int:id_sucursal>', methods=['GET'])
def get_mesas(id_sucursal):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM mesa WHERE id_sucursal = %s ORDER BY numero", (id_sucursal,))
    mesas = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(mesas)

@app.route('/pedidos/<int:id_sucursal>', methods=['GET'])
def obtener_pedidos(id_sucursal):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            p.id_pedido,
            p.id_mesa,
            p.estado,
            p.fecha,
            JSON_AGG(JSON_BUILD_OBJECT('producto', pr.nombre, 'cantidad', dp.cantidad)) as items
        FROM pedido p
        JOIN detalle_pedido dp ON p.id_pedido = dp.id_pedido
        JOIN producto pr ON dp.id_producto = pr.id_producto
        WHERE p.id_sucursal = %s
        GROUP BY p.id_pedido, p.id_mesa, p.estado, p.fecha
        ORDER BY p.id_pedido DESC
    """, (id_sucursal,))
    pedidos = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(pedidos)

@app.route('/pedido', methods=['POST'])
def crear_pedido():
    data = request.get_json()
    id_mesa = data['id_mesa']
    id_sucursal = data['id_sucursal']
    productos = data['productos']

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO pedido (id_mesa, id_sucursal, estado) VALUES (%s, %s, 'pendiente') RETURNING id_pedido",
            (id_mesa, id_sucursal)
        )
        id_pedido = cur.fetchone()['id_pedido']

        for p in productos:
            cur.execute(
                "INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad) VALUES (%s, %s, %s)",
                (id_pedido, p['id_producto'], p['cantidad'])
            )
        
        cur.execute("UPDATE mesa SET estado = 'ocupada' WHERE id_mesa = %s AND id_sucursal = %s", (id_mesa, id_sucursal))

        conn.commit()
        return jsonify({"mensaje": "Pedido creado", "id_pedido": id_pedido}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/pedido/<int:id>', methods=['PATCH'])
def actualizar_estado(id):
    data = request.get_json()
    nuevo_estado = data['estado']

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE pedido SET estado = %s WHERE id_pedido = %s RETURNING id_mesa, id_sucursal",
            (nuevo_estado, id)
        )
        row = cur.fetchone()
        
        if nuevo_estado in ['servido', 'pagado', 'cancelado']:
            if row:
                cur.execute("UPDATE mesa SET estado = 'libre' WHERE id_mesa = %s AND id_sucursal = %s", 
                           (row['id_mesa'], row['id_sucursal']))

        conn.commit()
        return jsonify({"mensaje": "Estado actualizado"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/pedido/<int:id>', methods=['DELETE'])
def eliminar_pedido(id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id_mesa, id_sucursal FROM pedido WHERE id_pedido = %s", (id,))
        row = cur.fetchone()
        
        cur.execute("DELETE FROM pedido WHERE id_pedido = %s", (id,))
        
        if row:
            cur.execute("UPDATE mesa SET estado = 'libre' WHERE id_mesa = %s AND id_sucursal = %s", 
                       (row['id_mesa'], row['id_sucursal']))

        conn.commit()
        return jsonify({"mensaje": "Pedido eliminado"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/reporte/ventas-hoy/<int:id_sucursal>', methods=['GET'])
def ventas_hoy(id_sucursal):
    conn = get_db_connection()
    cur = conn.cursor()
    # Solo contamos productos de pedidos 'servido' o 'pagado'
    cur.execute("""
        SELECT 
            pr.nombre,
            SUM(dp.cantidad) as total_vendido
        FROM detalle_pedido dp
        JOIN producto pr ON dp.id_producto = pr.id_producto
        JOIN pedido p ON dp.id_pedido = p.id_pedido
        WHERE p.fecha::date = CURRENT_DATE 
          AND p.id_sucursal = %s
          AND p.estado IN ('servido', 'pagado')
        GROUP BY pr.nombre
        ORDER BY total_vendido DESC
    """, (id_sucursal,))
    resultado = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(resultado)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
