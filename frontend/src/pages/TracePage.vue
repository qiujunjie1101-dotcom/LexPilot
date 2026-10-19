<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Clock3,
  Copy,
  GitBranch,
  Search,
  Workflow,
} from 'lucide-vue-next';
import { api } from '@/api/client';
import Card from '@/components/ui/card/Card.vue';
import Button from '@/components/ui/button/Button.vue';
import Input from '@/components/ui/input/Input.vue';
import Select from '@/components/ui/select/Select.vue';
import Alert from '@/components/ui/alert/Alert.vue';
import Skeleton from '@/components/ui/skeleton/Skeleton.vue';
import EmptyState from '@/components/ui/empty-state/EmptyState.vue';
import Tabs from '@/components/ui/tabs/Tabs.vue';
import { useToast } from '@/composables/useToast';
import { TRACE_NODE_LABELS, TRACE_NODE_ORDER, traceNodeLabel } from '@/lib/domain';
import { formatDateTime, formatDuration } from '@/lib/format';
import type { ReviewRecord, TraceEvent } from '@/types/api';

const route = useRoute();
const { pushToast } = useToast();

const traceId = ref('');
const recentTrace = ref('');
const events = ref<TraceEvent[]>([]);
const recentReviews = ref<ReviewRecord[]>([]);
const loading = ref(false);
const loadingRecent = ref(true);
const errorMessage = ref('');
const hasLoaded = ref(false);
const activeNode = ref('all');

function hasError(detail: Record<string, unknown> | undefined): boolean {
  if (!detail) return false;
  return Boolean(detail.error || detail.errors || detail.status === 'error' || detail.status === 'failed');
}

function errorText(detail: Record<string, unknown> | undefined): string {
  if (!detail) return '';
  const value = detail.error || detail.message || detail.reason;
  return value ? String(value) : '节点执行失败';
}

const recentOptions = computed(() => [
  { value: '', label: '选择最近审查记录' },
  ...recentReviews.value.slice(0, 20).map((review, index) => ({
    value: review.trace_id,
    label: `${index + 1}. ${review.summary?.title || review.contract_id} · ${formatDateTime(review.created_at)}`,
  })),
]);

const nodeStats = computed(() =>
  TRACE_NODE_ORDER.map((node) => {
    const nodeEvents = events.value.filter((event) => event.node === node);
    return {
      node,
      label: TRACE_NODE_LABELS[node] || node,
      count: nodeEvents.length,
      latency: nodeEvents.reduce((sum, event) => sum + (event.latency_ms || 0), 0),
      errors: nodeEvents.filter((event) => hasError(event.detail)).length,
      executed: nodeEvents.length > 0,
    };
  }),
);

const errorCount = computed(() => events.value.filter((event) => hasError(event.detail)).length);
const totalLatency = computed(() => events.value.reduce((sum, event) => sum + (event.latency_ms || 0), 0));
const slowest = computed(() => {
  const executed = nodeStats.value.filter((item) => item.executed);
  if (!executed.length) return null;
  return executed.reduce((slowestNode, current) => (current.latency > slowestNode.latency ? current : slowestNode));
});

const tabItems = computed(() => [
  { value: 'all', label: '全部节点', count: events.value.length },
  ...nodeStats.value.map((item) => ({ value: item.node, label: item.label, count: item.count })),
]);

const filteredEvents = computed(() =>
  activeNode.value === 'all' ? events.value : events.value.filter((event) => event.node === activeNode.value),
);

watch(activeNode, (value) => {
  if (value !== 'all' && !events.value.some((event) => event.node === value)) {
    activeNode.value = 'all';
  }
});

watch(recentTrace, (value) => {
  if (!value) return;
  traceId.value = value;
  loadTrace();
});

async function loadRecent() {
  loadingRecent.value = true;
  try {
    recentReviews.value = await api<ReviewRecord[]>('/api/reviews');
  } catch {
    recentReviews.value = [];
  } finally {
    loadingRecent.value = false;
  }
}

async function loadTrace() {
  const id = traceId.value.trim();
  if (!id) {
    pushToast('请输入 Trace ID', { variant: 'warning' });
    return;
  }
  loading.value = true;
  errorMessage.value = '';
  hasLoaded.value = true;
  activeNode.value = 'all';
  try {
    events.value = await api<TraceEvent[]>(`/api/traces/${encodeURIComponent(id)}`);
  } catch (error) {
    events.value = [];
    errorMessage.value = error instanceof Error ? error.message : '链路加载失败';
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  await loadRecent();
  const queryTrace = typeof route.query.trace_id === 'string' ? route.query.trace_id : '';
  if (queryTrace) {
    traceId.value = queryTrace;
    loadTrace();
  }
});

function latencyClass(ms: number): string {
  if (ms >= 1500) return 'border-red-200 bg-red-50 text-red-700 dark:border-red-500/30 dark:bg-red-500/10 dark:text-red-300';
  if (ms >= 500) return 'border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-300';
  return 'border-border bg-muted/40 text-muted-foreground';
}

async function copyTraceId() {
  if (!traceId.value) return;
  try {
    await navigator.clipboard.writeText(traceId.value);
    pushToast('Trace ID 已复制', { variant: 'success' });
  } catch {
    pushToast('复制失败', { variant: 'error' });
  }
}
</script>

<template>
  <div class="space-y-4">
    <Card>
      <div class="flex flex-col gap-3 p-4 lg:flex-row lg:items-center lg:justify-between">
        <div class="flex min-w-0 flex-1 flex-col gap-2 sm:flex-row sm:items-center">
          <div class="relative min-w-0 flex-1 sm:max-w-md">
            <GitBranch class="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
            <Input v-model="traceId" class="pl-8 font-mono text-xs" placeholder="粘贴 trace_id，例如 trace-1a2b3c4d5e6f" @keyup.enter="loadTrace" />
          </div>
          <div class="sm:w-[300px]">
            <Skeleton v-if="loadingRecent" class="h-9 w-full" />
            <Select v-else v-model="recentTrace" :options="recentOptions" class="text-xs" />
          </div>
        </div>
        <div class="flex shrink-0 items-center justify-end gap-2">
          <Button variant="outline" size="sm" :disabled="!traceId" @click="copyTraceId">
            <Copy class="h-4 w-4" />
            复制
          </Button>
          <Button size="sm" :loading="loading" @click="loadTrace">
            <Search v-if="!loading" class="h-4 w-4" />
            加载链路
          </Button>
        </div>
      </div>
    </Card>

    <Alert v-if="errorMessage" variant="destructive" title="链路加载失败">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <span>{{ errorMessage }}</span>
        <Button size="sm" variant="outline" @click="loadTrace">重试</Button>
      </div>
    </Alert>

    <template v-if="hasLoaded && !errorMessage">
      <div v-if="loading" class="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
        <Skeleton v-for="index in 5" :key="index" class="h-24 w-full" />
      </div>

      <template v-else-if="events.length">
        <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
          <button
            v-for="(item, index) in nodeStats"
            :key="item.node"
            type="button"
            :class="[
              'rounded-xl border p-3.5 text-left transition-colors',
              activeNode === item.node ? 'border-primary/40 bg-primary/[0.04]' : 'border-border bg-card hover:border-primary/25',
              !item.executed && 'opacity-60',
            ]"
            @click="activeNode = activeNode === item.node ? 'all' : item.node"
          >
            <div class="flex items-center justify-between gap-2">
              <span class="text-[10px] font-medium text-muted-foreground">STEP {{ index + 1 }}</span>
              <span
                v-if="item.executed"
                :class="[
                  'flex h-4 w-4 items-center justify-center rounded-full',
                  item.errors ? 'bg-red-500/15 text-red-600' : 'bg-emerald-500/15 text-emerald-600',
                ]"
              >
                <AlertTriangle v-if="item.errors" class="h-2.5 w-2.5" />
                <CheckCircle2 v-else class="h-2.5 w-2.5" />
              </span>
              <span v-else class="rounded bg-muted px-1 py-0.5 text-[9px] text-muted-foreground">未执行</span>
            </div>
            <p class="mt-1.5 text-xs font-semibold leading-5">{{ item.label }}</p>
            <p class="mt-0.5 truncate font-mono text-[9px] text-muted-foreground">{{ item.node }}</p>
            <div class="mt-2 flex items-center gap-2 text-[10px] text-muted-foreground">
              <span>{{ item.count }} 事件</span>
              <span>·</span>
              <span :class="item.errors ? 'text-red-600' : ''">{{ formatDuration(item.latency) }}</span>
            </div>
          </button>
        </div>

        <Card class="overflow-hidden">
          <div class="grid gap-px bg-border sm:grid-cols-2 xl:grid-cols-4">
            <div class="bg-card p-4">
              <p class="flex items-center gap-1.5 text-[11px] text-muted-foreground"><Activity class="h-3.5 w-3.5" />执行事件</p>
              <p class="mt-1.5 text-xl font-semibold tabular-nums">{{ events.length }}</p>
              <p class="mt-0.5 text-[10px] text-muted-foreground">{{ nodeStats.filter((item) => item.executed).length }} / 5 个节点已执行</p>
            </div>
            <div class="bg-card p-4">
              <p class="flex items-center gap-1.5 text-[11px] text-muted-foreground"><Clock3 class="h-3.5 w-3.5" />累计耗时</p>
              <p class="mt-1.5 text-xl font-semibold tabular-nums">{{ formatDuration(totalLatency) }}</p>
              <p class="mt-0.5 text-[10px] text-muted-foreground">各节点耗时之和</p>
            </div>
            <div class="bg-card p-4">
              <p class="flex items-center gap-1.5 text-[11px] text-muted-foreground"><Workflow class="h-3.5 w-3.5" />最慢节点</p>
              <p class="mt-1.5 truncate text-sm font-semibold">{{ slowest?.label || '—' }}</p>
              <p class="mt-0.5 text-[10px] text-muted-foreground">{{ slowest ? formatDuration(slowest.latency) : '暂无执行记录' }}</p>
            </div>
            <div class="bg-card p-4">
              <p class="flex items-center gap-1.5 text-[11px] text-muted-foreground"><AlertTriangle class="h-3.5 w-3.5" />异常事件</p>
              <p :class="['mt-1.5 text-xl font-semibold tabular-nums', errorCount ? 'text-red-600 dark:text-red-400' : '']">{{ errorCount }}</p>
              <p class="mt-0.5 text-[10px] text-muted-foreground">{{ errorCount ? '请展开事件详情排查' : '未发现节点异常' }}</p>
            </div>
          </div>
          <div class="flex flex-wrap items-center gap-2 border-t border-border bg-muted/20 px-4 py-2.5">
            <span class="text-[11px] text-muted-foreground">Trace</span>
            <span class="truncate font-mono text-[11px]">{{ traceId }}</span>
            <span class="ml-auto text-[10px] text-muted-foreground">最近事件 {{ formatDateTime(events[events.length - 1]?.created_at) }}</span>
          </div>
        </Card>

        <div class="flex items-center justify-between gap-2">
          <Tabs v-model="activeNode" :items="tabItems" />
          <span class="hidden text-[11px] text-muted-foreground sm:block">点击节点卡片也可筛选</span>
        </div>

        <Card>
          <div v-if="filteredEvents.length" class="p-5">
            <ol class="relative space-y-0 border-l border-border pl-5">
              <li
                v-for="event in filteredEvents"
                :key="event.id"
                :class="['relative pb-5 last:pb-0']"
              >
                <span
                  :class="[
                    'absolute -left-[25px] top-1.5 flex h-3 w-3 items-center justify-center rounded-full border-2 border-background',
                    hasError(event.detail) ? 'bg-red-500' : 'bg-primary',
                  ]"
                />
                <div class="flex flex-wrap items-center gap-2">
                  <p class="text-[13px] font-medium">{{ traceNodeLabel(event.node) }}</p>
                  <span class="rounded bg-muted px-1.5 py-0.5 font-mono text-[9px] text-muted-foreground">{{ event.node }}</span>
                  <span :class="['rounded border px-1.5 py-0.5 text-[10px] tabular-nums', latencyClass(event.latency_ms)]">
                    {{ formatDuration(event.latency_ms) }}
                  </span>
                  <span class="ml-auto text-[10px] text-muted-foreground">{{ formatDateTime(event.created_at) }}</span>
                </div>
                <div v-if="hasError(event.detail)" class="mt-2 rounded-md border border-red-200 bg-red-50 px-2.5 py-1.5 text-[11px] text-red-700 dark:border-red-500/30 dark:bg-red-500/10 dark:text-red-300">
                  {{ errorText(event.detail) }}
                </div>
                <details class="group mt-2">
                  <summary class="inline-flex cursor-pointer list-none items-center gap-1 text-[11px] text-muted-foreground hover:text-foreground">
                    查看事件详情
                  </summary>
                  <pre class="mono mt-1.5">{{ JSON.stringify(event.detail, null, 2) }}</pre>
                </details>
              </li>
            </ol>
          </div>
          <EmptyState v-else compact title="当前节点暂无事件" description="请切换其他节点或选择「全部节点」查看完整链路。" />
        </Card>
      </template>

      <Card v-else>
        <EmptyState
          title="没有找到链路事件"
          description="该 Trace ID 暂无执行记录，请确认 ID 是否正确，或从最近审查记录中选择。"
        >
          <template #icon><GitBranch class="h-5 w-5" /></template>
        </EmptyState>
      </Card>
    </template>

    <Card v-else-if="!loadingRecent">
      <EmptyState
        title="输入 Trace ID 查看 Agent 执行链路"
        description="支持粘贴审查返回的 trace_id，或从最近审查记录中快速选择。"
      >
        <template #icon><Workflow class="h-5 w-5" /></template>
        <template #action>
          <Button variant="outline" size="sm" :disabled="!recentReviews.length" @click="recentTrace = recentReviews[0]?.trace_id || ''">
            <GitBranch class="h-4 w-4" />
            加载最近一次审查
          </Button>
        </template>
      </EmptyState>
    </Card>
  </div>
</template>
