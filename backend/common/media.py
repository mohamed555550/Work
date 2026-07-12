import io
import logging
import os
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image, ImageOps, ImageSequence

logger = logging.getLogger(__name__)

MAX_IMAGE_DIMENSION = int(os.getenv('MEDIA_MAX_IMAGE_DIMENSION', '2048'))
IMAGE_QUALITY = int(os.getenv('MEDIA_IMAGE_QUALITY', '82'))
PREFERRED_FORMAT = os.getenv('MEDIA_IMAGE_FORMAT', 'WEBP').upper()


def _output_format():
    if PREFERRED_FORMAT == 'AVIF' and 'AVIF' in Image.SAVE:
        return 'AVIF', '.avif'
    return 'WEBP', '.webp'


def _prepare_frame(frame):
    frame = ImageOps.exif_transpose(frame)
    frame.thumbnail(
        (MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION),
        Image.Resampling.LANCZOS,
    )
    return frame.convert('RGBA' if frame.mode in {'RGBA', 'LA'} else 'RGB')


def optimize_image_field(field_file):
    """Return an optimized ContentFile for a newly uploaded image."""
    source = field_file.file
    source.seek(0)
    image = Image.open(source)
    output_format, extension = _output_format()
    output = io.BytesIO()
    is_animated = bool(getattr(image, 'is_animated', False))

    if is_animated:
        frames = [_prepare_frame(frame.copy()) for frame in ImageSequence.Iterator(image)]
        frames[0].save(
            output,
            format=output_format,
            save_all=True,
            append_images=frames[1:],
            duration=image.info.get('duration', 100),
            loop=image.info.get('loop', 0),
            quality=IMAGE_QUALITY,
            method=6,
        )
    else:
        prepared = _prepare_frame(image)
        save_options = {'format': output_format, 'quality': IMAGE_QUALITY}
        if output_format == 'WEBP':
            save_options['method'] = 6
        prepared.save(output, **save_options)

    output.seek(0)
    name = f'{Path(field_file.name).stem}{extension}'
    return ContentFile(output.read(), name=name)


def optimize_model_images(instance):
    from django.db.models import ImageField

    for field in instance._meta.concrete_fields:
        if not isinstance(field, ImageField):
            continue
        field_file = getattr(instance, field.attname, None)
        if not field_file or getattr(field_file, '_committed', True):
            continue
        try:
            setattr(instance, field.attname, optimize_image_field(field_file))
        except Exception:
            logger.exception(
                'Unable to optimize %s.%s upload',
                instance._meta.label,
                field.name,
            )
