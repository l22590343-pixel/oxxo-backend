import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { VentaService } from '../../services/venta.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  template: `
    <h2 class="mb-4">📊 Dashboard</h2>

    <div class="row g-3 mb-4">
      <div class="col-md-3">
        <div class="card text-white" style="background-color:#cc0000">
          <div class="card-body text-center">
            <h3 class="card-title">{{ data?.ventas_hoy }}</h3>
            <p class="card-text">Ventas Hoy</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-white bg-success">
          <div class="card-body text-center">
            <h3 class="card-title">\${{ data?.ingresos_hoy | number:'1.2-2' }}</h3>
            <p class="card-text">Ingresos Hoy</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-white bg-primary">
          <div class="card-body text-center">
            <h3 class="card-title">{{ data?.total_productos }}</h3>
            <p class="card-text">Total Productos</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-white bg-warning">
          <div class="card-body text-center">
            <h3 class="card-title">{{ data?.stock_bajo }}</h3>
            <p class="card-text">Stock Bajo</p>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-header fw-bold">🏆 Top Productos Más Vendidos</div>
      <div class="card-body">
        <div *ngIf="data?.top_productos?.length === 0" class="text-muted">Sin ventas aún.</div>
        <div *ngFor="let p of data?.top_productos" class="mb-2">
          <div class="d-flex justify-content-between">
            <span>{{ p.nombre }}</span>
            <span class="badge bg-danger">{{ p.cantidad }} vendidos</span>
          </div>
          <div class="progress" style="height:8px">
            <div class="progress-bar bg-danger" [style.width]="p.cantidad * 10 + '%'"></div>
          </div>
        </div>
      </div>
    </div>
  `
})
export class DashboardComponent implements OnInit {
  data: any = null;

  constructor(private ventaService: VentaService) {}

  ngOnInit() {
    this.ventaService.getDashboard().subscribe(d => this.data = d);
  }
}
