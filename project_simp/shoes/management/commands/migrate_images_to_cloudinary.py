import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from shoes.models import Shoes, ShoesVariant


class Command(BaseCommand):
    help = "Re-save existing local shoe images so they upload to Cloudinary"

    def handle(self, *args, **options):
        # Re-save Shoes.thumbnail
        for shoe in Shoes.objects.all():
            if shoe.thumbnail and shoe.thumbnail.name:
                local_path = os.path.join(settings.MEDIA_ROOT, shoe.thumbnail.name)

                if not os.path.exists(local_path):
                    self.stdout.write(self.style.WARNING(
                        f"Skipping Shoes id={shoe.id}: file not found locally ({local_path})"
                    ))
                    continue

                with open(local_path, 'rb') as f:
                    content = ContentFile(f.read())
                    filename = shoe.thumbnail.name.split('/')[-1]
                    shoe.thumbnail.save(filename, content, save=True)
                    self.stdout.write(self.style.SUCCESS(
                        f"Uploaded Shoes id={shoe.id} thumbnail -> {shoe.thumbnail.url}"
                    ))

        # Re-save ShoesVariant.shoes_photo
        for variant in ShoesVariant.objects.all():
            if variant.shoes_photo and variant.shoes_photo.name:
                local_path = os.path.join(settings.MEDIA_ROOT, variant.shoes_photo.name)

                if not os.path.exists(local_path):
                    self.stdout.write(self.style.WARNING(
                        f"Skipping Variant id={variant.id}: file not found locally ({local_path})"
                    ))
                    continue

                with open(local_path, 'rb') as f:
                    content = ContentFile(f.read())
                    filename = variant.shoes_photo.name.split('/')[-1]
                    variant.shoes_photo.save(filename, content, save=True)
                    self.stdout.write(self.style.SUCCESS(
                        f"Uploaded Variant id={variant.id} photo -> {variant.shoes_photo.url}"
                    ))

        self.stdout.write(self.style.SUCCESS("Done migrating images to Cloudinary."))
