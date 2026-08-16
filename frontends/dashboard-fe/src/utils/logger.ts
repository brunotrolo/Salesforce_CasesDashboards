interface LogContext {
  [key: string]: unknown
}

interface LogEntry {
  timestamp: string
  level: string
  message: string
  context?: LogContext
  error?: string
  stack?: string
}

class Logger {
  private isDev = (import.meta as any).env?.DEV === true

  private log(level: string, message: string, context?: LogContext, error?: Error) {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
    }

    if (context && Object.keys(context).length > 0) {
      entry.context = context
    }

    if (error) {
      entry.error = error.message
      entry.stack = error.stack
    }

    if (this.isDev) {
      const method = level.toLowerCase() as 'log' | 'info' | 'warn' | 'error' | 'debug'
      console[method](entry)
    }

    // In production, send to logging service
    if (!this.isDev && level === 'ERROR') {
      this.sendToServer(entry)
    }
  }

  private sendToServer(entry: LogEntry) {
    // TODO: Send to logging service
    console.error('Log entry would be sent to server:', entry)
  }

  info(message: string, context?: LogContext) {
    this.log('INFO', message, context)
  }

  warn(message: string, context?: LogContext) {
    this.log('WARN', message, context)
  }

  error(message: string, error?: Error, context?: LogContext) {
    this.log('ERROR', message, context, error)
  }

  debug(message: string, context?: LogContext) {
    if (this.isDev) {
      this.log('DEBUG', message, context)
    }
  }
}

export const logger = new Logger()
