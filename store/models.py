from django.db import models
from django.urls import reverse
from accounts.models import Account
from django.db.models import Avg,Count


from category.models import Category

# Create your models here.

class Product(models.Model):
    product_name = models.CharField(max_length=200,unique=True)
    slug = models.SlugField(max_length=200,unique=True)
    description = models.TextField(max_length=500,blank=True)
    price = models.IntegerField()
    images = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default = True )
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add = True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name
    
    def get_url(self):
        return reverse('product_detail',args=[self.category.slug,self.slug])
    def averageReview(self):
        avg = 0
        reviews = ReviewRating.objects.filter(product=self,status=True).aggregate(average=Avg('rating'))
        # return reviews["average"]
        
        if reviews["average"] is not None:
            avg = float(reviews["average"])
        return avg
    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self,status=True).aggregate(count=Count('id'))
        count = 0
        if reviews["count"] is not None:
            count = int(reviews["count"])
        return count    
    
class VariationManger(models.Manager):
    def colors(self):
        return super(VariationManger,self).filter(variation_category='color',is_active=True)
    def size(self):
        return super(VariationManger,self).filter(variation_category='size',is_active=True)     

variation_category_choice = (
    ('color','color'),
    ('size','size'),
)
class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100,choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManger()
    def __str__(self):
        return self.variation_value
class ReviewRating(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    subject = models.CharField(max_length=100,blank=True)
    review = models.TextField(max_length=500,blank=True)
    rating = models.FloatField(blank=False)
    ip = models.CharField(max_length=20,blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject
class ProductGallary(models.Model):
    product = models.ForeignKey(Product,default=None,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='store/products/',max_length=255)

    
    def __str__(self):
        return self.product.product_name
    class Meta:
        verbose_name = 'Product Gallary'
        verbose_name_plural = 'Product Gallary'
    
   