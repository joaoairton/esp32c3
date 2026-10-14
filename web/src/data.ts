export type Reservoir = {id:string;name:string;location:string;level:number;capacity:number;current:number;status:'normal'|'warning'|'critical';updatedAt:string};
export type Sample = {time:string;superior:number;inferior:number};
export const reservoirs:Reservoir[]=[
{id:'RES-001',name:'Reservatório Superior',location:'Estação Central · AI1',level:76,capacity:10000,current:16.16,status:'normal',updatedAt:'10:42:08'},
{id:'RES-002',name:'Reservatório Inferior',location:'Estação Central · AI2',level:28,capacity:5000,current:8.48,status:'warning',updatedAt:'10:42:08'},
{id:'RES-003',name:'Reservatório Norte',location:'Unidade Norte · AI1',level:92,capacity:15000,current:18.72,status:'normal',updatedAt:'10:42:04'},
{id:'RES-004',name:'Reservatório Sul',location:'Unidade Sul · AI1',level:14,capacity:8000,current:6.24,status:'critical',updatedAt:'10:41:58'}];
export const samples:Sample[]=Array.from({length:25},(_,i)=>({time:`${String(6+Math.floor(i/4)).padStart(2,'0')}:${String((i%4)*15).padStart(2,'0')}`,superior:Math.round(66+12*Math.sin(i/2.8)+i*.3),inferior:Math.round(43+17*Math.sin(i/3.1+1.4)-i*.45)}));
export const events=[{id:1,level:'critical',title:'Nível crítico detectado',detail:'Reservatório Sul · 14% da capacidade',time:'10:38'},{id:2,level:'warning',title:'Nível abaixo do limite',detail:'Reservatório Inferior · 28% da capacidade',time:'10:21'},{id:3,level:'normal',title:'Comunicação restabelecida',detail:'Dispositivo ECM50-003 · Ethernet',time:'09:56'},{id:4,level:'normal',title:'Sincronização concluída',detail:'Dispositivo ECM50-001 · Dados atualizados',time:'09:32'}] as const;
