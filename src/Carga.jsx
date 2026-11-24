import React,{useState}from "react";
import {FileSpreadsheet,Upload}from "lucide-react";
import {api}from "./services/api";

const nombresHoja={mascotas:"Hoja mascotas",citas:"Hoja citas"};
const suma=objeto=>Object.values(objeto||{}).reduce((total,n)=>total+n,0);
const Dato=({titulo,valor})=><article className="stat-card"><div className="stat-top"><span>{titulo}</span></div><div className="stat-value">{valor}</div></article>;

export default function Carga({setActive}){
  const[archivo,setArchivo]=useState(null),[enviando,setEnviando]=useState(false),[resumen,setResumen]=useState(),[error,setError]=useState("");
  async function subir(e){
    e.preventDefault();if(!archivo)return;
    setEnviando(true);setError("");setResumen();
    try{const formulario=new FormData();formulario.append("archivo",archivo);setResumen((await api.upload("/carga",formulario)).data)}
    catch(err){setError(err.message)}finally{setEnviando(false)}
  }
  return <div className="page-content">
    <div className="welcome-row"><div><div className="eyebrow">MÓDULO DE CARGA</div><h1>Carga de datos desde Excel</h1><p className="subheading">Sube un Excel: Python lo limpia con pandas y solo guarda en MySQL las filas buenas.</p></div></div>
    <section className="panel">
      <div className="panel-heading"><div><h2>1. Elige el archivo</h2><p>Formato .xlsx con una hoja "mascotas" y/o una hoja "citas"</p></div></div>
      <form onSubmit={subir} className="filtros-panel">
        <label className="filtro"><span><FileSpreadsheet size={14}/> Archivo Excel</span><input type="file" accept=".xlsx" onChange={e=>{setArchivo(e.target.files[0]||null);setResumen();setError("")}}/></label>
        <button className="primary-btn" disabled={!archivo||enviando}><Upload size={16}/>{enviando?"Procesando...":"Subir y limpiar"}</button>
      </form>
      <ul className="lista-analisis">
        <li>Hoja <b>mascotas</b>: cliente_dni, nombre, especie, raza, sexo, fecha_nacimiento, peso, color, observaciones</li>
        <li>Hoja <b>citas</b>: cliente_dni, mascota_nombre, veterinario_dni, servicio_nombre, fecha, hora, motivo, observaciones, estado</li>
      </ul>
    </section>
    {error&&<div className="api-warning">{error}</div>}
    {resumen&&<>
      <div className="notice success">Carga terminada. Estas son las filas que se leyeron, lo que se limpió y lo que se guardó.</div>
      {Object.entries(resumen).map(([hoja,r])=><section className="panel generic-panel" key={hoja} style={{marginBottom:18}}>
        <div className="panel-heading"><div><h2>{nombresHoja[hoja]||hoja}</h2><p>Resultado de la limpieza y de la carga</p></div></div>
        <div className="stats-grid stats-cinco" style={{marginTop:14}}>
          <Dato titulo="Filas leídas" valor={r.filas_leidas}/>
          <Dato titulo="Duplicados eliminados" valor={r.duplicados_eliminados}/>
          <Dato titulo="Nulos rellenados" valor={suma(r.nulos_rellenados)}/>
          <Dato titulo="Guardadas en MySQL" valor={r.insertadas}/>
          <Dato titulo="Omitidas" valor={r.omitidas.length}/>
        </div>
        <ul className="lista-analisis">
          <li>Nulos encontrados (isna): {Object.keys(r.nulos_por_columna).length?Object.entries(r.nulos_por_columna).map(([c,n])=><b key={c}>{c}: {n} </b>):<b>ninguno</b>}</li>
          <li>Nulos rellenados (fillna): {Object.keys(r.nulos_rellenados).length?Object.entries(r.nulos_rellenados).map(([c,n])=><b key={c}>{c}: {n} </b>):<b>ninguno</b>}</li>
          <li>Filas duplicadas del Excel que se quitaron: <b>{r.filas_duplicadas.length?r.filas_duplicadas.join(", "):"ninguna"}</b></li>
        </ul>
        {r.omitidas.length>0&&<><h3 className="subtitulo-panel">Filas omitidas (no se guardaron)</h3><div className="tabla-scroll tabla-alta"><table className="tabla-analisis"><thead><tr><th>Fila del Excel</th><th>Motivo</th></tr></thead><tbody>{r.omitidas.map(o=><tr key={o.fila}><td>{o.fila}</td><td>{o.motivo}</td></tr>)}</tbody></table></div></>}
      </section>)}
      <div className="filtros-panel" style={{padding:0}}><button className="primary-btn" onClick={()=>setActive("Análisis")}>Ver el análisis</button><button className="filter-btn" onClick={()=>setActive("Citas")}>Ver las citas</button></div>
    </>}
  </div>
}
