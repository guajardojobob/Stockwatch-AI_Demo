import React, { useMemo, useState } from 'react'

type Rec = {
  item_id: string;
  current_par: number;
  rop: number;
  proposed_par: number;
  reorder_qty: number;
  forecast: { avg_daily: number; lead_time_days: number; sigma_lead: number };
  safety_stock: number;
  rationale?: { summary: string, bullets: string[] }
}

export default function App(){
  const [site, setSite] = useState('SLC-660');
  const [rows, setRows] = useState<Rec[]>([]);
  const [ts, setTs] = useState<string>('');
  const [svc, setSvc] = useState(0.98);
  const [review, setReview] = useState(7);

  const run = async () => {
    const res = await fetch('/recommend', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ site_id: site, service_level: svc, review_period_days: review })
    });
    const data = await res.json();
    setTs(data.generated_at);
    setRows(data.items || []);
  }

  const totalDelta = useMemo(()=> rows.reduce((acc, r)=> acc + (r.proposed_par - r.current_par), 0), [rows]);

  return (
    <div style={{fontFamily:'system-ui', padding:16, maxWidth:1100, margin:'0 auto'}}>
      <h1>StockWatch-GPT</h1>
      <p style={{color:'#555'}}>AI PAR-level engineer — forecast, ROP, safety stock and rationale</p>

      <div style={{display:'flex', gap:12, alignItems:'center', marginBottom:12, flexWrap:'wrap'}}>
        <label>Site <input value={site} onChange={e=>setSite(e.target.value)} /></label>
        <label>Service level <input type="number" step="0.01" min="0" max="0.999" value={svc} onChange={e=>setSvc(parseFloat(e.target.value))} /></label>
        <label>Review days <input type="number" min="1" value={review} onChange={e=>setReview(parseInt(e.target.value))} /></label>
        <button onClick={run}>Recalculate</button>
      </div>

      <div style={{marginBottom:8, fontSize:13, color:'#666'}}>
        {ts && <>Generated: {ts} · Items: {rows.length} · Total PAR Δ: {totalDelta}</>}
      </div>

      <table style={{borderCollapse:'collapse', width:'100%'}}>
        <thead><tr>
          <th>Item</th><th>Current PAR</th><th>ROP</th><th>Proposed PAR</th>
          <th>Avg Daily</th><th>Lead Time</th><th>Safety</th><th>Reorder Qty</th><th>Rationale</th>
        </tr></thead>
        <tbody>
          {rows.map((r,i)=> (
            <tr key={i}>
              <td>{r.item_id}</td><td>{r.current_par}</td><td>{r.rop}</td><td><b>{r.proposed_par}</b></td>
              <td>{r.forecast.avg_daily}</td><td>{r.forecast.lead_time_days}</td><td>{r.safety_stock}</td><td>{r.reorder_qty}</td>
              <td>{r.rationale?.summary}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <p style={{marginTop:12, fontSize:12, color:'#666'}}>Use the /ingest endpoint to load your own CSVs. Then Recalculate.</p>
    </div>
  )
}
