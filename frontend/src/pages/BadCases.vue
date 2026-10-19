<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import {
  AlertTriangle,
  Bug,
  CheckCircle2,
  Plus,
  RefreshCw,
  RotateCcw,
  Search,
} from 'lucide-vue-next';
import { api } from '@/api/client';
import Card from '@/components/ui/card/Card.vue';
import Button from '@/components/ui/button/Button.vue';
import Input from '@/components/ui/input/Input.vue';
import Select from '@/components/ui/select/Select.vue';
import Textarea from '@/components/ui/textarea/Textarea.vue';
import Alert from '@/components/ui/alert/Alert.vue';
import Skeleton from '@/components/ui/skeleton/Skeleton.vue';
import EmptyState from '@/components/ui/empty-state/EmptyState.vue';
import Pagination from '@/components/ui/pagination/Pagination.vue';
import Dialog from '@/components/ui/dialog/Dialog.vue';
import StatCard from '@/components/business/StatCard.vue';
import StatusBadge from '@/components/business/StatusBadge.vue';
import Table from '@/components/ui/table/Table.vue';
import TableHeader from '@/components/ui/table/TableHeader.vue';
import TableBody from '@/components/ui/table/TableBody.vue';
import TableRow from '@/components/ui/table/TableRow.vue';
import TableHead from '@/components/ui/table/TableHead.vue';
import TableCell from '@/components/ui/table/TableCell.vue';
import { useToast } from '@/composables/useToast';
import { BAD_CASE_CATEGORIES, badCaseCategoryLabel } from '@/lib/domain';
import type { BadCase } from '@/types/api';

const { pushToast } = useToast();

const data = ref<BadCase[]>([]);
const loading = ref(true);
const errorMessage = ref('');
const search = ref('');
const categoryFilter = ref('');
const statusFilter = ref('');
const page = ref(1);
const pageSize = 10;

const addOpen = ref(false);
const formTitle = ref('');
const formCategory = ref('retrieval');
const formNote = ref('');
const submitting = ref(false);

async function load() {
  loading.value = true;
  errorMessage.value = '';
  try {
    data.value = await api<BadCase[]>('/api/bad-cases');
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '坏例加载失败';
  } finally {
    loading.value = false;
  }
}

onMounted(load);

const openCount = computed(() => data.value.filter((item) => item.status !== 'fixed').length);
const fixedCount = computed(() => data.value.filter((item) => item.status === 'fixed').length);
const categoryCount = computed(() => new Set(data.value.map((item) => item.category)).size);

const categoryOptions = computed(() => {
  const existing = Array.from(new Set(data.value.map((item) => item.category)));
  const values = Array.from(new Set([...existing, ...BAD_CASE_CATEGORIES.map((item) => item.value)]));
  return [
    { value: '', label: '全部分类' },
    ...values.map((value) => ({ value, label: badCaseCategoryLabel(value) })),
  ];
});

const statusOptions = [
  { value: '', label: '全部状态' },
  { value: 'open', label: '待处理' },
  { value: 'fixed', label: '已修复' },
];

const filtered = computed(() => {
  const keyword = search.value.trim().toLowerCase();
  return data.value.filter((item) => {
    const matchesKeyword =
      !keyword ||
      [item.title, item.id, item.note, item.category]
        .filter(Boolean)
        .some((field) => String(field).toLowerCase().includes(keyword));
    const matchesCategory = !categoryFilter.value || item.category === categoryFilter.value;
    const matchesStatus = !statusFilter.value || item.status === statusFilter.value;
    return matchesKeyword && matchesCategory && matchesStatus;
  });
});

const paged = computed(() => filtered.value.slice((page.value - 1) * pageSize, page.value * pageSize));

watch([search, categoryFilter, statusFilter], () => {
  page.value = 1;
});

watch(filtered, (rows) => {
  const maxPage = Math.max(1, Math.ceil(rows.length / pageSize));
  if (page.value > maxPage) page.value = maxPage;
});

function resetFilters() {
  search.value = '';
  categoryFilter.value = '';
  statusFilter.value = '';
}

function resetForm() {
  formTitle.value = '';
  formCategory.value = 'retrieval';
  formNote.value = '';
}

async function submit() {
  if (!formTitle.value.trim()) {
    pushToast('请填写坏例标题', { variant: 'warning' });
    return;
  }
  if (!formNote.value.trim()) {
    pushToast('请填写治理方案', { variant: 'warning' });
    return;
  }
  submitting.value = true;
  try {
    await api<BadCase>('/api/bad-cases', {
      method: 'POST',
      body: JSON.stringify({
        title: formTitle.value.trim(),
        category: formCategory.value,
        note: formNote.value.trim(),
      }),
    });
    pushToast('坏例已记录', { description: formTitle.value.trim(), variant: 'success' });
    addOpen.value = false;
    resetForm();
    await load();
  } catch (error) {
    pushToast('坏例记录失败', {
      description: error instanceof Error ? error.message : '请稍后重试',
      variant: 'error',
    });
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <div class="space-y-4">
    <Alert v-if="errorMessage" variant="destructive" title="坏例数据加载失败">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <span>{{ errorMessage }}</span>
        <Button size="sm" variant="outline" @click="load">重新加载</Button>
      </div>
    </Alert>

    <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      <StatCard title="全部坏例" :value="data.length" description="已沉淀的失败案例" :icon="Bug" tone="primary" :loading="loading" />
      <StatCard title="待处理" :value="openCount" description="等待治理与回归验证" :icon="AlertTriangle" tone="amber" :loading="loading" />
      <StatCard title="已修复" :value="fixedCount" description="已完成治理闭环" :icon="CheckCircle2" tone="emerald" :loading="loading" />
      <StatCard title="问题分类" :value="categoryCount" description="覆盖的失败类型数量" :icon="Bug" tone="sky" :loading="loading" />
    </div>

    <Card>
      <div class="flex flex-col gap-2 border-b border-border p-4 lg:flex-row lg:items-center lg:justify-between">
        <div class="flex min-w-0 flex-1 flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center">
          <div class="relative min-w-0 flex-1 sm:max-w-xs">
            <Search class="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
            <Input v-model="search" class="pl-8" placeholder="搜索标题、编号或治理方案" />
          </div>
          <Select v-model="categoryFilter" :options="categoryOptions" class="sm:w-[140px]" />
          <Select v-model="statusFilter" :options="statusOptions" class="sm:w-[120px]" />
          <button
            type="button"
            class="inline-flex h-9 items-center gap-1 rounded-md px-2 text-xs text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
            @click="resetFilters"
          >
            <RotateCcw class="h-3.5 w-3.5" />
            重置
          </button>
        </div>
        <div class="flex shrink-0 items-center justify-end gap-2">
          <Button variant="outline" size="sm" :disabled="loading" @click="load">
            <RefreshCw :class="['h-4 w-4', loading ? 'animate-spin' : '']" />
            刷新
          </Button>
          <Button size="sm" @click="addOpen = true">
            <Plus class="h-4 w-4" />
            记录坏例
          </Button>
        </div>
      </div>

      <div v-if="loading" class="space-y-2 p-4">
        <Skeleton v-for="index in 7" :key="index" class="h-11 w-full" />
      </div>

      <EmptyState
        v-else-if="!data.length"
        title="还没有坏例记录"
        description="将失败案例沉淀下来，形成可追踪的治理闭环。"
      >
        <template #icon><Bug class="h-5 w-5" /></template>
        <template #action>
          <Button size="sm" @click="addOpen = true">
            <Plus class="h-4 w-4" />
            记录第一个坏例
          </Button>
        </template>
      </EmptyState>

      <EmptyState
        v-else-if="!filtered.length"
        title="没有匹配的坏例"
        description="尝试调整关键词或筛选条件。"
      >
        <template #icon><Search class="h-5 w-5" /></template>
        <template #action>
          <Button size="sm" variant="outline" @click="resetFilters">清空筛选</Button>
        </template>
      </EmptyState>

      <template v-else>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead class="w-[100px]">编号</TableHead>
              <TableHead>标题</TableHead>
              <TableHead class="w-[120px]">分类</TableHead>
              <TableHead class="w-[100px]">状态</TableHead>
              <TableHead>治理方案</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow v-for="item in paged" :key="item.id">
              <TableCell class="font-mono text-[11px] text-muted-foreground">{{ item.id }}</TableCell>
              <TableCell class="min-w-[180px] text-[13px] font-medium">{{ item.title }}</TableCell>
              <TableCell>
                <span class="rounded border border-border bg-muted/40 px-1.5 py-0.5 text-[10px] text-muted-foreground">
                  {{ badCaseCategoryLabel(item.category) }}
                </span>
              </TableCell>
              <TableCell><StatusBadge :status="item.status" kind="badcase" /></TableCell>
              <TableCell class="max-w-[420px] whitespace-normal text-xs leading-5 text-muted-foreground">{{ item.note }}</TableCell>
            </TableRow>
          </TableBody>
        </Table>
        <div class="border-t border-border px-4 py-3">
          <Pagination v-model:page="page" :page-size="pageSize" :total="filtered.length" />
        </div>
      </template>
    </Card>

    <Dialog
      v-model:open="addOpen"
      title="记录坏例"
      description="沉淀 Agent 失败案例，便于后续治理与回归验证。"
      width="max-w-lg"
      :close-on-overlay="false"
    >
      <div class="space-y-3.5">
        <label class="block space-y-1.5">
          <span class="text-xs font-medium">标题</span>
          <Input v-model="formTitle" placeholder="例如：新版 Playbook 被错误召回" />
        </label>
        <label class="block space-y-1.5">
          <span class="text-xs font-medium">问题分类</span>
          <Select v-model="formCategory" :options="BAD_CASE_CATEGORIES" />
        </label>
        <label class="block space-y-1.5">
          <span class="text-xs font-medium">治理方案</span>
          <Textarea v-model="formNote" :rows="4" placeholder="描述根因、修复方式与回归验证要求" />
        </label>
      </div>

      <template #footer>
        <Button variant="outline" :disabled="submitting" @click="addOpen = false">取消</Button>
        <Button :loading="submitting" @click="submit">
          <Plus v-if="!submitting" class="h-4 w-4" />
          保存坏例
        </Button>
      </template>
    </Dialog>
  </div>
</template>
