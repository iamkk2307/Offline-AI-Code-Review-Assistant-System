import { useEffect, useRef } from 'react'
import {
  Chart,
  RadarController, RadialLinearScale, PointElement, LineElement,
  DoughnutController, ArcElement,
  BarController, BarElement, CategoryScale, LinearScale,
  Tooltip, Legend, Filler
} from 'chart.js'

Chart.register(
  RadarController, RadialLinearScale, PointElement, LineElement,
  DoughnutController, ArcElement,
  BarController, BarElement, CategoryScale, LinearScale,
  Tooltip, Legend, Filler
)

const DARK_THEME = {
  grid:   'rgba(255,255,255,0.05)',
  tick:   '#64748b',
  label:  '#94a3b8',
  legend: '#e2e8f0',
}

const COLORS = ['#6366f1','#818cf8','#10b981','#f59e0b','#ef4444','#22c55e','#3b82f6','#a855f7']

interface ScoresRadarProps { scores: Record<string, number> }

export function ScoresRadar({ scores }: ScoresRadarProps) {
  const ref = useRef<HTMLCanvasElement>(null)
  const chartRef = useRef<Chart | null>(null)

  useEffect(() => {
    if (!ref.current) return
    chartRef.current?.destroy()

    chartRef.current = new Chart(ref.current, {
      type: 'radar',
      data: {
        labels: ['Quality', 'Security', 'Maintainability', 'Performance', 'Readability'],
        datasets: [{
          label: 'Score',
          data: [
            scores.quality ?? 0,
            scores.security ?? 0,
            scores.maintainability ?? 0,
            scores.performance ?? 0,
            scores.readability ?? 0,
          ],
          backgroundColor: 'rgba(99, 102, 241, 0.15)',
          borderColor: '#6366f1',
          pointBackgroundColor: '#6366f1',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: '#6366f1',
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            min: 0, max: 100,
            grid: { color: DARK_THEME.grid },
            angleLines: { color: DARK_THEME.grid },
            ticks: { color: DARK_THEME.tick, stepSize: 25, backdropColor: 'transparent' },
            pointLabels: { color: DARK_THEME.label, font: { size: 11, family: 'Inter' } },
          }
        },
        plugins: {
          legend: { labels: { color: DARK_THEME.legend } },
          tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${c.raw}` } }
        }
      }
    })
    return () => chartRef.current?.destroy()
  }, [scores])

  return <canvas ref={ref} />
}

interface LanguageDonutProps { distribution: Record<string, number> }

export function LanguageDonut({ distribution }: LanguageDonutProps) {
  const ref = useRef<HTMLCanvasElement>(null)
  const chartRef = useRef<Chart | null>(null)

  useEffect(() => {
    if (!ref.current) return
    chartRef.current?.destroy()
    const labels = Object.keys(distribution)
    const data   = Object.values(distribution)

    chartRef.current = new Chart(ref.current, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data,
          backgroundColor: COLORS,
          borderColor: '#0f172a',
          borderWidth: 2,
          hoverOffset: 4,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right',
            labels: { color: DARK_THEME.legend, padding: 12, font: { size: 11 } }
          },
          tooltip: {
            callbacks: {
              label: (c) => {
                const total = data.reduce((a, b) => a + b, 0)
                const pct = ((c.raw as number) / total * 100).toFixed(1)
                return `${c.label}: ${c.raw} files (${pct}%)`
              }
            }
          }
        }
      }
    })
    return () => chartRef.current?.destroy()
  }, [distribution])

  return <canvas ref={ref} />
}

interface IssueBarChartProps { summary: Record<string, number> }

export function IssueBarChart({ summary }: IssueBarChartProps) {
  const ref = useRef<HTMLCanvasElement>(null)
  const chartRef = useRef<Chart | null>(null)

  useEffect(() => {
    if (!ref.current) return
    chartRef.current?.destroy()
    const labels = ['Critical', 'High', 'Medium', 'Low', 'Info']
    const colors = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6']
    const data   = labels.map(l => summary[l.toLowerCase()] ?? 0)

    chartRef.current = new Chart(ref.current, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Issues',
          data,
          backgroundColor: colors.map(c => c + '33'),
          borderColor: colors,
          borderWidth: 1.5,
          borderRadius: 6,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { color: DARK_THEME.grid }, ticks: { color: DARK_THEME.tick } },
          y: { grid: { color: DARK_THEME.grid }, ticks: { color: DARK_THEME.tick, precision: 0 } },
        },
        plugins: { legend: { display: false } }
      }
    })
    return () => chartRef.current?.destroy()
  }, [summary])

  return <canvas ref={ref} />
}
