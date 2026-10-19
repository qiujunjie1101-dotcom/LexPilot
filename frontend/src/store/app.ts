import { ref } from 'vue';

export type AppRole = 'sales' | 'legal';

const role = ref<AppRole>((localStorage.getItem('legal-role') as AppRole) || 'sales');

const storedCollapsed = localStorage.getItem('legal-sidebar-collapsed');
const sidebarCollapsed = ref<boolean>(
  storedCollapsed === null ? window.innerWidth < 1360 : storedCollapsed === '1',
);

export function useAppStore() {
  const setRole = (next: AppRole) => {
    localStorage.setItem('legal-role', next);
    role.value = next;
  };

  const setSidebarCollapsed = (value: boolean) => {
    sidebarCollapsed.value = value;
    localStorage.setItem('legal-sidebar-collapsed', value ? '1' : '0');
  };

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed.value);
  };

  return { role, setRole, sidebarCollapsed, setSidebarCollapsed, toggleSidebar };
}
