<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { ChevronRight, Moon, PanelLeftClose, PanelLeftOpen, Sun, UserRound } from 'lucide-vue-next';
import { api } from '@/api/client';
import { useAppStore, type AppRole } from '@/store/app';
import { useTheme } from '@/composables/useTheme';
import { useToast } from '@/composables/useToast';
import Select from '@/components/ui/select/Select.vue';
import Badge from '@/components/ui/badge/Badge.vue';
import { cn } from '@/lib/utils';
import type { RuntimeInfo } from '@/types/api';

const route = useRoute();
const { role, setRole, sidebarCollapsed, toggleSidebar } = useAppStore();
const { theme, toggleTheme } = useTheme();
const { pushToast } = useToast();

const runtime = ref<RuntimeInfo | null>(null);

const roleOptions = [
  { value: 'sales', label: '业务人员' },
  { value: 'legal', label: '法务审核员' },
];

const title = computed(() => route.meta.title || '仪表盘');
const description = computed(() => route.meta.description || '');
const group = computed(() => route.meta.group || '工作台');
const roleLabel = computed(() => (role.value === 'legal' ? '法务审核员' : '业务人员'));

onMounted(async () => {
  try {
    runtime.value = await api<RuntimeInfo>('/api/runtime');
  } catch {
    runtime.value = null;
  }
});

function onRoleChange(value: string) {
  const next = value as AppRole;
  if (next === role.value) return;
  setRole(next);
  pushToast('身份已切换', {
    description: next === 'legal' ? '当前以法务审核员身份查看，可处理人工复核。' : '当前以业务人员身份查看，可发起合同审查。',
    variant: 'success',
  });
}
</script>

<template>
  <header class="sticky top-0 z-20 border-b border-border bg-background/80 backdrop-blur-md">
    <div class="flex h-16 items-center gap-3 px-4 lg:px-6">
      <button
        type="button"
        class="flex h-8 w-8 shrink-0 items-center justify-center rounded-md border border-border bg-card text-muted-foreground transition-colors hover:text-foreground"
        :aria-label="sidebarCollapsed ? '展开侧栏' : '收起侧栏'"
        :title="sidebarCollapsed ? '展开侧栏' : '收起侧栏'"
        @click="toggleSidebar"
      >
        <PanelLeftOpen v-if="sidebarCollapsed" class="h-4 w-4" />
        <PanelLeftClose v-else class="h-4 w-4" />
      </button>

      <div class="min-w-0 flex-1">
        <nav class="flex items-center gap-1 text-[11px] text-muted-foreground" aria-label="面包屑">
          <span>工作台</span>
          <ChevronRight class="h-3 w-3" />
          <span>{{ group }}</span>
          <ChevronRight class="h-3 w-3" />
          <span class="font-medium text-foreground">{{ title }}</span>
        </nav>
        <div class="mt-0.5 flex min-w-0 items-baseline gap-2">
          <h1 class="truncate text-[15px] font-semibold leading-5">{{ title }}</h1>
          <p v-if="description" class="hidden truncate text-[11px] text-muted-foreground xl:block">{{ description }}</p>
        </div>
      </div>

      <div class="flex shrink-0 items-center gap-2">
        <Badge
          v-if="runtime"
          :class="
            cn(
              runtime.mock_mode
                ? 'border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-300'
                : 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-300',
            )
          "
          class="hidden sm:inline-flex"
          :title="runtime.mock_mode ? '当前为 Mock 模式，未调用真实模型' : `DeepSeek 模型：${runtime.deepseek_model}`"
        >
          <span class="h-1.5 w-1.5 rounded-full bg-current" />
          {{ runtime.mock_mode ? 'Mock 模式' : 'DeepSeek 在线' }}
        </Badge>

        <button
          type="button"
          class="flex h-8 w-8 items-center justify-center rounded-md border border-border bg-card text-muted-foreground transition-colors hover:text-foreground"
          :aria-label="theme === 'dark' ? '切换为浅色主题' : '切换为深色主题'"
          @click="toggleTheme"
        >
          <Sun v-if="theme === 'dark'" class="h-4 w-4" />
          <Moon v-else class="h-4 w-4" />
        </button>

        <div class="hidden items-center gap-1.5 md:flex">
          <span class="shrink-0 whitespace-nowrap text-[11px] text-muted-foreground">身份</span>
          <Select :model-value="role" :options="roleOptions" class="w-[132px]" @update:model-value="onRoleChange" />
        </div>

        <div class="flex items-center gap-2 rounded-md border border-border bg-card py-1 pl-1 pr-2">
          <span class="flex h-6 w-6 items-center justify-center rounded bg-primary/10 text-primary">
            <UserRound class="h-3.5 w-3.5" />
          </span>
          <span class="hidden text-[11px] font-medium sm:block">{{ roleLabel }}</span>
        </div>
      </div>
    </div>
  </header>
</template>
