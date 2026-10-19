<script setup lang="ts">
import { computed, ref } from 'vue';
import { FileUp } from 'lucide-vue-next';
import Dialog from '@/components/ui/dialog/Dialog.vue';
import Button from '@/components/ui/button/Button.vue';
import Input from '@/components/ui/input/Input.vue';
import Select from '@/components/ui/select/Select.vue';
import Textarea from '@/components/ui/textarea/Textarea.vue';
import { api } from '@/api/client';
import { CONTRACT_TYPES } from '@/lib/domain';
import { useToast } from '@/composables/useToast';
import type { Contract } from '@/types/api';

const props = defineProps<{
  open: boolean;
  contracts: Contract[];
}>();

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void;
  (e: 'imported', contract: Contract): void;
}>();

const { pushToast } = useToast();

const title = ref('');
const contractType = ref('saas');
const amount = ref('');
const parentId = ref('');
const content = ref('');
const submitting = ref(false);

const parentOptions = computed(() => [
  { value: '', label: '不关联父版本' },
  ...props.contracts.map((contract) => ({
    value: contract.id,
    label: `${contract.title} · ${contract.version}`,
  })),
]);

function reset() {
  title.value = '';
  contractType.value = 'saas';
  amount.value = '';
  parentId.value = '';
  content.value = '';
}

async function submit() {
  if (!title.value.trim()) {
    pushToast('请填写合同名称', { variant: 'warning' });
    return;
  }
  if (content.value.trim().length < 20) {
    pushToast('合同正文至少需要 20 个字符', { variant: 'warning' });
    return;
  }
  submitting.value = true;
  try {
    const contract = await api<Contract>('/api/contracts/import', {
      method: 'POST',
      body: JSON.stringify({
        title: title.value.trim(),
        contract_type: contractType.value,
        content: content.value,
        amount: amount.value ? Number(amount.value) : null,
        parent_contract_id: parentId.value || null,
      }),
    });
    pushToast('合同导入成功', { description: `${contract.title} · ${contract.version}`, variant: 'success' });
    emit('imported', contract);
    emit('update:open', false);
    reset();
  } catch (error) {
    pushToast('合同导入失败', {
      description: error instanceof Error ? error.message : '请检查接口与网络状态',
      variant: 'error',
    });
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <Dialog
    :open="props.open"
    title="导入合同"
    description="粘贴合同正文并按 [payment] 等标签分段，系统会自动解析条款结构。"
    width="max-w-2xl"
    :close-on-overlay="false"
    @update:open="emit('update:open', $event)"
  >
    <div class="space-y-3.5">
      <div class="grid gap-3 sm:grid-cols-2">
        <label class="space-y-1.5">
          <span class="text-xs font-medium">合同名称</span>
          <Input v-model="title" placeholder="例如：华东客户 SaaS 服务合同" />
        </label>
        <label class="space-y-1.5">
          <span class="text-xs font-medium">合同类型</span>
          <Select v-model="contractType" :options="CONTRACT_TYPES" />
        </label>
        <label class="space-y-1.5">
          <span class="text-xs font-medium">合同金额（元）</span>
          <Input v-model="amount" type="number" placeholder="例如 1200000" />
        </label>
        <label class="space-y-1.5">
          <span class="text-xs font-medium">关联父版本</span>
          <Select v-model="parentId" :options="parentOptions" />
        </label>
      </div>

      <label class="block space-y-1.5">
        <span class="text-xs font-medium">合同正文</span>
        <Textarea
          v-model="content"
          :rows="10"
          placeholder="[payment] 甲方在收到发票后 90 日内完成付款。&#10;[liability] 乙方承担无限责任。&#10;[ip] 项目成果及源代码全部归甲方所有。&#10;[renewal] 合同到期自动续约 12 个月。"
        />
      </label>

      <div class="rounded-md border border-border bg-muted/30 px-3 py-2.5 text-[11px] leading-5 text-muted-foreground">
        支持条款标签：<code class="text-foreground">[payment]</code>、<code class="text-foreground">[liability]</code>、<code class="text-foreground">[ip]</code>、<code class="text-foreground">[renewal]</code>、<code class="text-foreground">[termination]</code>、<code class="text-foreground">[jurisdiction]</code>。未识别到标签时，将整段正文作为付款条款导入。
      </div>
    </div>

    <template #footer>
      <Button variant="outline" :disabled="submitting" @click="emit('update:open', false)">取消</Button>
      <Button :loading="submitting" @click="submit">
        <FileUp v-if="!submitting" class="h-4 w-4" />
        导入合同
      </Button>
    </template>
  </Dialog>
</template>
