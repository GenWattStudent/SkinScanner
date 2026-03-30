import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs))
}

export function formatConfidence(confidence: number) {
    return confidence.toFixed(2)
}

export function formatDate(date: Date | string) {
    const dateObj = typeof date === 'string' ? new Date(date) : date
    return dateObj.toLocaleDateString('pl-PL', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

export function getWsBase() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    return `${protocol}//${window.location.host}`
}