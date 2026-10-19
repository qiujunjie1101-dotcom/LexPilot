<script setup lang="ts">
import { RouterView } from 'vue-router';
import AppHeader from '@/components/layout/AppHeader.vue';
import AppSidebar from '@/components/layout/AppSidebar.vue';
import ToastViewport from '@/components/ui/ToastViewport.vue';
import { useAppStore } from '@/store/app';
import { initTheme } from '@/composables/useTheme';

initTheme();
const { role, sidebarCollapsed } = useAppStore();
</script>

<template>
  <div class="min-h-screen bg-background text-foreground">
    <AppSidebar />
    <div
      :class="[
        'min-h-screen transition-[padding] duration-200',
        sidebarCollapsed ? 'pl-[68px]' : 'pl-[240px]',
      ]"
    >
      <AppHeader />
      <main class="mx-auto w-full max-w-[1680px] p-4 lg:p-6">
        <RouterView v-slot="{ Component }">
          <Transition name="page" mode="out-in">
            <component :is="Component" :key="role" />
          </Transition>
        </RouterView>
      </main>
    </div>
    <ToastViewport />
  </div>
</template>
