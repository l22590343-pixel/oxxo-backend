import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { VentaService } from '../../services/venta.service';

@Component({
  selector: 'app-inventario',
  standalone: true,
  imports: [CommonModule],
  template: `
    <h2 class="mb-4">📋 Inventario</h2>
    <div class="row mb-3">
      <div class="col-md-4">
        <div class="card text-white bg-danger text-center p-3">
          <h4>{{ agotados }}</h4><p class="mb-0">Agotados</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card text-white bg-warning text-center p-3">
          <h4>{{ bajos }}</h4><p class="mb-0">Stock Bajo (≤5)</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card text-white bg-success text-center p-3">
          <h4>{{ ok }}</h4><p class="mb-0">Stock OK</p>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-body p-0">
        <table class="table table-hover mb-0">
          <thead class="table-dark">
            <tr><th>Producto</th><th>Categoría</th><th>Stock</th><th>Estado</th></tr>
          </thead>
          <tbody>
            <tr *ngFor="let p of inventario">
              <td>{{ p.nombre }}</td>
              <td>{{ p.categoria }}</td>
              <td>{{ p.stock }}</td>
              <td>
                <span [class]="p.estado === 'agotado' ? 'badge bg-danger' : p.estado === 'bajo' ? 'badge bg-warning' : 'badge bg-success'">
                  {{ p.estado === 'agotado' ? 'Agotado' : p.estado === 'bajo' ? 'Stock Bajo' : 'OK' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `
})
export class InventarioComponent implements OnInit {
  inventario: any[] = [];

  get agotados() { return this.inventario.filter(p => p.estado === 'agotado').length; }
  get bajos() { return this.inventario.filter(p => p.estado === 'bajo').length; }
  get ok() { return this.inventario.filter(p => p.estado === 'ok').length; }

  constructor(private ventaService: VentaService) {}

  ngOnInit() {
    this.ventaService.getInventario().subscribe(i => this.inventario = i);
  }
}
