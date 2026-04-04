'use client'

import { HTMLAttributes } from 'react'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'outlined' | 'elevated'
}

function Card({ className = '', variant = 'default', children, ...props }: CardProps) {
  const variants = {
    default: 'bg-white border border-gray-200',
    outlined: 'bg-transparent border border-gray-300',
    elevated: 'bg-white shadow-lg',
  }

  return (
    <div
      className={`rounded-xl ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}

function CardHeader({ className = '', children, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={`px-4 py-3 border-b border-gray-200 ${className}`} {...props}>
      {children}
    </div>
  )
}

function CardContent({ className = '', children, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={`p-4 ${className}`} {...props}>
      {children}
    </div>
  )
}

function CardFooter({ className = '', children, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={`px-4 py-3 border-t border-gray-200 ${className}`} {...props}>
      {children}
    </div>
  )
}

export { Card, CardHeader, CardContent, CardFooter }
