import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ProductoService, Producto } from '../../services/producto.service';

@Component({
  selector: 'app-productos',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2>📦 Productos</h2>
      <button class="btn btn-danger" (click)="nuevo()">+ Agregar Producto</button>
    </div>

    <!-- Formulario -->
    <div *ngIf="mostrarForm" class="card mb-4">
      <div class="card-header fw-bold">{{ editando ? 'Editar' : 'Nuevo' }} Producto</div>
      <div class="card-body">
        <div class="row g-2">
          <div class="col-md-4">
            <label class="form-label">Nombre</label>
            <input class="form-control" [(ngModel)]="form.nombre" placeholder="Nombre del producto">
          </div>
          <div class="col-md-3">
            <label class="form-label">Categoría</label>
            <select class="form-select" [(ngModel)]="form.categoria">
              <option>Bebidas</option>
              <option>Botanas</option>
              <option>Dulces</option>
              <option>Lacteos</option>
              <option>Limpieza</option>
              <option>Otros</option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label">Precio</label>
            <input class="form-control" type="number" [(ngModel)]="form.precio" placeholder="0.00">
          </div>
          <div class="col-md-2">
            <label class="form-label">Stock</label>
            <input class="form-control" type="number" [(ngModel)]="form.stock" placeholder="0">
          </div>
          <div class="col-md-3">
            <label class="form-label">Código de Barras</label>
            <input class="form-control" [(ngModel)]="form.codigo_barras" placeholder="0000000000000">
          </div>
        </div>
        <div class="mt-3 d-flex gap-2">
          <button class="btn btn-danger" (click)="guardar()">💾 Guardar</button>
          <button class="btn btn-secondary" (click)="mostrarForm=false">Cancelar</button>
        </div>
      </div>
    </div>

    <!-- Tabla -->
    <div class="card">
      <div class="card-body p-0">
        <table class="table table-hover mb-0">
          <thead class="table-dark">
            <tr>
              <th>ID</th><th>Nombre</th><th>Categoría</th>
              <th>Precio</th><th>Stock</th><th>Código</th><th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let p of productos">
              <td>{{ p.id }}</td>
              <td>{{ p.nombre }}</td>
              <td><span class="badge bg-secondary">{{ p.categoria }}</span></td>
              <td>\${{ p.precio }}</td>
              <td>
                <span [class]="p.stock === 0 ? 'badge bg-danger' : p.stock <= 5 ? 'badge bg-warning' : 'badge bg-success'">
                  {{ p.stock }}
                </span>
              </td>
              <td><small>{{ p.codigo_barras }}</small></td>
              <td>
                <button class="btn btn-sm btn-outline-primary me-1" (click)="editar(p)">✏️</button>
                <button class="btn btn-sm btn-outline-danger" (click)="eliminar(p.id!)">🗑️</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `
})
export class ProductosComponent implements OnInit {
  productos: Producto[] = [];
  mostrarForm = false;
  editando = false;
  form: Producto = { nombre: '', categoria: 'Bebidas', precio: 0, stock: 0, codigo_barras: '' };

  constructor(private productoService: ProductoService) {}

  ngOnInit() { this.cargar(); }

  cargar() {
    this.productoService.getAll().subscribe(p => this.productos = p);
  }

  nuevo() {
    this.editando = false;
    this.form = { nombre: '', categoria: 'Bebidas', precio: 0, stock: 0, codigo_barras: '' };
    this.mostrarForm = true;
  }

  editar(p: Producto) {
    this.editando = true;
    this.form = { ...p };
    this.mostrarForm = true;
  }

  guardar() {
    if (this.editando && this.form.id) {
      this.productoService.update(this.form.id, this.form).subscribe(() => {
        this.cargar();
        this.mostrarForm = false;
      });
    } else {
      this.productoService.create(this.form).subscribe(() => {
        this.cargar();
        this.mostrarForm = false;
      });
    }
  }

  eliminar(id: number) {
    if (confirm('¿Eliminar este producto?')) {
      this.productoService.delete(id).subscribe(() => this.cargar());
    }
  }
}
