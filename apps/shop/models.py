from django.db import models
from apps.users.models import User


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class ModelCategory(models.Model):
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='model_category_icons/', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category of models'
        verbose_name_plural = 'Categories of models'


class Tag(models.Model):
    name = models.CharField(max_length=100)
    is_system = models.BooleanField(default=False)
    icon = models.ImageField(upload_to='tags_icons/', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'


class Attachment(models.Model):
    file_type = models.CharField(max_length=100,
                                 choices=(('1', 'Image'), ('2', 'Video'), ('3', 'Audio'), ('4', 'File')))
    _file = models.FileField(upload_to='attachments/')

    def __str__(self):
        return self.file_type

    class Meta:
        verbose_name = 'Attachment'
        verbose_name_plural = 'Attachments'


class Rating(models.Model):
    amount_of_stars = models.IntegerField()
    prompt = models.ForeignKey('Prompt', on_delete=models.CASCADE, related_name='ratings')

    def __str__(self):
        return f'{self.amount_of_stars} stars for {self.prompt.name}'

    class Meta:
        verbose_name = 'Rating'
        verbose_name_plural = 'Ratings'


class Prompt(models.Model):
    image = models.ImageField(upload_to='prompt_images/')
    model_category = models.ForeignKey(ModelCategory, on_delete=models.CASCADE)
    sell_amount = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    name = models.CharField(max_length=100)
    description = models.TextField()
    token_size = models.IntegerField()
    example_input = models.TextField()
    example_output = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prompt_creator')
    review_amount = models.IntegerField(default=0)
    creation_date = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag)
    amount_of_lookups = models.IntegerField(default=0)
    attachments = models.ManyToManyField(Attachment)
    prompt_template = models.TextField()
    instructions = models.TextField()
    categories = models.ManyToManyField(Category, related_name='prompts')
    favorite_prompts = models.ManyToManyField(
        User, related_name='favorited_by', blank=True, related_query_name='favorited_by')

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        return self.ratings.aggregate(models.Avg('amount_of_stars'))['amount_of_stars__avg']

    class Meta:
        verbose_name = 'Prompt'
        verbose_name_plural = 'Prompts'


class Order(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE, related_name='orders')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_created')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.buyer.username} - {self.prompt.name}"

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
