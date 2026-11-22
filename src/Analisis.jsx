import React,{useEffect,useState}from "react";
import {Activity,CalendarDays,CheckCircle2,CircleDollarSign,XCircle}from "lucide-react";
import {Bar,BarChart,CartesianGrid,Cell,ComposedChart,Line,Pie,PieChart,ResponsiveContainer,Tooltip,XAxis,YAxis}from "recharts";
import {api}from "./services/api";

const colores=["#176bdb","#16bfc4","#ff766b","#805ed4","#f0ad3d"];
const sinFiltros={especie:"",servicio:"",mes:""};
const filasPorPagina=50;

function Tarjeta({titulo,valor,Icono}){return <article className="stat-card"><div className="stat-top"><span>{titulo}</span><div className="stat-icon stat-0"><Icono size={18}/></div></div><div className="stat-value">{valor}</div></article>}
function Filtro({etiqueta,valor,opciones,cambiar}){return <label className="filtro">{etiqueta}<select value={valor} onChange={e=>cambiar(e.target.value)}><option value="">Todos</option>{opciones.map(o=><option key={o.valor} value={o.valor}>{o.nombre}</option>)}</select></label>}
function TooltipCaja({active,payload}){if(!active||!payload?.length)return null;const d=payload[0].payload;return <div className="tooltip-caja"><b>{d.servicio}</b><br/>Mínimo: S/ {d.minimo}<br/>Q1: S/ {d.q1}<br/>Mediana: S/ {d.mediana}<br/>Q3: S/ {d.q3}<br/>Máximo: S/ {d.maximo}<br/>Citas: {d.citas}</div>}

export default function Analisis(){
  const[opciones,setOpciones]=useState({especies:[],servicios:[],meses:[]}),[filtros,setFiltros]=useState(sinFiltros),[datos,setDatos]=useState(),[error,setError]=useState(""),[visibles,setVisibles]=useState(filasPorPagina);
  useEffect(()=>{api.get("/analisis/opciones").then(x=>setOpciones(x.data)).catch(e=>setError(e.message))},[]);
  useEffect(()=>{
    const consulta=new URLSearchParams(Object.entries(filtros).filter(([,v])=>v)).toString();
    api.get("/analisis"+(consulta?"?"+consulta:"")).then(x=>{setDatos(x.data);setError("");setVisibles(filasPorPagina)}).catch(e=>setError(e.message));
  },[filtros]);
  const cambiar=campo=>valor=>setFiltros(f=>({...f,[campo]:valor}));
  const k=datos?.kpis||{};
  const precio=datos?.estadisticas_precio||{};
  const limpieza=datos?.limpieza;
  const cajas=(datos?.boxplot_precio||[]).map(x=>({...x,base:x.q1,caja_baja:+(x.mediana-x.q1).toFixed(2),caja_alta:+(x.q3-x.mediana).toFixed(2)}));
  const tabla=datos?.tabla||[];
  const ver=v=>v??"—";
  return <div className="page-content">
    <div className="welcome-row"><div><div className="eyebrow">ANÁLISIS DE DATOS</div><h1>Análisis de la clínica</h1><p className="subheading">Todos los cálculos se hacen en Python con pandas y numpy.</p></div></div>
    {error&&<div className="api-warning">No se pudo cargar el análisis: {error}</div>}
    <section className="stats-grid stats-cinco">
      <Tarjeta titulo="Citas" valor={datos?k.total:"—"} Icono={CalendarDays}/>
      <Tarjeta titulo="Pendientes" valor={datos?k.pendientes:"—"} Icono={Activity}/>
      <Tarjeta titulo="Completadas" valor={datos?k.completadas:"—"} Icono={CheckCircle2}/>
      <Tarjeta titulo="Canceladas" valor={datos?k.canceladas:"—"} Icono={XCircle}/>
      <Tarjeta titulo="Ingresos (S/)" valor={datos?Number(k.ingresos).toLocaleString("es-PE"):"—"} Icono={CircleDollarSign}/>
    </section>
    <section className="panel filtros-panel">
      <Filtro etiqueta="Especie" valor={filtros.especie} opciones={opciones.especies.map(e=>({valor:e,nombre:e}))} cambiar={cambiar("especie")}/>
      <Filtro etiqueta="Servicio" valor={filtros.servicio} opciones={opciones.servicios.map(s=>({valor:s,nombre:s}))} cambiar={cambiar("servicio")}/>
      <Filtro etiqueta="Mes" valor={filtros.mes} opciones={opciones.meses.map(m=>({valor:m.valor,nombre:m.nombre}))} cambiar={cambiar("mes")}/>
      <button className="filter-btn" onClick={()=>setFiltros(sinFiltros)}>Limpiar filtros</button>
    </section>
    <section className="dashboard-charts">
      <article className="panel chart-panel"><div className="panel-heading"><div><h2>Citas por mes</h2><p>Tendencia durante el año</p></div></div><div className="rechart-box"><ResponsiveContainer width="100%" height="100%"><BarChart data={datos?.citas_por_mes||[]}><CartesianGrid vertical={false} stroke="#e8eef6"/><XAxis dataKey="mes" tickLine={false} axisLine={false}/><YAxis allowDecimals={false} tickLine={false} axisLine={false}/><Tooltip/><Bar dataKey="cantidad" name="Citas" fill="#176bdb" radius={[5,5,0,0]}/></BarChart></ResponsiveContainer></div></article>
      <article className="panel chart-panel"><div className="panel-heading"><div><h2>Citas por estado</h2><p>Distribución de las citas filtradas</p></div></div><div className="rechart-box"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={datos?.citas_por_estado||[]} dataKey="cantidad" nameKey="estado" cx="50%" cy="47%" innerRadius={48} outerRadius={76} paddingAngle={4} label={({estado,cantidad})=>estado+": "+cantidad}>{(datos?.citas_por_estado||[]).map((x,i)=><Cell key={x.estado} fill={colores[i%colores.length]}/>)}</Pie><Tooltip/></PieChart></ResponsiveContainer></div></article>
    </section>
    <section className="dashboard-charts">
      <article className="panel chart-panel"><div className="panel-heading"><div><h2>Histograma de edades</h2><p>Mascotas por rango de edad (años)</p></div></div><div className="rechart-box"><ResponsiveContainer width="100%" height="100%"><BarChart data={datos?.histograma_edades||[]} barCategoryGap={2}><CartesianGrid vertical={false} stroke="#e8eef6"/><XAxis dataKey="rango" tickLine={false} axisLine={false}/><YAxis allowDecimals={false} tickLine={false} axisLine={false}/><Tooltip/><Bar dataKey="cantidad" name="Mascotas" fill="#16bfc4" radius={[3,3,0,0]}/></BarChart></ResponsiveContainer></div></article>
      <article className="panel chart-panel"><div className="panel-heading"><div><h2>Boxplot de precio por servicio</h2><p>Caja: Q1 a Q3 · punto rojo: mediana · puntos oscuros: mínimo y máximo</p></div></div><div className="rechart-box"><ResponsiveContainer width="100%" height="100%"><ComposedChart data={cajas}><CartesianGrid vertical={false} stroke="#e8eef6"/><XAxis dataKey="servicio" tickLine={false} axisLine={false} interval={0} angle={-40} textAnchor="end" height={70}/><YAxis tickLine={false} axisLine={false}/><Tooltip content={<TooltipCaja/>}/><Bar dataKey="base" stackId="caja" fill="transparent"/><Bar dataKey="caja_baja" stackId="caja" fill="#16bfc4"/><Bar dataKey="caja_alta" stackId="caja" fill="#176bdb"/><Line dataKey="minimo" stroke="none" dot={{r:3,fill:"#17233d"}} isAnimationActive={false}/><Line dataKey="maximo" stroke="none" dot={{r:3,fill:"#17233d"}} isAnimationActive={false}/><Line dataKey="mediana" stroke="none" dot={{r:4,fill:"#ff766b"}} isAnimationActive={false}/></ComposedChart></ResponsiveContainer></div></article>
    </section>
    <section className="dashboard-charts">
      <article className="panel"><div className="panel-heading"><div><h2>Limpieza de datos</h2><p>Resumen de lo que se limpió con pandas</p></div></div>
        {limpieza&&<ul className="lista-analisis"><li>Filas leídas: <b>{limpieza.filas_antes}</b> · filas finales: <b>{limpieza.filas_despues}</b></li><li>Duplicados eliminados: <b>{limpieza.duplicados_eliminados}</b></li><li>Fechas convertidas con to_datetime: <b>{limpieza.fechas_convertidas.join(", ")}</b></li><li>Valores nulos: {Object.keys(limpieza.nulos_por_columna).length?Object.entries(limpieza.nulos_por_columna).map(([c,n])=><b key={c}>{c}: {n} </b>):<b>ninguno</b>}</li></ul>}
      </article>
      <article className="panel"><div className="panel-heading"><div><h2>Estadísticas de precio</h2><p>Calculadas con numpy</p></div></div>
        <ul className="lista-analisis"><li>Promedio: <b>S/ {ver(precio.promedio)}</b></li><li>Desviación estándar: <b>S/ {ver(precio.desviacion)}</b></li><li>Mínimo: <b>S/ {ver(precio.minimo)}</b></li><li>Máximo: <b>S/ {ver(precio.maximo)}</b></li></ul>
      </article>
    </section>
    <section className="panel generic-panel"><div className="panel-heading"><div><h2>Resumen estadístico</h2><p>describe() de pandas más la mediana</p></div></div>
      <div className="tabla-scroll"><table className="tabla-analisis"><thead><tr><th>Variable</th><th>Cantidad</th><th>Promedio</th><th>Desv. est.</th><th>Mínimo</th><th>Mediana</th><th>Máximo</th></tr></thead><tbody>{Object.entries(datos?.resumen_estadistico||{}).map(([nombre,r])=><tr key={nombre}><td>{nombre}</td><td>{r.cantidad}</td><td>{ver(r.promedio)}</td><td>{ver(r.desviacion)}</td><td>{ver(r.minimo)}</td><td>{ver(r.mediana)}</td><td>{ver(r.maximo)}</td></tr>)}</tbody></table></div>
    </section>
    <section className="panel generic-panel"><div className="panel-heading"><div><h2>Conclusiones</h2><p>Frases generadas con los datos filtrados</p></div></div><ul className="lista-analisis">{(datos?.conclusiones||[]).map(c=><li key={c}>{c}</li>)}</ul></section>
    <section className="panel generic-panel"><div className="panel-heading"><div><h2>Dataset filtrado</h2><p>Mostrando {Math.min(visibles,tabla.length)} de {tabla.length} citas</p></div></div>
      <div className="tabla-scroll"><table className="tabla-analisis"><thead><tr><th>ID</th><th>Fecha</th><th>Mascota</th><th>Especie</th><th>Servicio</th><th>Estado</th></tr></thead><tbody>{tabla.slice(0,visibles).map(c=><tr key={c.id}><td>{c.id}</td><td>{c.fecha}</td><td>{c.mascota}</td><td>{c.especie}</td><td>{c.servicio}</td><td>{c.estado}</td></tr>)}</tbody></table></div>
      {visibles<tabla.length&&<button className="filter-btn" onClick={()=>setVisibles(v=>v+filasPorPagina)}>Ver más</button>}
      {datos&&!tabla.length&&<div className="empty-state">No hay citas con estos filtros.</div>}
    </section>
  </div>
}
