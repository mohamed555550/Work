import { useEffect, useMemo, useState } from 'react'
import { imageFallback, publicAsset } from '../utils/assets'

const images = [
  '/backgrounds/trades/01-carpenter.jpg',
  '/backgrounds/trades/02-electrician.jpg',
  '/backgrounds/trades/03-plumber.jpg',
  '/backgrounds/trades/04-painter.jpg',
  '/backgrounds/trades/05-blacksmith.jpg',
  '/backgrounds/trades/06-tiler.jpg',
  '/backgrounds/trades/07-mason.jpg',
  '/backgrounds/trades/08-ac-technician.jpg',
  '/backgrounds/trades/09-appliance-repair.jpg',
  '/backgrounds/trades/10-upholsterer.jpg',
  '/backgrounds/trades/11-aluminum.jpg',
  '/backgrounds/trades/12-glass.jpg',
  '/backgrounds/trades/13-gypsum.jpg',
  '/backgrounds/trades/14-locksmith.jpg',
  '/backgrounds/trades/15-network.jpg',
  '/backgrounds/trades/16-cleaning.jpg',
  '/backgrounds/trades/17-roofing.jpg',
  '/backgrounds/trades/18-mechanic.jpg',
  '/backgrounds/trades/19-mobile-repair.jpg',
  '/backgrounds/trades/20-tailor.jpg',
]

export default function WorkerBackground() {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [previousIndex, setPreviousIndex] = useState<number | null>(null)
  const nextImage = useMemo(() => publicAsset(images[(currentIndex + 1) % images.length]), [currentIndex])

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
          src={publicAsset(images[previousIndex])}
          onError={imageFallback}
          alt=""
          className="worker-background__image worker-background__image--previous"
        />
      )}
      <img
        key={`current-${currentIndex}`}
        src={publicAsset(images[currentIndex])}
        onError={imageFallback}
        alt=""
        fetchPriority={currentIndex === 0 ? 'high' : 'auto'}
        className="worker-background__image worker-background__image--visible"
      />
      <div className="worker-background__overlay" />
    </div>
  )
}
