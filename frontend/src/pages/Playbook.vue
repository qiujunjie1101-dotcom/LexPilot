<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { BookOpen, Copy, Library, Search, ShieldCheck, Users } from 'lucide-vue-next';
import { api } from '@/api/client';
import Card from '@/components/ui/card/Card.vue';
import Input from '@/components/ui/input/Input.vue';
import Select from '@/components/ui/select/Select.vue';
import Alert from '@/components/ui/alert/Alert.vue';
import Button from '@/components/ui/button/Button.vue';
import Skeleton from '@/components/ui/skeleton/Skeleton.vue';
import EmptyState from '@/components/ui/empty-state/EmptyState.vue';
import { useToast } from '@/composables/useToast';
import { clauseTypeLabel, contractTypeLabel } from '@/lib/domain';
import type { Playbook } from '@/types/api';

const { pushToast } = useToast();

const playbooks = ref<Playbook[]>([]);
const loading = ref(true);
const errorMessage = ref('');
const search = ref('');
const typeFilter = ref('');
const selectedId = ref('');

async function load() {
  loading.value = true;
  errorMessage.value = '';
  try {
    playbooks.value = await api<Playbook[]>('/api/playbooks');
    if (!selectedId.value && playbooks.value.length) selectedId.value = playbooks.value[0].id;
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '法务手册加载失败';
  } finally {
    loading.value = false;
  }
}

onMounted(load);

const typeOptions = computed(() => {
  const values = Array.from(new Set(playbooks.value.map((item) => item.contract_type)));
  return [
    { value: '', label: '全部合同类型' },
    ...values.map((value) => ({ value, label: contractTypeLabel(value) })),
  ];
});

const filtered = computed(() => {
  const keyword = search.value.trim().toLowerCase();
  return playbooks.value.filter((item) => {
    const matchesType = !typeFilter.value || item.contract_type === typeFilter.value;
    const matchesKeyword =
      !keyword ||
      [item.title, item.content, item.id, item.clause_type]
        .filter(Boolean)
        .some((field) => String(field).toLowerCase().includes(keyword));
    return matchesType && matchesKeyword;
  });
});

const selectedDoc = computed(() => playbooks.value.find((item) => item.id === selectedId.value) || null);

const aclList = computed(() =>
  (selectedDoc.value?.acl_groups || '')
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean),
);

const coverage = computed(() => new Set(playbooks.value.map((item) => item.contract_type)).size);

watch(filtered, (rows) => {
  if (rows.length && !rows.some((item) => item.id === selectedId.value)) {
    selectedId.value = rows[0].id;
  }
});

async function copyContent() {
  if (!selectedDoc.value) return;
  try {
    await navigator.clipboard.writeText(selectedDoc.value.content);
    pushToast('审查口径已复制', { variant: 'success' });
  } catch {
    pushToast('复制失败', { variant: 'error' });
  }
}
</script>

<template>
  <div class="space-y-4">
    <Alert v-if="errorMessage" variant="destructive" title="法务手册加载失败">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <span>{{ errorMessage }}</span>
        <Button size="sm" variant="outline" @click="load">重新加载</Button>
      </div>
    </Alert>

    <div class="flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] text-muted-foreground">
      <span class="flex items-center gap-1.5"><Library class="h-3.5 w-3.5" />共 <span class="font-medium text-foreground">{{ playbooks.length }}</span> 篇生效文档</span>
      <span class="flex items-center gap-1.5"><BookOpen class="h-3.5 w-3.5" />覆盖 <span class="font-medium text-foreground">{{ coverage }}</span> 种合同类型</span>
      <span class="flex items-center gap-1.5"><ShieldCheck class="h-3.5 w-3.5" />仅展示 Active 版本</span>
    </div>

    <div class="grid gap-4 lg:grid-cols-[340px_minmax(0,1fr)]">
      <Card class="flex h-fit flex-col lg:sticky lg:top-[88px]">
        <div class="space-y-2 border-b border-border p-3">
          <div class="relative">
            <Search class="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
            <Input v-model="search" class="pl-8" placeholder="搜索标题、条款或正文" />
          </div>
          <Select v-model="typeFilter" :options="typeOptions" />
        </div>

        <div v-if="loading" class="space-y-2 p-3">
          <Skeleton v-for="index in 5" :key="index" class="h-16 w-full" />
        </div>

        <EmptyState
          v-else-if="!filtered.length"
          compact
          title="没有匹配的文档"
          description="尝试调整关键词或合同类型。"
        />

        <ul v-else class="max-h-[calc(100vh-280px)] divide-y divide-border overflow-y-auto">
          <li v-for="doc in filtered" :key="doc.id">
            <button
              type="button"
              :class="[
                'w-full border-l-2 px-3 py-3 text-left transition-colors',
                selectedId === doc.id
                  ? 'border-l-primary bg-primary/5'
                  : 'border-l-transparent hover:bg-muted/40',
              ]"
              @click="selectedId = doc.id"
            >
              <div class="flex items-start justify-between gap-2">
                <p class="line-clamp-2 text-xs font-medium leading-5">{{ doc.title }}</p>
                <span class="shrink-0 rounded bg-muted px-1 py-0.5 text-[9px] text-muted-foreground">{{ doc.version }}</span>
              </div>
              <div class="mt-1.5 flex flex-wrap items-center gap-1.5">
                <span class="rounded border border-border bg-card px-1 py-0.5 text-[10px] text-muted-foreground">
                  {{ contractTypeLabel(doc.contract_type) }}
                </span>
                <span class="rounded border border-border bg-card px-1 py-0.5 text-[10px] text-muted-foreground">
                  {{ clauseTypeLabel(doc.clause_type) }}
                </span>
              </div>
            </button>
          </li>
        </ul>
      </Card>

      <Card v-if="loading">
        <div class="space-y-3 p-6">
          <Skeleton class="h-6 w-2/3" />
          <Skeleton class="h-4 w-1/3" />
          <Skeleton class="h-40 w-full" />
        </div>
      </Card>

      <Card v-else-if="selectedDoc" class="min-h-[420px]">
        <div class="border-b border-border p-5">
          <div class="flex flex-wrap items-start justify-between gap-3">
            <div class="min-w-0">
              <div class="mb-2 flex flex-wrap items-center gap-1.5">
                <span class="inline-flex items-center gap-1 rounded-md border border-emerald-200 bg-emerald-50 px-1.5 py-0.5 text-[10px] font-medium text-emerald-700 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-300">
                  <span class="h-1.5 w-1.5 rounded-full bg-current" />
                  生效中
                </span>
                <span class="rounded border border-border bg-muted/40 px-1.5 py-0.5 text-[10px] text-muted-foreground">{{ selectedDoc.version }}</span>
                <span class="rounded border border-border bg-muted/40 px-1.5 py-0.5 text-[10px] text-muted-foreground">{{ contractTypeLabel(selectedDoc.contract_type) }}</span>
                <span class="rounded border border-border bg-muted/40 px-1.5 py-0.5 text-[10px] text-muted-foreground">{{ clauseTypeLabel(selectedDoc.clause_type) }}</span>
              </div>
              <h2 class="text-lg font-semibold leading-7">{{ selectedDoc.title }}</h2>
              <p class="mt-1 font-mono text-[10px] text-muted-foreground">{{ selectedDoc.id }}</p>
            </div>
            <Button variant="outline" size="sm" @click="copyContent">
              <Copy class="h-3.5 w-3.5" />
              复制口径
            </Button>
          </div>
        </div>

        <div class="p-5">
          <div class="mb-2 flex items-center gap-1.5 text-[11px] font-medium text-muted-foreground">
            <BookOpen class="h-3.5 w-3.5" />
            审查口径
          </div>
          <div class="max-w-3xl whitespace-pre-wrap text-[13px] leading-7 text-foreground">{{ selectedDoc.content }}</div>

          <div class="mt-6 grid gap-3 border-t border-border pt-4 sm:grid-cols-2">
            <div class="rounded-lg border border-border bg-muted/20 p-3">
              <p class="flex items-center gap-1.5 text-[11px] font-medium text-muted-foreground">
                <Users class="h-3.5 w-3.5" />
                可见范围
              </p>
              <div class="mt-2 flex flex-wrap gap-1.5">
                <span
                  v-for="acl in aclList"
                  :key="acl"
                  class="rounded border border-border bg-card px-1.5 py-0.5 text-[10px] text-muted-foreground"
                >
                  {{ acl }}
                </span>
                <span v-if="!aclList.length" class="text-[11px] text-muted-foreground">未配置</span>
              </div>
            </div>
            <div class="rounded-lg border border-amber-200 bg-amber-50/60 p-3 text-[11px] leading-5 text-amber-800 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-300">
              本手册为内部审查参考，不构成对外法律意见。对外出具结论前需经法务确认。
            </div>
          </div>
        </div>
      </Card>

      <Card v-else class="min-h-[420px]">
        <EmptyState title="选择一篇法务手册" description="从左侧文档列表选择需要阅读的审查口径。" />
      </Card>
    </div>
  </div>
</template>
