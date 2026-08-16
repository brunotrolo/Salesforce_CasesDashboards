interface LogContext {
  [key: string]: any
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
  private isDev: boolean

  constructor() {
    this.isDev = import.meta.env.DEV
  }

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
      const logLevel = level.toLowerCase()
      if (logLevel === 'info') {
        console.info(entry)
      } else if (logLevel === 'warn') {
        console.warn(entry)
      } else if (logLevel === 'error') {
        console.error(entry)
      } else if (logLevel === 'debug') {
        console.debug(entry)
      } else {
        console.log(entry)
      }
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
