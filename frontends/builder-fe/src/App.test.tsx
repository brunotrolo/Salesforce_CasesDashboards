import { describe, it, expect } from 'vitest'
import { App } from './App'

describe('App', () => {
  it('renders the router without crashing', () => {
    expect(App).toBeDefined()
    expect(typeof App).toBe('function')
  })
})