interface ArabicTimeSelectProps {
  value: string
  onChange: (value: string) => void
  required?: boolean
  className?: string
}

function labelForTime(value: string) {
  const [hoursRaw, minutes = '00'] = value.split(':')
  const hours = Number(hoursRaw)
  const period = hours >= 12 ? 'مساء' : 'صباحا'
  const hour12 = hours % 12 || 12
  return minutes === '00' ? `${hour12} ${period}` : `${hour12}:${minutes} ${period}`
}

const timeOptions = Array.from({ length: 48 }, (_, index) => {
  const hours = Math.floor(index / 2)
  const minutes = index % 2 === 0 ? '00' : '30'
  const value = `${String(hours).padStart(2, '0')}:${minutes}`
  return { value, label: labelForTime(value) }
})

export default function ArabicTimeSelect({ value, onChange, required, className = 'field-control mt-1' }: ArabicTimeSelectProps) {
  return (
    <select required={required} value={value} onChange={(event) => onChange(event.target.value)} className={className}>
      {timeOptions.map((option) => (
        <option key={option.value} value={option.value}>{option.label}</option>
      ))}
    </select>
  )
}
