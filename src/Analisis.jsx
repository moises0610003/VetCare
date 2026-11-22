import React,{useEffect,useState}from "react";
import {Activity,CalendarDays,CheckCircle2,CircleDollarSign,XCircle}from "lucide-react";
import {Bar,BarChart,CartesianGrid,Cell,ComposedChart,Line,Pie,PieChart,ResponsiveContainer,Tooltip,XAxis,YAxis}from "recharts";
import {api}from "./services/api";

// Un color fijo por estado
const coloresEstado={Completada:"#16bfc4",Pendiente:"#f0ad3d",Cancelada:"#ff766b"};
const sinFiltros={especie:"",servicio:"",mes:""};
const filasPorPagina=50;
const ver=v=>v??"—";

function Tarjeta({titulo,valor,Icono}){return <article className="stat-card"><div className="stat-top"><span>{titulo}</span><div className="stat-icon stat-0"><Icono size={18}/></div></div><div className="stat-value">{valor}</div></article>}
function Filtro({etiqueta,valor,opciones,cambiar}){return <label className="filtro">{etiqueta}<select value={valor} onChange={e=>cambiar(e.target.value)}><option value="">Todos</option>{opciones.map(o=><option key={o.valor} value={o.valor}>{o.nombre}</option>)}</select></label>}
function TooltipCaja({active,payload}){if(!active||!payload?.length)return null;const d=payload[0].payload;return <div className="tooltip-caja"><b>{d.especie}</b><br/>Mínimo: S/ {d.minimo}<br/>Q1: S/ {d.q1}<br/>Mediana: S/ {d.mediana}<br/>Q3: S/ {d.q3}<br/>Máximo: S/ {d.maximo}<br/>Citas: {d.citas}</div>}

// Sección con título y su contenido
function Seccion({titulo,children}){return <section className="seccion-analisis"><h2 className="titulo-seccion">{titulo}</h2>{children}</section>}
// Panel con título y subtítulo
function Panel({titulo,detalle,children}){return <article className="panel chart-panel"><div className="panel-heading"><div><h2>{titulo}</h2>{detalle&&<p>{detalle}</p>}</div></div>{children}</article>}
// Gráfico de barras (vertical u horizontal)
function Barras({datos,x,y="cantidad",nombre="Cantidad",color="#176bdb",horizontal=false}){
  return <div className="rechart-box"><ResponsiveContainer width="100%" height="100%"><BarChart data={datos} layout={horizontal?"vertical":"horizontal"} margin={horizontal?{left:20}:undefined}><CartesianGrid vertical={horizontal} horizontal={!horizontal} stroke="#e8eef6"/>{horizontal?<><XAxis type="number" allowDecimals={false} tickLine={false} axisLine={false}/><YAxis type="category" dataKey={x} width={130} tickLine={false} axisLine={false}/></>:<><XAxis dataKey={x} tickLine={false} axisLine={false}/><YAxis allowDecimals={false} tickLine={false} axisLine={false}/></>}<Tooltip/><Bar dataKey={y} name={nombre} fill={color} radius={horizontal?[0,5,5,0]:[5,5,0,0]}/></BarChart></ResponsiveContainer></div>
}
// Tabla simple: columnas = [[clave, título], ...]
function Tabla({columnas,filas}){return <div className="tabla-scroll"><table className="tabla-analisis"><thead><tr>{columnas.map(([,t])=><th key={t}>{t}</th>)}</tr></thead><tbody>{filas.map((f,i)=><tr key={i}>{columnas.map(([c])=><td key={c}>{ver(f[c])}</td>)}</tr>)}</tbody></table></div>}

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
  const ingresos=datos?.ingresos_por_mes;
  const dx=datos?.diagnosticos;
  const masc=datos?.mascotas;
  const horarios=datos?.horarios_demanda;
  const serv=datos?.servicios;
  const cajas=(datos?.boxplot_precio||[]).map(x=>({...x,base:x.q1,caja_baja:+(x.mediana-x.q1).toFixed(2),caja_alta:+(x.q3-x.mediana).toFixed(2)}));
  const tabla=datos?.tabla||[];
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

    <Seccion titulo="Ventas e ingresos">
      <div className="dashboard-charts">
        <Panel titulo="Ingresos por mes (S/)" detalle="Solo citas completadas"><Barras datos={ingresos?.meses||[]} x="mes" y="ingresos" nombre="Ingresos (S/)" color="#16bfc4"/></Panel>
        <Panel titulo="Mes con más y con menos ingresos" detalle="Entre los meses con ingresos">
          <ul className="lista-analisis"><li>Más ingresos: <b>{ingresos?.mes_mayor?`${ingresos.mes_mayor.nombre} (S/ ${ingresos.mes_mayor.ingresos})`:"—"}</b></li><li>Menos ingresos: <b>{ingresos?.mes_menor?`${ingresos.mes_menor.nombre} (S/ ${ingresos.mes_menor.ingresos})`:"—"}</b></li></ul>
          <h3 className="subtitulo-panel">Precio (numpy)</h3>
          <ul className="lista-analisis"><li>Promedio: <b>S/ {ver(precio.promedio)}</b> · desviación estándar: <b>S/ {ver(precio.desviacion)}</b></li><li>Mínimo: <b>S/ {ver(precio.minimo)}</b> · máximo: <b>S/ {ver(precio.maximo)}</b></li></ul>
        </Panel>
      </div>
      <div className="dashboard-charts">
        <Panel titulo="Ingresos por servicio" detalle="Y su porcentaje del total"><Tabla columnas={[["servicio","Servicio"],["ingresos","Ingresos (S/)"],["porcentaje","%"]]} filas={datos?.ingresos_por_servicio||[]}/></Panel>
        <Panel titulo="Boxplot de precio por especie" detalle="Caja: Q1 a Q3 · punto rojo: mediana · puntos oscuros: mínimo y máximo"><div className="rechart-box"><ResponsiveContainer width="100%" height="100%"><ComposedChart data={cajas}><CartesianGrid vertical={false} stroke="#e8eef6"/><XAxis dataKey="especie" tickLine={false} axisLine={false}/><YAxis tickLine={false} axisLine={false}/><Tooltip content={<TooltipCaja/>}/><Bar dataKey="base" stackId="caja" fill="transparent"/><Bar dataKey="caja_baja" stackId="caja" fill="#16bfc4"/><Bar dataKey="caja_alta" stackId="caja" fill="#176bdb"/><Line dataKey="minimo" stroke="none" dot={{r:3,fill:"#17233d"}} isAnimationActive={false}/><Line dataKey="maximo" stroke="none" dot={{r:3,fill:"#17233d"}} isAnimationActive={false}/><Line dataKey="mediana" stroke="none" dot={{r:4,fill:"#ff766b"}} isAnimationActive={false}/></ComposedChart></ResponsiveContainer></div></Panel>
      </div>
    </Seccion>

    <Seccion titulo="Diagnósticos">
      <div className="dashboard-charts">
        <Panel titulo="Casos por diagnóstico" detalle={dx?.mas_comun?`Más diagnosticado: ${dx.mas_comun.diagnostico} (${dx.mas_comun.cantidad} casos, ${dx.mas_comun.porcentaje}%)`:"Sin diagnósticos con estos filtros"}><Barras datos={(dx?.casos||[]).slice(0,10)} x="diagnostico" nombre="Casos" horizontal color="#805ed4"/></Panel>
        <Panel titulo="Todos los diagnósticos"><div className="tabla-alta"><Tabla columnas={[["diagnostico","Diagnóstico"],["cantidad","Casos"],["porcentaje","%"]]} filas={dx?.casos||[]}/></div></Panel>
      </div>
      <div className="dashboard-charts">
        <Panel titulo="Top 5 en perros"><Tabla columnas={[["diagnostico","Diagnóstico"],["cantidad","Casos"],["porcentaje","%"]]} filas={dx?.top_perros||[]}/></Panel>
        <Panel titulo="Top 5 en gatos"><Tabla columnas={[["diagnostico","Diagnóstico"],["cantidad","Casos"],["porcentaje","%"]]} filas={dx?.top_gatos||[]}/></Panel>
      </div>
    </Seccion>

    <Seccion titulo="Mascotas">
      <div className="dashboard-charts">
        <Panel titulo="Mascotas por especie" detalle={masc?`${masc.total} mascotas atendidas`:""}><Barras datos={masc?.por_especie||[]} x="especie" nombre="Mascotas" color="#176bdb"/></Panel>
        <Panel titulo="Top 5 razas"><Barras datos={masc?.top_razas||[]} x="raza" nombre="Mascotas" horizontal color="#16bfc4"/></Panel>
      </div>
      <div className="dashboard-charts">
        <Panel titulo="Distribución por sexo"><Tabla columnas={[["sexo","Sexo"],["cantidad","Mascotas"],["porcentaje","%"]]} filas={masc?.por_sexo||[]}/></Panel>
        <Panel titulo="Histograma de edades" detalle="Mascotas por rango de edad (años)"><Barras datos={datos?.histograma_edades||[]} x="rango" nombre="Mascotas" color="#ff766b"/></Panel>
      </div>
      <Panel titulo="Resumen estadístico" detalle="describe() de pandas más la mediana"><Tabla columnas={[["variable","Variable"],["cantidad","Cantidad"],["promedio","Promedio"],["desviacion","Desv. est."],["minimo","Mínimo"],["mediana","Mediana"],["maximo","Máximo"]]} filas={Object.entries(datos?.resumen_estadistico||{}).map(([variable,r])=>({variable,...r}))}/></Panel>
    </Seccion>

    <Seccion titulo="Citas">
      <div className="dashboard-charts">
        <Panel titulo="Citas por mes" detalle="Tendencia durante el año"><Barras datos={datos?.citas_por_mes||[]} x="mes" nombre="Citas"/></Panel>
        <Panel titulo="Citas por estado" detalle="Distribución de las citas filtradas"><div className="rechart-box"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={datos?.citas_por_estado||[]} dataKey="cantidad" nameKey="estado" cx="50%" cy="47%" innerRadius={48} outerRadius={76} paddingAngle={4} label={({estado,cantidad})=>estado+": "+cantidad}>{(datos?.citas_por_estado||[]).map(x=><Cell key={x.estado} fill={coloresEstado[x.estado]}/>)}</Pie><Tooltip/></PieChart></ResponsiveContainer></div></Panel>
      </div>
      <div className="dashboard-charts">
        <Panel titulo="Citas por hora del día" detalle={horarios?.promedio_por_dia?`Promedio de ${horarios.promedio_por_dia} citas por día · hora con más citas: ${horarios.hora_pico}`:""}><Barras datos={horarios?.por_hora||[]} x="hora" nombre="Citas" color="#f0ad3d"/></Panel>
        <Panel titulo="Limpieza de datos" detalle="Resumen de lo que se limpió con pandas">
          {limpieza&&<ul className="lista-analisis"><li>Filas leídas: <b>{limpieza.filas_antes}</b> · filas finales: <b>{limpieza.filas_despues}</b></li><li>Duplicados eliminados: <b>{limpieza.duplicados_eliminados}</b></li><li>Fechas convertidas con to_datetime: <b>{limpieza.fechas_convertidas.join(", ")}</b></li><li>Valores nulos: {Object.keys(limpieza.nulos_por_columna).length?Object.entries(limpieza.nulos_por_columna).map(([c,n])=><b key={c}>{c}: {n} </b>):<b>ninguno</b>}</li></ul>}
        </Panel>
      </div>
      <Panel titulo="Conclusiones" detalle="Frases generadas con los datos filtrados"><ul className="lista-analisis">{(datos?.conclusiones||[]).map(c=><li key={c}>{c}</li>)}</ul></Panel>
      <Panel titulo="Dataset filtrado" detalle={`Mostrando ${Math.min(visibles,tabla.length)} de ${tabla.length} citas`}>
        <Tabla columnas={[["id","ID"],["fecha","Fecha"],["mascota","Mascota"],["especie","Especie"],["servicio","Servicio"],["estado","Estado"]]} filas={tabla.slice(0,visibles)}/>
        {visibles<tabla.length&&<button className="filter-btn" onClick={()=>setVisibles(v=>v+filasPorPagina)}>Ver más</button>}
        {datos&&!tabla.length&&<div className="empty-state">No hay citas con estos filtros.</div>}
      </Panel>
    </Seccion>

    <Seccion titulo="Servicios">
      <div className="dashboard-charts">
        <Panel titulo="Servicios más solicitados" detalle="Top 5 por cantidad de citas"><Barras datos={serv?.mas_solicitados||[]} x="servicio" nombre="Citas" horizontal color="#176bdb"/></Panel>
        <Panel titulo="Servicios menos solicitados" detalle="Los 5 con menos citas"><Barras datos={serv?.menos_solicitados||[]} x="servicio" nombre="Citas" horizontal color="#ff766b"/></Panel>
      </div>
      <Panel titulo="Ranking completo" detalle="Con su porcentaje de la demanda"><div className="tabla-alta"><Tabla columnas={[["servicio","Servicio"],["cantidad","Citas"],["porcentaje","% de la demanda"]]} filas={serv?.ranking||[]}/></div></Panel>
    </Seccion>
  </div>
}
