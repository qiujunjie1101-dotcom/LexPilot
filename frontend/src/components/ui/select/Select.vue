<script setup lang="ts">
import { ChevronDown } from 'lucide-vue-next';

const props = defineProps<{
  modelValue?: string;
  options: { value: string; label: string }[];
  disabled?: boolean;
}>();

const emit = defineEmits<{ (e: 'update:modelValue', value: string): void }>();

const onChange = (event: Event) => {
  emit('update:modelValue', (event.target as HTMLSelectElement).value);
};
</script>

<template>
  <div class="relative inline-flex w-full">
    <select
      :value="props.modelValue"
      :disabled="props.disabled"
      class="h-9 w-full appearance-none rounded-md border border-input bg-card px-3 pr-8 text-sm shadow-sm transition-colors hover:border-primary/30 focus-visible:border-primary/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/30 disabled:cursor-not-allowed disabled:opacity-50"
      @change="onChange"
    >
      <option v-for="option in props.options" :key="option.value" :value="option.value">
        {{ option.label }}
      </option>
    </select>
    <ChevronDown class="pointer-events-none absolute right-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
  </div>
</template>
