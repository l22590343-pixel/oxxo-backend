from flask import Flask, request, jsonify
from flask_cors import CORS
from config import get_connection

app = Flask(__name__)
CORS(app)

# ══════════════════════════════════════
# PRODUCTOS
# ══════════════════════════════════════

# Obtener todos los productos
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

# Obtener un producto
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

# Crear producto
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

# Actualizar producto
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

# Eliminar producto
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

# Obtener todas las ventas
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

# Crear venta
@app.route('/ventas', methods=['POST'])
def create_venta():
    data = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()

    # Calcular total
    total = sum(item['precio'] * item['cantidad'] for item in data['productos'])

    # Insertar venta
    cursor.execute(
        "INSERT INTO ventas_oxxo (total, metodo_pago) VALUES (%s, %s) RETURNING id",
        (total, data['metodo_pago'])
    )
    venta_id = cursor.fetchone()[0]

    # Insertar detalle y actualizar stock
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

    # Ventas del dia
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM ventas_oxxo WHERE DATE(fecha) = CURRENT_DATE")
    r = cursor.fetchone()
    ventas_hoy = int(r[0])
    ingresos_hoy = float(r[1])

    # Total productos
    cursor.execute("SELECT COUNT(*) FROM productos_oxxo")
    total_productos = cursor.fetchone()[0]

    # Productos con stock bajo
    cursor.execute("SELECT COUNT(*) FROM productos_oxxo WHERE stock <= 5")
    stock_bajo = cursor.fetchone()[0]

    # Top 5 productos mas vendidos
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
