import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

export interface SearchResult {
  text: string;
  metadata: {
    source: string;
    chunk_index: number;
    [key: string]: any;
  };
  score: number;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  answer: string;
}

export interface IngestResponse {
  message: string;
  filename: string;
  chunks_added: number;
}

export interface StatsResponse {
  total_documents: number;
  embedding_dimension: number;
  model_name: string;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  getStats(): Observable<StatsResponse> {
    return this.http.get<StatsResponse>(`${this.apiUrl}/stats`);
  }

  search(query: string, topK: number = 5): Observable<SearchResponse> {
    return this.http.post<SearchResponse>(`${this.apiUrl}/search`, {
      query,
      top_k: topK
    });
  }

  ingestDocument(file: File): Observable<IngestResponse> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<IngestResponse>(`${this.apiUrl}/ingest`, formData);
  }

  clearIndex(): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.apiUrl}/clear`);
  }
}
