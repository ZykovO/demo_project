// truncate.pipe.ts
import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'truncate',
  standalone: true,
  pure: true
})
export class TruncatePipe implements PipeTransform {
  /**
   * Обрезает текст до указанной длины и добавляет многоточие
   * @param value - исходный текст
   * @param limit - максимальная длина (по умолчанию 100)
   * @param trail - символы для добавления в конец (по умолчанию '...')
   * @param wordBoundary - обрезать по границе слов (по умолчанию true)
   */
  transform(
    value: string | null | undefined,
    limit: number = 100,
    trail: string = '...',
    wordBoundary: boolean = true
  ): string {
    // Проверка входных данных
    if (!value || typeof value !== 'string') {
      return '';
    }

    // Очистка лишних пробелов
    const cleanValue = value.trim();

    if (cleanValue.length <= limit) {
      return cleanValue;
    }

    // Базовая обрезка
    let truncated = cleanValue.substring(0, limit);

    // Обрезка по границе слов, если включена
    if (wordBoundary && truncated.length > 0) {
      const lastSpaceIndex = truncated.lastIndexOf(' ');
      if (lastSpaceIndex > limit * 0.5) { // Только если найден пробел не слишком близко к началу
        truncated = truncated.substring(0, lastSpaceIndex);
      }
    }

    return truncated + trail;
  }
}
