export const REQUEST_TIMEOUT_MS=30_000

export async function api<T>(path:string, body?:unknown):Promise<T>{
  const controller=new AbortController()
  let timer:ReturnType<typeof setTimeout>|undefined
  const timeout=new Promise<never>((_,reject)=>{
    timer=setTimeout(()=>{
      reject(new Error('The server did not respond within 30 seconds. A hosted demo may be waking up; wait briefly and retry.'))
      controller.abort()
    },REQUEST_TIMEOUT_MS)
  })
  try{
    const request=(async()=>{
      const response=await fetch(`/api${path}`,{method:body?'POST':'GET',headers:body?{'Content-Type':'application/json'}:undefined,body:body?JSON.stringify(body):undefined,signal:controller.signal})
      if(!response.ok){let message=`Request failed (${response.status})`; try{const e=await response.json();message=typeof e.detail==='string'?e.detail:JSON.stringify(e.detail)}catch{/* preserve HTTP error */}throw new Error(message)}
      return await response.json() as T
    })()
    // Bound the full response, including its body, even if a transport ignores abort.
    return await Promise.race([request,timeout])
  }finally{
    clearTimeout(timer)
  }
}
