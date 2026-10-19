import { create } from 'zustand';
type AppState={role:'sales'|'legal';setRole:(role:'sales'|'legal')=>void};
export const useAppStore=create<AppState>((set)=>({role:(localStorage.getItem('legal-role') as 'sales'|'legal')||'sales',setRole:(role)=>{localStorage.setItem('legal-role',role);set({role});window.location.reload();}}));
