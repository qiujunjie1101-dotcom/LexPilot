import { reactive } from 'vue';

export type ToastVariant = 'success' | 'error' | 'warning' | 'info';

export interface ToastItem {
  id: number;
  title: string;
  description?: string;
  variant: ToastVariant;
}

const toasts = reactive<ToastItem[]>([]);
let seed = 0;

function remove(id: number) {
  const index = toasts.findIndex((item) => item.id === id);
  if (index > -1) toasts.splice(index, 1);
}

export function useToast() {
  const pushToast = (
    title: string,
    options: { description?: string; variant?: ToastVariant; duration?: number } = {},
  ) => {
    const id = ++seed;
    const variant = options.variant || 'info';
    toasts.push({ id, title, description: options.description, variant });
    const duration = options.duration ?? (variant === 'error' ? 5000 : 3500);
    window.setTimeout(() => remove(id), duration);
    return id;
  };

  return { toasts, pushToast, removeToast: remove };
}
