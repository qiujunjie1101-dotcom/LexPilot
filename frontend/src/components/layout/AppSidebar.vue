<script setup lang="ts">
import type { Component } from 'vue';
import { useRoute } from 'vue-router';
import {
  AlertTriangle,
  BookOpen,
  ClipboardCheck,
  FileSearch,
  FolderOpen,
  GitCompare,
  LayoutDashboard,
  Route as RouteIcon,
  Scale,
  UserCheck,
} from 'lucide-vue-next';
import { cn } from '@/lib/utils';
import { useAppStore } from '@/store/app';

const route = useRoute();
const { sidebarCollapsed } = useAppStore();

interface NavItem {
  to: string;
  label: string;
  icon: Component;
}

interface NavGroup {
  label: string;
  items: NavItem[];
}

const groups: NavGroup[] = [
  {
    label: '概览',
    items: [{ to: '/', label: '仪表盘', icon: LayoutDashboard }],
  },
  {
    label: '合同工作台',
    items: [
      { to: '/review', label: '合同审查', icon: FileSearch },
      { to: '/contracts', label: '合同中心', icon: FolderOpen },
      { to: '/diff', label: '条款比对', icon: GitCompare },
    ],
  },
  {
    label: '法务协作',
    items: [
      { to: '/playbook', label: '法务手册', icon: BookOpen },
      { to: '/human-review', label: '人工复核', icon: UserCheck },
    ],
  },
  {
    label: 'Agent 质量',
    items: [
      { to: '/trace', label: '链路追踪', icon: RouteIcon },
      { to: '/evaluation', label: '效果评估', icon: ClipboardCheck },
      { to: '/bad-cases', label: '坏例中心', icon: AlertTriangle },
    ],
  },
];

const isActive = (path: string) => route.path === path;
</script>

<template>
  <aside
    :class="[
      'fixed inset-y-0 left-0 z-30 flex flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground transition-[width] duration-200',
      sidebarCollapsed ? 'w-[68px]' : 'w-[240px]',
    ]"
  >
    <div :class="['flex h-16 shrink-0 items-center border-b border-sidebar-border', sidebarCollapsed ? 'justify-center px-2' : 'gap-2.5 px-4']">
      <span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-indigo-500 text-white shadow-sm">
        <Scale class="h-4 w-4" />
      </span>
      <div v-if="!sidebarCollapsed" class="min-w-0">
        <p class="truncate text-[13px] font-semibold leading-4 text-white">Legal Copilot</p>
        <p class="mt-0.5 truncate text-[10px] leading-3 text-sidebar-muted">Legal Ops Workspace</p>
      </div>
    </div>

    <nav class="flex-1 space-y-5 overflow-y-auto overflow-x-hidden px-3 py-4">
      <div v-for="group in groups" :key="group.label" class="space-y-1">
        <p v-if="!sidebarCollapsed" class="px-2 pb-1 text-[10px] font-medium tracking-wider text-sidebar-muted">
          {{ group.label }}
        </p>
        <RouterLink
          v-for="item in group.items"
          :key="item.to"
          :to="item.to"
          :title="sidebarCollapsed ? item.label : undefined"
          :class="
            cn(
              'group relative flex h-9 items-center rounded-md text-[13px] font-medium transition-colors',
              sidebarCollapsed ? 'justify-center px-0' : 'gap-2.5 px-2.5',
              isActive(item.to)
                ? 'bg-white/[0.08] text-white'
                : 'text-sidebar-muted hover:bg-white/[0.04] hover:text-sidebar-foreground',
            )
          "
        >
          <span
            v-if="isActive(item.to)"
            class="absolute left-0 top-1/2 h-4 w-[2px] -translate-y-1/2 rounded-full bg-indigo-400"
          />
          <component
            :is="item.icon"
            :class="['h-4 w-4 shrink-0', isActive(item.to) ? 'text-indigo-300' : 'text-sidebar-muted group-hover:text-sidebar-foreground']"
          />
          <span v-if="!sidebarCollapsed" class="truncate">{{ item.label }}</span>
        </RouterLink>
      </div>
    </nav>

    <div v-if="!sidebarCollapsed" class="shrink-0 border-t border-sidebar-border p-3">
      <div class="rounded-md border border-sidebar-border bg-white/[0.05] px-2.5 py-2">
        <p class="text-[11px] font-medium text-sidebar-foreground">AI 初审 · 法务终审</p>
        <p class="mt-0.5 text-[10px] leading-4 text-sidebar-muted">高风险合同自动进入人工复核</p>
      </div>
    </div>
  </aside>
</template>
