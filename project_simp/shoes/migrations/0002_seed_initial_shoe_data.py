from django.db import migrations


def seed_data(apps, schema_editor):
    Category = apps.get_model('shoes', 'Category')
    Brand = apps.get_model('shoes', 'Brand')
    Shoes = apps.get_model('shoes', 'Shoes')
    ShoesColor = apps.get_model('shoes', 'ShoesColor')
    ShoesSize = apps.get_model('shoes', 'ShoesSize')
    ShoesVariant = apps.get_model('shoes', 'ShoesVariant')

    # ---- Categories ----
    cat_sneakers, _ = Category.objects.get_or_create(name='Sneakers')
    cat_boots, _ = Category.objects.get_or_create(name='Boots')

    # ---- Brands ----
    brand_nike, _ = Brand.objects.get_or_create(name='nike')
    brand_converse, _ = Brand.objects.get_or_create(name='Converse')
    brand_simp, _ = Brand.objects.get_or_create(name='SIMP')

    # ---- Shoes ----
    shoe_air_runner, _ = Shoes.objects.get_or_create(
        name='Air Runner',
        defaults=dict(
            category=cat_sneakers, brand=brand_nike,
            description='Nike Air Force 1-style sneaker with customizable leather, fabric, and outsole panels.',
            thumbnail='shoes/thumbnails/air-runner-thumb.jpg',
            customizer_id='air-runner',
        ),
    )
    shoe_air_jordan, _ = Shoes.objects.get_or_create(
        name='Air Jordan 1',
        defaults=dict(
            category=cat_sneakers, brand=brand_nike,
            description='Classic high-top basketball sneaker with customizable toe, upper body, ankle patch, heel, and sole color zones.',
            thumbnail='shoes/thumbnails/air_jordan1.jpg',
            customizer_id='air-jordan-1',
        ),
    )
    shoe_converse_low, _ = Shoes.objects.get_or_create(
        name='Converse Chuck Taylor All Star — Low Top',
        defaults=dict(
            category=cat_sneakers, brand=brand_converse,
            description='Iconic low-top canvas sneaker with customizable body, tongue, heel stripe, lining, stitching, laces, and rubber sole detailing.',
            thumbnail='shoes/thumbnails/nike-converse-low-top.jpeg',
            customizer_id='nike-converse-low-top',
        ),
    )
    shoe_converse_high, _ = Shoes.objects.get_or_create(
        name='Converse Chuck Taylor All Star — High Top',
        defaults=dict(
            category=cat_sneakers, brand=brand_converse,
            description='Classic high-top canvas sneaker with the same full customization as the low-top — body, tongue, heel stripe, lining, stitching, laces, and sole.',
            thumbnail='shoes/thumbnails/nike-converse-high-top.jpeg',
            customizer_id='nike-converse-high-top',
        ),
    )
    shoe_boot, _ = Shoes.objects.get_or_create(
        name='Low Poly Boot',
        defaults=dict(
            category=cat_boots, brand=brand_simp,
            description='Rugged lace-up leather boot with customizable body, eyelet, and lace colors.',
            thumbnail='shoes/thumbnails/boot.jpg',
            customizer_id='low-poly-boot',
        ),
    )
    shoe_urban_canvas, _ = Shoes.objects.get_or_create(
        name='Urban Canvas',
        defaults=dict(
            category=cat_sneakers, brand=brand_simp,
            description='Original SIMP canvas sneaker design with fully customizable upper, toe caps, lining, sole, side stripes, heel band, logo patch, and laces.',
            thumbnail='shoes/thumbnails/urban-canvas-thumb.jpg',
            customizer_id='urban-canvas',
        ),
    )

    # ---- Colors ----
    color_names = ['red', 'Black', 'Green', 'Blue', 'Brown', 'White', 'Red']
    colors = {}
    for name in color_names:
        colors[name], _ = ShoesColor.objects.get_or_create(name=name)

    # ---- Sizes ----
    size_values = ['32', '34', '37', '38', '39', '40', '36', '41']
    sizes = {}
    for val in size_values:
        sizes[val], _ = ShoesSize.objects.get_or_create(size_value=val)

    # ---- Variants: (shoe, color_name, size_value, price, stock) ----
    variants = [
        (shoe_air_runner, 'red', '32', '4500.00', 10),
        (shoe_air_jordan, 'red', '32', '3400.00', 9),
        (shoe_converse_low, 'red', '32', '2000.00', 13),
        (shoe_converse_high, 'red', '32', '3000.00', 18),
        (shoe_boot, 'red', '32', '6000.00', 20),
        (shoe_urban_canvas, 'Black', '37', '4000.00', 18),
        (shoe_air_runner, 'Black', '38', '2149.00', 21),
        (shoe_air_runner, 'Black', '39', '2149.00', 30),
        (shoe_air_runner, 'Black', '40', '2149.00', 13),
        (shoe_air_runner, 'Black', '41', '2149.00', 8),
        (shoe_air_runner, 'White', '38', '2149.00', 28),
        (shoe_air_runner, 'White', '39', '2149.00', 24),
        (shoe_air_runner, 'White', '40', '2149.00', 20),
        (shoe_air_runner, 'White', '41', '2149.00', 27),
        (shoe_air_runner, 'Red', '38', '2149.00', 16),
        (shoe_air_runner, 'Red', '39', '2149.00', 13),
        (shoe_air_runner, 'Red', '40', '2149.00', 10),
        (shoe_air_runner, 'Red', '41', '2149.00', 22),
        (shoe_air_runner, 'Blue', '38', '2149.00', 18),
        (shoe_air_runner, 'Blue', '39', '2149.00', 5),
        (shoe_air_runner, 'Blue', '40', '2149.00', 15),
        (shoe_air_runner, 'Blue', '41', '2149.00', 25),
        (shoe_air_jordan, 'Black', '38', '3628.00', 29),
        (shoe_air_jordan, 'Black', '39', '3628.00', 23),
        (shoe_air_jordan, 'Black', '40', '3628.00', 30),
        (shoe_air_jordan, 'Black', '41', '3628.00', 6),
        (shoe_air_jordan, 'White', '38', '3628.00', 21),
        (shoe_air_jordan, 'White', '39', '3628.00', 11),
        (shoe_air_jordan, 'White', '40', '3628.00', 21),
        (shoe_air_jordan, 'White', '41', '3628.00', 15),
        (shoe_air_jordan, 'Red', '38', '3628.00', 13),
        (shoe_air_jordan, 'Red', '39', '3628.00', 10),
        (shoe_air_jordan, 'Red', '40', '3628.00', 11),
        (shoe_air_jordan, 'Red', '41', '3628.00', 14),
        (shoe_air_jordan, 'Blue', '38', '3628.00', 19),
        (shoe_air_jordan, 'Blue', '39', '3628.00', 11),
        (shoe_air_jordan, 'Blue', '40', '3628.00', 8),
        (shoe_air_jordan, 'Blue', '41', '3628.00', 22),
        (shoe_converse_low, 'Black', '38', '5536.00', 21),
        (shoe_converse_low, 'Black', '39', '5536.00', 29),
        (shoe_converse_low, 'Black', '40', '5536.00', 30),
        (shoe_converse_low, 'Black', '41', '5536.00', 5),
        (shoe_converse_low, 'White', '38', '5536.00', 5),
        (shoe_converse_low, 'White', '39', '5536.00', 10),
        (shoe_converse_low, 'White', '40', '5536.00', 15),
        (shoe_converse_low, 'White', '41', '5536.00', 7),
        (shoe_converse_low, 'Red', '38', '5536.00', 8),
        (shoe_converse_low, 'Red', '39', '5536.00', 27),
        (shoe_converse_low, 'Red', '40', '5536.00', 21),
        (shoe_converse_low, 'Red', '41', '5536.00', 14),
        (shoe_converse_low, 'Blue', '38', '5536.00', 6),
        (shoe_converse_low, 'Blue', '39', '5536.00', 27),
        (shoe_converse_low, 'Blue', '40', '5536.00', 21),
        (shoe_converse_low, 'Blue', '41', '5536.00', 30),
        (shoe_converse_high, 'Black', '38', '2733.00', 6),
        (shoe_converse_high, 'Black', '39', '2733.00', 7),
        (shoe_converse_high, 'Black', '40', '2733.00', 10),
        (shoe_converse_high, 'Black', '41', '2733.00', 29),
        (shoe_converse_high, 'White', '38', '2733.00', 10),
        (shoe_converse_high, 'White', '39', '2733.00', 7),
        (shoe_converse_high, 'White', '40', '2733.00', 29),
        (shoe_converse_high, 'White', '41', '2733.00', 15),
        (shoe_converse_high, 'Red', '38', '2733.00', 27),
        (shoe_converse_high, 'Red', '39', '2733.00', 22),
        (shoe_converse_high, 'Red', '40', '2733.00', 12),
        (shoe_converse_high, 'Red', '41', '2733.00', 9),
        (shoe_converse_high, 'Blue', '38', '2733.00', 22),
        (shoe_converse_high, 'Blue', '39', '2733.00', 26),
        (shoe_converse_high, 'Blue', '40', '2733.00', 19),
        (shoe_converse_high, 'Blue', '41', '2733.00', 29),
        (shoe_boot, 'Black', '38', '4911.00', 12),
        (shoe_boot, 'Black', '39', '4911.00', 11),
        (shoe_boot, 'Black', '40', '4911.00', 29),
        (shoe_boot, 'Black', '41', '4911.00', 11),
        (shoe_boot, 'White', '38', '4911.00', 21),
        (shoe_boot, 'White', '39', '4911.00', 22),
        (shoe_boot, 'White', '40', '4911.00', 24),
        (shoe_boot, 'White', '41', '4911.00', 13),
        (shoe_boot, 'Red', '38', '4911.00', 25),
        (shoe_boot, 'Red', '39', '4911.00', 5),
        (shoe_boot, 'Red', '40', '4911.00', 6),
        (shoe_boot, 'Red', '41', '4911.00', 19),
        (shoe_boot, 'Blue', '38', '4911.00', 23),
        (shoe_boot, 'Blue', '39', '4911.00', 18),
        (shoe_boot, 'Blue', '40', '4911.00', 6),
        (shoe_boot, 'Blue', '41', '4911.00', 9),
        (shoe_urban_canvas, 'Black', '38', '5064.00', 23),
        (shoe_urban_canvas, 'Black', '39', '5064.00', 26),
        (shoe_urban_canvas, 'Black', '40', '5064.00', 24),
        (shoe_urban_canvas, 'Black', '41', '5064.00', 13),
        (shoe_urban_canvas, 'White', '38', '5064.00', 10),
        (shoe_urban_canvas, 'White', '39', '5064.00', 29),
        (shoe_urban_canvas, 'White', '40', '5064.00', 22),
        (shoe_urban_canvas, 'White', '41', '5064.00', 13),
        (shoe_urban_canvas, 'Red', '38', '5064.00', 22),
        (shoe_urban_canvas, 'Red', '39', '5064.00', 11),
        (shoe_urban_canvas, 'Red', '40', '5064.00', 16),
        (shoe_urban_canvas, 'Red', '41', '5064.00', 16),
        (shoe_urban_canvas, 'Blue', '38', '5064.00', 27),
        (shoe_urban_canvas, 'Blue', '39', '5064.00', 11),
        (shoe_urban_canvas, 'Blue', '40', '5064.00', 7),
        (shoe_urban_canvas, 'Blue', '41', '5064.00', 8),
    ]

    for shoe, color_name, size_val, price, stock in variants:
        ShoesVariant.objects.get_or_create(
            shoe=shoe,
            color=colors[color_name],
            size=sizes[size_val],
            defaults={'price': price, 'stock_quantity': stock},
        )


def reverse_seed(apps, schema_editor):
    # Intentionally left as a no-op: we don't want `migrate <app> zero`
    # or unapplying this migration to delete real product data that
    # may have been edited by admins since it was first seeded.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('shoes', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_data, reverse_seed),
    ]
    