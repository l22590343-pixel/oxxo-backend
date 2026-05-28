import { Component } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <nav class="navbar navbar-expand-lg navbar-dark" style="background-color:#cc0000">
      <div class="container">
        <a class="navbar-brand fw-bold" href="#">🏪 OXXO Sistema</a>
        <div class="navbar-nav flex-row gap-3">
          <a class="nav-link text-white" routerLink="/dashboard" routerLinkActive="fw-bold">📊 Dashboard</a>
          <a class="nav-link text-white" routerLink="/productos" routerLinkActive="fw-bold">📦 Productos</a>
          <a class="nav-link text-white" routerLink="/ventas" routerLinkActive="fw-bold">💰 Ventas</a>
          <a class="nav-link text-white" routerLink="/inventario" routerLinkActive="fw-bold">📋 Inventario</a>
        </div>
      </div>
    </nav>
    <div class="container mt-4">
      <router-outlet />
    </div>
  `
})
export class App { title = 'oxxo'; }
