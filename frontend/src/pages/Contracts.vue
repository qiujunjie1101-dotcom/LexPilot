<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import {
  FileSearch,
  FileText,
  FileUp,
  RefreshCw,
  RotateCcw,
  Search,
} from 'lucide-vue-next';
import { api } from '@/api/client';
import Card from '@/components/ui/card/Card.vue';
import Button from '@/components/ui/button/Button.vue';
import Input from '@/components/ui/input/Input.vue';
import Select from '@/components/ui/select/Select.vue';
import Alert from '@/components/ui/alert/Alert.vue';
import Skeleton from '@/components/ui/skeleton/Skeleton.vue';
import EmptyState from '@/components/ui/empty-state/EmptyState.vue';
import Pagination from '@/components/ui/pagination/Pagination.vue';
import Dialog from '@/components/ui/dialog/Dialog.vue';
import Table from '@/components/ui/table/Table.vue';
import TableHeader from '@/components/ui/table/TableHeader.vue';
import TableBody from '@/components/ui/table/TableBody.vue';
import TableRow from '@/components/ui/table/TableRow.vue';
import TableHead from '@/components/ui/table/TableHead.vue';
import TableCell from '@/components/ui/table/TableCell.vue';
import StatusBadge from '@/components/business/StatusBadge.vue';
import ContractImportDialog from '@/components/business/ContractImportDialog.vue';
import { CONTRACT_TYPES, clauseTypeLabel, contractTypeLabel, fieldLabel, formatFieldValue } from '@/lib/domain';
import { formatAmount, formatDateTime } from '@/lib/format';
import type { Contract, ContractDetail } from '@/types/api';

const router = useRouter();

const contracts = ref<Contract[]>([]);
const loading = ref(true);
const errorMessage = ref('');
const search = ref('');
const typeFilter = ref('');
const statusFilter = ref('');
const page = ref(1);
const pageSize = 10;
const importOpen = ref(false);

const detailOpen = ref(false);
const detailLoading = ref(false);
const detail = ref<ContractDetail | null>(null);

const typeOptions = [{ value: '', label: '全部类型' }, ...CONTRACT_TYPES];
const statusOptions = [
  { value: '', label: '全部状态' },
  { value: 'active', label: '生效中' },
  { value: 'draft', label: '草稿' },
  { value: 'archived', label: '已归档' },
];

async function load() {
  loading.value = true;
  errorMessage.value = '';
  try {
    const rows = await api<Contract[]>('/api/contracts');
    contracts.value = [...rows].sort((a, b) => b.created_at.localeCompare(a.created_at));
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '合同列表加载失败';
  } finally {
    loading.value = false;
  }
}

onMounted(load);

const filtered = computed(() => {
  const keyword = search.value.trim().toLowerCase();
  return contracts.value.filter((contract) => {
    const matchesKeyword =
      !keyword ||
      [contract.title, contract.id, contract.department_id, contract.owner_user_id, contract.version]
        .filter(Boolean)
        .some((field) => String(field).toLowerCase().includes(keyword));
    const matchesType = !typeFilter.value || contract.contract_type === typeFilter.value;
    const matchesStatus = !statusFilter.value || contract.status === statusFilter.value;
    return matchesKeyword && matchesType && matchesStatus;
  });
});

const paged = computed(() => filtered.value.slice((page.value - 1) * pageSize, page.value * pageSize));

const activeCount = computed(() => contracts.value.filter((contract) => contract.status === 'active').length);
const versionChainCount = computed(() => contracts.value.filter((contract) => contract.parent_contract_id).length);

const detailMeta = computed(() => {
  if (!detail.value) return [];
  return [
    { label: '合同类型', value: contractTypeLabel(detail.value.contract_type) },
    { label: '当前版本', value: detail.value.version },
    { label: '合同状态', value: detail.value.status },
    { label: '合同金额', value: formatAmount(detail.value.amount) },
    { label: '所属部门', value: detail.value.department_id },
    { label: '负责人', value: detail.value.owner_user_id },
    { label: '父版本', value: detail.value.parent_contract_id || '无' },
    { label: '创建时间', value: formatDateTime(detail.value.created_at) },
  ];
});

watch([search, typeFilter, statusFilter], () => {
  page.value = 1;
});

watch(filtered, (rows) => {
  const maxPage = Math.max(1, Math.ceil(rows.length / pageSize));
  if (page.value > maxPage) page.value = maxPage;
});

async function openDetail(contract: Contract) {
  detailOpen.value = true;
  detailLoading.value = true;
  detail.value = null;
  try {
    detail.value = await api<ContractDetail>(`/api/contracts/${contract.id}`);
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '合同详情加载失败';
    detailOpen.value = false;
  } finally {
    detailLoading.value = false;
  }
}

function resetFilters() {
  search.value = '';
  typeFilter.value = '';
  statusFilter.value = '';
}

function goReview(contract: Contract) {
  detailOpen.value = false;
  router.push({ path: '/review', query: { contract: contract.id } });
}

function onImported() {
  load();
}
</script>

<template>
  <div class="space-y-4">
    <Alert v-if="errorMessage" variant="destructive" title="合同数据异常">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <span>{{ errorMessage }}</span>
        <Button size="sm" variant="outline" @click="load">重新加载</Button>
      </div>
    </Alert>

    <Card>
      <div class="space-y-3 p-4">
        <div class="flex flex-col gap-2 lg:flex-row lg:items-center lg:justify-between">
          <div class="flex flex-1 flex-col gap-2 sm:flex-row sm:items-center">
            <div class="relative min-w-0 flex-1 sm:max-w-xs">
              <Search class="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
              <Input v-model="search" class="pl-8" placeholder="搜索合同名称、编号、部门" />
            </div>
            <Select v-model="typeFilter" :options="typeOptions" class="sm:w-[140px]" />
            <Select v-model="statusFilter" :options="statusOptions" class="sm:w-[130px]" />
            <button
              type="button"
              class="inline-flex h-9 items-center gap-1 rounded-md px-2 text-xs text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
              @click="resetFilters"
            >
              <RotateCcw class="h-3.5 w-3.5" />
              重置
            </button>
          </div>
          <div class="flex shrink-0 items-center gap-2">
            <Button variant="outline" size="sm" :disabled="loading" @click="load">
              <RefreshCw :class="['h-4 w-4', loading ? 'animate-spin' : '']" />
              刷新
            </Button>
            <Button size="sm" @click="importOpen = true">
              <FileUp class="h-4 w-4" />
              导入合同
            </Button>
          </div>
        </div>
        <div class="flex flex-wrap items-center gap-x-4 gap-y-1 border-t border-border pt-2.5 text-[11px] text-muted-foreground">
          <span>共 <span class="font-medium text-foreground">{{ contracts.length }}</span> 份合同</span>
          <span>生效中 <span class="font-medium text-emerald-600 dark:text-emerald-400">{{ activeCount }}</span></span>
          <span>版本链合同 <span class="font-medium text-foreground">{{ versionChainCount }}</span></span>
          <span>筛选结果 <span class="font-medium text-foreground">{{ filtered.length }}</span></span>
        </div>
      </div>
    </Card>

    <Card>
      <div v-if="loading" class="space-y-2 p-4">
        <Skeleton v-for="index in 8" :key="index" class="h-10 w-full" />
      </div>

      <EmptyState
        v-else-if="!contracts.length"
        title="暂无合同档案"
        description="导入合同后即可发起 AI 审查、条款比对与版本追踪。"
      >
        <template #icon><FileText class="h-5 w-5" /></template>
        <template #action>
          <Button size="sm" @click="importOpen = true">
            <FileUp class="h-4 w-4" />
            导入合同
          </Button>
        </template>
      </EmptyState>

      <EmptyState
        v-else-if="!filtered.length"
        title="没有匹配的合同"
        description="尝试调整搜索关键词或筛选条件。"
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
              <TableHead>合同</TableHead>
              <TableHead class="w-[110px]">类型</TableHead>
              <TableHead class="w-[90px]">版本</TableHead>
              <TableHead class="w-[110px]">所属部门</TableHead>
              <TableHead class="w-[130px]">金额</TableHead>
              <TableHead class="w-[100px]">状态</TableHead>
              <TableHead class="w-[140px]">创建时间</TableHead>
              <TableHead class="w-[130px] text-right">操作</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow v-for="contract in paged" :key="contract.id" class="cursor-pointer" @click="openDetail(contract)">
              <TableCell>
                <div class="flex min-w-0 items-center gap-2.5">
                  <span class="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-primary/10 text-primary">
                    <FileText class="h-3.5 w-3.5" />
                  </span>
                  <div class="min-w-0">
                    <p class="truncate text-[13px] font-medium">{{ contract.title }}</p>
                    <p class="mt-0.5 truncate font-mono text-[10px] text-muted-foreground">{{ contract.id }}</p>
                  </div>
                </div>
              </TableCell>
              <TableCell class="text-xs text-muted-foreground">{{ contractTypeLabel(contract.contract_type) }}</TableCell>
              <TableCell>
                <span class="rounded border border-border bg-muted/40 px-1.5 py-0.5 text-[11px]">{{ contract.version }}</span>
                <p v-if="contract.parent_contract_id" class="mt-1 truncate font-mono text-[9px] text-muted-foreground">
                  {{ contract.parent_contract_id }}
                </p>
              </TableCell>
              <TableCell class="text-xs text-muted-foreground">{{ contract.department_id }}</TableCell>
              <TableCell class="whitespace-nowrap text-xs tabular-nums">{{ formatAmount(contract.amount) }}</TableCell>
              <TableCell><StatusBadge :status="contract.status" kind="contract" /></TableCell>
              <TableCell class="whitespace-nowrap text-xs text-muted-foreground">{{ formatDateTime(contract.created_at) }}</TableCell>
              <TableCell class="text-right">
                <div class="flex items-center justify-end gap-1">
                  <Button variant="ghost" size="xs" @click.stop="openDetail(contract)">查看</Button>
                  <Button variant="outline" size="xs" @click.stop="goReview(contract)">
                    <FileSearch class="h-3 w-3" />
                    审查
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
        <div class="border-t border-border px-4 py-3">
          <Pagination v-model:page="page" :page-size="pageSize" :total="filtered.length" />
        </div>
      </template>
    </Card>

    <ContractImportDialog v-model:open="importOpen" :contracts="contracts" @imported="onImported" />

    <Dialog
      v-model:open="detailOpen"
      :title="detail?.title || '合同详情'"
      :description="detail ? `${detail.id} · ${detail.version}` : '加载合同档案与条款结构'"
      width="max-w-3xl"
    >
      <div v-if="detailLoading" class="space-y-2">
        <Skeleton class="h-20 w-full" />
        <Skeleton class="h-40 w-full" />
      </div>
      <div v-else-if="detail" class="space-y-4">
        <div class="grid grid-cols-2 gap-px overflow-hidden rounded-lg border border-border bg-border sm:grid-cols-4">
          <div v-for="meta in detailMeta" :key="meta.label" class="bg-card px-3 py-2.5">
            <p class="text-[10px] text-muted-foreground">{{ meta.label }}</p>
            <p class="mt-0.5 truncate text-xs font-medium" :title="meta.value">{{ meta.value }}</p>
          </div>
        </div>

        <section>
          <h3 class="mb-2 text-[13px] font-semibold">合同正文</h3>
          <div class="max-h-48 overflow-y-auto whitespace-pre-wrap rounded-lg border border-border bg-muted/20 p-3 text-xs leading-6 text-muted-foreground">
            {{ detail.content || '暂无正文内容' }}
          </div>
        </section>

        <section>
          <div class="mb-2 flex items-center justify-between">
            <h3 class="text-[13px] font-semibold">条款结构</h3>
            <span class="text-[11px] text-muted-foreground">{{ detail.clauses.length }} 个条款</span>
          </div>
          <div v-if="detail.clauses.length" class="space-y-2">
            <details v-for="clause in detail.clauses" :key="clause.id" class="group rounded-lg border border-border bg-card">
              <summary class="flex cursor-pointer list-none items-center justify-between gap-2 px-3 py-2.5">
                <div class="flex items-center gap-2">
                  <span class="rounded border border-border bg-muted/40 px-1.5 py-0.5 text-[10px] text-muted-foreground">
                    {{ clauseTypeLabel(clause.clause_type) }}
                  </span>
                  <span class="text-xs font-medium">{{ clause.title || clauseTypeLabel(clause.clause_type) }}</span>
                </div>
                <span class="text-[10px] text-muted-foreground group-open:hidden">展开</span>
                <span class="hidden text-[10px] text-muted-foreground group-open:inline">收起</span>
              </summary>
              <div class="border-t border-border px-3 py-2.5">
                <p class="whitespace-pre-wrap text-xs leading-5 text-muted-foreground">{{ clause.content }}</p>
                <div v-if="Object.keys(clause.normalized || {}).length" class="mt-2 flex flex-wrap gap-1.5">
                  <span
                    v-for="(value, key) in clause.normalized"
                    :key="key"
                    class="rounded border border-border bg-muted/30 px-1.5 py-0.5 text-[10px] text-muted-foreground"
                  >
                    {{ fieldLabel(String(key)) }}：{{ formatFieldValue(String(key), value) }}
                  </span>
                </div>
              </div>
            </details>
          </div>
          <EmptyState v-else compact title="暂无条款结构" description="该合同尚未解析出结构化条款。" />
        </section>
      </div>

      <template #footer>
        <Button variant="outline" @click="detailOpen = false">关闭</Button>
        <Button v-if="detail" @click="goReview(detail)">
          <FileSearch class="h-4 w-4" />
          发起审查
        </Button>
      </template>
    </Dialog>
  </div>
</template>
