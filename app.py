from flask import Flask, request, jsonify
from flask_cors import CORS
from config import get_connection
import os

app = Flask(__name__)
CORS(app)

# ══════════════════════════════════════
# RUTA RAIZ
# ══════════════════════════════════════

@app.route('/')
def index():
    return jsonify({'mensaje': 'API OXXO funcionando'})

# ══════════════════════════════════════
# LOGIN
# ══════════════════════════════════════

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nombre, rol FROM usuarios_oxxo WHERE usuario = %s AND password = %s",
        (data['usuario'], data['password'])
    )
    user = cursor.fetchone()
    conn.close()
    if user:
        return jsonify({'id': user[0], 'nombre': user[1], 'rol': user[2]})
    return jsonify({'mensaje': 'Credenciales incorrectas'}), 401

# ══════════════════════════════════════
# PRODUCTOS
# ══════════════════════════════════════

@app.route('/productos', methods=['GET'])
def get_productos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, categoria, precio, stock, codigo_barras FROM productos_oxxo ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    productos = [
        {'id': r[0], 'nombre': r[1], 'categoria': r[2],
         'precio': float(r[3]), 'stock': r[4], 'codigo_barras': r[5]}
        for r in rows
    ]
    return jsonify(productos)

@app.route('/productos/<int:id>', methods=['GET'])
def get_producto(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, categoria, precio, stock, codigo_barras FROM productos_oxxo WHERE id = %s", (id,))
    r = cursor.fetchone()
    conn.close()
    if r:
        return jsonify({'id': r[0], 'nombre': r[1], 'categoria': r[2],
                        'precio': float(r[3]), 'stock': r[4], 'codigo_barras': r[5]})
    return jsonify({'mensaje': 'Producto no encontrado'}), 404

@app.route('/productos', methods=['POST'])
def create_producto():
    data = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO productos_oxxo (nombre, categoria, precio, stock, codigo_barras) VALUES (%s, %s, %s, %s, %s) RETURNING id",
        (data['nombre'], data['categoria'], data['precio'], data['stock'], data.get('codigo_barras', ''))
    )
    new_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Producto creado', 'id': new_id}), 201

@app.route('/productos/<int:id>', methods=['PUT'])
def update_producto(id):
    data = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE productos_oxxo SET nombre=%s, categoria=%s, precio=%s, stock=%s, codigo_barras=%s WHERE id=%s",
        (data['nombre'], data['categoria'], data['precio'], data['stock'], data.get('codigo_barras', ''), id)
    )
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Producto actualizado'})

@app.route('/productos/<int:id>', methods=['DELETE'])
def delete_producto(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos_oxxo WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Producto eliminado'})

# ══════════════════════════════════════
# VENTAS
# ══════════════════════════════════════

@app.route('/ventas', methods=['GET'])
def get_ventas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT v.id, v.fecha, v.total, v.metodo_pago,
               COUNT(dv.id) as num_productos
        FROM ventas_oxxo v
        LEFT JOIN detalle_venta_oxxo dv ON dv.venta_id = v.id
        GROUP BY v.id, v.fecha, v.total, v.metodo_pago
        ORDER BY v.fecha DESC
        LIMIT 50
    """)
    rows = cursor.fetchall()
    conn.close()
    ventas = [
        {'id': r[0], 'fecha': str(r[1]), 'total': float(r[2]),
         'metodo_pago': r[3], 'num_productos': r[4]}
        for r in rows
    ]
    return jsonify(ventas)

@app.route('/ventas', methods=['POST'])
def create_venta():
    data = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()

    total = sum(item['precio'] * item['cantidad'] for item in data['productos'])

    cursor.execute(
        "INSERT INTO ventas_oxxo (total, metodo_pago) VALUES (%s, %s) RETURNING id",
        (total, data['metodo_pago'])
    )
    venta_id = cursor.fetchone()[0]

    for item in data['productos']:
        cursor.execute(
            "INSERT INTO detalle_venta_oxxo (venta_id, producto_id, cantidad, precio_unit, subtotal) VALUES (%s, %s, %s, %s, %s)",
            (venta_id, item['id'], item['cantidad'], item['precio'], item['precio'] * item['cantidad'])
        )
        cursor.execute(
            "UPDATE productos_oxxo SET stock = GREATEST(0, stock - %s) WHERE id = %s",
            (item['cantidad'], item['id'])
        )

    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Venta registrada', 'id': venta_id, 'total': total}), 201

# ══════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════

@app.route('/dashboard', methods=['GET'])
def get_dashboard():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM ventas_oxxo WHERE DATE(fecha) = CURRENT_DATE")
    r = cursor.fetchone()
    ventas_hoy = int(r[0])
    ingresos_hoy = float(r[1])

    cursor.execute("SELECT COUNT(*) FROM productos_oxxo")
    total_productos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM productos_oxxo WHERE stock <= 5")
    stock_bajo = cursor.fetchone()[0]

    cursor.execute("""
        SELECT p.nombre, SUM(dv.cantidad) as total_vendido
        FROM detalle_venta_oxxo dv
        JOIN productos_oxxo p ON p.id = dv.producto_id
        GROUP BY p.nombre
        ORDER BY total_vendido DESC
        LIMIT 5
    """)
    top_productos = [{'nombre': r[0], 'cantidad': int(r[1])} for r in cursor.fetchall()]

    conn.close()
    return jsonify({
        'ventas_hoy': ventas_hoy,
        'ingresos_hoy': ingresos_hoy,
        'total_productos': total_productos,
        'stock_bajo': stock_bajo,
        'top_productos': top_productos
    })

# ══════════════════════════════════════
# INVENTARIO
# ══════════════════════════════════════

@app.route('/inventario', methods=['GET'])
def get_inventario():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nombre, categoria, stock,
               CASE WHEN stock = 0 THEN 'agotado'
                    WHEN stock <= 5 THEN 'bajo'
                    ELSE 'ok' END as estado
        FROM productos_oxxo
        ORDER BY stock ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return jsonify([
        {'id': r[0], 'nombre': r[1], 'categoria': r[2], 'stock': r[3], 'estado': r[4]}
        for r in rows
    ])

# ══════════════════════════════════════
# REPORTES
# ══════════════════════════════════════

@app.route('/reportes', methods=['GET'])
def get_reportes():
    fecha_inicio = request.args.get('inicio')
    fecha_fin = request.args.get('fin')
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DATE(fecha) as dia, COUNT(*) as num, SUM(total) as total
        FROM ventas_oxxo
        WHERE DATE(fecha) BETWEEN %s::date AND %s::date
        GROUP BY DATE(fecha)
        ORDER BY dia DESC
    """, (fecha_inicio, fecha_fin))
    rows = cursor.fetchall()
    conn.close()
    return jsonify([
        {'fecha': str(r[0]), 'num_ventas': r[1], 'total': float(r[2])}
        for r in rows
    ])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

# ══════════════════════════════════════
# HISTORIAL DETALLE DE VENTA
# ══════════════════════════════════════

@app.route('/ventas/<int:id>/detalle', methods=['GET'])
def get_detalle_venta(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.cantidad, d.precio_unit, d.subtotal, p.nombre, p.categoria
        FROM detalle_venta_oxxo d
        JOIN productos_oxxo p ON p.id = d.producto_id
        WHERE d.venta_id = %s
    """, (id,))
    rows = cursor.fetchall()
    conn.close()
    return jsonify([
        {'cantidad': r[0], 'precio_unit': float(r[1]),
         'subtotal': float(r[2]), 'nombre': r[3], 'categoria': r[4]}
        for r in rows
    ])

# ══════════════════════════════════════
# USUARIOS
# ══════════════════════════════════════

@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, usuario, rol FROM usuarios_oxxo ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([
        {'id': r[0], 'nombre': r[1], 'usuario': r[2], 'rol': r[3]}
        for r in rows
    ])

@app.route('/usuarios', methods=['POST'])
def create_usuario():
    data = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO usuarios_oxxo (nombre, usuario, password, rol) VALUES (%s, %s, %s, %s) RETURNING id",
            (data['nombre'], data['usuario'], data['password'], data['rol'])
        )
        new_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return jsonify({'mensaje': 'Usuario creado', 'id': new_id}), 201
    except Exception as ex:
        conn.close()
        return jsonify({'mensaje': 'Error: ' + str(ex)}), 400

@app.route('/usuarios/<int:id>', methods=['PUT'])
def update_usuario(id):
    data = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios_oxxo SET nombre=%s, usuario=%s, rol=%s WHERE id=%s",
        (data['nombre'], data['usuario'], data['rol'], id)
    )
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Usuario actualizado'})

@app.route('/usuarios/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios_oxxo WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Usuario eliminado'})
