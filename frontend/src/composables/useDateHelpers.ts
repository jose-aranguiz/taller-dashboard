// src/composables/useDateHelpers.ts

import { addDays, set, getDay } from 'date-fns';

/**
 * Composable con funciones de ayuda para la manipulación de fechas de negocio.
 * 💡 IMPORTANTE: Estas funciones deben ser llamadas cuando un estado cambia
 * (ej. al detener un trabajo) y su resultado debe guardarse en la base de datos
 * en un campo como `fecha_eta` para que las alertas funcionen correctamente.
 */
export function useDateHelpers() {
  /**
   * Añade un número de días hábiles a una fecha, saltando fines de semana.
   */
  const addBusinessDays = (date: Date, days: number): Date => {
    let result = new Date(date);
    let addedDays = 0;
    while (addedDays < days) {
      result = addDays(result, 1);
      const dayOfWeek = getDay(result); // 0 = Domingo, 6 = Sábado
      if (dayOfWeek !== 0 && dayOfWeek !== 6) {
        addedDays++;
      }
    }
    return result;
  };

  /**
   * Calcula la ETA para la aprobación del cliente (2 días hábiles).
   */
  const calculateAprobacionEta = (): Date => {
    return addBusinessDays(new Date(), 2);
  };

  /**
   * Calcula la ETA para repuestos a pedido según las reglas de negocio.
   */
  const calculateRepuestoEta = (): Date => {
    const now = new Date();
    const dayOfWeek = getDay(now);
    const hour = now.getHours();

    let etaDate: Date;

    if (dayOfWeek >= 1 && dayOfWeek <= 3) { // Lunes a Miércoles
      const daysToAdd = hour < 13 ? 2 : 3;
      etaDate = addBusinessDays(now, daysToAdd);
    } else if (dayOfWeek === 4) { // Jueves
      etaDate = hour < 13 ? addBusinessDays(now, 1) : addBusinessDays(now, 2);
    } else { // Viernes, Sábado o Domingo
      etaDate = addBusinessDays(now, 2);
    }

    return set(etaDate, { hours: 11, minutes: 0, seconds: 0, milliseconds: 0 });
  };

  return {
    addBusinessDays,
    calculateAprobacionEta,
    calculateRepuestoEta,
  };
}