<script setup lang="ts">
import { nextTick, onBeforeUnmount, ref, watch } from 'vue';
import { X } from 'lucide-vue-next';
import { cn } from '@/lib/utils';

const props = withDefaults(
  defineProps<{
    open: boolean;
    title?: string;
    description?: string;
    width?: string;
    closeOnOverlay?: boolean;
  }>(),
  { width: 'max-w-lg', closeOnOverlay: true },
);

const emit = defineEmits<{ (e: 'update:open', value: boolean): void }>();

const panel = ref<HTMLElement | null>(null);
let previousOverflow = '';

function close() {
  emit('update:open', false);
}

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && props.open) close();
}

watch(
  () => props.open,
  async (open) => {
    if (open) {
      previousOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
      await nextTick();
      panel.value?.focus();
    } else {
      document.body.style.overflow = previousOverflow;
    }
  },
  { immediate: true },
);

window.addEventListener('keydown', onKeydown);
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown);
  document.body.style.overflow = previousOverflow;
});
</script>

<template>
  <Teleport to="body">
    <Transition name="dialog">
      <div v-if="props.open" class="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-slate-950/45 p-4 backdrop-blur-[2px] sm:p-8" @click.self="props.closeOnOverlay && close()">
        <section
          ref="panel"
          role="dialog"
          aria-modal="true"
          tabindex="-1"
          :class="cn('dialog-panel my-auto w-full rounded-xl border border-border bg-card text-card-foreground shadow-popover outline-none', props.width)"
        >
          <header class="flex items-start justify-between gap-4 border-b border-border px-5 py-4">
            <div class="min-w-0 space-y-1">
              <h2 v-if="props.title" class="text-[15px] font-semibold leading-6">{{ props.title }}</h2>
              <p v-if="props.description" class="text-xs leading-5 text-muted-foreground">{{ props.description }}</p>
              <slot name="header" />
            </div>
            <button
              type="button"
              class="flex h-7 w-7 shrink-0 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
              aria-label="关闭"
              @click="close"
            >
              <X class="h-4 w-4" />
            </button>
          </header>
          <div class="max-h-[calc(100vh-220px)] overflow-y-auto px-5 py-4">
            <slot />
          </div>
          <footer v-if="$slots.footer" class="flex items-center justify-end gap-2 border-t border-border bg-muted/30 px-5 py-3">
            <slot name="footer" />
          </footer>
        </section>
      </div>
    </Transition>
  </Teleport>
</template>
