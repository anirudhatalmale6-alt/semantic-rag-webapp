import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService, SearchResponse, StatsResponse } from './api.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  private api = inject(ApiService);

  query = signal('');
  results = signal<SearchResponse | null>(null);
  stats = signal<StatsResponse | null>(null);
  loading = signal(false);
  uploading = signal(false);
  error = signal<string | null>(null);
  uploadMessage = signal<string | null>(null);

  constructor() {
    this.loadStats();
  }

  loadStats(): void {
    this.api.getStats().subscribe({
      next: (data) => this.stats.set(data),
      error: (err) => console.error('Failed to load stats:', err)
    });
  }

  search(): void {
    const q = this.query().trim();
    if (!q) return;

    this.loading.set(true);
    this.error.set(null);
    this.results.set(null);

    this.api.search(q, 5).subscribe({
      next: (data) => {
        this.results.set(data);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'Search failed. Please try again.');
        this.loading.set(false);
      }
    });
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    this.uploading.set(true);
    this.error.set(null);
    this.uploadMessage.set(null);

    this.api.ingestDocument(file).subscribe({
      next: (data) => {
        this.uploadMessage.set(`${data.filename}: ${data.chunks_added} chunks indexed`);
        this.uploading.set(false);
        this.loadStats();
        input.value = '';
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'Upload failed. Please try again.');
        this.uploading.set(false);
        input.value = '';
      }
    });
  }

  onKeyPress(event: KeyboardEvent): void {
    if (event.key === 'Enter') {
      this.search();
    }
  }

  formatScore(score: number): string {
    return (score * 100).toFixed(1) + '%';
  }
}
