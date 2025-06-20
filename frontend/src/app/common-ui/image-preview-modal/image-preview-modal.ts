// image-preview-modal.component.ts
import {Component, EventEmitter, Input, Output} from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-image-preview-modal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './image-preview-modal.html',
  styleUrls: ['./image-preview-modal.css']
})
export class ImagePreviewModal {
  @Input() imageUrl: string | null = null;
  @Output() close = new EventEmitter<void>();

  closeModal() {
    this.imageUrl = null;
    this.close.emit();
  }
}
