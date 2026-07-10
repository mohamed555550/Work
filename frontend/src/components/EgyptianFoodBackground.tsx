import { useEffect, useMemo, useState } from 'react'

const images = [
  '/backgrounds/trades/15-network.jpg',
  '/backgrounds/trades/11-aluminum.jpg',
  '/backgrounds/trades/08-ac-technician.jpg',
  '/backgrounds/trades/01-carpenter.jpg',
]

export default function WorkerBackground() {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [previousIndex, setPreviousIndex] = useState<number | null>(null)
  const nextImage = useMemo(() => images[(currentIndex + 1) % images.length], [currentIndex])

  useEffect(() => {
    const preload = new Image()
    preload.src = nextImage

    const interval = window.setInterval(() => {
      setCurrentIndex((index) => {
        setPreviousIndex(index)
        return (index + 1) % images.length
      })
    }, 18000)

    return () => window.clearInterval(interval)
  }, [nextImage])

  useEffect(() => {
    if (previousIndex === null) return
    const timeout = window.setTimeout(() => setPreviousIndex(null), 4600)
    return () => window.clearTimeout(timeout)
  }, [previousIndex])

  return (
    <div className="worker-background" aria-hidden="true">
      {previousIndex !== null && (
        <img
          key={`previous-${previousIndex}`}
          src={images[previousIndex]}
          alt=""
          className="worker-background__image worker-background__image--previous"
        />
      )}
      <img
        key={`current-${currentIndex}`}
        src={images[currentIndex]}
        alt=""
        fetchPriority={currentIndex === 0 ? 'high' : 'auto'}
        className="worker-background__image worker-background__image--visible"
      />
      <div className="worker-background__overlay" />
    </div>
  )
}
