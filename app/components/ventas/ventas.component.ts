import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ProductoService, Producto } from '../../services/producto.service';
import { VentaService } from '../../services/venta.service';

@Component({
  selector: 'app-ventas',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <h2 class="mb-4">💰 Nueva Venta</h2>
    <div class="row g-4">

      <!-- Productos disponibles -->
      <div class="col-md-6">
        <div class="card">
          <div class="card-header fw-bold">📦 Productos</div>
          <div class="card-body p-0">
            <table class="table table-sm table-hover mb-0">
              <thead class="table-dark">
                <tr><th>Nombre</th><th>Precio</th><th>Stock</th><th></th></tr>
              </thead>
              <tbody>
                <tr *ngFor="let p of productos">
                  <td>{{ p.nombre }}</td>
                  <td>\${{ p.precio }}</td>
                  <td>{{ p.stock }}</td>
                  <td>
                    <button class="btn btn-sm btn-danger" (click)="agregar(p)" [disabled]="p.stock === 0">+</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Carrito -->
      <div class="col-md-6">
        <div class="card">
          <div class="card-header fw-bold">🛒 Carrito</div>
          <div class="card-body">
            <div *ngIf="carrito.length === 0" class="text-muted text-center py-3">Sin productos</div>
            <div *ngFor="let item of carrito; let i = index" class="d-flex justify-content-between align-items-center mb-2">
              <span>{{ item.nombre }}</span>
              <div class="d-flex align-items-center gap-2">
                <button class="btn btn-sm btn-outline-secondary" (click)="quitar(i)">-</button>
                <span class="fw-bold">{{ item.cantidad }}</span>
                <button class="btn btn-sm btn-outline-secondary" (click)="agregar(item)">+</button>
                <span class="text-danger fw-bold">\${{ item.precio * item.cantidad }}</span>
              </div>
            </div>

            <hr>
            <div class="d-flex justify-content-between fw-bold fs-5">
              <span>Total:</span>
              <span class="text-danger">\${{ total }}</span>
            </div>

            <div class="mt-3">
              <label class="form-label">Método de Pago</label>
              <select class="form-select" [(ngModel)]="metodoPago">
                <option value="efectivo">💵 Efectivo</option>
                <option value="tarjeta">💳 Tarjeta</option>
              </select>
            </div>

            <button class="btn btn-danger w-100 mt-3" (click)="cobrar()" [disabled]="carrito.length === 0">
              ✅ Cobrar \${{ total }}
            </button>

            <div *ngIf="msgExito" class="alert alert-success mt-2">{{ msgExito }}</div>
          </div>
        </div>

        <!-- Ultimas ventas -->
        <div class="card mt-3">
          <div class="card-header fw-bold">📋 Últimas Ventas</div>
          <div class="card-body p-0">
            <table class="table table-sm mb-0">
              <thead><tr><th>#</th><th>Total</th><th>Pago</th><th>Fecha</th></tr></thead>
              <tbody>
                <tr *ngFor="let v of ventas">
                  <td>{{ v.id }}</td>
                  <td>\${{ v.total }}</td>
                  <td>{{ v.metodo_pago }}</td>
                  <td><small>{{ v.fecha | slice:0:16 }}</small></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  `
})
export class VentasComponent implements OnInit {
  productos: Producto[] = [];
  ventas: any[] = [];
  carrito: any[] = [];
  metodoPago = 'efectivo';
  msgExito = '';

  get total() {
    return this.carrito.reduce((s, i) => s + i.precio * i.cantidad, 0);
  }

  constructor(private productoService: ProductoService, private ventaService: VentaService) {}

  ngOnInit() {
    this.productoService.getAll().subscribe(p => this.productos = p);
    this.ventaService.getAll().subscribe(v => this.ventas = v);
  }

  agregar(p: any) {
    const existe = this.carrito.find(i => i.id === p.id);
    if (existe) { existe.cantidad++; }
    else { this.carrito.push({ ...p, cantidad: 1 }); }
  }

  quitar(i: number) {
    if (this.carrito[i].cantidad > 1) { this.carrito[i].cantidad--; }
    else { this.carrito.splice(i, 1); }
  }

  cobrar() {
    const venta = {
      metodo_pago: this.metodoPago,
      productos: this.carrito.map(i => ({ id: i.id, cantidad: i.cantidad, precio: i.precio }))
    };
    this.ventaService.create(venta).subscribe(res => {
      this.msgExito = `✅ Venta #${res.id} registrada por $${res.total}`;
      this.carrito = [];
      this.productoService.getAll().subscribe(p => this.productos = p);
      this.ventaService.getAll().subscribe(v => this.ventas = v);
      setTimeout(() => this.msgExito = '', 3000);
    });
  }
}
