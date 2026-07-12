import { describe, expect, it } from 'vitest'
import { dataOf, errorMessage, listOf } from './response'

describe('API response helpers', () => {
  it('unwraps success envelopes', () => {
    expect(dataOf<{ id: number }>({ data: { data: { id: 7 } } })).toEqual({ id: 7 })
    expect(listOf<number>({ data: { data: [1, 2] } })).toEqual([1, 2])
  })

  it('extracts nested validation errors', () => {
    expect(errorMessage({ error: { available_at: ['حدد الموعد'] } }))
      .toBe('حدد الموعد')
  })

  it('returns the fallback for unknown errors', () => {
    expect(errorMessage({}, 'تعذر التنفيذ')).toBe('تعذر التنفيذ')
  })
})
