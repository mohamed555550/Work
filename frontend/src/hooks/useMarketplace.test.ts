import { describe, expect, it } from 'vitest'
import { fallbackMealImage, fallbackTradeImage } from './useMarketplace'

describe('trade fallback images', () => {
  it('uses a selected trade image when a trade is provided', () => {
    expect(fallbackTradeImage('electrician', 99)).toBe('/backgrounds/trades/02-electrician.jpg')
  })

  it('uses worker and trade backgrounds without old food assets', () => {
    expect(fallbackMealImage('any product', undefined, 1)).toBe('/backgrounds/trades/02-electrician.jpg')
    expect(fallbackMealImage('any product', undefined, 19)).toBe('/backgrounds/trades/20-tailor.jpg')
    expect(fallbackMealImage('any product', undefined, 20)).toBe('/backgrounds/trades/01-carpenter.jpg')
  })
})
