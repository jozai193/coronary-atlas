import {afterEach,beforeEach,describe,expect,it,vi} from 'vitest'
import {api,REQUEST_TIMEOUT_MS} from './api'

beforeEach(()=>vi.useFakeTimers())
afterEach(()=>{vi.useRealTimers();vi.unstubAllGlobals()})

describe('API request deadline',()=>{
  it('returns the normal response, preserves POST data, and clears the deadline',async()=>{
    const fetchMock=vi.fn().mockResolvedValue({ok:true,json:async()=>({probability:.42})})
    vi.stubGlobal('fetch',fetchMock)
    const input={features:{Age:42},model_variant:'baseline'}
    await expect(api('/predict',input)).resolves.toEqual({probability:.42})
    const [url,request]=fetchMock.mock.calls[0] as [string,RequestInit]
    expect(url).toBe('/api/predict')
    expect(request.method).toBe('POST')
    expect(request.headers).toEqual({'Content-Type':'application/json'})
    expect(JSON.parse(String(request.body))).toEqual(input)
    expect(vi.getTimerCount()).toBe(0)
    await vi.advanceTimersByTimeAsync(REQUEST_TIMEOUT_MS)
    expect(request.signal?.aborted).toBe(false)
  })

  it('rejects a hung fetch even when abort is ignored, and allows a fresh retry',async()=>{
    const fetchMock=vi.fn().mockImplementationOnce(()=>new Promise(()=>{}))
      .mockResolvedValueOnce({ok:true,json:async()=>({ready:true})})
    vi.stubGlobal('fetch',fetchMock)
    const pending=api('/predict',{features:{Age:42}})
    const rejected=expect(pending).rejects.toThrow('The server did not respond within 30 seconds. A hosted demo may be waking up; wait briefly and retry.')
    const request=fetchMock.mock.calls[0][1] as RequestInit
    await vi.advanceTimersByTimeAsync(REQUEST_TIMEOUT_MS-1)
    expect(request.signal?.aborted).toBe(false)
    await vi.advanceTimersByTimeAsync(1)
    await rejected
    expect(request.signal?.aborted).toBe(true)
    expect(vi.getTimerCount()).toBe(0)
    await expect(api('/model/info')).resolves.toEqual({ready:true})
    expect(fetchMock.mock.calls[1][1].method).toBe('GET')
    expect(fetchMock.mock.calls[1][1].body).toBeUndefined()
    expect(fetchMock.mock.calls[1][1].signal.aborted).toBe(false)
    expect(vi.getTimerCount()).toBe(0)
  })

  it('keeps the actionable timeout error when fetch rejects on abort',async()=>{
    vi.stubGlobal('fetch',vi.fn((_url:string,request:RequestInit)=>new Promise((_resolve,reject)=>{
      request.signal?.addEventListener('abort',()=>reject(new Error('AbortError')),{once:true})
    })))
    const rejected=expect(api('/model/info')).rejects.toThrow('The server did not respond within 30 seconds.')
    await vi.advanceTimersByTimeAsync(REQUEST_TIMEOUT_MS)
    await rejected
    expect(vi.getTimerCount()).toBe(0)
  })

  it('also bounds a stalled response body after headers have arrived',async()=>{
    const fetchMock=vi.fn().mockResolvedValue({ok:true,json:()=>new Promise(()=>{})})
    vi.stubGlobal('fetch',fetchMock)
    const rejected=expect(api('/model/info')).rejects.toThrow('The server did not respond within 30 seconds.')
    await vi.advanceTimersByTimeAsync(REQUEST_TIMEOUT_MS)
    await rejected
    expect(fetchMock.mock.calls[0][1].signal.aborted).toBe(true)
    expect(vi.getTimerCount()).toBe(0)
  })

  it('preserves validation and network errors and clears their deadlines',async()=>{
    const fetchMock=vi.fn().mockResolvedValueOnce({ok:false,status:422,json:async()=>({detail:'Age invalid'})})
      .mockRejectedValueOnce(new Error('Network unavailable'))
    vi.stubGlobal('fetch',fetchMock)
    await expect(api('/predict',{features:{Age:-1}})).rejects.toThrow('Age invalid')
    expect(vi.getTimerCount()).toBe(0)
    await expect(api('/model/info')).rejects.toThrow('Network unavailable')
    expect(vi.getTimerCount()).toBe(0)
    await vi.advanceTimersByTimeAsync(REQUEST_TIMEOUT_MS)
    expect(fetchMock.mock.calls.every(([,request])=>!request.signal.aborted)).toBe(true)
  })
})
