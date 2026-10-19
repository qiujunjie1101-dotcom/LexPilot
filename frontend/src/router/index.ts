import { createRouter, createWebHistory } from 'vue-router';
import Dashboard from '@/pages/Dashboard.vue';
import ContractReview from '@/pages/ContractReview.vue';
import Contracts from '@/pages/Contracts.vue';
import ClauseDiff from '@/pages/ClauseDiff.vue';
import Playbook from '@/pages/Playbook.vue';
import HumanReview from '@/pages/HumanReview.vue';
import TracePage from '@/pages/TracePage.vue';
import Evaluation from '@/pages/Evaluation.vue';
import BadCases from '@/pages/BadCases.vue';

declare module 'vue-router' {
  interface RouteMeta {
    title?: string;
    description?: string;
    group?: string;
  }
}

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior: () => ({ top: 0 }),
  routes: [
    {
      path: '/',
      component: Dashboard,
      meta: { title: '仪表盘', description: '合同审查概览与风险态势', group: '概览' },
    },
    {
      path: '/review',
      component: ContractReview,
      meta: { title: '合同审查', description: '发起 AI 初审并查看风险问题与修改建议', group: '合同工作台' },
    },
    {
      path: '/contracts',
      component: Contracts,
      meta: { title: '合同中心', description: '统一管理合同档案、版本与审查入口', group: '合同工作台' },
    },
    {
      path: '/diff',
      component: ClauseDiff,
      meta: { title: '条款比对', description: '对比标准条款与客户合同，定位风险变化', group: '合同工作台' },
    },
    {
      path: '/playbook',
      component: Playbook,
      meta: { title: '法务手册', description: '检索生效中的审查规则与标准口径', group: '法务协作' },
    },
    {
      path: '/human-review',
      component: HumanReview,
      meta: { title: '人工复核', description: '法务确认高风险条款并完成审核流转', group: '法务协作' },
    },
    {
      path: '/trace',
      component: TracePage,
      meta: { title: '链路追踪', description: '查看 LangGraph 节点执行状态与耗时', group: 'Agent 质量' },
    },
    {
      path: '/evaluation',
      component: Evaluation,
      meta: { title: '效果评估', description: 'Golden Dataset 回归测试与指标分析', group: 'Agent 质量' },
    },
    {
      path: '/bad-cases',
      component: BadCases,
      meta: { title: '坏例中心', description: '沉淀失败案例与治理动作', group: 'Agent 质量' },
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
});

export default router;
